"""Tests for PlotStylingMixin.

Tests line property determination, fill between, and annotation functionality.
"""

import numpy as np
import pandas as pd

from src.gui.main_tab.plot_canvas.plot_canvas import PlotCanvas


class TestDetermineLineProperties:
    """Tests for line property determination."""

    def test_cumulative_upper_bound_properties(self, qtbot):
        """Should return cumulative upper bound config."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        props = canvas.determine_line_properties("cumulative_upper_bound_coeffs")

        assert "linewidth" in props
        assert props["linewidth"] == 0.1
        assert props["color"] == "grey"

    def test_cumulative_lower_bound_properties(self, qtbot):
        """Should return cumulative lower bound config."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        props = canvas.determine_line_properties("cumulative_lower_bound_coeffs")

        assert "linewidth" in props
        assert props["linewidth"] == 0.1

    def test_cumulative_coeffs_properties(self, qtbot):
        """Should return cumulative line config for cumulative_coeffs."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        props = canvas.determine_line_properties("cumulative_coeffs")

        assert props["linestyle"] == "dotted"

    def test_upper_bound_coeffs_properties(self, qtbot):
        """Should return bound config for upper_bound_coeffs."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        props = canvas.determine_line_properties("upper_bound_coeffs")

        assert props["linewidth"] == 1.25
        assert props["linestyle"] == "-."

    def test_lower_bound_coeffs_properties(self, qtbot):
        """Should return bound config for lower_bound_coeffs."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        props = canvas.determine_line_properties("lower_bound_coeffs")

        assert props["linewidth"] == 1.25

    def test_default_line_properties(self, qtbot):
        """Should return default config for unknown names."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        props = canvas.determine_line_properties("unknown_reaction")

        assert props == {}


class TestUpdateFillBetween:
    """Tests for fill between regions."""

    def test_update_fill_between_no_lines(self, qtbot):
        """update_fill_between should not crash without lines."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        # Should not raise
        canvas.update_fill_between()

    def test_update_fill_between_with_bounds(self, qtbot):
        """update_fill_between should fill between bound lines."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        x = np.array([100, 200, 300])
        upper_y = np.array([0.5, 0.6, 0.4])
        lower_y = np.array([0.3, 0.4, 0.2])

        canvas.add_or_update_line("upper_bound_coeffs", x, upper_y)
        canvas.add_or_update_line("lower_bound_coeffs", x, lower_y)

        # Should not raise - fill_between is called
        canvas.update_fill_between()


class TestMockPlot:
    """Tests for mock plot generation."""

    def test_mock_plot_clears_previous_lines(self, qtbot):
        """mock_plot should clear existing custom lines."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        # Add a custom line (note: mock_plot is called in __init__, so lines exist)
        canvas.add_or_update_line("custom_test_line", [1, 2, 3], [1, 2, 3])
        assert "custom_test_line" in canvas.lines

        canvas.mock_plot()

        # Custom line should be gone (mock_plot clears and redraws)
        assert "custom_test_line" not in canvas.lines
        # Should still have model lines
        assert len(canvas.lines) > 0

    def test_mock_plot_adds_model_lines(self, qtbot):
        """mock_plot should add kinetic model lines."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        # mock_plot is called in __init__, so lines already exist
        # Just verify we have model lines
        assert len(canvas.lines) > 0

    def test_mock_plot_sets_labels(self, qtbot):
        """mock_plot should set axis labels."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        canvas.mock_plot()

        # Should have xlabel set to alpha
        xlabel = canvas.axes.get_xlabel()
        assert xlabel == "α"


class TestModelFitAnnotation:
    """Tests for model fit annotation."""

    def test_add_model_fit_annotation(self, qtbot):
        """add_model_fit_annotation should add annotation patch."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        annotation = r"$E_a = 150$\n$A = 10^{12}$"
        canvas.add_model_fit_annotation(annotation)

        # Check that patches were added (rectangle + text)
        patches = canvas.axes.patches
        assert len(patches) > 0

    def test_plot_model_fit_result(self, qtbot):
        """plot_model_fit_result should plot data with annotation."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        plot_df = pd.DataFrame(
            {"reverse_temperature": [0.002, 0.003, 0.004], "lhs_clean": [1.0, 2.0, 3.0], "y": [1.1, 2.1, 3.1]}
        )

        plot_kwargs = {"title": "Test Plot", "xlabel": "X", "ylabel": "Y", "annotation": r"$test$"}

        canvas.plot_model_fit_result([{"plot_df": plot_df, "plot_kwargs": plot_kwargs}])

        assert "lhs_clean" in canvas.lines
        assert "y" in canvas.lines
        assert canvas.axes.get_title() == "Test Plot"


class TestModelFreeAnnotation:
    """Tests for model free annotation."""

    def test_add_model_free_annotation(self, qtbot):
        """add_model_free_annotation should add annotation patch."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        annotation = r"$E_a = 150$\n$R^2 = 0.99$"
        canvas.add_model_free_annotation(annotation)

        # Check that patches were added
        patches = canvas.axes.patches
        assert len(patches) > 0

    def test_plot_model_free_result(self, qtbot):
        """plot_model_free_result should plot conversion data."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        plot_df = pd.DataFrame({"conversion": [0.1, 0.2, 0.3], "Ea": [150, 155, 160], "logA": [12, 12.5, 13]})

        plot_kwargs = {"title": "Isoconversional", "xlabel": "α", "ylabel": "Ea (kJ/mol)"}

        canvas.plot_model_free_result([{"plot_df": plot_df, "plot_kwargs": plot_kwargs}])

        assert "Ea" in canvas.lines
        assert "logA" in canvas.lines
        assert "conversion" not in canvas.lines  # x-axis, not plotted


class TestNormalizeData:
    """Tests for data normalization."""

    def test_normalize_data_basic(self, qtbot):
        """_normalize_data should normalize to [0, 1] range."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        data = np.array([0, 50, 100])
        normalized = canvas._normalize_data(data)

        assert np.isclose(normalized.min(), 0)
        assert np.isclose(normalized.max(), 1)

    def test_normalize_data_with_nan(self, qtbot):
        """_normalize_data should handle NaN values."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        data = np.array([0, np.nan, 100])
        normalized = canvas._normalize_data(data)

        # Should not crash and should return valid values
        assert not np.all(np.isnan(normalized))

    def test_normalize_data_with_inf(self, qtbot):
        """_normalize_data should handle inf values."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        data = np.array([0, np.inf, 100])
        normalized = canvas._normalize_data(data)

        # Should not crash
        assert not np.all(np.isnan(normalized))
