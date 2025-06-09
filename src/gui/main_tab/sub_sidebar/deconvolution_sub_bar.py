# filepath: c:\IDE\repository\solid-state_kinetics\src\gui\main_tab\sub_sidebar\deconvolution_sub_bar.py
"""
Deconvolution Sub Bar Component

Main container for deconvolution analysis tools, integrating reaction management,
coefficients editing, file operations, and calculation controls.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.core.logger_console import LoggerConsole as console
from src.gui.controls.calculation_controls import CalcButtons
from src.gui.experiment.file_operations import FileTransferButtons
from src.gui.tables.coefficients_table import CoeffsTable
from src.gui.tables.reaction_table import ReactionTable


class DeconvolutionSubBar(QWidget):
    """
    Main deconvolution analysis sidebar widget.

    Integrates reaction management, coefficients editing, file operations,
    and calculation controls into a unified interface for deconvolution analysis.

    Signals:
        update_value: Emitted when parameter values are updated
    """

    update_value = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize the deconvolution sub bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface components."""
        layout = QVBoxLayout(self)

        # Create component widgets
        self.reactions_table = ReactionTable(self)
        self.coeffs_table = CoeffsTable(self)
        self.file_transfer_buttons = FileTransferButtons(self)
        self.calc_buttons = CalcButtons(self)

        # Add widgets to layout
        layout.addWidget(self.reactions_table)
        layout.addWidget(self.coeffs_table)
        layout.addWidget(self.file_transfer_buttons)
        layout.addWidget(self.calc_buttons)

    def _connect_signals(self):
        """Connect component signals to handlers."""
        # Connect coefficient table updates
        self.coeffs_table.update_value.connect(self.handle_update_value)

        # Connect reaction table function changes
        self.reactions_table.reaction_function_changed.connect(self.handle_update_function_value)

    def handle_update_value(self, data: dict):
        """
        Handle updates to reaction parameter values.

        Inserts the active reaction into path_keys and emits the update_value signal.

        Args:
            data (dict): Update data containing path_keys and new value
        """
        if self.reactions_table.active_reaction:
            data["path_keys"].insert(0, self.reactions_table.active_reaction)
            self.update_value.emit(data)
        else:
            console.log("Select a reaction before changing its values.")

    def handle_update_function_value(self, data: dict):
        """
        Handle updates to a reaction's function.

        Args:
            data (dict): Data for updating the reaction function
        """
        if self.reactions_table.active_reaction is not None:
            self.update_value.emit(data)

    def open_settings_dialog(self):
        """
        Open the calculation settings dialog via the ReactionTable instance.

        Delegates to the ReactionTable's settings dialog functionality.
        """
        self.reactions_table.open_settings()

    def get_reactions_for_file(self, file_name: str) -> dict:
        """
        Retrieve a dictionary of reaction names and their associated ComboBoxes for a given file.

        Args:
            file_name (str): The name of the file

        Returns:
            dict: Mapping of reaction_name -> QComboBox for reactions in the file
        """
        return self.reactions_table.get_reactions_for_file(file_name)

    def switch_file(self, file_name: str):
        """
        Switch the active file for all components.

        Args:
            file_name (str): Name of the file to switch to
        """
        self.reactions_table.switch_file(file_name)

    def add_reaction(self, reaction_name: str = None, function_name: str = None, emit_signal: bool = True):
        """
        Add a new reaction through the reaction table.

        Args:
            reaction_name (str, optional): Custom reaction name
            function_name (str, optional): Initial function type
            emit_signal (bool): Whether to emit the reaction_added signal
        """
        self.reactions_table.add_reaction(
            checked=False, reaction_name=reaction_name, function_name=function_name, emit_signal=emit_signal
        )

    def get_calculation_settings(self, file_name: str = None) -> dict:
        """
        Get calculation settings for a specific file.

        Args:
            file_name (str, optional): File name, defaults to active file

        Returns:
            dict: Calculation settings for the file
        """
        return self.reactions_table.get_calculation_settings(file_name)

    def get_deconvolution_settings(self, file_name: str = None) -> dict:
        """
        Get deconvolution settings for a specific file.

        Args:
            file_name (str, optional): File name, defaults to active file

        Returns:
            dict: Deconvolution settings for the file
        """
        return self.reactions_table.get_deconvolution_settings(file_name)

    def fill_coefficients_table(self, reaction_params: dict):
        """
        Fill the coefficients table with reaction parameters.

        Args:
            reaction_params (dict): Reaction parameters to display
        """
        self.coeffs_table.fill_table(reaction_params)

    def revert_calculation_buttons(self):
        """
        Revert calculation buttons to default state.

        Used when calculations complete or are interrupted externally.
        """
        self.calc_buttons.revert_to_default()
