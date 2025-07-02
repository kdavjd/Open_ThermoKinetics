# config.py for series module
"""Configuration settings for the series sub-sidebar module."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SeriesDialogDimensions:
    """Dimensions configuration for series dialogs."""

    min_window_width: int = 300
    field_width: int = 290
    heating_rate_width: int = 80
    file_input_row_height: int = 50
    add_button_height: int = 40
    window_padding: int = 50


@dataclass(frozen=True)
class SeriesTableLayout:
    """Layout configuration for series tables."""

    columns: int = 3
    headers: List[str] = None

    def __post_init__(self):
        if self.headers is None:
            object.__setattr__(self, "headers", ["reactions", "Ea", "A"])


@dataclass(frozen=True)
class SeriesComboBoxDefaults:
    """Default items for series combo boxes."""

    reaction_placeholder: str = "select reaction"


@dataclass(frozen=True)
class SeriesLabels:
    """Label texts for series module."""

    load_deconvolution_results_button: str = "load deconvolution results"
    export_results_button: str = "Export Results"

    # Dialog labels
    experimental_data_label: str = "Experimental Data:"
    heating_rates_label: str = "Heating Rates (K/min):"
    masses_label: str = "Masses:"
    add_file_button: str = "Add File"
    file_label_prefix: str = "File"


@dataclass(frozen=True)
class SeriesDialogConfig:
    """Dialog configuration for series module."""

    # Dialog titles
    deconvolution_results_title: str = "load deconvolution results"

    # Dialog dimensions
    min_window_width: int = 300
    field_width: int = 290
    heating_rate_width: int = 80
    file_input_row_height: int = 50
    add_button_height: int = 40
    window_padding: int = 50

    # Dialog button texts
    add_file_button_text: str = "add file"
    heating_rate_placeholder: str = "heating rate"


@dataclass(frozen=True)
class SeriesConfig:
    """Main configuration for series module."""

    dialog_dimensions: SeriesDialogDimensions = SeriesDialogDimensions()
    dialog: SeriesDialogConfig = SeriesDialogConfig()
    table_layout: SeriesTableLayout = SeriesTableLayout()
    combobox: SeriesComboBoxDefaults = SeriesComboBoxDefaults()
    labels: SeriesLabels = SeriesLabels()
