"""
Modeling Configuration Module
Contains dataclasses for model-based analysis, reaction schemes, and parameter adjustment.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ReactionDefaults:
    """Default values for reaction parameters"""

    ea_default: float = 120.0
    log_a_default: float = 8.0
    contribution_default: float = 0.5
    ea_range: Tuple[float, float] = (1.0, 2000.0)
    log_a_range: Tuple[float, float] = (-100.0, 100.0)
    contribution_range: Tuple[float, float] = (0.01, 1.0)


@dataclass
class AdjustmentConfig:
    """Configuration for parameter adjustment widgets"""

    button_size: int = 24
    slider_min: int = -5
    slider_max: int = 5
    slider_tick_interval: int = 1
    decimals: int = 3

    # Adjustment steps
    ea_button_step: float = 5.0
    ea_slider_scale: float = 1.0
    log_a_button_step: float = 0.5
    log_a_slider_scale: float = 0.1
    contribution_button_step: float = 0.05
    contribution_slider_scale: float = 0.01


@dataclass
class SchemeConfig:
    """Configuration for reaction scheme graphics"""

    node_width: float = 40.0
    node_height: float = 40.0
    node_spacing_x: float = 80.0
    node_spacing_y: float = 60.0
    arrow_width: float = 2.0

    # Colors
    node_color: str = "lightblue"
    node_border_color: str = "black"
    arrow_color: str = "black"
    selected_color: str = "yellow"

    # Available kinetic models
    available_models: List[str] = None

    def __post_init__(self):
        if self.available_models is None:
            self.available_models = ["F1/3", "F3/4", "F3/2", "F2", "F3", "A2", "R3", "D1"]


@dataclass
class ModelBasedTabConfig:
    """Configuration for model-based tab layout"""

    reactions_combo_min_width: int = 200
    reactions_combo_min_height: int = 30
    reaction_type_combo_min_width: int = 100
    reaction_type_combo_min_height: int = 30
    range_calc_widget_min_height: int = 45
    reaction_table_min_height: int = 90
    adjusting_settings_box_min_height: int = 180
    models_scene_min_width: int = 200
    models_scene_min_height: int = 150
    calc_button_width: int = 80
    calc_button_height: int = 30


@dataclass
class TableConfig:
    """Configuration for reaction table"""

    column_count: int = 4
    row_count: int = 3
    column_headers: List[str] = None
    row_labels: List[str] = None

    def __post_init__(self):
        if self.column_headers is None:
            self.column_headers = ["Parameter", "Value", "Min", "Max"]
        if self.row_labels is None:
            self.row_labels = ["Ea, kJ", "log(A)", "contribution"]


@dataclass
class CalculationSettingsConfig:
    """Configuration for calculation settings dialog"""

    deconvolution_methods: List[str] = None
    differential_evolution_strategies: List[str] = None
    differential_evolution_init_options: List[str] = None
    differential_evolution_updating_options: List[str] = None

    def __post_init__(self):
        if self.deconvolution_methods is None:
            self.deconvolution_methods = ["differential_evolution", "another_method"]
        if self.differential_evolution_strategies is None:
            self.differential_evolution_strategies = [
                "best1bin",
                "best1exp",
                "rand1exp",
                "randtobest1exp",
                "currenttobest1exp",
                "best2exp",
                "rand2exp",
                "randtobest1bin",
                "currenttobest1bin",
                "best2bin",
                "rand2bin",
                "rand1bin",
            ]
        if self.differential_evolution_init_options is None:
            self.differential_evolution_init_options = ["latinhypercube", "random"]
        if self.differential_evolution_updating_options is None:
            self.differential_evolution_updating_options = ["immediate", "deferred"]


@dataclass
class DialogConfig:
    """Configuration for dialog dimensions and settings"""

    # Dialog dimensions
    calculation_settings_width: int = 800
    calculation_settings_height: int = 600
    annotation_settings_width: int = 300
    annotation_settings_height: int = 300
    models_selection_width: int = 400
    models_selection_height: int = 300

    # Dialog padding and spacing
    layout_margin: int = 10
    layout_spacing: int = 5
    button_spacing: int = 10


@dataclass
class ModelFitAnnotationConfig:
    """Configuration for model fit annotation settings"""

    block_top_default: float = 0.98
    block_left_default: float = 0.4
    block_right_default: float = 0.6
    delta_y_default: float = 0.03
    fontsize_default: int = 8
    facecolor_default: str = "white"
    edgecolor_default: str = "black"
    alpha_default: float = 1.0

    # Spinbox ranges
    position_range: Tuple[float, float] = (0.0, 1.0)
    position_decimals: int = 2
    position_step: float = 0.01
    fontsize_range: Tuple[int, int] = (1, 100)
    alpha_range: Tuple[float, float] = (0.0, 1.0)
    alpha_decimals: int = 2
    alpha_step: float = 0.1


@dataclass
class ModelFreeAnnotationConfig:
    """Configuration for model free annotation settings"""

    block_top_default: float = 0.98
    block_left_default: float = 0.35
    block_right_default: float = 0.65
    delta_y_default: float = 0.03
    fontsize_default: int = 8
    facecolor_default: str = "white"
    edgecolor_default: str = "black"
    alpha_default: float = 1.0

    # Spinbox ranges (same as model fit for consistency)
    position_range: Tuple[float, float] = (0.0, 1.0)
    position_decimals: int = 2
    position_step: float = 0.01
    fontsize_range: Tuple[int, int] = (1, 100)
    alpha_range: Tuple[float, float] = (0.0, 1.0)
    alpha_decimals: int = 2
    alpha_step: float = 0.1


@dataclass
class ModelFitSubBarConfig:
    """Configuration for model fit sub bar"""

    # Default calculation parameters
    alpha_min_default: str = "0.005"
    alpha_max_default: str = "0.995"
    valid_proportion_default: str = "0.8"

    # Form field tooltips
    alpha_min_tooltip: str = "alpha_min - minimum conversion value for calculation"
    alpha_max_tooltip: str = "alpha_max - maximum conversion value for calculation"
    valid_proportion_tooltip: str = (
        "valid proportion - the proportion of values in the model calculation that is not infinity or NaN. "
        "If it is smaller, the model is ignored."
    )


@dataclass
class SeriesDialogConfig:
    """Configuration for series dialog dimensions"""

    min_window_width: int = 300
    field_width: int = 290
    heating_rate_width: int = 80
    file_input_row_height: int = 50
    add_button_height: int = 40
    window_padding: int = 50


@dataclass
class ModelBasedConfig:
    """Configuration for model based scheme graphics"""

    node_width: int = 30
    node_height: int = 20
    arrow_inset: int = 3
    horizontal_gap: int = 45
    vertical_step: int = 22
    arrow_size: int = 3
    pen_color: str = "black"
    node_brush_color: str = "white"
    arrow_color: str = "black"


@dataclass
class ModelingConfig:
    """Main modeling configuration combining all modeling settings"""

    reaction_defaults: ReactionDefaults = None
    adjustment: AdjustmentConfig = None
    scheme: SchemeConfig = None
    model_based_tab: ModelBasedTabConfig = None
    table: TableConfig = None
    calculation_settings: CalculationSettingsConfig = None
    dialogs: DialogConfig = None
    model_fit_annotation: ModelFitAnnotationConfig = None
    model_free_annotation: ModelFreeAnnotationConfig = None
    model_fit_sub_bar: ModelFitSubBarConfig = None
    series_dialogs: SeriesDialogConfig = None
    model_based_scheme: ModelBasedConfig = None

    def __post_init__(self):
        """Initialize nested configurations with defaults"""
        self.reaction_defaults = self.reaction_defaults or ReactionDefaults()
        self.adjustment = self.adjustment or AdjustmentConfig()
        self.scheme = self.scheme or SchemeConfig()
        self.model_based_tab = self.model_based_tab or ModelBasedTabConfig()
        self.table = self.table or TableConfig()
        self.calculation_settings = self.calculation_settings or CalculationSettingsConfig()
        self.dialogs = self.dialogs or DialogConfig()
        self.model_fit_annotation = self.model_fit_annotation or ModelFitAnnotationConfig()
        self.model_free_annotation = self.model_free_annotation or ModelFreeAnnotationConfig()
        self.model_fit_sub_bar = self.model_fit_sub_bar or ModelFitSubBarConfig()
        self.series_dialogs = self.series_dialogs or SeriesDialogConfig()
        self.model_based_scheme = self.model_based_scheme or ModelBasedConfig()


def get_modeling_config() -> ModelingConfig:
    """Get the default modeling configuration instance"""
    return ModelingConfig()
