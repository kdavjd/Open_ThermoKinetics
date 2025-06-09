"""
Calculation control buttons and widgets for deconvolution analysis.
Handles start/stop/cancel operations for calculations.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.app_settings import OperationType
from src.core.logger_config import logger


class CalculationButtons(QWidget):
    """
    Control buttons for calculation operations.

    Provides start, stop, and cancel functionality for calculation processes.
    """

    calculation_started = pyqtSignal(dict)
    calculation_stopped = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize calculation control buttons.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.layout = QHBoxLayout(self)

        # Create buttons
        self.start_button = QPushButton("Start Calculation")
        self.stop_button = QPushButton("Stop")
        self.cancel_button = QPushButton("Cancel")

        # Setup button states
        self.stop_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        # Add buttons to layout
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.cancel_button)

        # Connect signals
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)

        logger.debug("CalculationButtons initialized")

    def _on_start_clicked(self):
        """Handle start button click."""
        self._set_calculation_state(True)
        self.calculation_started.emit({"operation": "start_calculation"})
        logger.debug("Calculation start requested")

    def _on_stop_clicked(self):
        """Handle stop button click."""
        self._set_calculation_state(False)
        self.calculation_stopped.emit({"operation": "stop_calculation"})
        logger.debug("Calculation stop requested")

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self._set_calculation_state(False)
        self.calculation_stopped.emit({"operation": "cancel_calculation"})
        logger.debug("Calculation cancel requested")

    def _set_calculation_state(self, running: bool):
        """
        Update button states based on calculation status.

        Args:
            running: Whether calculation is currently running
        """
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.cancel_button.setEnabled(running)

    def revert_to_default(self):
        """Revert buttons to default state (calculation stopped)."""
        self._set_calculation_state(False)
        logger.debug("Calculation buttons reverted to default state")

    def set_enabled(self, enabled: bool):
        """
        Enable or disable all buttons.

        Args:
            enabled: Whether buttons should be enabled
        """
        self.start_button.setEnabled(enabled)
        if not enabled:
            self.stop_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
        logger.debug(f"Calculation buttons enabled: {enabled}")


class CalcButtons(QWidget):
    """
    Simplified calculation control buttons for deconvolution operations.

    Provides start/stop functionality with dynamic button state management
    for calculation processes in deconvolution analysis.

    Signals:
        calculation_started: Emitted when calculation is started
        calculation_stopped: Emitted when calculation is stopped
    """

    calculation_started = pyqtSignal(dict)
    calculation_stopped = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize calculation control buttons.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Create buttons
        self.start_button = QPushButton("calculate")
        self.stop_button = QPushButton("stop calculating")

        # Add start button initially
        self.layout.addWidget(self.start_button)

        # Connect signals
        self.start_button.clicked.connect(self.check_and_start_calculation)
        self.stop_button.clicked.connect(self.stop_calculation)

        # State tracking
        self.is_calculating = False
        self.parent = parent

    def check_and_start_calculation(self):
        """
        Check conditions and start calculation if valid.

        Validates that all required conditions are met before starting
        the calculation process and switches to stop button state.
        """
        if not self.is_calculating:
            self.is_calculating = True

            # Switch to stop button
            self.layout.replaceWidget(self.start_button, self.stop_button)
            self.start_button.hide()
            self.stop_button.show()

            # Emit calculation started signal
            self.calculation_started.emit({"operation": OperationType.DECONVOLUTION})

            logger.info("Calculation started")

    def stop_calculation(self):
        """
        Stop the currently running calculation.

        Stops the calculation process and reverts to the start button state.
        """
        if self.is_calculating:
            self.is_calculating = False

            # Switch back to start button
            self.layout.replaceWidget(self.stop_button, self.start_button)
            self.stop_button.hide()
            self.start_button.show()

            # Emit calculation stopped signal
            self.calculation_stopped.emit({"operation": OperationType.DECONVOLUTION})

            logger.info("Calculation stopped")

    def revert_to_default(self):
        """
        Revert button state to default (start button visible).

        Used to reset the button state when calculations complete
        or are interrupted externally.
        """
        if self.is_calculating:
            self.is_calculating = False

            # Ensure start button is visible
            self.layout.replaceWidget(self.stop_button, self.start_button)
            self.stop_button.hide()
            self.start_button.show()

            logger.debug("Calculation buttons reverted to default state")


class ActionButtonsBlock(QWidget):
    """
    Block of action buttons for data operations.

    Provides buttons for common data transformation operations.
    """

    cancel_changes_clicked = pyqtSignal()
    derivative_clicked = pyqtSignal()
    deconvolution_clicked = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize action buttons block.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.layout = QHBoxLayout(self)

        # Create action buttons
        self.cancel_changes_button = QPushButton("Cancel Changes")
        self.derivative_button = QPushButton("To Derivative")
        self.deconvolution_button = QPushButton("Deconvolution")

        # Add buttons to layout
        self.layout.addWidget(self.cancel_changes_button)
        self.layout.addWidget(self.derivative_button)
        self.layout.addWidget(self.deconvolution_button)

        # Connect signals
        self.cancel_changes_button.clicked.connect(self.cancel_changes_clicked.emit)
        self.derivative_button.clicked.connect(self.derivative_clicked.emit)
        self.deconvolution_button.clicked.connect(self.deconvolution_clicked.emit)

        logger.debug("ActionButtonsBlock initialized")

    def set_enabled(self, enabled: bool):
        """
        Enable or disable all action buttons.

        Args:
            enabled: Whether buttons should be enabled
        """
        self.cancel_changes_button.setEnabled(enabled)
        self.derivative_button.setEnabled(enabled)
        self.deconvolution_button.setEnabled(enabled)
        logger.debug(f"Action buttons enabled: {enabled}")
