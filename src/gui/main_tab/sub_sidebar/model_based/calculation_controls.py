"""
Calculation control widgets for model-based analysis.
Contains widgets for starting/stopping calculations and toggling settings.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget

from src.core.app_settings import OperationType


class ModelCalcButtons(QWidget):
    """Widget containing calculation control buttons."""

    simulation_started = pyqtSignal(dict)
    simulation_stopped = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize calculation control buttons."""
        super().__init__(parent)
        self.parent_ref = parent
        self.is_calculating = False

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Create buttons
        self.settings_button = QPushButton("Settings")
        self.settings_button.setObjectName("btn_secondary")
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("btn_primary")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("btn_danger")

        layout.addWidget(self.settings_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # Initially hide stop button
        self.stop_button.hide()

        # Connect signals
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.start_button.clicked.connect(self.check_and_start_simulation)
        self.stop_button.clicked.connect(self.stop_simulation)

    def open_settings_dialog(self):
        """Open settings dialog through parent reference."""
        if hasattr(self.parent_ref, "open_settings"):
            self.parent_ref.open_settings()

    def check_and_start_simulation(self):
        """Start simulation with current scheme data."""
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
        """Switch to stop button and mark as calculating."""
        self.is_calculating = True
        self.layout().replaceWidget(self.start_button, self.stop_button)
        self.start_button.hide()
        self.stop_button.show()

    def stop_simulation(self):
        """Stop calculation and switch back to start button."""
        if self.is_calculating:
            self.simulation_stopped.emit({"operation": OperationType.STOP_CALCULATION})
            self.is_calculating = False
            self.layout().replaceWidget(self.stop_button, self.start_button)
            self.stop_button.hide()
            self.start_button.show()


class RangeAndCalculateWidget(QWidget):
    """Widget with checkboxes for range display and calculation options."""

    showRangeToggled = pyqtSignal(bool)
    calculateToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialize range and calculate checkboxes."""
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Create checkboxes
        self.showRangeCheckbox = QCheckBox("Show Range")
        self.calculateCheckbox = QCheckBox("Calculate")

        layout.addWidget(self.showRangeCheckbox)
        layout.addWidget(self.calculateCheckbox)

        # Connect signals
        self.showRangeCheckbox.stateChanged.connect(
            lambda state: self.showRangeToggled.emit(state == Qt.CheckState.Checked.value)
        )
        self.calculateCheckbox.stateChanged.connect(
            lambda state: self.calculateToggled.emit(state == Qt.CheckState.Checked.value)
        )
