"""
Configuration for Model Based sub-sidebar component.
Contains all settings and constants specific to model-based analysis.
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from src.core.app_settings import PARAMETER_BOUNDS


@dataclass
class ModelBasedAdjustmentDefaults:
    """Default values for adjustment controls."""

    BUTTON_SIZE: int = 24
    SLIDER_MIN: int = -5
    SLIDER_MAX: int = 5
    SLIDER_TICK_INTERVAL: int = 1


@dataclass
class ModelBasedReactionParams:
    """Default parameters for reactions."""

    def __init__(self):
        bounds = PARAMETER_BOUNDS.model_based
        self.ea_default = bounds.ea_default
        self.log_a_default = bounds.log_a_default
        self.contribution_default = bounds.contribution_default
        self.ea_button_step = 10.0
        self.log_a_button_step = 1.0
        self.contribution_button_step = 0.1
        self.ea_slider_scale = 1.0
        self.log_a_slider_scale = 0.1
        self.contribution_slider_scale = 0.01


@dataclass
class ModelBasedLayoutSettings:
    """Layout settings for model based components."""

    # Reaction table settings
    reaction_table_column_widths: Tuple[int, int, int, int] = (70, 50, 50, 50)
    reaction_table_row_heights: Tuple[int, int, int] = (30, 30, 30)

    # Component minimum dimensions
    reactions_combo_min_width: int = 200
    reactions_combo_min_height: int = 30
    reaction_type_combo_min_width: int = 100
    reaction_type_combo_min_height: int = 30
    range_calc_widget_min_height: int = 45
    reaction_table_min_height: int = 90
    adjusting_settings_box_min_height: int = 180
    models_scene_min_width: int = 200
    models_scene_min_height: int = 150
    calc_buttons_width: int = 80
    calc_buttons_height: int = 30

    def get_layout_config(self) -> Dict[str, Dict[str, Any]]:
        """Get complete layout configuration as dictionary."""
        return {
            "reactions_combo": {
                "min_width": self.reactions_combo_min_width,
                "min_height": self.reactions_combo_min_height,
            },
            "reaction_type_combo": {
                "min_width": self.reaction_type_combo_min_width,
                "min_height": self.reaction_type_combo_min_height,
            },
            "range_calc_widget": {"min_height": self.range_calc_widget_min_height},
            "reaction_table": {"min_height": self.reaction_table_min_height},
            "adjusting_settings_box": {"min_height": self.adjusting_settings_box_min_height},
            "models_scene": {"min_width": self.models_scene_min_width, "min_height": self.models_scene_min_height},
            "calc_buttons": {"button_width": self.calc_buttons_width, "button_height": self.calc_buttons_height},
        }


@dataclass
class ModelBasedTableConfig:
    """Configuration for reaction parameter table."""

    # Table headers
    COLUMN_HEADERS = ["Parameter", "Value", "Min", "Max"]

    # Parameter labels
    EA_LABEL: str = "Ea, kJ"
    LOG_A_LABEL: str = "log(A)"
    CONTRIBUTION_LABEL: str = "contribution"

    # Table dimensions
    DEFAULT_ROWS: int = 3
    DEFAULT_COLS: int = 4

    # Hidden columns (min/max ranges)
    HIDDEN_COLUMNS = [2, 3]


@dataclass
class ModelBasedConfig:
    """Complete configuration for model based analysis."""

    adjustment_defaults: ModelBasedAdjustmentDefaults
    reaction_params: ModelBasedReactionParams
    layout_settings: ModelBasedLayoutSettings
    table_config: ModelBasedTableConfig

    def __init__(self):
        self.adjustment_defaults = ModelBasedAdjustmentDefaults()
        self.reaction_params = ModelBasedReactionParams()
        self.layout_settings = ModelBasedLayoutSettings()
        self.table_config = ModelBasedTableConfig()


# Global instance
MODEL_BASED_CONFIG = ModelBasedConfig()
