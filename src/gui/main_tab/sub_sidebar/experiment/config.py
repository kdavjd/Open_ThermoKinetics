# config.py for experiment module
"""Configuration settings for the experiment sub-sidebar module."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SmoothingDefaults:
    """Default values for smoothing operations."""

    # Default methods
    smoothing_methods: List[str] = None
    default_method: str = "Savitzky-Golay"

    # Default parameters
    window_size_default: str = "1"
    polynomial_order_default: str = "0"

    # Settings
    spec_settings: List[str] = None
    default_spec_setting: str = "Nearest"

    def __post_init__(self):
        if self.smoothing_methods is None:
            object.__setattr__(self, "smoothing_methods", ["Savitzky-Golay", "Other"])
        if self.spec_settings is None:
            object.__setattr__(self, "spec_settings", ["Nearest", "Other"])


@dataclass(frozen=True)
class BackgroundSubtractionDefaults:
    """Default values for background subtraction operations."""

    # Background subtraction methods
    methods: List[str] = None

    def __post_init__(self):
        if self.methods is None:
            object.__setattr__(
                self,
                "methods",
                [
                    "Linear",
                    "Sigmoidal",
                    "Tangential",
                    "Left Tangential",
                    "Left Sigmoidal",
                    "Right Tangential",
                    "Right Sigmoidal",
                    "Bezier",
                ],
            )


@dataclass(frozen=True)
class ExperimentLabels:
    """Label texts for experiment module."""

    # Smoothing labels
    smoothing_method_label: str = "smoothing method:"
    window_size_label: str = "window size:"
    polynomial_order_label: str = "polynomial order:"
    specific_settings_label: str = "specific settings:"

    # Background subtraction labels
    background_method_label: str = "background subtraction method:"
    background_range_label: str = "background subtraction range:"
    range_left_label: str = "left:"
    range_right_label: str = "right:"

    # Button labels
    apply_button: str = "apply"
    reset_changes_button: str = "reset changes"
    conversion_button: str = "to α(t)"
    dtg_button: str = "to DTG"
    deconvolution_button: str = "deconvolution"


@dataclass(frozen=True)
class ExperimentConfig:
    """Main configuration for experiment module."""

    smoothing: SmoothingDefaults = SmoothingDefaults()
    background_subtraction: BackgroundSubtractionDefaults = BackgroundSubtractionDefaults()
    labels: ExperimentLabels = ExperimentLabels()
