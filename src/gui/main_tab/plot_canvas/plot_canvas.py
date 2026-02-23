"""
Main PlotCanvas widget implementation using modular architecture.
Orchestrates plotting functionality through multiple mixin classes.
"""

from typing import Dict, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt6.QtCore import QEvent, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console
from src.gui.main_tab.plot_canvas.anchor_group import HeightAnchorGroup, PositionAnchorGroup
from src.gui.main_tab.plot_canvas.config import PLOT_CANVAS_CONFIG
from src.gui.main_tab.plot_canvas.plot_interaction import PlotInteractionMixin
from src.gui.main_tab.plot_canvas.plot_styling import PlotStylingMixin
from src.gui.styles import get_saved_theme

plt.rcParams.update(PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS)
# Set NPG palette as default color cycle so mock_plot() (called before apply_theme)
# already uses colors that are visible on both light and dark backgrounds.
plt.rcParams["axes.prop_cycle"] = cycler(color=PLOT_CANVAS_CONFIG.NPG_PALETTE)

_TOOLBAR_ICON_MAP = {
    "Home": "home.png",
    "Back": "back.png",
    "Forward": "forward.png",
    "Pan": "move.png",
    "Zoom": "zoom_to_rect.png",
    "Subplots": "subplots.png",
    "Save": "filesave.png",
}


