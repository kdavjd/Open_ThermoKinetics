"""
Adjustment controls for fine-tuning kinetic parameters.
Contains slider-based parameter adjustment widgets.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QVBoxLayout, QWidget

from .config import MODEL_BASED_CONFIG


class AdjustmentRowWidget(QWidget):
    """Widget for adjusting a single parameter with buttons and slider."""

    valueChanged = pyqtSignal(str, float)

    def __init__(
        self,
        parameter_name: str,
        initial_value: float,
        button_step: float,
        slider_scale: float,
        display_name: str = None,
        parent=None,
        decimals: int = 3,
    ):
        """Initialize adjustment widget for a parameter.

        Args:
            parameter_name: Internal parameter name
            initial_value: Starting parameter value
            button_step: Step size for button clicks
            slider_scale: Scale factor for slider movement
            display_name: Human-readable parameter name
            parent: Parent widget
            decimals: Number of decimal places to display
        """
        super().__init__(parent)
        self.parameter_name = parameter_name
        self.display_name = display_name if display_name is not None else parameter_name
        self.decimals = decimals
        self.base_value = round(initial_value, self.decimals)
        self.button_step = button_step
        self.slider_scale = slider_scale

        layout = QVBoxLayout(self)
        self.value_label = QLabel(f"{self.display_name}: {self.base_value:.{self.decimals}f}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)

        h_layout = QHBoxLayout()
        config = MODEL_BASED_CONFIG.adjustment_defaults

        # Left button
        self.left_button = QPushButton("<")
        self.left_button.setObjectName("btn_small")
        self.left_button.setFixedSize(config.BUTTON_SIZE, config.BUTTON_SIZE)
        self.left_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(config.SLIDER_MIN, config.SLIDER_MAX)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(config.SLIDER_TICK_INTERVAL)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Right button
        self.right_button = QPushButton(">")
        self.right_button.setObjectName("btn_small")
        self.right_button.setFixedSize(config.BUTTON_SIZE, config.BUTTON_SIZE)
        self.right_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        h_layout.addWidget(self.left_button)
        h_layout.addWidget(self.slider)
        h_layout.addWidget(self.right_button)
        layout.addLayout(h_layout)

        # Connect signals
        self.left_button.clicked.connect(self.on_left_clicked)
        self.right_button.clicked.connect(self.on_right_clicked)
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.sliderReleased.connect(self.on_slider_released)

    def on_left_clicked(self):
        """Handle left button click - decrease parameter value."""
        self.base_value -= self.button_step
        self.base_value = round(self.base_value, self.decimals)
        self.slider.setValue(0)
        self.update_label()
        self.valueChanged.emit(self.parameter_name, self.base_value)

    def on_right_clicked(self):
        """Handle right button click - increase parameter value."""
        self.base_value += self.button_step
        self.base_value = round(self.base_value, self.decimals)
        self.slider.setValue(0)
        self.update_label()
        self.valueChanged.emit(self.parameter_name, self.base_value)

    def on_slider_value_changed(self, value):
        """Handle slider movement - show preview value."""
        potential_value = self.base_value + (value * self.slider_scale)
        self.value_label.setText(f"{self.display_name}: {potential_value:.{self.decimals}f}")

    def on_slider_released(self):
        """Handle slider release - commit new value."""
        offset = self.slider.value() * self.slider_scale
        self.base_value += offset
        self.base_value = round(self.base_value, self.decimals)
        self.slider.setValue(0)
        self.update_label()
        self.valueChanged.emit(self.parameter_name, self.base_value)

    def update_label(self):
        """Update the parameter value label."""
        self.value_label.setText(f"{self.display_name}: {self.base_value:.{self.decimals}f}")


class AdjustingSettingsBox(QWidget):
    """Container widget for all parameter adjustment controls."""

    def __init__(self, parent=None):
        """Initialize adjustment settings with three parameter controls."""
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        params = MODEL_BASED_CONFIG.reaction_params

        # Create adjustment widgets for each parameter
        self.ea_adjuster = AdjustmentRowWidget(
            "Ea", params.ea_default, params.ea_button_step, params.ea_slider_scale, "Ea", parent=self
        )

        self.log_a_adjuster = AdjustmentRowWidget(
            "log_A", params.log_a_default, params.log_a_button_step, params.log_a_slider_scale, "log(A)", parent=self
        )

        self.contrib_adjuster = AdjustmentRowWidget(
            "contribution",
            params.contribution_default,
            params.contribution_button_step,
            params.contribution_slider_scale,
            "contribution",
            parent=self,
        )

        # Add widgets to layout
        main_layout.addWidget(self.ea_adjuster)
        main_layout.addWidget(self.log_a_adjuster)
        main_layout.addWidget(self.contrib_adjuster)
