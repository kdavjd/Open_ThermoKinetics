"""
Reaction Table Component

This module provides the ReactionTable widget for managing reactions in deconvolution analysis,
including adding/removing reactions, function selection, and calculation settings.
"""

from collections import defaultdict

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.gui.dialogs.calculation_dialogs import CalculationSettingsDialog
from src.gui.modeling.modeling_config import get_modeling_config


class ReactionTable(QWidget):
    """
    Widget for managing reactions in deconvolution analysis.

    Provides functionality for adding/removing reactions, selecting function types,
    and configuring calculation settings through a tabular interface.

    Signals:
        reaction_added: Emitted when a new reaction is added
        reaction_removed: Emitted when a reaction is removed
        reaction_chosed: Emitted when a reaction is selected
        reaction_function_changed: Emitted when a reaction's function type changes
    """

    reaction_added = pyqtSignal(dict)
    reaction_removed = pyqtSignal(dict)
    reaction_chosed = pyqtSignal(dict)
    reaction_function_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize the reaction table widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # State tracking
        self.reactions_tables = {}
        self.reactions_counters = defaultdict(int)
        self.active_file = None
        self.active_reaction = ""
        self.calculation_settings = defaultdict(dict)
        self.deconvolution_settings = defaultdict(dict)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface components."""
        self.layout = QVBoxLayout(self)

        # Action buttons
        self.add_reaction_button = QPushButton("add reaction")
        self.del_reaction_button = QPushButton("delete")

        self.top_buttons_layout = QHBoxLayout()
        self.top_buttons_layout.addWidget(self.add_reaction_button)
        self.top_buttons_layout.addWidget(self.del_reaction_button)
        self.layout.addLayout(self.top_buttons_layout)

        # Settings button
        self.settings_button = QPushButton("settings")
        self.layout.addWidget(self.settings_button)

    def _connect_signals(self):
        """Connect button signals to their handlers."""
        self.add_reaction_button.clicked.connect(self.add_reaction)
        self.del_reaction_button.clicked.connect(self.del_reaction)
        self.settings_button.clicked.connect(self.open_settings)

    def switch_file(self, file_name: str):
        """
        Switch the active file's reaction table to the specified file_name.

        Creates a new table if none exists for that file and manages visibility
        of tables for different files.

        Args:
            file_name (str): Name of the file to switch to
        """
        if file_name not in self.reactions_tables:
            # Create new table for this file
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["name", "function"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.itemClicked.connect(self.selected_reaction)

            self.reactions_tables[file_name] = table
            self.layout.addWidget(table)

        # Hide current active table
        if self.active_file and self.active_file in self.reactions_tables:
            self.reactions_tables[self.active_file].setVisible(False)

        # Show new active table
        self.reactions_tables[file_name].setVisible(True)
        self.active_file = file_name

        logger.debug(f"Switched to file: {file_name}")

    def add_reaction(self, checked=False, reaction_name=None, function_name=None, emit_signal=True):
        """
        Add a new reaction to the currently active file's table.

        Args:
            checked (bool): Button checked state (unused)
            reaction_name (str, optional): Custom reaction name
            function_name (str, optional): Initial function type
            emit_signal (bool): Whether to emit the reaction_added signal
        """
        if not self.active_file:
            QMessageBox.warning(self, "No Active File", "Please select a file first.")
            return

        table = self.reactions_tables[self.active_file]

        # Generate reaction name if not provided
        if reaction_name is None:
            self.reactions_counters[self.active_file] += 1
            reaction_name = f"reaction_{self.reactions_counters[self.active_file] - 1}"

        # Add new row
        row_position = table.rowCount()
        table.insertRow(row_position)

        # Set reaction name
        table.setItem(row_position, 0, QTableWidgetItem(reaction_name))

        # Create function selection combo box
        function_combo = QComboBox()
        function_combo.addItems(["ads", "gauss", "fraser"])

        if function_name and function_name in ["ads", "gauss", "fraser"]:
            function_combo.setCurrentText(function_name)

        # Connect function change signal
        function_combo.currentTextChanged.connect(
            lambda text, name=reaction_name: self.function_changed(name, function_combo)
        )

        table.setCellWidget(row_position, 1, function_combo)

        # Emit signal if requested
        if emit_signal:
            self.reaction_added.emit(
                {
                    "path_keys": [reaction_name],
                    "operation": OperationType.ADD_REACTION,
                    "function": function_combo.currentText(),
                }
            )

        logger.info(f"Added reaction: {reaction_name} with function: {function_combo.currentText()}")

    def del_reaction(self):
        """
        Delete the currently selected reaction from the active file's table.
        """
        if not self.active_file or not self.active_reaction:
            QMessageBox.warning(self, "No Selection", "Please select a reaction to delete.")
            return

        table = self.reactions_tables[self.active_file]

        # Find and remove the selected reaction
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.text() == self.active_reaction:
                table.removeRow(row)

                # Emit removal signal
                self.reaction_removed.emit(
                    {"path_keys": [self.active_reaction], "operation": OperationType.REMOVE_REACTION}
                )

                # Clear active reaction
                self.active_reaction = ""

                logger.info(f"Deleted reaction: {self.active_reaction}")
                break

    def selected_reaction(self, item):
        """
        Handle reaction selection in the table.

        Args:
            item (QTableWidgetItem): Selected table item
        """
        if item.column() == 0:  # Only respond to name column clicks
            reaction_name = item.text()
            self.active_reaction = reaction_name

            logger.debug(f"Active reaction: {reaction_name}")
            self.reaction_chosed.emit({"path_keys": [reaction_name], "operation": OperationType.HIGHLIGHT_REACTION})

    def function_changed(self, reaction_name: str, combo: QComboBox):
        """
        Handle changes in the reaction function.

        Args:
            reaction_name (str): Name of the reaction
            combo (QComboBox): ComboBox widget for selecting the function
        """
        function = combo.currentText()
        data_change = {
            "path_keys": [reaction_name, "function"],
            "operation": OperationType.UPDATE_VALUE,
            "value": function,
        }
        self.reaction_function_changed.emit(data_change)
        logger.debug(f"Reaction changed for {reaction_name}: {function}")

    def open_settings(self):
        """
        Open a dialog to configure calculation and deconvolution settings.

        Opens the CalculationSettingsDialog for the current file's reactions,
        allowing users to select functions and configure deconvolution parameters.
        """
        if not self.active_file:
            QMessageBox.warning(self, "File is not selected.", "Choose an experiment")
            return

        table = self.reactions_tables[self.active_file]
        reactions = {}

        # Collect current reactions and their combo boxes
        for row in range(table.rowCount()):
            reaction_name = table.item(row, 0).text()
            combo = table.cellWidget(row, 1)
            reactions[reaction_name] = combo

        # Get initial settings
        initial_settings = self.calculation_settings[self.active_file]
        initial_deconvolution_settings = self.deconvolution_settings.get(self.active_file, {})

        # Open settings dialog
        dialog = CalculationSettingsDialog(reactions, initial_settings, initial_deconvolution_settings, self)

        if dialog.exec():
            selected_functions, selected_method, deconvolution_parameters = dialog.get_selected_functions()

            # Validate that each reaction has at least one function selected
            empty_keys = [key for key, value in selected_functions.items() if not value]
            if empty_keys:
                QMessageBox.warning(
                    self,
                    "unselected functions",
                    f"{', '.join(empty_keys)} must be described by at least one function.",
                )
                self.open_settings()  # Reopen dialog
                return

            # Save settings
            self.calculation_settings[self.active_file] = selected_functions
            self.deconvolution_settings[self.active_file] = {
                "method": selected_method,
                "method_parameters": deconvolution_parameters,
            }

            logger.info(f"Selected functions: {selected_functions}")
            logger.info(f"Deconvolution settings: {self.deconvolution_settings[self.active_file]}")

            # Show confirmation message
            formatted_functions = "\n".join([f"{key}: {value}" for key, value in selected_functions.items()])
            message = f"    {self.active_file}\n{formatted_functions}"
            QMessageBox.information(self, "calculation settings", f"updated for:\n{message}")

    def get_reactions_for_file(self, file_name: str) -> dict:
        """
        Retrieve a dictionary of reaction names and their associated ComboBoxes for a given file.

        Args:
            file_name (str): The name of the file

        Returns:
            dict: Mapping of reaction_name -> QComboBox for reactions in the file
        """
        if file_name not in self.reactions_tables:
            return {}

        table = self.reactions_tables[file_name]
        reactions = {}

        for row in range(table.rowCount()):
            reaction_name = table.item(row, 0).text()
            combo = table.cellWidget(row, 1)
            reactions[reaction_name] = combo

        return reactions

    def get_calculation_settings(self, file_name: str = None) -> dict:
        """
        Get calculation settings for a specific file or the active file.

        Args:
            file_name (str, optional): File name, defaults to active file

        Returns:
            dict: Calculation settings for the file
        """
        target_file = file_name or self.active_file
        return self.calculation_settings.get(target_file, {})

    def get_deconvolution_settings(self, file_name: str = None) -> dict:
        """
        Get deconvolution settings for a specific file or the active file.

        Args:
            file_name (str, optional): File name, defaults to active file

        Returns:
            dict: Deconvolution settings for the file
        """
        target_file = file_name or self.active_file
        return self.deconvolution_settings.get(target_file, {})


class ModelReactionTable(QTableWidget):
    """
    Table widget for model-based kinetics parameter configuration.

    Provides interface for setting activation energy, pre-exponential factor,
    and contribution parameters with optional range constraints for optimization.
    Used in model-based kinetics analysis workflows.
    """

    def __init__(self, parent=None):
        """
        Initialize the model reaction table with parameter inputs.

        Args:
            parent: Parent widget
        """
        config = get_modeling_config()
        table_config = config.table
        super().__init__(table_config.row_count, table_config.column_count, parent)
        self.setHorizontalHeaderLabels(table_config.column_headers)

        self.setColumnHidden(2, True)  # Min column
        self.setColumnHidden(3, True)  # Max column

        # Ea row
        self.setItem(0, 0, QTableWidgetItem(table_config.row_labels[0]))
        self.activation_energy_edit = QLineEdit()
        self.setCellWidget(0, 1, self.activation_energy_edit)

        self.ea_min_item = QLineEdit()
        self.setCellWidget(0, 2, self.ea_min_item)
        self.ea_max_item = QLineEdit()
        self.setCellWidget(0, 3, self.ea_max_item)

        # log(A) row
        self.setItem(1, 0, QTableWidgetItem(table_config.row_labels[1]))
        self.log_a_edit = QLineEdit()
        self.setCellWidget(1, 1, self.log_a_edit)

        self.log_a_min_item = QLineEdit()
        self.setCellWidget(1, 2, self.log_a_min_item)
        self.log_a_max_item = QLineEdit()
        self.setCellWidget(1, 3, self.log_a_max_item)

        # contribution row
        self.setItem(2, 0, QTableWidgetItem(table_config.row_labels[2]))
        self.contribution_edit = QLineEdit()
        self.setCellWidget(2, 1, self.contribution_edit)

        self.contribution_min_item = QLineEdit()
        self.setCellWidget(2, 2, self.contribution_min_item)
        self.contribution_max_item = QLineEdit()
        self.setCellWidget(2, 3, self.contribution_max_item)

        # Store defaults from configuration
        self.defaults = config.reaction_defaults

    def set_ranges_visible(self, visible: bool):
        """
        Toggle visibility of min/max range columns.

        Args:
            visible: Whether to show range columns
        """
        self.setColumnHidden(2, not visible)  # Min column
        self.setColumnHidden(3, not visible)  # Max column
        self.viewport().update()

    def update_value_with_best(self, best_data: dict):
        """
        Update parameter values with optimization results.

        Args:
            best_data: Dictionary containing optimized parameter values
        """
        if not best_data:
            return

        # Update Ea value
        ea_val = best_data.get("Ea")
        if ea_val is not None:
            self.activation_energy_edit.setText(f"{ea_val:.1f}")

        # Update log(A) value
        log_a_val = best_data.get("logA")
        if log_a_val is not None:
            self.log_a_edit.setText(f"{log_a_val:.2f}")

        # Update contribution value
        contribution_val = best_data.get("contribution")
        if contribution_val is not None:
            self.contribution_edit.setText(f"{contribution_val:.3f}")

    def update_table(self, reaction_data: dict):
        """
        Update table with reaction parameter data.

        Args:
            reaction_data: Dictionary containing reaction parameters and bounds
        """
        if not reaction_data:
            self.activation_energy_edit.clear()
            self.log_a_edit.clear()
            self.contribution_edit.clear()
            self.ea_min_item.clear()
            self.ea_max_item.clear()
            self.log_a_min_item.clear()
            self.log_a_max_item.clear()
            self.contribution_min_item.clear()
            self.contribution_max_item.clear()
            return

        self.activation_energy_edit.setText(str(reaction_data.get("Ea", self.defaults.ea_default)))
        self.log_a_edit.setText(str(reaction_data.get("log_A", self.defaults.log_a_default)))
        self.contribution_edit.setText(str(reaction_data.get("contribution", self.defaults.contribution_default)))

        self.ea_min_item.setText(str(reaction_data.get("Ea_min", self.defaults.ea_range[0])))
        self.ea_max_item.setText(str(reaction_data.get("Ea_max", self.defaults.ea_range[1])))

        self.log_a_min_item.setText(str(reaction_data.get("log_A_min", self.defaults.log_a_range[0])))
        self.log_a_max_item.setText(str(reaction_data.get("log_A_max", self.defaults.log_a_range[1])))

        self.contribution_min_item.setText(
            str(reaction_data.get("contribution_min", self.defaults.contribution_range[0]))
        )
        self.contribution_max_item.setText(
            str(reaction_data.get("contribution_max", self.defaults.contribution_range[1]))
        )
