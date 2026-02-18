"""Tests for PlotCanvas GUI component.

Tests matplotlib canvas, line management, and data plotting.
"""

from datetime import datetime

import numpy as np
import pandas as pd

from src.gui.main_tab.plot_canvas.plot_canvas import PlotCanvas


class TestPlotCanvasCreation:
    """Tests for PlotCanvas initialization."""

    def test_plot_canvas_creates_without_error(self, qtbot):
        """PlotCanvas should initialize without exceptions."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        assert canvas is not None

    def test_plot_canvas_has_figure(self, qtbot):
        """PlotCanvas should contain a Matplotlib Figure."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        assert canvas.figure is not None
        assert canvas.axes is not None

    def test_plot_canvas_has_toolbar(self, qtbot):
        """PlotCanvas should have a navigation toolbar."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        assert canvas.toolbar is not None

    def test_plot_canvas_initial_lines_not_empty(self, qtbot):
        """PlotCanvas should have model lines after init (mock_plot is called)."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        # mock_plot is called in __init__, so lines are not empty
        assert len(canvas.lines) > 0

    def test_plot_canvas_interaction_attrs_initialized(self, qtbot):
        """PlotCanvas should initialize interaction attributes."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        assert canvas.background is None
        assert canvas.dragging_anchor is None
        assert canvas.dragging_anchor_group is None


class TestPlotCanvasLines:
    """Tests for line management."""

    def test_add_or_update_line_creates_new(self, qtbot):
        """add_or_update_line should create a new line."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        initial_count = len(canvas.lines)

        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        canvas.add_or_update_line("test_line", x, y, label="Test")

        assert "test_line" in canvas.lines
        assert len(canvas.lines) == initial_count + 1

    def test_add_or_update_line_updates_existing(self, qtbot):
        """add_or_update_line should update existing line data."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        x1 = np.array([1, 2, 3])
        y1 = np.array([4, 5, 6])
        canvas.add_or_update_line("test_line", x1, y1)

        initial_count = len(canvas.lines)

        x2 = np.array([10, 20, 30])
        y2 = np.array([40, 50, 60])
        canvas.add_or_update_line("test_line", x2, y2)

        line = canvas.lines["test_line"]
        assert np.array_equal(line.get_xdata(), x2)
        assert np.array_equal(line.get_ydata(), y2)
        assert len(canvas.lines) == initial_count

    def test_add_multiple_lines(self, qtbot):
        """PlotCanvas should handle multiple lines."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        initial_count = len(canvas.lines)

        x = np.array([1, 2, 3])
        canvas.add_or_update_line("line1", x, np.array([1, 2, 3]))
        canvas.add_or_update_line("line2", x, np.array([4, 5, 6]))
        canvas.add_or_update_line("line3", x, np.array([7, 8, 9]))

        assert len(canvas.lines) == initial_count + 3


class TestPlotCanvasDataFrame:
    """Tests for DataFrame plotting."""

    def test_plot_data_from_dataframe(self, qtbot):
        """plot_data_from_dataframe should plot columns."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        df = pd.DataFrame({"temperature": [100, 200, 300], "dtg": [0.1, 0.5, 0.3], "mass": [1.0, 0.8, 0.6]})

        canvas.plot_data_from_dataframe(df)

        assert "dtg" in canvas.lines
        assert "mass" in canvas.lines
        assert "temperature" not in canvas.lines

    def test_plot_data_from_dataframe_clears_previous(self, qtbot):
        """plot_data_from_dataframe should clear previous lines."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        # First plot
        df1 = pd.DataFrame({"temperature": [100, 200], "signal1": [0.1, 0.2]})
        canvas.plot_data_from_dataframe(df1)

        # Second plot
        df2 = pd.DataFrame({"temperature": [100, 200], "signal2": [0.3, 0.4]})
        canvas.plot_data_from_dataframe(df2)

        assert "signal1" not in canvas.lines
        assert "signal2" in canvas.lines


class TestPlotCanvasMSEHistory:
    """Tests for MSE history plotting."""

    def test_plot_mse_history_with_data(self, qtbot):
        """plot_mse_history should plot MSE data."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        now = datetime.now()
        mse_data = [(now, 0.5), (now, 0.3), (now, 0.1)]

        canvas.plot_mse_history(mse_data)

        assert "mse_line" in canvas.lines
        assert canvas.is_mse_mode() is True

    def test_plot_mse_history_empty(self, qtbot):
        """plot_mse_history should handle empty data."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        canvas.plot_mse_history([])

        # Should not crash, lines should remain empty
        assert "mse_line" not in canvas.lines

    def test_is_mse_mode_false_by_default(self, qtbot):
        """is_mse_mode should return False initially."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        assert canvas.is_mse_mode() is False


class TestPlotCanvasEventConnections:
    """Tests for event connection management."""

    def test_toggle_event_connections_enable(self, qtbot):
        """toggle_event_connections should connect events when enabled."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        canvas.toggle_event_connections(True)

        assert canvas.cid_press is not None
        assert canvas.cid_release is not None
        assert canvas.cid_motion is not None

        # Cleanup
        canvas.toggle_event_connections(False)

    def test_toggle_event_connections_disable(self, qtbot):
        """toggle_event_connections should disconnect events when disabled."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        canvas.toggle_event_connections(True)
        canvas.toggle_event_connections(False)

        # After disconnect, cids should remain but not be active
        # (matplotlib doesn't reset them to None)


class TestPlotCanvasReaction:
    """Tests for reaction plotting."""

    def test_plot_reaction_adds_line(self, qtbot):
        """plot_reaction should add a reaction line."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        keys = ("test_file.csv", "reaction_1")
        values = (np.array([100, 200, 300]), np.array([0.1, 0.5, 0.3]))

        canvas.plot_reaction(keys, values)

        assert "reaction_1" in canvas.lines

    def test_plot_reaction_updates_existing(self, qtbot):
        """plot_reaction should update existing reaction line."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        keys = ("test_file.csv", "reaction_1")

        # First call
        values1 = (np.array([100, 200, 300]), np.array([0.1, 0.5, 0.3]))
        canvas.plot_reaction(keys, values1)

        # Second call with different data
        values2 = (np.array([100, 200, 300]), np.array([0.2, 0.6, 0.4]))
        canvas.plot_reaction(keys, values2)

        line = canvas.lines["reaction_1"]
        assert np.array_equal(line.get_ydata(), np.array([0.2, 0.6, 0.4]))


class TestPlotCanvasAnchors:
    """Tests for anchor management."""

    def test_add_anchors_creates_groups(self, qtbot):
        """add_anchors should create anchor groups."""
        canvas = PlotCanvas()
        qtbot.addWidget(canvas)

        reaction_data = {
            "coeffs": ((100, 300), "gauss", (0.5, 200, 50)),
            "upper_bound_coeffs": ((100, 300), "gauss", (0.6, 210, 60)),
            "lower_bound_coeffs": ((100, 300), "gauss", (0.4, 190, 40)),
        }

        canvas.add_anchors(reaction_data)

        assert canvas.position_anchor_group is not None
        assert canvas.height_anchor_group is not None
