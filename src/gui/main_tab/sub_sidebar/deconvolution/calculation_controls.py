"""
Calculation control buttons for deconvolution analysis.

This module provides the start/stop calculation controls for the deconvolution
process, including validation and state management.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QPushButton, QVBoxLayout, QWidget

from src.core.app_settings import OperationType

from .config import DeconvolutionConfig


class CalculationControls(QWidget):
    """
    Widget providing calculation control functionality.

    This component handles starting and stopping deconvolution calculations,
    including validation of required settings and state management.
    """

    calculation_started = pyqtSignal(dict)
    calculation_stopped = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the calculation controls widget."""
        super().__init__(parent)

        self.config = DeconvolutionConfig()
        self.layout = QVBoxLayout(self)

        # Create control buttons
        self.start_button = QPushButton("calculate")
        self.stop_button = QPushButton("stop calculating")

        # Add start button to layout (stop button added dynamically)
        self.layout.addWidget(self.start_button)

        # Connect signals
        self.start_button.clicked.connect(self.check_and_start_calculation)
        self.stop_button.clicked.connect(self.stop_calculation)

        # State management
        self.is_calculating = False
        self.parent_panel = parent

    def revert_to_default(self):
        """
        Revert the UI to default state (show start button, hide stop button).
        """
        if self.is_calculating:
            self.is_calculating = False
            self.layout.replaceWidget(self.stop_button, self.start_button)
            self.stop_button.hide()
            self.start_button.show()

    def check_and_start_calculation(self):
        """
        Check that a file is active and settings are chosen before starting calculation.
        If settings are missing, prompt the user to configure them.
        """
        # Get parent panel reference
        if not self.parent_panel:
            return

        parent_panel = self.parent_panel

        # Check if file is selected
        if not parent_panel.reactions_table.active_file:
            QMessageBox.warning(
                self, self.config.labels.file_not_selected_title, self.config.labels.file_not_selected_message
            )
            return

        # Check if settings are configured
        active_file = parent_panel.reactions_table.active_file
        settings = parent_panel.reactions_table.calculation_settings.get(active_file, {})
        deconvolution_settings = parent_panel.reactions_table.deconvolution_settings.get(active_file, {})

        if not settings or not deconvolution_settings:
            QMessageBox.information(self, "Settings are required.", "The calculation settings are not set.")
            parent_panel.open_settings_dialog()
        else:
            # Start calculation with proper data structure
            data = {
                "path_keys": [],
                "operation": OperationType.DECONVOLUTION,
                "chosen_functions": settings,
                "deconvolution_settings": deconvolution_settings,
            }
            self.calculation_started.emit(data)
            self.start_calculation()

    def start_calculation(self):
        """
        Switch to 'stop' mode indicating that the calculation is in progress.
        """
        self.is_calculating = True
        self.layout.replaceWidget(self.start_button, self.stop_button)
        self.start_button.hide()
        self.stop_button.show()

    def stop_calculation(self):
        """
        Stop the current calculation and revert to start mode.
        """
        if self.is_calculating:
            self.calculation_stopped.emit({"operation": OperationType.STOP_CALCULATION})
            self.is_calculating = False
            self.layout.replaceWidget(self.stop_button, self.start_button)
            self.stop_button.hide()
            self.start_button.show()
