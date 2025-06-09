"""
Application Configuration Module
Contains dataclasses for main window and application-level settings.
"""

from dataclasses import dataclass


@dataclass
class WindowConfig:
    """Configuration for main application window"""

    title: str = "Open ThermoKinetics"
    min_width: int = 1200
    min_height: int = 800
    default_width: int = 1600
    default_height: int = 1000


@dataclass
class TabConfig:
    """Configuration for application tabs"""

    main_tab_name: str = "Main"
    table_tab_name: str = "Table"


@dataclass
class SplitterConfig:
    """Configuration for splitter ratios and sizes"""

    # Main tab splitter ratios
    sidebar_ratio: float = 0.2
    sub_sidebar_ratio: float = 0.2
    console_ratio: float = 0.15
    plot_ratio: float = 0.45

    # Minimum widths
    min_width_sidebar: int = 220
    min_width_subsidebar: int = 220
    min_width_console: int = 150
    min_width_plotcanvas: int = 500
    splitter_width: int = 100

    # Heights
    min_height_maintab: int = 700


@dataclass
class ComponentSizes:
    """Component size configurations"""

    # Button sizes
    button_width_standard: int = 80
    button_height_standard: int = 30
    button_size_small: int = 24

    # Table sizes
    table_cell_width: int = 50
    table_cell_height: int = 20

    # Input field sizes
    input_field_min_width: int = 100
    input_field_min_height: int = 30


@dataclass
class LayoutConfig:
    """Layout spacing and margins configuration"""

    layout_margin: int = 5
    layout_spacing: int = 5
    form_spacing: int = 10
    group_box_margin: int = 10


@dataclass
class ApplicationConfig:
    """Main application configuration combining all settings"""

    window: WindowConfig = None
    tabs: TabConfig = None
    splitter: SplitterConfig = None
    component_sizes: ComponentSizes = None
    layout: LayoutConfig = None

    def __post_init__(self):
        """Initialize nested configurations with defaults"""
        if self.window is None:
            self.window = WindowConfig()
        if self.tabs is None:
            self.tabs = TabConfig()
        if self.splitter is None:
            self.splitter = SplitterConfig()
        if self.component_sizes is None:
            self.component_sizes = ComponentSizes()
        if self.layout is None:
            self.layout = LayoutConfig()
