"""
Adjustment Controls Component

This module provides interactive adjustment controls for model-based parameter tuning,
including slider-based parameter adjusters and settings management.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.gui.config import get_modeling_config


class AdjustmentRowWidget(QWidget):
    """
    Interactive parameter adjustment widget with buttons and slider.

    Provides fine-grained control over model parameters with step buttons
    and continuous slider adjustment.

    Signals:
        valueChanged: Emitted when parameter value changes (parameter_name, new_value)
    """

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
        """
        Initialize parameter adjustment widget.

        Args:
            parameter_name: Internal parameter name for signals
            initial_value: Starting parameter value
            button_step: Step size for button clicks
            slider_scale: Scale factor for slider movements
            display_name: Human-readable parameter name
            parent: Parent widget
            decimals: Decimal precision for display
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
        config = get_modeling_config()
        adjustment_config = config.adjustment

        self.left_button = QPushButton("<")
        self.left_button.setFixedSize(adjustment_config.button_size, adjustment_config.button_size)
        self.left_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(adjustment_config.slider_min, adjustment_config.slider_max)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(adjustment_config.slider_tick_interval)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.right_button = QPushButton(">")
        self.right_button.setFixedSize(adjustment_config.button_size, adjustment_config.button_size)
        self.right_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        h_layout.addWidget(self.left_button)
        h_layout.addWidget(self.slider)
        h_layout.addWidget(self.right_button)
        layout.addLayout(h_layout)

        self.left_button.clicked.connect(self.on_left_clicked)
        self.right_button.clicked.connect(self.on_right_clicked)
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.sliderReleased.connect(self.on_slider_released)

    def on_left_clicked(self):
        """Decrease parameter value by button step."""
        self.base_value -= self.button_step
        self.base_value = round(self.base_value, self.decimals)
        self.slider.setValue(0)
        self.update_label()
        self.valueChanged.emit(self.parameter_name, self.base_value)

    def on_right_clicked(self):
        """Increase parameter value by button step."""
        self.base_value += self.button_step
        self.base_value = round(self.base_value, self.decimals)
        self.slider.setValue(0)
        self.update_label()
        self.valueChanged.emit(self.parameter_name, self.base_value)

    def on_slider_value_changed(self, value):
        """Update display during slider movement without emitting signals."""
        potential_value = self.base_value + (value * self.slider_scale)
        self.value_label.setText(f"{self.display_name}: {potential_value:.{self.decimals}f}")

    def on_slider_released(self):
        """Apply slider offset to base value and emit change signal."""
        offset = self.slider.value() * self.slider_scale
        self.base_value += offset
        self.base_value = round(self.base_value, self.decimals)
        self.slider.setValue(0)
        self.update_label()
        self.valueChanged.emit(self.parameter_name, self.base_value)

    def update_label(self):
        """Update the parameter value display label."""
        self.value_label.setText(f"{self.display_name}: {self.base_value:.{self.decimals}f}")


class AdjustingSettingsBox(QWidget):
    """
    Container widget for parameter adjustment controls.

    Provides adjustment widgets for Ea, log(A), and contribution parameters
    with configuration-driven defaults and step sizes.
    """

    def __init__(self, parent=None):
        """
        Initialize adjustment settings container.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        config = get_modeling_config()
        adjustment_config = config.adjustment
        defaults = config.reaction_defaults

        self.ea_adjuster = AdjustmentRowWidget(
            "Ea",
            defaults.ea_default,
            adjustment_config.ea_button_step,
            adjustment_config.ea_slider_scale,
            "Ea",
            parent=self,
        )
        self.log_a_adjuster = AdjustmentRowWidget(
            "log_A",
            defaults.log_a_default,
            adjustment_config.log_a_button_step,
            adjustment_config.log_a_slider_scale,
            "log(A)",
            parent=self,
        )
        self.contrib_adjuster = AdjustmentRowWidget(
            "contribution",
            defaults.contribution_default,
            adjustment_config.contribution_button_step,
            adjustment_config.contribution_slider_scale,
            "contribution",
            parent=self,
        )

        main_layout.addWidget(self.ea_adjuster)
        main_layout.addWidget(self.log_a_adjuster)
        main_layout.addWidget(self.contrib_adjuster)
