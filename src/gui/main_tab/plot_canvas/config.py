from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PlotCanvasConfig:
    """Configuration constants for PlotCanvas module."""

    # Style configurations
    PLOT_STYLE: List[str] = None

    # Mock plot configurations
    MOCK_PLOT_FUNCTION_TYPES: List[str] = None
    MOCK_PLOT_LINE_STYLES: List[str] = None
    MOCK_PLOT_LINE_WIDTHS: List[float] = None

    # Line property configurations
    BOUND_LINE_CONFIG: Dict[str, object] = None
    CUMULATIVE_LINE_CONFIG: Dict[str, object] = None
    DEFAULT_LINE_CONFIG: Dict[str, object] = None

    # Fill between configurations
    FILL_ALPHA: float = None
    FILL_COLOR: str = None

    def __post_init__(self):
        """Initialize default values."""
        if self.PLOT_STYLE is None:
            self.PLOT_STYLE = ["science", "no-latex", "nature", "grid"]

        if self.MOCK_PLOT_FUNCTION_TYPES is None:
            self.MOCK_PLOT_FUNCTION_TYPES = ["y", "g", "z"]

        if self.MOCK_PLOT_LINE_STYLES is None:
            self.MOCK_PLOT_LINE_STYLES = ["-", "--", "-."]

        if self.MOCK_PLOT_LINE_WIDTHS is None:
            self.MOCK_PLOT_LINE_WIDTHS = [0.5, 0.75, 1]

        if self.BOUND_LINE_CONFIG is None:
            self.BOUND_LINE_CONFIG = {
                "cumulative_upper_bound": {"linewidth": 0.1, "linestyle": "-", "color": "grey"},
                "cumulative_lower_bound": {"linewidth": 0.1, "linestyle": "-", "color": "grey"},
                "upper_bound_coeffs": {"linewidth": 1.25, "linestyle": "-."},
                "lower_bound_coeffs": {"linewidth": 1.25, "linestyle": "-."},
            }

        if self.CUMULATIVE_LINE_CONFIG is None:
            self.CUMULATIVE_LINE_CONFIG = {"linewidth": 1, "linestyle": "dotted"}

        if self.DEFAULT_LINE_CONFIG is None:
            self.DEFAULT_LINE_CONFIG = {}

        if self.FILL_ALPHA is None:
            self.FILL_ALPHA = 0.1

        if self.FILL_COLOR is None:
            self.FILL_COLOR = "grey"


# Global configuration instance
PLOT_CANVAS_CONFIG = PlotCanvasConfig()
