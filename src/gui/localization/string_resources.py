"""
String resources dataclass for centralized string management.
Contains hardcoded string literals extracted from the GUI components.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ButtonStrings:
    """Button text strings."""

    ok: str = "OK"
    cancel: str = "Cancel"
    calculate: str = "calculate"
    plot: str = "plot"
    settings: str = "settings"
    add_models: str = "Add models"
    add_models_format: str = "Add models ({count})"


@dataclass
class LabelStrings:
    """Label text strings."""

    alpha_min: str = "α_min:"
    alpha_max: str = "α_max:"
    ea_min: str = "Ea min, kJ:"
    ea_max: str = "Ea max, kJ:"
    ea_mean: str = "Ea mean, kJ:"
    plot_type: str = "Plot type:"
    parameter: str = "Parameter"
    value: str = "Value"
    min_value: str = "Min"
    max_value: str = "Max"
    from_bound: str = "from"
    to_bound: str = "to"
    method: str = "method"
    ea_result: str = "Ea"
    std_result: str = "std"
    ea_kj: str = "Ea, kJ"
    log_a: str = "log(A)"
    contribution: str = "contribution"


@dataclass
class TooltipStrings:
    """Tooltip text strings."""

    alpha_min: str = "alpha_min - minimum conversion value for calculation"
    alpha_max: str = "alpha_max - maximum conversion value for calculation"
    ea_min: str = "Ea min, kJ"
    ea_max: str = "Ea max, kJ"
    ea_mean: str = "Ea mean, kJ"


@dataclass
class DialogTitleStrings:
    """Dialog title strings."""

    annotation_settings: str = "annotation settings"
    calculation_settings: str = "calculation settings"
    calculation_settings_alt: str = "Calculation Settings"
    select_models: str = "Select Models"


@dataclass
class GroupBoxStrings:
    """Group box title strings."""

    functions: str = "functions"
    deconv_parameters: str = "deconvolution parameters"
    de_settings: str = "Differential Evolution Settings"


@dataclass
class FieldLabelStrings:
    """Form field label strings."""

    deconv_method: str = "deconvolution method:"
    calc_method: str = "Calculation method:"
    block_top: str = "block Top:"
    block_left: str = "block Left:"
    block_right: str = "block Right:"
    delta_y: str = "delta Y:"
    font_size: str = "font size:"
    face_color: str = "face color:"
    edge_color: str = "edge color:"
    alpha: str = "alpha:"
    annotation: str = "annotation"
    many_models: str = "Many models"


@dataclass
class ValidationStrings:
    """Validation error message strings."""

    alpha_min_range: str = "alpha_min must be between 0 and 0.999"
    alpha_max_range: str = "alpha_max must be between 0 and 1"
    alpha_min_greater: str = "alpha_min cannot be greater than alpha_max"
    file_not_selected: str = "Choose an experiment"
    empty_functions: str = "{functions} must be described by at least one function."
    invalid_de_params: str = "Invalid DE parameters"
    unselected_functions: str = "unselected functions"
    file_not_selected_title: str = "File is not selected."
    error_entering_params: str = "Error entering parameters"


@dataclass
class MessageStrings:
    """Message text strings."""

    settings_updated: str = "updated for:\n{message}"


@dataclass
class DefaultValueStrings:
    """Default values for input fields."""

    alpha_min: str = "0.005"
    alpha_max: str = "0.995"
    ea_min: str = "10"
    ea_max: str = "2000"
    select_reaction: str = "select reaction"
    select_beta: str = "select beta"
    face_color_default: str = "white"
    edge_color_default: str = "black"


@dataclass
class ComboBoxItemStrings:
    """Items for combo box widgets."""

    model_free_methods: List[str] = None
    master_plot_types: List[str] = None
    deconv_methods: List[str] = None
    calc_methods: List[str] = None

    def __post_init__(self):
        if self.model_free_methods is None:
            self.model_free_methods = ["linear approximation", "Friedman", "Vyazovkin", "master plots"]

        if self.master_plot_types is None:
            self.master_plot_types = ["y(α)", "g(α)", "z(α)"]

        if self.deconv_methods is None:
            self.deconv_methods = ["differential_evolution", "another_method"]

        if self.calc_methods is None:
            self.calc_methods = ["differential_evolution", "another_method"]


@dataclass
class ParameterTooltipStrings:
    """Tooltips for optimization parameters."""

    strategy: str = "The strategy for differential evolution. Choose one of the available options."
    maxiter: str = "Maximum number of iterations. An integer >= 1."
    popsize: str = "Population size. An integer >= 1."
    tol: str = "Relative tolerance for stop criteria. A non-negative number."
    mutation: str = "Mutation factor. A number or tuple of two numbers in [0, 2]."
    recombination: str = "Recombination factor in [0, 1]."
    seed: str = "Random seed. An integer or None."
    callback: str = "Callback function. Leave empty if not required."
    disp: str = "Display status during optimization."
    polish: str = "Perform a final polish optimization after differential evolution is done."
    init: str = "Population initialization method."
    atol: str = "Absolute tolerance for stop criteria. A non-negative number."
    updating: str = "Population updating mode: immediate or deferred."
    workers: str = "Number of processes for parallel computing. Must be 1 here."
    constraints: str = "Constraints for the optimization. Leave empty if not required."


@dataclass
class StringResources:
    """Main container for all string resources."""

    buttons: ButtonStrings = None
    labels: LabelStrings = None
    tooltips: TooltipStrings = None
    dialog_titles: DialogTitleStrings = None
    group_boxes: GroupBoxStrings = None
    field_labels: FieldLabelStrings = None
    validation: ValidationStrings = None
    messages: MessageStrings = None
    defaults: DefaultValueStrings = None
    combo_items: ComboBoxItemStrings = None
    param_tooltips: ParameterTooltipStrings = None

    def __post_init__(self):  # noqa: C901
        if self.buttons is None:
            self.buttons = ButtonStrings()
        if self.labels is None:
            self.labels = LabelStrings()
        if self.tooltips is None:
            self.tooltips = TooltipStrings()
        if self.dialog_titles is None:
            self.dialog_titles = DialogTitleStrings()
        if self.group_boxes is None:
            self.group_boxes = GroupBoxStrings()
        if self.field_labels is None:
            self.field_labels = FieldLabelStrings()
        if self.validation is None:
            self.validation = ValidationStrings()
        if self.messages is None:
            self.messages = MessageStrings()
        if self.defaults is None:
            self.defaults = DefaultValueStrings()
        if self.combo_items is None:
            self.combo_items = ComboBoxItemStrings()
        if self.param_tooltips is None:
            self.param_tooltips = ParameterTooltipStrings()
