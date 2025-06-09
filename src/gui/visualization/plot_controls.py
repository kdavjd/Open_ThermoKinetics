"""
Plot interaction controls for the visualization system.
Handles mouse events, anchor dragging, and plot interactions.
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.app_settings import OperationType
from src.core.logger_config import logger


class PlotControls(QObject):
    """
    Manages interactive controls for plot canvas including mouse events and anchor dragging.

    Responsibilities:
    - Mouse event handling
    - Anchor selection and dragging
    - Event connection management
    - Position calculations
    """

    update_value = pyqtSignal(list)

    def __init__(self, canvas: FigureCanvas, axes, anchor_manager):
        """
        Initialize plot controls.

        Args:
            canvas: The matplotlib canvas
            axes: The matplotlib axes
            anchor_manager: Reference to anchor management system
        """
        super().__init__()
        self.canvas = canvas
        self.axes = axes
        self.anchor_manager = anchor_manager

        # Control state
        self.dragging_anchor = None
        self.dragging_anchor_group = None
        self.background = None

        # Event connection IDs
        self.cid_draw = None
        self.cid_press = None
        self.cid_release = None
        self.cid_motion = None

        logger.debug("PlotControls initialized")

    def toggle_event_connections(self, enable: bool):
        """
        Enable or disable mouse event connections.

        Args:
            enable: Whether to enable or disable events
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
        self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)

    def restore_background(self):
        """Restore the previously saved background to the canvas."""
        if self.background:
            self.canvas.restore_region(self.background)

    def find_dragging_anchor(self, event, anchor_group):
        """
        Determine if the mouse click event took place on any of the anchors in the given group.

        Args:
            event: Matplotlib mouse event
            anchor_group: The anchor group to check

        Returns:
            The anchor line object if an anchor was clicked, else None
        """
        if not anchor_group:
            return None

        if anchor_group.center.contains(event)[0]:
            return anchor_group.center
        elif anchor_group.upper_bound.contains(event)[0] or anchor_group.lower_bound.contains(event)[0]:
            return anchor_group.upper_bound if anchor_group.upper_bound.contains(event)[0] else anchor_group.lower_bound
        return None

    def update_anchor_position(self, event, anchor_group, axis):
        """
        Update the position of the currently dragged anchor in the specified anchor group.

        Args:
            event: Matplotlib mouse event containing the new coordinates
            anchor_group: The anchor group to be updated
            axis: 'x' or 'y' axis along which to update the anchor
        """
        if self.dragging_anchor == anchor_group.center:
            if axis == "x":
                anchor_group.set_center_position(event.xdata)
            else:
                anchor_group.set_center_position(event.ydata)
        elif self.dragging_anchor in [anchor_group.upper_bound, anchor_group.lower_bound]:
            if axis == "x":
                anchor_group.set_bound_position(self.dragging_anchor, event.xdata)
            else:
                anchor_group.set_bound_position(self.dragging_anchor, event.ydata)

    def _calculate_center(self, positions: dict[str, tuple]):
        """
        Calculate the center point between the upper and lower bounds.

        Args:
            positions: Dictionary of 'upper_bound' and 'lower_bound' positions

        Returns:
            dict: A dictionary with a 'center' key containing the (x, y) of the calculated center
        """
        center_x = (positions["upper_bound"][0] + positions["lower_bound"][0]) / 2
        center_y = (positions["upper_bound"][1] + positions["lower_bound"][1]) / 2
        return {"center": (center_x, center_y)}

    def on_click(self, event):
        """
        Handle mouse button press events. Check if an anchor was clicked and
        initiate dragging if so.

        Args:
            event: Matplotlib mouse event
        """
        logger.debug(f"Mouse button pressed at x={event.xdata}, y={event.ydata}")
        if event.inaxes != self.axes:
            return

        # Check position anchors first
        position_anchor_group = getattr(self.anchor_manager, "position_anchor_group", None)
        height_anchor_group = getattr(self.anchor_manager, "height_anchor_group", None)

        self.dragging_anchor = self.find_dragging_anchor(event, position_anchor_group)
        if self.dragging_anchor:
            self.dragging_anchor_group = "position"
        else:
            self.dragging_anchor = self.find_dragging_anchor(event, height_anchor_group)
            if self.dragging_anchor:
                self.dragging_anchor_group = "height"

    def on_release(self, event):
        """
        Handle mouse button release events. When an anchor drag finishes, this method
        calculates the updated positions of bounds and center, emits signals, and logs
        the final positions.

        Args:
            event: Matplotlib mouse event
        """
        logger.debug(f"Mouse button released at x={event.xdata}, y={event.ydata}")

        if self.dragging_anchor_group:
            logger.debug(f"Anchor group being updated: {self.dragging_anchor_group}")

            position_anchor_group = getattr(self.anchor_manager, "position_anchor_group", None)
            height_anchor_group = getattr(self.anchor_manager, "height_anchor_group", None)

            anchor_group = position_anchor_group if self.dragging_anchor_group == "position" else height_anchor_group

            if anchor_group:
                positions = anchor_group.get_bound_positions()
                logger.debug(f"New anchor positions: {positions}")

                axis = "z" if self.dragging_anchor_group == "position" else "h"

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

                # Log final anchor positions for both groups
                if position_anchor_group:
                    position_anchor_group.log_anchor_positions()
                if height_anchor_group:
                    height_anchor_group.log_anchor_positions()

        self.dragging_anchor = None
        self.dragging_anchor_group = None

    def on_motion(self, event):
        """
        Handle mouse motion events. If an anchor is currently being dragged,
        update its position accordingly. This method updates position and height
        anchors on separate axes.

        Args:
            event: Matplotlib mouse event
        """
        if self.dragging_anchor is None or event.inaxes != self.axes:
            return

        position_anchor_group = getattr(self.anchor_manager, "position_anchor_group", None)
        height_anchor_group = getattr(self.anchor_manager, "height_anchor_group", None)

        # Update horizontal position anchors
        if position_anchor_group:
            self.update_anchor_position(event, position_anchor_group, "x")

        # Update vertical height anchors
        if height_anchor_group:
            self.update_anchor_position(event, height_anchor_group, "y")

        self.canvas.draw_idle()
        logger.debug("Redrawing canvas after anchor motion.")
