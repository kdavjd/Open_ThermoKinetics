"""
Dialog configuration dataclasses for GUI dialog components.
Contains configuration for modal dialogs, settings dialogs, and file selection dialogs.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class DialogDimensions:
    """Standard dimensions for dialog windows."""

    # Window dimensions
    min_window_width: int = 300
    annotation_dialog_width: int = 300
    annotation_dialog_height: int = 300
    calculation_settings_width: int = 600
    calculation_settings_height: int = 400

    # Padding and spacing
    window_padding: int = 50
    field_width: int = 290
    heating_rate_width: int = 80
    file_input_row_height: int = 50
    add_button_height: int = 40


@dataclass
class AnnotationDialogConfig:
    """Configuration for annotation settings dialogs."""

    # Default annotation values
    default_block_top: float = 0.98
    default_block_left_model_fit: float = 0.4
    default_block_left_model_free: float = 0.35
    default_block_right_model_fit: float = 0.6
    default_block_right_model_free: float = 0.65
    default_delta_y: float = 0.03
    default_fontsize: int = 8
    default_facecolor: str = "white"
    default_edgecolor: str = "black"
    default_alpha: float = 1.0

    # Spin box ranges and steps
    position_range: Tuple[float, float] = (0.0, 1.0)
    position_decimals: int = 2
    position_step: float = 0.01
    alpha_range: Tuple[float, float] = (0.0, 1.0)
    alpha_decimals: int = 2
    alpha_step: float = 0.1
    fontsize_range: Tuple[int, int] = (1, 100)

    # Labels
    title: str = "annotation settings"
    annotation_label: str = "annotation"
    block_top_label: str = "block Top:"
    block_left_label: str = "block Left:"
    block_right_label: str = "block Right:"
    delta_y_label: str = "delta Y:"
    fontsize_label: str = "font size:"
    facecolor_label: str = "face color:"
    edgecolor_label: str = "edge color:"
    alpha_label: str = "alpha:"


@dataclass
class CalculationSettingsDialogConfig:
    """Configuration for calculation settings dialogs."""

    # Window settings
    title: str = "calculation settings"
    deconv_title: str = "Calculation Settings"

    # Group box labels
    functions_group: str = "functions"
    deconv_params_group: str = "deconvolution parameters"
    de_settings_group: str = "Differential Evolution Settings"

    # Method labels
    deconv_method_label: str = "deconvolution method:"
    calc_method_label: str = "Calculation method:"

    # Default methods
    default_deconv_method: str = "differential_evolution"
    default_calc_method: str = "differential_evolution"

    # Available methods
    deconv_methods: List[str] = None
    calc_methods: List[str] = None

    # Parameter validation messages
    validation_title: str = "Invalid DE parameters"
    empty_functions_title: str = "unselected functions"
    file_not_selected_title: str = "File is not selected."
    file_not_selected_message: str = "Choose an experiment"
    update_success_title: str = "calculation settings"
    update_success_prefix: str = "updated for:\n"

    # Differential evolution strategy options
    strategy_options: List[str] = None
    init_options: List[str] = None
    updating_options: List[str] = None

    # Parameter tooltips
    parameter_tooltips: Dict[str, str] = None

    def __post_init__(self):
        if self.deconv_methods is None:
            self.deconv_methods = ["differential_evolution", "another_method"]

        if self.calc_methods is None:
            self.calc_methods = ["differential_evolution", "another_method"]

        if self.strategy_options is None:
            self.strategy_options = [
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

        if self.init_options is None:
            self.init_options = ["latinhypercube", "random"]

        if self.updating_options is None:
            self.updating_options = ["immediate", "deferred"]

        if self.parameter_tooltips is None:
            self.parameter_tooltips = {
                "strategy": "The strategy for differential evolution. Choose one of the available options.",
                "maxiter": "Maximum number of iterations. An integer >= 1.",
                "popsize": "Population size. An integer >= 1.",
                "tol": "Relative tolerance for stop criteria. A non-negative number.",
                "mutation": "Mutation factor. A number or tuple of two numbers in [0, 2].",
                "recombination": "Recombination factor in [0, 1].",
                "seed": "Random seed. An integer or None.",
                "callback": "Callback function. Leave empty if not required.",
                "disp": "Display status during optimization.",
                "polish": "Perform a final polish optimization after differential evolution is done.",
                "init": "Population initialization method.",
                "atol": "Absolute tolerance for stop criteria. A non-negative number.",
                "updating": "Population updating mode: immediate or deferred.",
                "workers": "Number of processes for parallel computing. Must be 1 here.",
                "constraints": "Constraints for the optimization. Leave empty if not required.",
            }


@dataclass
class ModelsSelectionDialogConfig:
    """Configuration for models selection dialog."""

    title: str = "Select Models"
    grid_columns: int = 6
    add_models_button_text: str = "Add models"
    add_models_button_format: str = "Add models ({count})"
    many_models_label: str = "Many models"


@dataclass
class FileSelectionDialogConfig:
    """Configuration for file selection dialog."""

    ok_button_text: str = "OK"
    cancel_button_text: str = "Cancel"


@dataclass
class ValidationConfig:
    """Configuration for parameter validation."""

    # Validation messages
    invalid_strategy_msg: str = "Invalid strategy. Choose from {strategies}."
    invalid_maxiter_msg: str = "Must be an integer >= 1."
    invalid_popsize_msg: str = "Must be an integer >= 1."
    invalid_tol_msg: str = "Must be non-negative."
    invalid_mutation_tuple_msg: str = "Must be a tuple of two numbers in [0, 2]."
    invalid_mutation_range_msg: str = "Must be in [0, 2]."
    invalid_mutation_format_msg: str = "Invalid format."
    invalid_recombination_msg: str = "Must be in [0, 1]."
    invalid_seed_msg: str = "Must be an integer or None."
    invalid_atol_msg: str = "Must be non-negative."
    invalid_updating_msg: str = "Must be one of {options}."
    invalid_workers_msg: str = "Must be an integer = 1. Parallel processing is not supported. Up to 4 for test"

    # Validation ranges
    mutation_range: Tuple[float, float] = (0.0, 2.0)
    recombination_range: Tuple[float, float] = (0.0, 1.0)
    workers_range: Tuple[int, int] = (1, 4)


@dataclass
class DialogsConfig:
    """Main configuration class for all dialogs."""

    dimensions: DialogDimensions = None
    annotation: AnnotationDialogConfig = None
    calculation_settings: CalculationSettingsDialogConfig = None
    models_selection: ModelsSelectionDialogConfig = None
    file_selection: FileSelectionDialogConfig = None
    validation: ValidationConfig = None

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = DialogDimensions()
        if self.annotation is None:
            self.annotation = AnnotationDialogConfig()
        if self.calculation_settings is None:
            self.calculation_settings = CalculationSettingsDialogConfig()
        if self.models_selection is None:
            self.models_selection = ModelsSelectionDialogConfig()
        if self.file_selection is None:
            self.file_selection = FileSelectionDialogConfig()
        if self.validation is None:
            self.validation = ValidationConfig()
