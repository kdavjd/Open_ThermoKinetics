"""Tests for AnchorGroup classes.

Tests for PositionAnchorGroup, HeightAnchorGroup, and base AnchorGroup.
"""

import pytest
from matplotlib.figure import Figure

from src.gui.main_tab.plot_canvas.anchor_group import (
    AnchorGroup,
    HeightAnchorGroup,
    PositionAnchorGroup,
)


class TestAnchorGroupBase:
    """Tests for base AnchorGroup class."""

    @pytest.fixture
    def axes(self):
        """Create matplotlib axes for testing."""
        fig = Figure()
        return fig.add_subplot(111)

    @pytest.fixture
    def anchor_params(self):
        """Sample anchor parameters (h, z, w)."""
        center = (1.0, 200.0, 50.0)
        upper = (1.5, 250.0, 60.0)
        lower = (0.5, 150.0, 40.0)
        return center, upper, lower

    def test_anchor_group_creates_anchors(self, axes, anchor_params):
        """AnchorGroup should create center, upper, and lower anchors."""
        center, upper, lower = anchor_params
        group = AnchorGroup(axes, center, upper, lower)

        assert group.center is not None
        assert group.upper_bound is not None
        assert group.lower_bound is not None

    def test_anchor_group_initial_positions(self, axes, anchor_params):
        """AnchorGroup should set initial positions correctly."""
        center, upper, lower = anchor_params
        group = AnchorGroup(axes, center, upper, lower)

        # Center anchor: x=z, y=h
        assert group.center.get_xdata()[0] == 200.0
        assert group.center.get_ydata()[0] == 1.0

    def test_set_center_position(self, axes, anchor_params):
        """set_center_position should move all anchors together."""
        center, upper, lower = anchor_params
        group = AnchorGroup(axes, center, upper, lower)

        group.set_center_position(300.0, 2.0)

        assert group.center.get_xdata()[0] == 300.0
        assert group.center.get_ydata()[0] == 2.0

    def test_get_bound_positions(self, axes, anchor_params):
        """get_bound_positions should return current positions."""
        center, upper, lower = anchor_params
        group = AnchorGroup(axes, center, upper, lower)

        positions = group.get_bound_positions()

        assert "upper_bound" in positions
        assert "lower_bound" in positions
        assert len(positions["upper_bound"]) == 2


class TestPositionAnchorGroup:
    """Tests for PositionAnchorGroup (horizontal movement)."""

    @pytest.fixture
    def axes(self):
        """Create matplotlib axes for testing."""
        fig = Figure()
        return fig.add_subplot(111)

    @pytest.fixture
    def anchor_params(self):
        """Sample anchor parameters for position group."""
        center = (1.0, 200.0, 50.0)
        upper = (1.0, 250.0, 60.0)
        lower = (1.0, 150.0, 40.0)
        return center, upper, lower

    def test_position_anchor_y_fixed_at_zero(self, axes, anchor_params):
        """PositionAnchorGroup should fix y values at 0."""
        center, upper, lower = anchor_params
        group = PositionAnchorGroup(axes, center, upper, lower)

        # All anchors should have y=0
        assert group.center.get_ydata()[0] == 0
        assert group.upper_bound.get_ydata()[0] == 0
        assert group.lower_bound.get_ydata()[0] == 0

    def test_set_center_position_horizontal(self, axes, anchor_params):
        """set_center_position should only move horizontally."""
        center, upper, lower = anchor_params
        group = PositionAnchorGroup(axes, center, upper, lower)

        initial_upper_x = group.upper_bound.get_xdata()[0]
        initial_lower_x = group.lower_bound.get_xdata()[0]

        group.set_center_position(300.0)

        # Center should move to new x, y stays 0
        assert group.center.get_xdata()[0] == 300.0
        assert group.center.get_ydata()[0] == 0

        # Bounds should shift by same delta
        assert group.upper_bound.get_xdata()[0] == initial_upper_x + 100.0
        assert group.lower_bound.get_xdata()[0] == initial_lower_x + 100.0

    def test_set_bound_position_symmetric(self, axes, anchor_params):
        """set_bound_position should maintain symmetric bounds."""
        center, upper, lower = anchor_params
        group = PositionAnchorGroup(axes, center, upper, lower)

        center_x = group.center.get_xdata()[0]
        group.set_bound_position(group.upper_bound, 280.0)

        # Lower bound should be symmetric
        expected_lower_x = center_x - (280.0 - center_x)
        assert group.lower_bound.get_xdata()[0] == expected_lower_x

    def test_upper_bound_cannot_cross_center(self, axes, anchor_params):
        """Upper bound should not cross to left of center."""
        center, upper, lower = anchor_params
        group = PositionAnchorGroup(axes, center, upper, lower)

        center_x = group.center.get_xdata()[0]
        group.set_bound_position(group.upper_bound, center_x - 10.0)

        # Should be constrained to center + 0.1
        assert group.upper_bound.get_xdata()[0] == center_x + 0.1


