"""
Controls configuration dataclasses for GUI components.
Contains configuration for buttons, input fields, tables, and other UI controls.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ButtonConfig:
    """Configuration for button components."""

    # Standard button sizes
    standard_width: int = 80
    standard_height: int = 30
    small_width: int = 24
    small_height: int = 24
    large_width: int = 120
    large_height: int = 40

    # Common button texts
    ok_text: str = "OK"
    cancel_text: str = "Cancel"
    calculate_text: str = "calculate"
    plot_text: str = "plot"
    settings_text: str = "settings"

    # Button styles
    default_style: str = ""
    primary_style: str = "QPushButton { background-color: #0078d4; color: white; }"


@dataclass
class InputConfig:
    """Configuration for input field components."""

    # Default values for common inputs
    alpha_min_default: str = "0.005"
    alpha_max_default: str = "0.995"
    ea_min_default: str = "10"
    ea_max_default: str = "2000"
    ea_mean_default: str = ""

    # Input field dimensions
    standard_width: int = 100
    field_width: int = 290
    heating_rate_width: int = 80

    # Validation ranges
    alpha_min_range: Tuple[float, float] = (0.0, 0.999)
    alpha_max_range: Tuple[float, float] = (0.0, 1.0)
    ea_range: Tuple[float, float] = (10.0, 2000.0)


@dataclass
class ComboBoxConfig:
    """Configuration for combo box components."""

    # Common items
    model_free_methods: List[str] = None
    master_plot_types: List[str] = None
    deconvolution_methods: List[str] = None
    calculation_methods: List[str] = None

    # Default selections
    default_reaction: str = "select reaction"
    default_beta: str = "select beta"
    default_deconv_method: str = "differential_evolution"

    def __post_init__(self):
        if self.model_free_methods is None:
            self.model_free_methods = ["linear approximation", "Friedman", "Vyazovkin", "master plots"]

        if self.master_plot_types is None:
            self.master_plot_types = ["y(α)", "g(α)", "z(α)"]

        if self.deconvolution_methods is None:
            self.deconvolution_methods = ["differential_evolution", "another_method"]

        if self.calculation_methods is None:
            self.calculation_methods = ["differential_evolution", "another_method"]


@dataclass
class TableConfig:
    """Configuration for table components."""

    # Standard table dimensions
    coeffs_table_rows: int = 5
    coeffs_table_cols: int = 2
    results_table_cols: int = 3
    reaction_table_rows: int = 3
    reaction_table_cols: int = 4

    # Header labels
    coeffs_headers: List[str] = None
    results_headers: List[str] = None
    reaction_headers: List[str] = None
    parameter_table_headers: List[str] = None

    # Row labels
    gauss_row_labels: List[str] = None
    fraser_row_labels: List[str] = None
    ads_row_labels: List[str] = None
    default_row_labels: List[str] = None

    # Table styling
    selection_style: str = """
        QTableWidget::item:selected {
            background-color: lightgray;
            color: black;
        }
        QTableWidget::item:focus {
            background-color: lightgray;
            color: black;
        }
    """

    # Row heights
    standard_row_height: int = 30
    file_input_row_height: int = 50

    def __post_init__(self):
        if self.coeffs_headers is None:
            self.coeffs_headers = ["from", "to"]

        if self.results_headers is None:
            self.results_headers = ["method", "Ea", "std"]

        if self.reaction_headers is None:
            self.reaction_headers = ["Parameter", "Value", "Min", "Max"]

        if self.parameter_table_headers is None:
            self.parameter_table_headers = ["Min", "Max"]

        if self.gauss_row_labels is None:
            self.gauss_row_labels = ["h", "z", "w"]

        if self.fraser_row_labels is None:
            self.fraser_row_labels = ["h", "z", "w", "fr"]

        if self.ads_row_labels is None:
            self.ads_row_labels = ["h", "z", "w", "ads1", "ads2"]

        if self.default_row_labels is None:
            self.default_row_labels = ["h", "z", "w", "_", "_"]


@dataclass
class SliderConfig:
    """Configuration for slider components."""

    # Slider ranges
    min_value: int = -5
    max_value: int = 5
    tick_interval: int = 1

    # Slider behavior
    orientation: str = "horizontal"
    tick_position: str = "below"


@dataclass
class SpinBoxConfig:
    """Configuration for spin box components."""

    # Double spin box settings
    double_decimals: int = 2
    double_step: float = 0.01
    double_range: Tuple[float, float] = (0.0, 1.0)

    # Integer spin box settings
    int_min: int = 1
    int_max: int = 100
    int_step: int = 1

    # Font size specific
    fontsize_min: int = 1
    fontsize_max: int = 100
    fontsize_default: int = 8


@dataclass
class CheckBoxConfig:
    """Configuration for checkbox components."""

    # Default states
    annotation_default: bool = True
    polish_default: bool = True
    many_models_default: bool = False

    # Checkbox labels
    annotation_label: str = "annotation"
    many_models_label: str = "Many models"
    polish_label: str = "polish"


@dataclass
class ControlsConfig:
    """Main configuration class for all controls."""

    buttons: ButtonConfig = None
    inputs: InputConfig = None
    combos: ComboBoxConfig = None
    tables: TableConfig = None
    sliders: SliderConfig = None
    spinboxes: SpinBoxConfig = None
    checkboxes: CheckBoxConfig = None

    def __post_init__(self):
        if self.buttons is None:
            self.buttons = ButtonConfig()
        if self.inputs is None:
            self.inputs = InputConfig()
        if self.combos is None:
            self.combos = ComboBoxConfig()
        if self.tables is None:
            self.tables = TableConfig()
        if self.sliders is None:
            self.sliders = SliderConfig()
        if self.spinboxes is None:
            self.spinboxes = SpinBoxConfig()
        if self.checkboxes is None:
            self.checkboxes = CheckBoxConfig()
