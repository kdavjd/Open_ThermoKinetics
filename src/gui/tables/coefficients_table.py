"""
Coefficients Table Component

This module provides the CoeffsTable widget for displaying and editing reaction parameters
in a tabular format with proper validation and signal emission for data updates.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class CoeffsTable(QTableWidget):
    """
    Table widget for displaying and editing reaction coefficients.

    Provides functionality for displaying parameter bounds (lower/upper) for different
    reaction function types (ads, gauss, fraser) with appropriate labels and validation.

    Signals:
        update_value: Emitted when a parameter value is changed
    """

    update_value = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize the coefficients table.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Table configuration
        self.header_labels = ["from", "to"]
        self.default_row_labels = ["h", "z", "w", "ads1", "ads2", "n", "skewness"]
        self.row_labels_dict = {
            "ads": ["h", "z", "w", "ads1", "ads2"],
            "gauss": ["h", "z", "w"],
            "fraser": ["h", "z", "w", "n", "skewness"],
        }

        # Setup table structure
        self._setup_table()

        # State tracking
        self._is_table_filling = False

        # Connect signals
        self.itemChanged.connect(self.update_reaction_params)

    def _setup_table(self):
        """Initialize table structure and headers."""
        self.setColumnCount(len(self.header_labels))
        self.setRowCount(len(self.default_row_labels))

        self.setHorizontalHeaderLabels(self.header_labels)
        self.setVerticalHeaderLabels(self.default_row_labels)

        # Fill with default NaN values
        self._fill_with_default_values()

    def _fill_with_default_values(self):
        """Fill table with default 'NaN' values."""
        for i in range(len(self.default_row_labels)):
            for j in range(len(self.header_labels)):
                self.setItem(i, j, QTableWidgetItem("NaN"))

    def fill_table(self, reaction_params: dict):
        """
        Fill the table with given reaction parameters.

        Args:
            reaction_params (dict): Dictionary containing 'lower_bound_coeffs' and 'upper_bound_coeffs',
                                  each a list with indices [2] for parameter data.
        """
        logger.debug(f"Received reaction parameters for the table: {reaction_params}")

        param_keys = ["lower_bound_coeffs", "upper_bound_coeffs"]
        function_type = reaction_params[param_keys[0]][1]

        if function_type not in self.row_labels_dict:
            logger.error(f"Unknown function type: {function_type}")
            return

        self._is_table_filling = True

        # Update table structure for function type
        row_labels = self.row_labels_dict[function_type]
        self.setRowCount(len(row_labels))
        self.setVerticalHeaderLabels(row_labels)

        # Fill parameter data
        for j, key in enumerate(param_keys):
            try:
                # Data structure: [x_range, function_type, params]
                data = reaction_params[key][2]
                for i in range(min(len(row_labels), len(data))):
                    value = f"{data[i]:.3f}"
                    self.setItem(i, j, QTableWidgetItem(value))
            except IndexError as e:
                logger.error(f"Index error processing data '{key}': {e}")

        self._mock_remaining_cells(len(row_labels))
        self._is_table_filling = False

    def _mock_remaining_cells(self, num_rows):
        """
        Fill remaining cells below the actual data with 'NaN'.

        Args:
            num_rows (int): Number of actual data rows
        """
        for i in range(num_rows, len(self.default_row_labels)):
            for j in range(len(self.header_labels)):
                self.setItem(i, j, QTableWidgetItem("NaN"))

    def update_reaction_params(self, item):
        """
        Handle updates to the reaction parameter cell values.

        Args:
            item (QTableWidgetItem): The item that was changed
        """
        if not self._is_table_filling:
            try:
                row = item.row()
                column = item.column()
                value = float(item.text())
                row_label = self.verticalHeaderItem(row).text()
                column_label = self.horizontalHeaderItem(column).text()

                path_keys = [self._column_to_bound(column_label), row_label]
                data_change = {
                    "path_keys": path_keys,
                    "operation": OperationType.UPDATE_VALUE,
                    "value": value,
                }
                self.update_value.emit(data_change)

            except ValueError as e:
                console.log(f"Invalid data for conversion to number: row {row+1}, column {column+1}")
                logger.error(f"Invalid data for conversion to number: row {row}, column {column}: {e}")

    def _column_to_bound(self, column_label: str) -> str:
        """
        Convert column label to corresponding bound coefficient name.

        Args:
            column_label (str): Column header label

        Returns:
            str: Corresponding bound coefficient name
        """
        return {"from": "lower_bound_coeffs", "to": "upper_bound_coeffs"}.get(column_label, "")