class TestHeightAnchorGroup:
    """Tests for HeightAnchorGroup (vertical movement)."""

    @pytest.fixture
    def axes(self):
        """Create matplotlib axes for testing."""
        fig = Figure()
        return fig.add_subplot(111)

    @pytest.fixture
    def anchor_params(self):
        """Sample anchor parameters for height group."""
        center = (1.0, 200.0, 50.0)
        upper = (1.5, 200.0, 60.0)
        lower = (0.5, 200.0, 40.0)
        return center, upper, lower

    def test_height_anchor_x_constant(self, axes, anchor_params):
        """HeightAnchorGroup should keep x values constant."""
        center, upper, lower = anchor_params
        group = HeightAnchorGroup(axes, center, upper, lower)

        # All anchors should have same x (z value)
        assert group.center.get_xdata()[0] == 200.0
        assert group.upper_bound.get_xdata()[0] == 200.0
        assert group.lower_bound.get_xdata()[0] == 200.0

    def test_set_center_position_vertical(self, axes, anchor_params):
        """set_center_position should only move vertically."""
        center, upper, lower = anchor_params
        group = HeightAnchorGroup(axes, center, upper, lower)

        initial_x = group.center.get_xdata()[0]

        group.set_center_position(2.0)

        # x should stay constant, y should change
        assert group.center.get_xdata()[0] == initial_x
        assert group.center.get_ydata()[0] == 2.0

    def test_set_bound_position_symmetric(self, axes, anchor_params):
        """set_bound_position should maintain symmetric vertical bounds."""
        center, upper, lower = anchor_params
        group = HeightAnchorGroup(axes, center, upper, lower)

        center_y = group.center.get_ydata()[0]
        group.set_bound_position(group.upper_bound, 2.0)

        # Lower bound should be symmetric
        expected_lower_y = center_y - (2.0 - center_y)
        assert group.lower_bound.get_ydata()[0] == expected_lower_y

    def test_lower_bound_cannot_cross_center(self, axes, anchor_params):
        """Lower bound should not go above center."""
        center, upper, lower = anchor_params
        group = HeightAnchorGroup(axes, center, upper, lower)

        center_y = group.center.get_ydata()[0]
        group.set_bound_position(group.lower_bound, center_y + 0.5)

        # Should be constrained to center - 0.1
        assert group.lower_bound.get_ydata()[0] == center_y - 0.1

    def test_get_bound_positions_returns_numbers_not_none(self, axes, anchor_params):
        """get_bound_positions should return numeric values, never None."""
        center, upper, lower = anchor_params
        group = HeightAnchorGroup(axes, center, upper, lower)

        # Move anchors to new positions
        group.set_center_position(2.0)
        group.set_bound_position(group.upper_bound, 2.5)

        positions = group.get_bound_positions()

        # Verify all values are numeric (not None)
        assert positions["upper_bound"][0] is not None
        assert positions["upper_bound"][1] is not None
        assert positions["lower_bound"][0] is not None
        assert positions["lower_bound"][1] is not None

        # Verify they are actually numbers
        assert isinstance(positions["upper_bound"][0], (int, float))
        assert isinstance(positions["upper_bound"][1], (int, float))
        assert isinstance(positions["lower_bound"][0], (int, float))
        assert isinstance(positions["lower_bound"][1], (int, float))


