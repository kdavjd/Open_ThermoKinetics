"""
Reaction table management for deconvolution analysis.

This module handles the display and management of reactions for deconvolution,
including adding/removing reactions, function selection, and settings configuration.

CRITICAL: This module properly handles path_keys construction to avoid
the errors described in SESSION_CHANGES.md
"""

from collections import defaultdict
from typing import Dict, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import OperationType
from src.core.logger_config import logger

from .config import DeconvolutionConfig
from .settings_dialog import CalculationSettingsDialog


class ReactionTable(QWidget):
    """
    Widget for managing reactions in deconvolution analysis.

    This component handles the display and management of reactions for each file,
    including adding/removing reactions, changing function types, and configuring
    calculation settings.

    CRITICAL: Signal emissions include proper path_keys to fix SESSION_CHANGES.md errors.
    """

    # Signals emitted to parent components
    reaction_added = pyqtSignal(dict)
    reaction_removed = pyqtSignal(dict)
    reaction_chosed = pyqtSignal(dict)
    reaction_function_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the reaction table widget."""
        super().__init__(parent)

        self.config = DeconvolutionConfig()
        self.layout = QVBoxLayout(self)

        # Create control buttons
        self.add_reaction_button = QPushButton(self.config.labels.add_reaction_button)
        self.del_reaction_button = QPushButton(self.config.labels.delete_reaction_button)

        # Setup top buttons layout
        self.top_buttons_layout = QHBoxLayout()
        self.top_buttons_layout.addWidget(self.add_reaction_button)
        self.top_buttons_layout.addWidget(self.del_reaction_button)
        self.layout.addLayout(self.top_buttons_layout)

        # State management
        self.reactions_tables = {}  # file_name -> QTableWidget
        self.reactions_counters = defaultdict(int)  # file_name -> int
        self.active_file = None
        self.active_reaction = ""
        self.calculation_settings = defaultdict(dict)  # file_name -> settings
        self.deconvolution_settings = defaultdict(dict)  # file_name -> settings

        # Settings button
        self.settings_button = QPushButton("settings")
        self.layout.addWidget(self.settings_button)

        # Connect signals
        self.add_reaction_button.clicked.connect(self.add_reaction)
        self.del_reaction_button.clicked.connect(self.del_reaction)
        self.settings_button.clicked.connect(self.open_settings)

    def switch_file(self, file_name: str):
        """
        Switch the active file's reaction table to the specified file_name.
        Create a new table if none exists for that file.

        Args:
            file_name (str): Name of the file to switch to.
        """
        if file_name not in self.reactions_tables:
            # Create new table for this file
            table = QTableWidget()
            table.setColumnCount(self.config.table_layout.columns)
            table.setHorizontalHeaderLabels(self.config.table_layout.column_headers)
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

    def function_changed(self, reaction_name: str, combo: QComboBox):
        """
        Handle changes in the reaction function.

        CRITICAL: Constructs proper path_keys to avoid SESSION_CHANGES.md errors.

        Args:
            reaction_name (str): Name of the reaction.
            combo (QComboBox): ComboBox widget for selecting the function.
        """
        function = combo.currentText()

        # CRITICAL: Path keys should only include reaction info, file_name added in main_tab
        data_change = {
            "path_keys": [reaction_name, "function"],
            "operation": OperationType.UPDATE_VALUE,
            "value": function,
        }

        self.reaction_function_changed.emit(data_change)
        logger.debug(f"Reaction function changed for {reaction_name}: {function}")

    def add_reaction(
        self,
        checked=False,
        reaction_name: Optional[str] = None,
        function_name: Optional[str] = None,
        emit_signal: bool = True,
    ):
        """
        Add a new reaction to the currently active file's table.
        If no file is active, show a warning message.

        Args:
            checked (bool): Unused checkbox state for signal/slot compatibility.
            reaction_name (str, optional): Custom reaction name. Auto-generated if None.
            function_name (str, optional): Initial function name. Defaults to 'gauss'.
            emit_signal (bool): Whether to emit the 'reaction_added' signal.
        """
        if not self.active_file:
            QMessageBox.warning(
                self, self.config.labels.file_not_selected_title, self.config.labels.file_not_selected_message
            )
            return

        table = self.reactions_tables[self.active_file]
        row_count = table.rowCount()
        table.insertRow(row_count)

        # Generate or validate reaction name
        if reaction_name is None:
            reaction_name = f"reaction_{self.reactions_counters[self.active_file]}"
        else:
            # Validate the reaction name format and update counter
            try:
                counter_value = int(reaction_name.split("_")[-1])
                self.reactions_counters[self.active_file] = max(
                    self.reactions_counters[self.active_file], counter_value + 1
                )
            except (ValueError, IndexError):
                logger.error(f"Invalid reaction name format: {reaction_name}")

        # Create function selection combo
        combo = QComboBox()
        combo.addItems(self.config.defaults.function_items)

        if function_name and function_name in self.config.defaults.function_items:
            combo.setCurrentText(function_name)
        else:
            combo.setCurrentText(self.config.defaults.default_function)

        # Connect function change signal
        combo.currentIndexChanged.connect(lambda: self.function_changed(reaction_name, combo))

        # Add items to table
        table.setItem(row_count, 0, QTableWidgetItem(reaction_name))
        table.setCellWidget(row_count, 1, combo)

        # Emit signal if requested
        if emit_signal:
            reaction_data = {"path_keys": [reaction_name], "operation": OperationType.ADD_REACTION}
            self.reaction_added.emit(reaction_data)

        self.reactions_counters[self.active_file] += 1

    def on_fail_add_reaction(self):
        """
        Roll back the last added reaction if addition failed.
        """
        if not self.active_file:
            logger.debug("No file selected. Cannot roll back last addition.")
            return

        table = self.reactions_tables[self.active_file]
        if table.rowCount() > 0:
            last_row = table.rowCount() - 1
            table.removeRow(last_row)
            self.reactions_counters[self.active_file] -= 1
            logger.debug("Failed to add reaction. The last row has been removed.")

    def del_reaction(self):
        """
        Delete the last reaction from the currently active file's table.
        If no file is active or no reactions are available, show a warning.
        """
        if not self.active_file:
            QMessageBox.warning(
                self, self.config.labels.file_not_selected_title, self.config.labels.file_not_selected_message
            )
            return

        table = self.reactions_tables[self.active_file]
        if table.rowCount() > 0:
            last_row = table.rowCount() - 1
            item = table.item(last_row, 0)

            if item is not None:
                reaction_name = item.text()
                table.removeRow(last_row)
                self.reactions_counters[self.active_file] -= 1

                # Emit reaction removed signal
                reaction_data = {
                    "path_keys": [reaction_name],
                    "operation": OperationType.REMOVE_REACTION,
                }
                self.reaction_removed.emit(reaction_data)
            else:
                logger.debug("Attempted to delete an empty cell.")
        else:
            QMessageBox.warning(self, "Empty list", "There are no reactions to delete.")

    def selected_reaction(self, item: QTableWidgetItem):
        """
        Handle selection of a reaction from the table.

        CRITICAL: Emits proper path_keys to fix SESSION_CHANGES.md errors.

        Args:
            item (QTableWidgetItem): The selected table item.
        """
        row = item.row()
        reaction_name = self.reactions_tables[self.active_file].item(row, 0).text()
        self.active_reaction = reaction_name

        logger.debug(f"Active reaction: {reaction_name}")

        # CRITICAL: Emit only reaction_name in path_keys, file_name added in main_tab
        self.reaction_chosed.emit({"path_keys": [reaction_name], "operation": OperationType.HIGHLIGHT_REACTION})

    def open_settings(self):
        """
        Open a dialog to configure calculation and deconvolution settings
        for the current file's reactions.
        """
        if not self.active_file:
            QMessageBox.warning(
                self, self.config.labels.file_not_selected_title, self.config.labels.file_not_selected_message
            )
            return

        # Get reactions for current file
        table = self.reactions_tables[self.active_file]
        reactions = {}
        for row in range(table.rowCount()):
            reaction_name = table.item(row, 0).text()
            combo = table.cellWidget(row, 1)
            reactions[reaction_name] = combo

        # Get current settings
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
                self.open_settings()  # Recursive call to reopen dialog
                return

            # Save settings
            self.calculation_settings[self.active_file] = selected_functions
            self.deconvolution_settings[self.active_file] = {
                "method": selected_method,
                "method_parameters": deconvolution_parameters,
            }

            # Log settings
            logger.info(f"Selected functions: {selected_functions}")
            logger.info(f"Deconvolution settings: {self.deconvolution_settings[self.active_file]}")

            # Show confirmation message
            formatted_functions = "\n".join([f"{key}: {value}" for key, value in selected_functions.items()])
            message = f"    {self.active_file}\n{formatted_functions}"

            QMessageBox.information(
                self,
                self.config.labels.calculation_settings_title,
                f"{self.config.labels.updated_for_message}\n{message}",
            )

    def get_reactions_for_file(self, file_name: str) -> Dict[str, QComboBox]:
        """
        Retrieve a dictionary of reaction names and their ComboBoxes for a given file.

        Args:
            file_name (str): The name of the file.

        Returns:
            dict: Mapping of reaction_name -> QComboBox for reactions in the file.
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
