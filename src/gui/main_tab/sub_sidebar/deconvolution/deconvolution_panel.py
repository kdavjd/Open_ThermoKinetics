"""
Main orchestrating panel for deconvolution analysis.

This file serves as the main orchestrator for the deconvolution module,
coordinating between child components while maintaining the same external
interface as the original DeconvolutionSubBar.

CRITICAL: This module properly handles signal routing and path_keys construction
to avoid the errors described in SESSION_CHANGES.md
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from .calculation_controls import CalculationControls
from .coefficients_view import CoefficientsView
from .config import DeconvolutionConfig
from .file_transfer import FileTransferButtons
from .reaction_table import ReactionTable


class DeconvolutionPanel(QWidget):
    """
    Main orchestrating panel for deconvolution analysis.

    This class coordinates all deconvolution-related components and maintains
    the same external interface as the original DeconvolutionSubBar for
    backward compatibility.

    CRITICAL: Proper signal routing ensures path_keys are constructed correctly
    to fix the errors described in SESSION_CHANGES.md
    """

    # External signals - maintain same interface as original DeconvolutionSubBar
    update_value = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the deconvolution panel with all child components."""
        super().__init__(parent)

        self.config = DeconvolutionConfig()

        # Setup layout
        layout = QVBoxLayout(self)

        # Initialize child components
        self.reactions_table = ReactionTable(self)
        self.coeffs_table = CoefficientsView(self)
        self.file_transfer_buttons = FileTransferButtons(self)
        self.calc_buttons = CalculationControls(self)

        # Add components to layout
        layout.addWidget(self.reactions_table)
        layout.addWidget(self.coeffs_table)
        layout.addWidget(self.file_transfer_buttons)
        layout.addWidget(self.calc_buttons)

        # Setup signal connections
        self._connect_signals()

    def _connect_signals(self):
        """
        Connect internal component signals to handle communication.

        CRITICAL: This method ensures proper signal routing and path_keys
        construction to avoid the SESSION_CHANGES.md errors.
        """
        # Coefficients table updates
        self.coeffs_table.update_value.connect(self._handle_coeffs_update)

        # Reaction table function changes
        self.reactions_table.reaction_function_changed.connect(self._handle_function_update)
        # Reaction selection changes - update coefficients table context
        self.reactions_table.reaction_chosed.connect(self._handle_reaction_selection)

    def _handle_coeffs_update(self, data: dict):
        """
        Handle coefficient updates from CoefficientsView.

        CRITICAL: Do NOT modify path_keys here - they are already correctly constructed
        in CoefficientsView. This fixes the SESSION_CHANGES.md duplicate reaction_name error.

        Args:
            data (dict): Update data containing path_keys and new value.
        """
        # CRITICAL: Just pass through the data without modification
        # CoefficientsView already constructs correct path_keys: [reaction_name, bound_type, param_name]
        # file_name will be added by main_tab.py
        self.update_value.emit(data)

    def _handle_function_update(self, data: dict):
        """
        Handle reaction function updates from ReactionTable.

        Args:
            data (dict): Data for updating the reaction function.
        """
        if self.reactions_table.active_reaction is not None:
            self.update_value.emit(data)

    def _handle_reaction_selection(self, data: dict):
        """
        Handle reaction selection changes.
        Update coefficients table context for proper path_keys construction.

        Args:
            data (dict): Selection data containing reaction path_keys.
        """
        if data.get("path_keys") and len(data["path_keys"]) > 0:
            reaction_name = data["path_keys"][0]
            # Update coefficients table context with current file and reaction
            self.coeffs_table.set_context(self.reactions_table.active_file, reaction_name)

    def open_settings_dialog(self):
        """
        Open the calculation settings dialog via the ReactionTable instance.
        Maintains backward compatibility with original interface.
        """
        self.reactions_table.open_settings()

    def get_reactions_for_file(self, file_name: str) -> dict:
        """
        Retrieve a dictionary of reaction names and their ComboBoxes for a file.
        Maintains backward compatibility with original interface.

        Args:
            file_name (str): The name of the file.

        Returns:
            dict: Mapping of reaction_name -> QComboBox for reactions in the file.
        """
        return self.reactions_table.get_reactions_for_file(file_name)

    # Backward compatibility methods - delegate to child components
    @property
    def active_file(self):
        """Get the currently active file name."""
        return self.reactions_table.active_file

    @property
    def active_reaction(self):
        """Get the currently active reaction name."""
        return self.reactions_table.active_reaction

    def switch_file(self, file_name: str):
        """
        Switch the active file's reaction table.
        Maintains backward compatibility with original interface.

        Args:
            file_name (str): Name of the file to switch to.
        """
        self.reactions_table.switch_file(file_name)

    def add_reaction(self, checked=False, reaction_name=None, function_name=None, emit_signal=True):
        """
        Add a new reaction to the currently active file's table.
        Maintains backward compatibility with original interface.
        """
        self.reactions_table.add_reaction(checked, reaction_name, function_name, emit_signal)

    def on_fail_add_reaction(self):
        """
        Roll back the last added reaction if addition failed.
        Maintains backward compatibility with original interface.
        """
        self.reactions_table.on_fail_add_reaction()

    def fill_coeffs_table(self, reaction_params: dict):
        """
        Fill the coefficients table with reaction parameters.
        Maintains backward compatibility with original interface.

        Args:
            reaction_params (dict): Reaction parameters for display.
        """
        self.coeffs_table.fill_table(reaction_params)

    def handle_update_coeffs_value(self, updates: list):
        """
        Handle batch updates to coefficient values.
        Maintains backward compatibility with original interface.

        Args:
            updates (list): List of coefficient updates.
        """
        self.coeffs_table.handle_update_value(updates)