class PlotCanvas(QWidget, PlotInteractionMixin, PlotStylingMixin):
    """
    A PyQt6 widget that contains a Matplotlib figure with interactive anchors.

    This class orchestrates plotting functionality through multiple mixin classes:
    - PlotInteractionMixin: Handles mouse events and anchor interactions
    - PlotStylingMixin: Manages plot appearance and styling operations

    Attributes:
        update_value (pyqtSignal): Signal emitted when anchor positions change.
        figure: Matplotlib Figure instance.
        canvas: FigureCanvas instance for the Figure.
        axes: Matplotlib Axes instance.
        toolbar: NavigationToolbar for the canvas.
        lines (Dict[str, Line2D]): Dictionary of line objects keyed by their name.
        background: Stored background for efficient redrawing.
        dragging_anchor: The currently dragged anchor line object (if any).
        dragging_anchor_group: Which group ('position' or 'height') is being dragged.
        position_anchor_group: An instance of PositionAnchorGroup.
        height_anchor_group: An instance of HeightAnchorGroup.
    """

    update_value = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the plot canvas widget with a toolbar, a figure, and axes."""
        super().__init__(parent)

        # Initialize matplotlib components
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.lines: Dict[str, Line2D] = {}

        # Setup layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Initialize interaction-related attributes
        self.background = None
        self.dragging_anchor = None
        self.dragging_anchor_group = None
        self.cid_draw = None
        self.cid_press = None
        self.cid_release = None
        self.cid_motion = None

        # Initialize anchor groups
        self.position_anchor_group = None
        self.height_anchor_group = None

        # Create initial mock plot (delegated to PlotStylingMixin)
        self.mock_plot()

        # Apply saved theme
        self._current_theme = get_saved_theme()
        self.apply_theme(self._current_theme)

    def changeEvent(self, event):
        """React to Qt style changes by re-applying the current theme."""
        if event.type() == QEvent.Type.StyleChange:
            self.apply_theme(get_saved_theme())
        super().changeEvent(event)

    def _rebuild_toolbar_icons(self):
        """Rebuild toolbar icons to match the current Qt palette (light/dark)."""
        try:
            for action in self.toolbar.actions():
                filename = _TOOLBAR_ICON_MAP.get(action.text())
                if filename:
                    action.setIcon(self.toolbar._icon(filename))
        except AttributeError:
            pass  # graceful degradation for older matplotlib versions

    def toggle_event_connections(self, enable: bool):
        """Toggle mouse event connections for interactive functionality."""
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
        """Handle the draw_event to capture the background after the figure is first drawn."""
        logger.debug("Capturing the canvas background after initial draw.")
        self.background = self.canvas.copy_from_bbox(self.figure.bbox)

    def restore_background(self):
        """Restore the previously saved background to the canvas."""
        if self.background:
            self.canvas.restore_region(self.background)

    def add_or_update_line(self, key, x, y, **kwargs):
        """Add a new line or update an existing line on the axes."""
        if key in self.lines:
            logger.debug(f"Updating line '{key}' with new data.")
            line = self.lines[key]
            line.set_data(x, y)
        else:
            logger.debug(f"Adding a new line '{key}' to the plot.")
            (line,) = self.axes.plot(x, y, **kwargs)
            self.lines[key] = line
        self.canvas.draw_idle()
        self.figure.tight_layout()

    def plot_data_from_dataframe(self, data: pd.DataFrame):
        """Plot data from a Pandas DataFrame with 'temperature' column for x-axis."""
        self.axes.clear()
        self.lines.clear()

        if "temperature" in data.columns:
            logger.debug("Plotting file data from DataFrame.")
            x = data["temperature"]
            for column in data.columns:
                if column != "temperature":
                    self.add_or_update_line(column, x, data[column], label=column)
        else:
            logger.error("DataFrame does not contain 'temperature' column.")
            console.log("The file does not contain a 'temperature' column for X-axis.")

    def plot_mse_history(self, mse_data):
        """Plot MSE history over time with proper clearing and time formatting."""
        if not mse_data:
            logger.debug("No MSE data to plot")
            return

        # Extract times and MSE values
        times, mses = zip(*mse_data)
        logger.debug(f"Plotting MSE history with {len(times)} points")
        logger.debug(f"Time range: {times[0].strftime('%H:%M:%S')} to {times[-1].strftime('%H:%M:%S')}")

        # Clear previous plot completely
        self.axes.clear()
        self.lines.clear()

        # Clear any existing anchors that might interfere
        if hasattr(self, "position_anchor_group"):
            self.position_anchor_group = None
        if hasattr(self, "height_anchor_group"):
            self.height_anchor_group = None

        # Set up the plot
        self.axes.set_title("MSE over time")
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("MSE")

        # Plot the MSE line
        self.add_or_update_line("mse_line", times, mses, color="red", marker="o", linestyle="-")

        # Format time axis
        self.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        # Rotate date labels for better readability
        self.figure.autofmt_xdate()

        # Ensure the plot is redrawn
        self.canvas.draw()
        self.figure.tight_layout()
        logger.debug("MSE history plot updated")

    def is_mse_mode(self) -> bool:
        """Check if the canvas is currently displaying MSE data."""
        return self.axes.get_title() == "MSE over time"

    @pyqtSlot(tuple, list)
    def plot_reaction(self, keys, values):
        """Slot to plot reaction data with automatic line property determination."""
        file_name, reaction_name = keys
        x, y = values

        if reaction_name in self.lines:
            logger.debug(f"Removing existing line '{reaction_name}' before replotting.")
            line = self.lines[reaction_name]
            line.remove()
            del self.lines[reaction_name]
            # Delegate to PlotStylingMixin for line properties and fill operations
        line_properties = self.determine_line_properties(reaction_name)
        logger.debug(f"Plotting reaction '{reaction_name}' with provided data.")
        self.add_or_update_line(reaction_name, x, y, **line_properties)

        # Update fill between areas if needed (delegated to PlotStylingMixin)
        self.update_fill_between()

    @pyqtSlot(dict)
    def add_anchors(self, reaction_data: dict):
        """Slot to add anchors to the plot based on reaction data."""
        logger.debug(f"Received reaction data for anchors: {reaction_data}")

        # Extract tuple format parameters (x_range, function_type, coeffs_tuple)
        def extract_anchor_params(params_tuple):
            """Extract h, z, w values from tuple format (x_range, function_type, coeffs_tuple)."""
            if isinstance(params_tuple, tuple) and len(params_tuple) >= 3:
                # params_tuple = (x_range, function_type, coeffs_tuple)
                # coeffs_tuple = (h, z, w, ...)
                coeffs_tuple = params_tuple[2]
                if len(coeffs_tuple) >= 3:
                    h, z, w = coeffs_tuple[:3]
                    return (h, z, w)
                else:
                    logger.warning(f"Insufficient coefficients in tuple: {coeffs_tuple}")
                    return (0.0, 0.0, 0.0)
            elif isinstance(params_tuple, dict):
                # Fallback for dictionary format
                h = params_tuple.get("h", 0.0)
                z = params_tuple.get("z", 0.0)
                w = params_tuple.get("w", 0.0)
                return (h, z, w)
            else:
                logger.warning(f"Unexpected parameter format: {params_tuple}")
                return (0.0, 0.0, 0.0)

        center_params = extract_anchor_params(reaction_data["coeffs"])
        upper_params = extract_anchor_params(reaction_data["upper_bound_coeffs"])
        lower_params = extract_anchor_params(reaction_data["lower_bound_coeffs"])

        # Create anchor groups
        self.position_anchor_group = PositionAnchorGroup(self.axes, center_params, upper_params, lower_params)
        self.height_anchor_group = HeightAnchorGroup(self.axes, center_params, upper_params, lower_params)

        self.canvas.draw_idle()
        self.figure.tight_layout()
