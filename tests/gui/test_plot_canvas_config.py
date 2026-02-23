"""Tests for PlotCanvasConfig constants.

Verifies BASE_STYLE_PARAMS, NPG_PALETTE, THEME_PARAMS, ANNOTATION_THEME_PARAMS,
and PLOT_STYLE fields added in feature/plot-canvas-design-system.
"""

from src.gui.main_tab.plot_canvas.config import PLOT_CANVAS_CONFIG


class TestBaseStyleParams:
    """Tests for BASE_STYLE_PARAMS — replaces scienceplots functionality."""

    def test_plot_style_is_empty(self):
        """PLOT_STYLE must be empty — scienceplots removed."""
        assert PLOT_CANVAS_CONFIG.PLOT_STYLE == []

    def test_base_style_params_grid_enabled(self):
        """axes.grid must be True (was provided by scienceplots 'grid' style)."""
        assert PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS["axes.grid"] is True

    def test_base_style_params_no_latex(self):
        """text.usetex must be False (was provided by scienceplots 'no-latex')."""
        assert PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS["text.usetex"] is False

    def test_base_style_params_hides_top_spine(self):
        """Top spine must be hidden for scientific plot style."""
        assert PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS["axes.spines.top"] is False

    def test_base_style_params_hides_right_spine(self):
        """Right spine must be hidden for scientific plot style."""
        assert PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS["axes.spines.right"] is False

    def test_base_style_params_has_font_size(self):
        """font.size must be present for typography control."""
        assert "font.size" in PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS

    def test_base_style_params_has_linewidth(self):
        """lines.linewidth must be present (was set by scienceplots)."""
        assert "lines.linewidth" in PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS


class TestNPGPalette:
    """Tests for NPG_PALETTE — 10-color scientific palette."""

    def test_npg_palette_has_ten_colors(self):
        """NPG_PALETTE must contain exactly 10 colors."""
        assert len(PLOT_CANVAS_CONFIG.NPG_PALETTE) == 10

    def test_npg_palette_all_hex_strings(self):
        """All NPG_PALETTE entries must be valid 6-digit hex color strings."""
        for color in PLOT_CANVAS_CONFIG.NPG_PALETTE:
            assert color.startswith("#"), f"{color!r} is not a hex color"
            assert len(color) == 7, f"{color!r} is not a valid 6-digit hex"


class TestThemeParams:
    """Tests for THEME_PARAMS — light/dark matplotlib rcParams."""

    def test_light_theme_figure_facecolor(self):
        """Light theme figure background must be white."""
        assert PLOT_CANVAS_CONFIG.THEME_PARAMS["light"]["figure.facecolor"] == "#FFFFFF"

    def test_dark_theme_figure_facecolor(self):
        """Dark theme figure background must be #0F172A."""
        assert PLOT_CANVAS_CONFIG.THEME_PARAMS["dark"]["figure.facecolor"] == "#0F172A"

    def test_light_theme_text_color(self):
        """Light theme text must be dark (#0F172A)."""
        assert PLOT_CANVAS_CONFIG.THEME_PARAMS["light"]["text.color"] == "#0F172A"

    def test_dark_theme_text_color(self):
        """Dark theme text must be light (#F8FAFC)."""
        assert PLOT_CANVAS_CONFIG.THEME_PARAMS["dark"]["text.color"] == "#F8FAFC"

    def test_dark_theme_grid_color(self):
        """Dark theme grid must use muted color (#334155)."""
        assert PLOT_CANVAS_CONFIG.THEME_PARAMS["dark"]["grid.color"] == "#334155"

    def test_light_theme_grid_color(self):
        """Light theme grid must use light color (#E2E8F0)."""
        assert PLOT_CANVAS_CONFIG.THEME_PARAMS["light"]["grid.color"] == "#E2E8F0"

    def test_both_themes_have_required_keys(self):
        """Both themes must define all required matplotlib rcParam keys."""
        required_keys = [
            "figure.facecolor",
            "axes.facecolor",
            "axes.edgecolor",
            "axes.labelcolor",
            "xtick.color",
            "ytick.color",
            "text.color",
            "grid.color",
            "legend.facecolor",
            "legend.edgecolor",
        ]
        for theme in ("light", "dark"):
            for key in required_keys:
                assert key in PLOT_CANVAS_CONFIG.THEME_PARAMS[theme], f"THEME_PARAMS[{theme!r}] missing key {key!r}"


class TestModuleLevelPropCycle:
    """Tests that NPG_PALETTE is set as the default prop_cycle at import time.

    This ensures mock_plot() (called before apply_theme()) already uses
    NPG colors visible on dark backgrounds.
    """

    def test_prop_cycle_uses_npg_palette_after_import(self):
        """axes.prop_cycle must equal NPG_PALETTE after plot_canvas is imported."""
        import matplotlib

        # Importing plot_canvas.py triggers module-level rcParams update
        import src.gui.main_tab.plot_canvas.plot_canvas  # noqa: F401

        cycle_colors = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
        assert cycle_colors == PLOT_CANVAS_CONFIG.NPG_PALETTE, (
            "Module-level prop_cycle is not set to NPG_PALETTE. "
            "mock_plot() will use matplotlib default colors instead of NPG palette."
        )


class TestAnnotationThemeParams:
    """Tests for ANNOTATION_THEME_PARAMS — annotation box styling."""

    def test_dark_annotation_facecolor(self):
        """Dark annotation background must be #1E293B."""
        assert PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS["dark"]["facecolor"] == "#1E293B"

    def test_light_annotation_facecolor(self):
        """Light annotation background must be #F8FAFC."""
        assert PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS["light"]["facecolor"] == "#F8FAFC"

    def test_both_themes_have_text_color(self):
        """Both themes must define text_color for annotation text."""
        for theme in ("light", "dark"):
            assert "text_color" in PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS[theme]

    def test_dark_annotation_text_color(self):
        """Dark annotation text must be light (#F8FAFC)."""
        assert PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS["dark"]["text_color"] == "#F8FAFC"

    def test_light_annotation_text_color(self):
        """Light annotation text must be dark (#0F172A)."""
        assert PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS["light"]["text_color"] == "#0F172A"

    def test_both_themes_have_all_keys(self):
        """Both themes must define facecolor, edgecolor, text_color."""
        for theme in ("light", "dark"):
            for key in ("facecolor", "edgecolor", "text_color"):
                assert key in PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS[theme], (
                    f"ANNOTATION_THEME_PARAMS[{theme!r}] missing key {key!r}"
                )
