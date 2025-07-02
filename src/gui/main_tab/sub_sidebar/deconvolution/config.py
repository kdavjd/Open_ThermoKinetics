# config.py for deconvolution module
"""Configuration settings for the deconvolution sub-sidebar module."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DeconvolutionDefaults:
    """Default values for deconvolution parameters."""

    # Default function options
    function_items: List[str] = None
    default_function: str = "gauss"

    # Deconvolution method options
    method_options: List[str] = None
    default_method: str = "differential_evolution"

    # Default reactions counter
    reactions_counter_default: int = 0

    def __post_init__(self):
        if self.function_items is None:
            object.__setattr__(self, "function_items", ["gauss", "fraser", "ads"])
        if self.method_options is None:
            object.__setattr__(self, "method_options", ["differential_evolution", "another_method"])


@dataclass(frozen=True)
class ReactionTableLayout:
    """Layout configuration for reaction table."""

    columns: int = 2
    column_headers: List[str] = None

    def __post_init__(self):
        if self.column_headers is None:
            object.__setattr__(self, "column_headers", ["name", "function"])


@dataclass(frozen=True)
class FileTransferConfig:
    """Configuration for file transfer operations."""

    file_extensions: str = "JSON Files (*.json)"
    export_indent: int = 4
    encoding: str = "utf-8"


@dataclass(frozen=True)
class CalculationSettingsDefaults:
    """Default values for calculation settings dialog."""

    # Method options
    calculation_methods: List[str] = None
    default_method: str = "differential_evolution"

    # Differential Evolution strategy options
    strategy_options: List[str] = None
    init_options: List[str] = None
    updating_options: List[str] = None

    def __post_init__(self):
        if self.calculation_methods is None:
            object.__setattr__(self, "calculation_methods", ["differential_evolution", "another_method"])

        if self.strategy_options is None:
            object.__setattr__(
                self,
                "strategy_options",
                [
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
                ],
            )

        if self.init_options is None:
            object.__setattr__(self, "init_options", ["latinhypercube", "random"])

        if self.updating_options is None:
            object.__setattr__(self, "updating_options", ["immediate", "deferred"])


@dataclass(frozen=True)
class DeconvolutionDialogLayout:
    """Layout configuration for deconvolution dialogs."""

    # GroupBox titles
    reactions_groupbox_title: str = "functions"
    deconvolution_groupbox_title: str = "deconvolution parameters"

    # Grid layout settings
    grid_row_start: int = 0
    grid_col_start: int = 0


@dataclass(frozen=True)
class DeconvolutionLabels:
    """Label texts for deconvolution module."""

    add_reaction_button: str = "add reaction"
    delete_reaction_button: str = "delete"
    import_button: str = "import"
    export_button: str = "export"
    deconvolution_method_label: str = "deconvolution method:"

    # Tooltips and messages
    file_not_selected_title: str = "The file is not selected"
    file_not_selected_message: str = "Choose an experiment"
    calculation_settings_title: str = "calculation settings"
    updated_for_message: str = "updated for:"


@dataclass(frozen=True)
class DeconvolutionConfig:
    """Main configuration for deconvolution module."""

    defaults: DeconvolutionDefaults = DeconvolutionDefaults()
    table_layout: ReactionTableLayout = ReactionTableLayout()
    file_transfer: FileTransferConfig = FileTransferConfig()
    calculation_settings: CalculationSettingsDefaults = CalculationSettingsDefaults()
    dialog_layout: DeconvolutionDialogLayout = DeconvolutionDialogLayout()
    labels: DeconvolutionLabels = DeconvolutionLabels()
