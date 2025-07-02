# config.py for model_fit module
"""Configuration settings for the model fit sub-sidebar module."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ModelFitDefaults:
    """Default values for model fit parameters."""

    alpha_min: str = "0.005"
    alpha_max: str = "0.995"
    valid_proportion: str = "0.8"

    # Validation ranges
    alpha_min_range: tuple[float, float] = (0.0, 0.999)
    alpha_max_range: tuple[float, float] = (0.0, 1.0)
    valid_proportion_range: tuple[float, float] = (0.001, 1.0)


@dataclass(frozen=True)
class ModelFitLayout:
    """Layout configuration for model fit components."""

    results_table_columns: int = 4
    results_table_headers: List[str] = None

    # Button layout stretch factors
    plot_model_combobox_stretch: int = 2
    plot_button_stretch: int = 4
    settings_button_stretch: int = 4

    def __post_init__(self):
        if self.results_table_headers is None:
            # Workaround for mutable default in dataclass
            object.__setattr__(self, "results_table_headers", ["Model", "R2_score", "Ea", "A"])


@dataclass(frozen=True)
class ModelFitAnnotationDefaults:
    """Default values for model fit annotation settings."""

    block_top: float = 0.98
    block_left: float = 0.4
    block_right: float = 0.6
    delta_y: float = 0.03
    fontsize: int = 8
    facecolor: str = "white"
    edgecolor: str = "black"
    alpha: float = 1.0

    # Widget ranges and steps
    range_min: float = 0.0
    range_max: float = 1.0
    decimal_places: int = 2
    step_value: float = 0.01
    fontsize_min: int = 1
    fontsize_max: int = 100


@dataclass(frozen=True)
class ModelFitComboBoxDefaults:
    """Default items for combo boxes."""

    beta_default_items: List[str] = None
    reaction_default_items: List[str] = None

    def __post_init__(self):
        if self.beta_default_items is None:
            object.__setattr__(self, "beta_default_items", ["β"])
        if self.reaction_default_items is None:
            object.__setattr__(self, "reaction_default_items", ["select reaction"])


@dataclass(frozen=True)
class ModelFitLabels:
    """UI labels and text for model fit module."""

    alpha_min_label: str = "α_min:"
    alpha_max_label: str = "α_max:"
    valid_proportion_label: str = "valid proportion:"

    # Tooltips
    alpha_min_tooltip: str = "alpha_min - minimum conversion value for calculation"
    alpha_max_tooltip: str = "alpha_max - maximum conversion value for calculation"
    valid_proportion_tooltip: str = "valid proportion for data validation"

    # Button texts
    calculate_button_text: str = "calculate"
    plot_button_text: str = "plot"
    settings_button_text: str = "settings"

    # Table headers
    table_headers: List[str] = None

    # Dialog titles
    annotation_settings_title: str = "annotation settings"
    annotation_settings_width: int = 300
    annotation_settings_height: int = 300

    def __post_init__(self):
        if self.table_headers is None:
            object.__setattr__(self, "table_headers", ["Model", "R2_score", "Ea", "A"])


@dataclass(frozen=True)
class ModelFitDialogConfig:
    """Dialog configuration for model fit module."""

    annotation_settings_title: str = "annotation settings"
    annotation_settings_width: int = 300
    annotation_settings_height: int = 300


@dataclass(frozen=True)
class ModelFitConfig:
    """Main configuration for model fit module."""

    defaults: ModelFitDefaults = ModelFitDefaults()
    layout: ModelFitLayout = ModelFitLayout()
    annotation: ModelFitAnnotationDefaults = ModelFitAnnotationDefaults()
    combobox: ModelFitComboBoxDefaults = ModelFitComboBoxDefaults()
    ui: ModelFitLabels = ModelFitLabels()
    dialog: ModelFitDialogConfig = ModelFitDialogConfig()
