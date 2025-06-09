"""
Model Calculation Controls Component

This module provides calculation control widgets for model-based analysis,
including simulation buttons and settings management.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget

from src.core.app_settings import OperationType


class ModelCalcButtons(QWidget):
    """
    Widget providing calculation control buttons for model-based analysis.

    Manages simulation start/stop state and emits signals for calculation operations.

    Signals:
        simulation_started: Emitted when simulation starts with operation data
        simulation_stopped: Emitted when simulation is stopped
    """

    simulation_started = pyqtSignal(dict)
    simulation_stopped = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize calculation control buttons.

        Args:
            parent: Parent widget reference for accessing scheme data
        """
        super().__init__(parent)
        self.parent_ref = parent
        self.is_calculating = False

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.settings_button = QPushButton("Settings")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        layout.addWidget(self.settings_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.stop_button.hide()

        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.start_button.clicked.connect(self.check_and_start_simulation)
        self.stop_button.clicked.connect(self.stop_simulation)

    def open_settings_dialog(self):
        """Open calculation settings dialog through parent reference."""
        if hasattr(self.parent_ref, "open_settings"):
            self.parent_ref.open_settings()

    def check_and_start_simulation(self):
        """
        Validate scheme and start simulation.

        Extracts reaction scheme from parent and emits simulation started signal.
        """
        scheme = {}
        if hasattr(self.parent_ref, "models_scene"):
            scheme = self.parent_ref.models_scene.get_reaction_scheme_as_json()

        data = {
            "operation": OperationType.MODEL_BASED_CALCULATION,
            "scheme": scheme,
        }

        self.simulation_started.emit(data)
        self.start_simulation()

    def start_simulation(self):
        """Switch to calculating state with stop button visible."""
        self.is_calculating = True
        self.layout().replaceWidget(self.start_button, self.stop_button)
        self.start_button.hide()
        self.stop_button.show()

    def stop_simulation(self):
        """Stop simulation and return to ready state."""
        if self.is_calculating:
            self.simulation_stopped.emit({"operation": OperationType.STOP_CALCULATION})
            self.is_calculating = False
            self.layout().replaceWidget(self.stop_button, self.start_button)
            self.stop_button.hide()
            self.start_button.show()


class RangeAndCalculateWidget(QWidget):
    """
    Widget providing checkboxes for range display and calculation options.

    Allows users to toggle range visibility and calculation mode for model-based analysis.

    Signals:
        showRangeToggled: Emitted when range visibility is toggled
        calculateToggled: Emitted when calculation mode is toggled
    """

    showRangeToggled = pyqtSignal(bool)
    calculateToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        """
        Initialize range and calculate control checkboxes.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.showRangeCheckbox = QCheckBox("Show Range")
        self.calculateCheckbox = QCheckBox("Calculate")

        layout.addWidget(self.showRangeCheckbox)
        layout.addWidget(self.calculateCheckbox)

        self.showRangeCheckbox.stateChanged.connect(
            lambda state: self.showRangeToggled.emit(state == Qt.CheckState.Checked.value)
        )
        self.calculateCheckbox.stateChanged.connect(
            lambda state: self.calculateToggled.emit(state == Qt.CheckState.Checked.value)
        )
