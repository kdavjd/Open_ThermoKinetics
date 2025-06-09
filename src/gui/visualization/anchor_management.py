"""
Anchor management system for plot canvas.
Handles creation, positioning, and management of interactive anchors.
"""

from PyQt6.QtCore import pyqtSlot

from src.core.logger_config import logger
from src.gui.main_tab.plot_canvas.anchor_group import HeightAnchorGroup, PositionAnchorGroup


class AnchorManager:
    """
    Manages interactive anchors on the plot canvas.

    Responsibilities:
    - Creation and management of anchor groups
    - Anchor positioning and updates
    - Anchor state tracking
    - Integration with plot controls
    """

    def __init__(self, axes):
        """
        Initialize anchor management system.

        Args:
            axes: The matplotlib axes for anchor placement
        """
        self.axes = axes
        self.position_anchor_group = None
        self.height_anchor_group = None

        logger.debug("AnchorManager initialized")

    @pyqtSlot(dict)
    def add_anchors(self, reaction_data: dict):
        """
        Add anchors to the plot based on given reaction data. This will create
        both position and height anchor groups and plot their initial positions.

        Args:
            reaction_data: A dictionary containing reaction coefficients and bounds
        """
        logger.debug(f"Received reaction data for anchors: {reaction_data}")

        center_params = reaction_data["coeffs"][2]
        upper_params = reaction_data["upper_bound_coeffs"][2]
        lower_params = reaction_data["lower_bound_coeffs"][2]

        # Create anchor groups
        self.position_anchor_group = PositionAnchorGroup(self.axes, center_params, upper_params, lower_params)
        self.height_anchor_group = HeightAnchorGroup(self.axes, center_params, upper_params, lower_params)

        logger.debug("Position and height anchor groups created successfully")

    def clear_anchors(self):
        """Remove all anchors from the plot."""
        if self.position_anchor_group:
            self.position_anchor_group.remove_anchors()
            self.position_anchor_group = None

        if self.height_anchor_group:
            self.height_anchor_group.remove_anchors()
            self.height_anchor_group = None

        logger.debug("All anchors cleared")

    def update_anchor_visibility(self, visible: bool):
        """
        Update visibility of all anchors.

        Args:
            visible: Whether anchors should be visible
        """
        if self.position_anchor_group:
            self.position_anchor_group.set_visibility(visible)

        if self.height_anchor_group:
            self.height_anchor_group.set_visibility(visible)

        logger.debug(f"Anchor visibility set to: {visible}")

    def log_anchor_positions(self, anchor_group):
        """
        Log positions of the provided anchor group for debugging purposes.

        Args:
            anchor_group: An instance of an anchor group
        """
        if anchor_group:
            anchor_group.log_anchor_positions()

    def get_anchor_data(self):
        """
        Get current anchor position data for both groups.

        Returns:
            dict: Dictionary containing position and height anchor data
        """
        data = {}

        if self.position_anchor_group:
            data["position"] = self.position_anchor_group.get_bound_positions()

        if self.height_anchor_group:
            data["height"] = self.height_anchor_group.get_bound_positions()

        return data

    def has_anchors(self):
        """
        Check if any anchor groups are currently active.

        Returns:
            bool: True if any anchor groups exist, False otherwise
        """
        return self.position_anchor_group is not None or self.height_anchor_group is not None

    def update_anchor_from_data(self, reaction_data: dict):
        """
        Update existing anchors with new reaction data.

        Args:
            reaction_data: Updated reaction coefficients and bounds
        """
        if not self.has_anchors():
            self.add_anchors(reaction_data)
            return

        center_params = reaction_data["coeffs"][2]
        upper_params = reaction_data["upper_bound_coeffs"][2]
        lower_params = reaction_data["lower_bound_coeffs"][2]

        if self.position_anchor_group:
            self.position_anchor_group.update_positions(center_params, upper_params, lower_params)

        if self.height_anchor_group:
            self.height_anchor_group.update_positions(center_params, upper_params, lower_params)

        logger.debug("Anchors updated with new reaction data")

    def remove_anchors_if_exists(self):
        """Remove anchors if they exist, handling cases where anchor groups might not have remove methods."""
        if hasattr(self, "position_anchor_group") and self.position_anchor_group:
            if hasattr(self.position_anchor_group, "remove_anchors"):
                self.position_anchor_group.remove_anchors()
            self.position_anchor_group = None

        if hasattr(self, "height_anchor_group") and self.height_anchor_group:
            if hasattr(self.height_anchor_group, "remove_anchors"):
                self.height_anchor_group.remove_anchors()
            self.height_anchor_group = None

        logger.debug("Anchor cleanup completed")