class TestPlotInteractionMixinCalculateCenter:
    """Tests for _calculate_center method in PlotInteractionMixin."""

    @pytest.fixture
    def mixin(self):
        """Create a PlotInteractionMixin instance for testing."""
        from src.gui.main_tab.plot_canvas.plot_interaction import PlotInteractionMixin

        class ConcreteMixin(PlotInteractionMixin):
            pass

        instance = ConcreteMixin()
        return instance

    def test_calculate_center_returns_numeric_values(self, mixin):
        """_calculate_center should return numeric values, never None."""
        positions = {
            "upper_bound": (250.0, 1.5),
            "lower_bound": (150.0, 0.5),
        }

        result = mixin._calculate_center(positions)

        assert result["center"][0] is not None
        assert result["center"][1] is not None
        assert isinstance(result["center"][0], (int, float))
        assert isinstance(result["center"][1], (int, float))

    def test_calculate_center_correct_calculation(self, mixin):
        """_calculate_center should correctly calculate midpoint."""
        positions = {
            "upper_bound": (250.0, 2.0),
            "lower_bound": (150.0, 0.0),
        }

        result = mixin._calculate_center(positions)

        # Center should be average of bounds
        assert result["center"][0] == 200.0  # (250 + 150) / 2
        assert result["center"][1] == 1.0  # (2.0 + 0.0) / 2

    def test_calculate_center_with_negative_values(self, mixin):
        """_calculate_center should handle negative coordinates."""
        positions = {
            "upper_bound": (-100.0, -0.5),
            "lower_bound": (-200.0, -1.5),
        }

        result = mixin._calculate_center(positions)

        assert result["center"][0] == -150.0
        assert result["center"][1] == -1.0


class TestAnchorGroupNeverReturnsNone:
    """Tests verifying anchor operations never return None values."""

    @pytest.fixture
    def axes(self):
        """Create matplotlib axes for testing."""
        fig = Figure()
        return fig.add_subplot(111)

    def test_position_anchor_get_bound_positions_after_drag(self, axes):
        """PositionAnchorGroup.get_bound_positions should return numbers after drag."""
        center = (1.0, 200.0, 50.0)
        upper = (1.0, 250.0, 60.0)
        lower = (1.0, 150.0, 40.0)
        group = PositionAnchorGroup(axes, center, upper, lower)

        # Simulate drag operations
        group.set_center_position(300.0)
        group.set_bound_position(group.upper_bound, 350.0)

        positions = group.get_bound_positions()

        # All values must be numeric
        for key in ["upper_bound", "lower_bound"]:
            x, y = positions[key]
            assert x is not None, f"{key} x-coordinate is None"
            assert y is not None, f"{key} y-coordinate is None"
            assert isinstance(x, (int, float)), f"{key} x is not numeric: {type(x)}"
            assert isinstance(y, (int, float)), f"{key} y is not numeric: {type(y)}"

    def test_height_anchor_get_bound_positions_after_drag(self, axes):
        """HeightAnchorGroup.get_bound_positions should return numbers after drag."""
        center = (1.0, 200.0, 50.0)
        upper = (1.5, 200.0, 60.0)
        lower = (0.5, 200.0, 40.0)
        group = HeightAnchorGroup(axes, center, upper, lower)

        # Simulate drag operations
        group.set_center_position(2.0)
        group.set_bound_position(group.upper_bound, 2.5)

        positions = group.get_bound_positions()

        # All values must be numeric
        for key in ["upper_bound", "lower_bound"]:
            x, y = positions[key]
            assert x is not None, f"{key} x-coordinate is None"
            assert y is not None, f"{key} y-coordinate is None"
            assert isinstance(x, (int, float)), f"{key} x is not numeric: {type(x)}"
            assert isinstance(y, (int, float)), f"{key} y is not numeric: {type(y)}"
