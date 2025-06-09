"""
Visualization Configuration Module
Contains dataclasses for plot styling, anchor management, and visualization settings.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PlotConfig:
    """Configuration for plot styling"""

    style: List[str] = None
    figure_dpi: int = 100
    default_colors: List[str] = None
    line_width: float = 1.5
    marker_size: float = 4.0

    # Plot appearance
    grid_alpha: float = 0.3
    legend_fontsize: int = 8
    axis_labelsize: int = 10
    tick_labelsize: int = 8
    title_fontsize: int = 12

    def __post_init__(self):
        if self.style is None:
            self.style = ["science", "no-latex", "nature", "grid"]
        if self.default_colors is None:
            self.default_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


@dataclass
class AnnotationConfig:
    """Configuration for plot annotations"""

    default_fontsize: int = 8
    default_facecolor: str = "white"
    default_edgecolor: str = "black"
    default_alpha: float = 1.0
    delta_x_default: float = 0.02
    delta_y_default: float = 0.02

    # Text positioning
    text_offset_x: int = -10
    text_offset_y: int = -10
    text_alignment: str = "center"


@dataclass
class AnchorConfig:
    """Configuration for plot anchors"""

    anchor_size: float = 8.0
    anchor_color: str = "red"
    line_color: str = "gray"
    line_style: str = "--"
    line_width: float = 1.0

    # Interaction
    selection_tolerance: float = 10.0
    drag_threshold: float = 5.0

    # Position constraints
    position_offset: float = 0.1  # Minimum offset for bound anchors from center
    picker_tolerance: int = 5  # Picker tolerance for anchor selection


@dataclass
class FillBetweenConfig:
    """Configuration for fill between areas"""

    color: str = "grey"
    alpha: float = 0.1
    line_width: float = 0.5


@dataclass
class MockPlotConfig:
    """Configuration for mock plotting"""

    line_styles: List[str] = None
    line_widths: List[float] = None
    alpha_range: Tuple[float, float] = (0.001, 1.0)
    alpha_points: int = 100

    # Normalization settings
    normalize_line_styles: List[str] = None
    normalize_line_widths: List[float] = None

    def __post_init__(self):
        if self.line_styles is None:
            self.line_styles = ["-", "--", "-."]
        if self.line_widths is None:
            self.line_widths = [0.5, 0.75, 1.0]
        if self.normalize_line_styles is None:
            self.normalize_line_styles = ["-", "--", "-."]
        if self.normalize_line_widths is None:
            self.normalize_line_widths = [0.5, 0.75, 1]


@dataclass
class AxisConfig:
    """Configuration for plot axes"""

    xlabel_default: str = "α"
    ylabel_mappings: dict = None
    title_mappings: dict = None

    def __post_init__(self):
        if self.ylabel_mappings is None:
            self.ylabel_mappings = {"g": "g(α)", "y": "y(α)", "z": "z(α)"}
        if self.title_mappings is None:
            self.title_mappings = {
                "g": "Theoretical view of g(α) graphs",
                "y": "Theoretical view of y(α) master graphs",
                "z": "Theoretical view of z(α) master graphs",
            }


@dataclass
class NavigationConfig:
    """Configuration for plot navigation and toolbar"""

    enable_toolbar: bool = True
    toolbar_position: str = "bottom"
    pan_key: str = "p"
    zoom_key: str = "z"
    home_key: str = "h"


@dataclass
class VisualizationConfig:
    """Main visualization configuration combining all plot settings"""

    plot: PlotConfig = None
    annotation: AnnotationConfig = None
    anchor: AnchorConfig = None
    fill_between: FillBetweenConfig = None
    mock_plot: MockPlotConfig = None
    axis: AxisConfig = None
    navigation: NavigationConfig = None

    def __post_init__(self):
        """Initialize nested configurations with defaults"""
        if self.plot is None:
            self.plot = PlotConfig()
        if self.annotation is None:
            self.annotation = AnnotationConfig()
        if self.anchor is None:
            self.anchor = AnchorConfig()
        if self.fill_between is None:
            self.fill_between = FillBetweenConfig()
        if self.mock_plot is None:
            self.mock_plot = MockPlotConfig()
        if self.axis is None:
            self.axis = AxisConfig()
        if self.navigation is None:
            self.navigation = NavigationConfig()
