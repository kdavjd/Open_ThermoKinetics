"""
Coefficients table for displaying and editing reaction parameters.
Handles coefficient bounds with proper path_keys structure.

CRITICAL: This component must handle path_keys updates correctly to avoid errors
described in SESSION_CHANGES.md
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class CoefficientsView(QTableWidget):
    """
    Table widget for displaying and editing reaction coefficients.

    CRITICAL: Must properly construct path_keys for nested data access
    to avoid the errors described in SESSION_CHANGES.md
    """

    update_value = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the coefficients table."""
        super().__init__(5, 2, parent)
        self.setObjectName("input_numeric")

        self.header_labels = ["from", "to"]
        self.row_labels_dict = {
            "gauss": ["h", "z", "w"],
            "fraser": ["h", "z", "w", "fr"],
            "ads": ["h", "z", "w", "ads1", "ads2"],
        }
        self.default_row_labels = ["h", "z", "w", "_", "_"]

        self.setHorizontalHeaderLabels(self.header_labels)
        self.setVerticalHeaderLabels(self.default_row_labels)

        # Set consistent row height (matches reaction_table row height)
        self.verticalHeader().setDefaultSectionSize(28)

        self.mock_table()
        self.calculate_fixed_height()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Connect signal
        self.cellChanged.connect(self.update_reaction_params)

        # State management
        self._is_table_filling = False
        self.active_file = None
        self.active_reaction = None

    def calculate_fixed_height(self):
        """Adjust the table's height based on the number of rows and header heights."""
        row_height = self.rowHeight(0)
        borders_height = len(self.default_row_labels) * 2
        header_height = self.horizontalHeader().height()
        total_height = (row_height * len(self.default_row_labels)) + header_height + borders_height
        self.setFixedHeight(total_height)

    def mock_table(self):
        """Fill the table with 'NaN' as placeholder values."""
        for i in range(len(self.default_row_labels)):
            for j in range(len(self.header_labels)):
                self.setItem(i, j, QTableWidgetItem("NaN"))

    def set_context(self, active_file: str, active_reaction: str):
        """
        Set the current context for proper path_keys construction.

        CRITICAL: This method ensures we have the complete path_keys context
        needed to avoid the SESSION_CHANGES.md errors.

        Args:
            active_file (str): Currently active file name
            active_reaction (str): Currently active reaction name
        """
        self.active_file = active_file
        self.active_reaction = active_reaction

    def fill_table(self, reaction_params: dict):
        """
        Fill the table with given reaction parameters.

        Args:
            reaction_params (dict): Dictionary containing 'lower_bound_coeffs' and 'upper_bound_coeffs',
                                    each a list with indices [2] for parameter data.
        """
        logger.debug(f"Received reaction parameters for the table: {reaction_params}")
        param_keys = ["lower_bound_coeffs", "upper_bound_coeffs"]

        if param_keys[0] not in reaction_params or param_keys[1] not in reaction_params:
            logger.error(f"Missing required keys in reaction_params: {list(reaction_params.keys())}")
            return

        function_type = reaction_params[param_keys[0]][1]
        if function_type not in self.row_labels_dict:
            logger.error(f"Unknown function type: {function_type}")
            return

        self._is_table_filling = True
        row_labels = self.row_labels_dict[function_type]
        self.setRowCount(len(row_labels))
        self.setVerticalHeaderLabels(row_labels)

        for j, key in enumerate(param_keys):
            try:
                # data structure: [x_range, function_type, params]
                data = reaction_params[key][2]
                for i in range(min(len(row_labels), len(data))):
                    value = f"{data[i]:.3f}"
                    self.setItem(i, j, QTableWidgetItem(value))
            except (IndexError, TypeError) as e:
                logger.error(f"Index error processing data '{key}': {e}")

        self.mock_remaining_cells(len(row_labels))
        self._is_table_filling = False

    def mock_remaining_cells(self, num_rows: int):
        """
        Fill remaining cells below the actual data with 'NaN'.
        This ensures a consistent table size if needed.
        """
        for i in range(num_rows, len(self.default_row_labels)):
            for j in range(len(self.header_labels)):
                self.setItem(i, j, QTableWidgetItem("NaN"))

    def update_reaction_params(self, row: int, column: int):
        """
        Handle updates to the reaction parameter cell values.
        Emits 'update_value' signal with the changed data.

        CRITICAL: This method must construct complete path_keys to avoid
        the errors described in SESSION_CHANGES.md

        Args:
            row (int): Row index of the changed cell.
            column (int): Column index of the changed cell.
        """
        if self._is_table_filling:
            return

        if not self.active_file or not self.active_reaction:
            console.log("Select a file and reaction before changing values.")
            return

        try:
            item = self.item(row, column)
            if not item:
                return

            value = float(item.text())
            row_label = self.verticalHeaderItem(row).text()
            column_label = self.horizontalHeaderItem(column).text()

            # Convert column label to bound type
            bound_type = self.column_to_bound(column_label)

            # CRITICAL: Use only reaction_name, bound_type, param_name - file_name will be added by main_tab.py
            # This fixes the SESSION_CHANGES.md error where duplicate file_name caused issues
            path_keys = [self.active_reaction, bound_type, row_label]

            data_change = {
                "path_keys": path_keys,
                "operation": OperationType.UPDATE_VALUE,
                "value": value,
            }
            self.update_value.emit(data_change)

        except ValueError as e:
            console.log(f"Invalid data for conversion to number: row {row + 1}, column {column + 1}")
            logger.error(f"Invalid data for conversion to number: row {row}, column {column}: {e}")

    def column_to_bound(self, column_label: str) -> str:
        """Convert column label to bound coefficient type."""
        return {"from": "lower_bound_coeffs", "to": "upper_bound_coeffs"}.get(column_label, "")

    def handle_update_value(self, updates: list):
        """
        Handle batch updates to coefficient values.

        CRITICAL: This method properly constructs full path_keys for hierarchical data access
        to fix the SESSION_CHANGES.md errors.

        Args:
            updates (list): List of update dictionaries
        """
        if not self.active_file or not self.active_reaction:
            console.log("Select a file and reaction before updating values.")
            return

        for update in updates:
            original_path_keys = update["path_keys"]

            # CRITICAL: Construct complete path_keys including file and reaction context
            # This fixes the error from SESSION_CHANGES.md where path construction was incomplete
            full_path_keys = [self.active_file, self.active_reaction] + original_path_keys

            update["path_keys"] = full_path_keys
            self.update_value.emit(update)
