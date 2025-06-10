"""
Global UI configuration for the Solid State Kinetics GUI application.
This module contains all configuration constants and settings extracted from GUI modules.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class UIStrings:
    """Global UI text strings and labels."""

    # Window titles
    MAIN_WINDOW_TITLE: str = "Solid State Kinetics Analysis"  # Tab names
    MAIN_TAB_NAME: str = "Analysis"
    USER_GUIDE_TAB_NAME: str = "User Guide"

    # Sidebar sections
    EXPERIMENTS_SECTION: str = "experiments"
    SERIES_SECTION: str = "series"
    CALCULATION_SECTION: str = "calculation"
    SETTINGS_SECTION: str = "settings"

    # Menu items
    ADD_FILE_DATA: str = "add file data"
    DELETE_SELECTED: str = "delete selected"
    ADD_NEW_SERIES: str = "add new series"
    IMPORT_SERIES: str = "import series"
    DELETE_SERIES: str = "delete series"

    # Calculation methods
    MODEL_FIT: str = "model fit"
    MODEL_FREE: str = "model free"
    MODEL_BASED: str = "model based"

    # Console states
    CONSOLE_SHOW: str = "show"
    CONSOLE_HIDE: str = "hide"

    # Tree view header
    APP_TREE_HEADER: str = "app tree"

    # Buttons
    CALCULATE_BUTTON: str = "calculate"
    PLOT_BUTTON: str = "plot"
    SETTINGS_BUTTON: str = "settings"
    START_BUTTON: str = "start"
    STOP_BUTTON: str = "stop"
    OK_BUTTON: str = "Ok"
    CANCEL_BUTTON: str = "Cancel"


@dataclass
class GlobalLayoutConfig:
    """Global layout configuration constants."""

    # Main tab dimensions
    MIN_WIDTH_SIDEBAR: int = 220
    MIN_WIDTH_SUBSIDEBAR: int = 220
    MIN_WIDTH_CONSOLE: int = 150
    MIN_WIDTH_PLOTCANVAS: int = 500
    SPLITTER_WIDTH: int = 100
    MIN_HEIGHT_MAINTAB: int = 700

    # Table tab dimensions
    TABLE_SIDEBAR_RATIO: float = 0.2  # 1/5 of total width

    @property
    def COMPONENTS_MIN_WIDTH(self) -> int:
        """Calculate minimum width for all components."""
        return (
            self.MIN_WIDTH_SIDEBAR
            + self.MIN_WIDTH_SUBSIDEBAR
            + self.MIN_WIDTH_CONSOLE
            + self.MIN_WIDTH_PLOTCANVAS
            + self.SPLITTER_WIDTH
        )


@dataclass
class AnnotationConfig:
    """Configuration for plot annotations."""

    # Model Fit annotation settings
    MODEL_FIT_BLOCK_TOP: float = 0.98
    MODEL_FIT_BLOCK_LEFT: float = 0.35
    MODEL_FIT_BLOCK_RIGHT: float = 0.65
    MODEL_FIT_DELTA_Y: float = 0.03
    MODEL_FIT_FONTSIZE: int = 8
    MODEL_FIT_FACECOLOR: str = "white"
    MODEL_FIT_EDGECOLOR: str = "black"
    MODEL_FIT_ALPHA: float = 1.0

    # Model Free annotation settings
    MODEL_FREE_BLOCK_TOP: float = 0.98
    MODEL_FREE_BLOCK_LEFT: float = 0.35
    MODEL_FREE_BLOCK_RIGHT: float = 0.65
    MODEL_FREE_DELTA_Y: float = 0.03
    MODEL_FREE_FONTSIZE: int = 8
    MODEL_FREE_FACECOLOR: str = "white"
    MODEL_FREE_EDGECOLOR: str = "black"
    MODEL_FREE_ALPHA: float = 1.0

    def get_model_fit_config(self) -> Dict[str, Any]:
        """Get model fit annotation configuration as dictionary."""
        return {
            "block_top": self.MODEL_FIT_BLOCK_TOP,
            "block_left": self.MODEL_FIT_BLOCK_LEFT,
            "block_right": self.MODEL_FIT_BLOCK_RIGHT,
            "delta_y": self.MODEL_FIT_DELTA_Y,
            "fontsize": self.MODEL_FIT_FONTSIZE,
            "facecolor": self.MODEL_FIT_FACECOLOR,
            "edgecolor": self.MODEL_FIT_EDGECOLOR,
            "alpha": self.MODEL_FIT_ALPHA,
        }

    def get_model_free_config(self) -> Dict[str, Any]:
        """Get model free annotation configuration as dictionary."""
        return {
            "block_top": self.MODEL_FREE_BLOCK_TOP,
            "block_left": self.MODEL_FREE_BLOCK_LEFT,
            "block_right": self.MODEL_FREE_BLOCK_RIGHT,
            "delta_y": self.MODEL_FREE_DELTA_Y,
            "fontsize": self.MODEL_FREE_FONTSIZE,
            "facecolor": self.MODEL_FREE_FACECOLOR,
            "edgecolor": self.MODEL_FREE_EDGECOLOR,
            "alpha": self.MODEL_FREE_ALPHA,
        }


# Global configuration instances
UI_STRINGS = UIStrings()
LAYOUT_CONFIG = GlobalLayoutConfig()
ANNOTATION_CONFIG = AnnotationConfig()
