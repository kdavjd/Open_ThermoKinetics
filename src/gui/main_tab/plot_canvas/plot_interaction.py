"""
Interactive functionality for PlotCanvas - mouse and keyboard event handling.
Handles anchor dragging, mouse events, and interactive parameter updates.
"""

from typing import Optional

from PyQt6.QtCore import pyqtSignal

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.gui.main_tab.plot_canvas.anchor_group import HeightAnchorGroup, PositionAnchorGroup


class PlotInteractionMixin:
    """
    Mixin class providing interactive functionality for PlotCanvas.
    Handles mouse events, anchor dragging, and parameter updates.
    """

    # Signal for emitting parameter updates
    update_value: pyqtSignal

    def __init__(self):
        """Initialize interaction-related attributes."""
        self.background = None
        self.dragging_anchor = None
        self.dragging_anchor_group = None
        self.cid_draw = None
        self.cid_press = None
        self.cid_release = None
        self.cid_motion = None
        self.position_anchor_group: Optional[PositionAnchorGroup] = None
        self.height_anchor_group: Optional[HeightAnchorGroup] = None

    def toggle_event_connections(self, enable: bool):
        """
        Enable or disable mouse event connections for interactive functionality.

        Args:
            enable: True to enable mouse events, False to disable
        """
        if enable:
            self.cid_draw = self.canvas.mpl_connect("draw_event", self.on_draw)
            self.cid_press = self.canvas.mpl_connect("button_press_event", self.on_click)
            self.cid_release = self.canvas.mpl_connect("button_release_event", self.on_release)
            self.cid_motion = self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        else:
            if self.cid_draw:
                self.canvas.mpl_disconnect(self.cid_draw)
            if self.cid_press:
                self.canvas.mpl_disconnect(self.cid_press)
            if self.cid_release:
                self.canvas.mpl_disconnect(self.cid_release)
            if self.cid_motion:
                self.canvas.mpl_disconnect(self.cid_motion)

    def on_draw(self, event):
        """
        Handle the draw_event to capture the background after the figure is first drawn.
        This background can be restored later for performance.
        """
        logger.debug("Capturing the canvas background after initial draw.")
        self.background = self.canvas.copy_from_bbox(self.figure.bbox)

    def restore_background(self):
        """Restore the previously saved background to the canvas."""
        if self.background:
            self.canvas.restore_region(self.background)

    def find_dragging_anchor(self, event, anchor_group):
        """
        Determine which anchor (if any) within the anchor group is closest to the event position.

        Args:
            event: The mouse event.
            anchor_group: The anchor group to check against.

        Returns:
            The anchor line that's being dragged, or None if no anchor is close enough.
        """
        if not anchor_group:
            return None

        for anchor in [anchor_group.center, anchor_group.upper_bound, anchor_group.lower_bound]:
            if anchor.contains(event)[0]:
                return anchor

        return None

    def log_anchor_positions(self, anchor_group):
        """
        Log current positions of anchors in the given anchor group for debugging.

        Args:
            anchor_group: The anchor group to log positions for.
        """
        if anchor_group:
            anchor_group.log_anchor_positions()

    def update_anchor_position(self, event, anchor_group, axis):
        """
        Update anchor positions based on mouse movement and return the new positions.

        Args:
            event: The mouse motion event.
            anchor_group: The anchor group being modified.
            axis: The axis type ('z' for position, 'h' for height).

        Returns:
            dict: Dictionary of updated anchor positions.
        """
        # Determine if this is a position or height anchor group
        is_position_group = hasattr(anchor_group, "__class__") and "Position" in anchor_group.__class__.__name__

        if self.dragging_anchor == anchor_group.center:
            if is_position_group:
                # PositionAnchorGroup only takes x coordinate
                anchor_group.set_center_position(event.xdata)
            else:
                # HeightAnchorGroup only takes y coordinate
                anchor_group.set_center_position(event.ydata)
        elif self.dragging_anchor in [anchor_group.upper_bound, anchor_group.lower_bound]:
            if is_position_group:
                # PositionAnchorGroup only takes x coordinate
                anchor_group.set_bound_position(self.dragging_anchor, event.xdata)
            else:
                # HeightAnchorGroup only takes y coordinate
                anchor_group.set_bound_position(self.dragging_anchor, event.ydata)

        # Get updated positions
        return anchor_group.get_bound_positions()

    def on_click(self, event):
        """
        Handle mouse click events to start anchor dragging.

        Args:
            event: The mouse click event.
        """
        if event.inaxes != self.axes:
            return

        # Check if any anchor is clicked
        position_anchor = self.find_dragging_anchor(event, self.position_anchor_group)
        height_anchor = self.find_dragging_anchor(event, self.height_anchor_group)

        if position_anchor:
            self.dragging_anchor = position_anchor
            self.dragging_anchor_group = "position"
            logger.debug("Started dragging position anchor.")
        elif height_anchor:
            self.dragging_anchor = height_anchor
            self.dragging_anchor_group = "height"
            logger.debug("Started dragging height anchor.")

    def _calculate_center(self, positions: dict[str, tuple]):
        """
        Calculate the center point between the upper and lower bounds.

        Args:
            positions: Dictionary of 'upper_bound' and 'lower_bound' positions.

        Returns:
            dict: A dictionary with a 'center' key containing the (x, y) of the calculated center.
        """
        center_x = (positions["upper_bound"][0] + positions["lower_bound"][0]) / 2
        center_y = (positions["upper_bound"][1] + positions["lower_bound"][1]) / 2
        return {"center": (center_x, center_y)}

    def on_release(self, event):
        """
        Handle mouse release events to finish anchor dragging and emit parameter updates.

        Args:
            event: The mouse release event.
        """
        if not self.dragging_anchor or not self.dragging_anchor_group:
            return

        axis = "z" if self.dragging_anchor_group == "position" else "h"
        anchor_group = (
            self.position_anchor_group if self.dragging_anchor_group == "position" else self.height_anchor_group
        )

        positions = self.update_anchor_position(event, anchor_group, axis)

        logger.debug(f"Mouse released. Finalizing {self.dragging_anchor_group} anchor updates.")

        # Prepare updates to emit
        updates = [
            {
                "path_keys": ["upper_bound_coeffs", axis],
                "operation": OperationType.UPDATE_VALUE,
                "value": positions["upper_bound"][0 if axis == "z" else 1],
            },
            {
                "path_keys": ["lower_bound_coeffs", axis],
                "operation": OperationType.UPDATE_VALUE,
                "value": positions["lower_bound"][0 if axis == "z" else 1],
            },
        ]
        center = self._calculate_center(positions)
        updates.append(
            {
                "path_keys": ["coeffs", axis],
                "operation": OperationType.UPDATE_VALUE,
                "value": center["center"][0 if axis == "z" else 1],
            }
        )
        self.update_value.emit(updates)

        self.dragging_anchor = None
        self.dragging_anchor_group = None

        # Log final anchor positions for both groups
        self.log_anchor_positions(self.position_anchor_group)
        self.log_anchor_positions(self.height_anchor_group)

    def on_motion(self, event):
        """
        Handle mouse motion events to update anchor positions during dragging.

        Args:
            event: The mouse motion event.
        """
        if not self.dragging_anchor or not self.dragging_anchor_group or not event.inaxes:
            return

        axis = "z" if self.dragging_anchor_group == "position" else "h"
        anchor_group = (
            self.position_anchor_group if self.dragging_anchor_group == "position" else self.height_anchor_group
        )

        # Update anchor positions
        self.update_anchor_position(event, anchor_group, axis)

        # Efficiently update display
        if self.background:
            self.restore_background()
            self.axes.draw_artist(anchor_group.center)
            self.axes.draw_artist(anchor_group.upper_bound)
            self.axes.draw_artist(anchor_group.lower_bound)
            self.canvas.blit(self.figure.bbox)
        else:
            self.canvas.draw_idle()
