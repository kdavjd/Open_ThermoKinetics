# config.py for model_free module
"""Configuration settings for the model free sub-sidebar module."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ModelFreeDefaults:
    """Default values for model free parameters."""

    alpha_min: str = "0.005"
    alpha_max: str = "0.995"
    ea_min: str = "10"
    ea_max: str = "2000"

    # Validation ranges
    alpha_min_range: tuple[float, float] = (0.0, 0.999)
    alpha_max_range: tuple[float, float] = (0.0, 1.0)


@dataclass(frozen=True)
class ModelFreeLayout:
    """Layout configuration for model free components."""

    results_table_columns: int = 3
    results_table_headers: List[str] = None

    # Button layout stretch factors
    plot_button_stretch: int = 4
    settings_button_stretch: int = 4

    def __post_init__(self):
        if self.results_table_headers is None:
            # Workaround for mutable default in dataclass
            object.__setattr__(self, "results_table_headers", ["method", "Ea", "std"])


@dataclass(frozen=True)
class ModelFreeComboBoxDefaults:
    """Default items for combo boxes."""

    reaction_default_items: List[str] = None
    beta_default_items: List[str] = None
    plot_type_items: List[str] = None

    def __post_init__(self):
        if self.reaction_default_items is None:
            object.__setattr__(self, "reaction_default_items", ["select reaction"])
        if self.beta_default_items is None:
            object.__setattr__(self, "beta_default_items", ["select beta"])
        if self.plot_type_items is None:
            object.__setattr__(self, "plot_type_items", ["y(α)", "g(α)", "z(α)"])


@dataclass(frozen=True)
class ModelFreeAnnotationDefaults:
    """Default values for model free annotation settings."""

    block_top: float = 0.98
    block_left: float = 0.35
    block_right: float = 0.65
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
class ModelFreeLabels:
    """Label texts for model free module."""

    # Alpha labels
    alpha_min_label: str = "α_min:"
    alpha_max_label: str = "α_max:"

    # Ea labels
    ea_min_label: str = "Ea min, kJ:"
    ea_max_label: str = "Ea max, kJ:"
    ea_mean_label: str = "Ea mean, kJ:"
    plot_type_label: str = "Plot type:"

    # Tooltips
    alpha_min_tooltip: str = "alpha_min - minimum conversion value for calculation"
    alpha_max_tooltip: str = "alpha_max - maximum conversion value for calculation"
    ea_min_tooltip: str = "Ea min, kJ"
    ea_max_tooltip: str = "Ea max, kJ"
    ea_mean_tooltip: str = "Ea mean, kJ"

    # Plot type options
    plot_type_options: List[str] = None

    def __post_init__(self):
        if self.plot_type_options is None:
            object.__setattr__(self, "plot_type_options", ["y(α)", "g(α)", "z(α)"])


@dataclass(frozen=True)
class ModelFreeConfig:
    """Main configuration for model free module."""

    defaults: ModelFreeDefaults = ModelFreeDefaults()
    layout: ModelFreeLayout = ModelFreeLayout()
    combobox: ModelFreeComboBoxDefaults = ModelFreeComboBoxDefaults()
    annotation: ModelFreeAnnotationDefaults = ModelFreeAnnotationDefaults()
    labels: ModelFreeLabels = ModelFreeLabels()
    ui: ModelFreeLabels = ModelFreeLabels()  # Alias for backward compatibility
