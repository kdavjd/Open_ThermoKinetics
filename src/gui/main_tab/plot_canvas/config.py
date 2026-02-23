from dataclasses import dataclass, field
from typing import Dict, List


def _default_base_style_params() -> Dict[str, object]:
    return {
        # Typography
        "font.family": "sans-serif",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        # Lines
        "lines.linewidth": 1.0,
        # Grid
        "axes.grid": True,
        "grid.alpha": 0.4,
        "grid.linewidth": 0.5,
        # Spines (scientific style: hide top and right)
        "axes.spines.top": False,
        "axes.spines.right": False,
        # Misc
        "figure.autolayout": True,
        "text.usetex": False,
        "axes.axisbelow": True,
    }


def _default_npg_palette() -> List[str]:
    return [
        "#E64B35",  # coral red      (NPG-original)
        "#4DBBD5",  # sky cyan       (NPG-original)
        "#00A087",  # emerald teal   (NPG-original)
        "#7B9AFF",  # periwinkle     (brightened from #3C5488)
        "#F39B7F",  # peach salmon   (NPG-original)
        "#B0BCF5",  # soft lavender  (brightened from #8491B4)
        "#91D1C2",  # mint           (NPG-original)
        "#FF6B6B",  # bright coral   (brightened from #DC0000)
        "#C4956A",  # warm caramel   (brightened from #7E6148)
        "#FBBF24",  # amber          (replaces muted beige #B09C85)
    ]


def _default_theme_params() -> Dict[str, dict]:
    return {
        "light": {
            "figure.facecolor": "#FFFFFF",
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": "#0F172A",
            "axes.labelcolor": "#0F172A",
            "xtick.color": "#0F172A",
            "ytick.color": "#0F172A",
            "text.color": "#0F172A",
            "grid.color": "#E2E8F0",
            "legend.facecolor": "#F8FAFC",
            "legend.edgecolor": "#E2E8F0",
        },
        "dark": {
            "figure.facecolor": "#0F172A",
            "axes.facecolor": "#0F172A",
            "axes.edgecolor": "#F8FAFC",
            "axes.labelcolor": "#F8FAFC",
            "xtick.color": "#F8FAFC",
            "ytick.color": "#F8FAFC",
            "text.color": "#F8FAFC",
            "grid.color": "#334155",
            "legend.facecolor": "#1E293B",
            "legend.edgecolor": "#334155",
        },
    }


def _default_annotation_theme_params() -> Dict[str, dict]:
    return {
        "light": {
            "facecolor": "#F8FAFC",
            "edgecolor": "#E2E8F0",
            "text_color": "#0F172A",
        },
        "dark": {
            "facecolor": "#1E293B",
            "edgecolor": "#334155",
            "text_color": "#F8FAFC",
        },
    }


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

    # Theme and styling configurations
    BASE_STYLE_PARAMS: Dict[str, object] = field(default_factory=_default_base_style_params)
    NPG_PALETTE: List[str] = field(default_factory=_default_npg_palette)
    THEME_PARAMS: Dict[str, dict] = field(default_factory=_default_theme_params)
    ANNOTATION_THEME_PARAMS: Dict[str, dict] = field(default_factory=_default_annotation_theme_params)

    def __post_init__(self):
        """Initialize default values."""
        if self.PLOT_STYLE is None:
            self.PLOT_STYLE = []

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
