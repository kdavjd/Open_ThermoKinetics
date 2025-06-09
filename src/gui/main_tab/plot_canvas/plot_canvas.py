import random
from typing import Dict, Optional

import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# see: https://pypi.org/project/SciencePlots/
import scienceplots  # noqa pylint: disable=unused-import
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.core.app_settings import (
    MODEL_FIT_ANNOTATION_CONFIG,
    MODEL_FREE_ANNOTATION_CONFIG,
    NUC_MODELS_TABLE,
    OperationType,
)
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console
from src.gui.visualization.anchor_management import AnchorManager
from src.gui.visualization.plot_controls import PlotControls

plt.style.use(["science", "no-latex", "nature", "grid"])


class PlotCanvas(QWidget):
    """
    A PyQt6 widget that contains a Matplotlib figure with interactive anchors.
    Users can interact with the plot to adjust certain parameters. Anchors can be
    dragged and released, and signals are emitted to update underlying values.

    Attributes:
        update_value (pyqtSignal): Signal emitted when anchor positions change.
        figure: Matplotlib Figure instance.
        canvas: FigureCanvas instance for the Figure.
        axes: Matplotlib Axes instance.
        toolbar: NavigationToolbar for the canvas.
        lines (Dict[str, Line2D]): Dictionary of line objects keyed by their name.
        anchor_manager: Manages interactive anchors on the plot.
        plot_controls: Handles mouse events and interactions.
    """

    update_value = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the plot canvas widget with a toolbar, a figure, and axes.
        Sets up mouse event connections for interactive anchor dragging.
        """
        super().__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.lines: Dict[str, Line2D] = {}

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Initialize anchor management and plot controls
        self.anchor_manager = AnchorManager(self.axes)
        self.plot_controls = PlotControls(self.canvas, self.axes, self.anchor_manager)

        # Connect signals
        self.plot_controls.update_value.connect(self.update_value)

        self.mock_plot()

    def toggle_event_connections(self, enable: bool):
        """Toggle mouse event connections on/off."""
        self.plot_controls.toggle_event_connections(enable)

    def mock_plot(self, data=None):  # noqa: C901
        def get_random_line_style_and_width():
            line_styles = ["-", "--", "-."]
            line_widths = [0.5, 0.75, 1]
            return np.random.choice(line_styles), np.random.choice(line_widths)

        def normalize_data(data):
            if np.isinf(np.max(data)) or np.isnan(np.max(data)):
                data_max = np.nanmax(data[~np.isinf(data) & ~np.isnan(data)])
            else:
                data_max = np.max(data)
            if np.isinf(np.min(data)) or np.isnan(np.min(data)):
                data_min = np.nanmin(data[~np.isinf(data) & ~np.isnan(data)])
            else:
                data_min = np.min(data)
            return (data - data_min) / (data_max - data_min)

        a = np.linspace(0.001, 1, 100)
        e = 1 - a

        function_type = random.choice(["y", "g", "z"])

        self.axes.clear()
        self.lines.clear()

        for model_key, funcs in NUC_MODELS_TABLE.items():
            try:
                if function_type == "y":
                    values = normalize_data(funcs["differential_form"](e))
                elif function_type == "g":
                    values = normalize_data(funcs["integral_form"](e))
                elif function_type == "z":
                    y_values = funcs["differential_form"](e)
                    g_values = funcs["integral_form"](e)
                    values = normalize_data(y_values * g_values)
                else:
                    continue

                line_style, line_width = get_random_line_style_and_width()

                self.add_or_update_line(
                    model_key,
                    a,
                    values,
                    label=model_key,
                    linestyle=line_style,
                    linewidth=line_width,
                )

                rand_index = np.random.choice(range(len(a)))
                self.axes.annotate(
                    model_key,
                    (a[rand_index], values[rand_index]),
                    textcoords="offset points",
                    xytext=(-10, -10),
                    ha="center",
                )
            except Exception as exc:
                logger.error(f"Error while plotting model {model_key}: {exc}")

        self.axes.set_xlabel("α", fontsize=10)

        label_mapping = {
            "g": ("g(α)", "Theoretical view of g(α) graphs"),
            "y": ("y(α)", "Theoretical view of y(α) master graphs"),
            "z": ("z(α)", "Theoretical view of z(α) master graphs"),
        }

        if function_type in label_mapping:
            ylabel, title = label_mapping[function_type]
            self.axes.set_ylabel(
                ylabel,
            )
            self.axes.set_title(title, loc="left")

        self.axes.tick_params(axis="both", which="major", labelsize=8)
        self.canvas.draw_idle()

    def add_or_update_line(self, key, x, y, **kwargs):
        """
        Add a new line or update an existing line on the axes.

        Args:
            key: Unique key name for the line.
            x: x-values for the line data.
            y: y-values for the line data.
            kwargs: Additional Matplotlib line properties.
        """
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
        """
        Plot data from a Pandas DataFrame. The DataFrame is expected to contain
        a 'temperature' column for the x-axis, and one or more other columns
        for the y-values.

        Args:
            data: Pandas DataFrame with columns including 'temperature'.
        """
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
        if not mse_data:
            return
        times, mses = zip(*mse_data)

        self.axes.clear()
        self.lines.clear()

        self.axes.set_title("MSE over time")
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("MSE")

        self.add_or_update_line("mse_line", times, mses, color="red", marker="o", linestyle="-")

        self.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self.figure.autofmt_xdate()

    def determine_line_properties(self, reaction_name):
        """
        Determine line properties (such as linewidth, linestyle, color)
        based on the given reaction name patterns.

        Args:
            reaction_name: A string identifying the reaction line.

        Returns:
            dict: Line properties for Matplotlib.
        """
        if "cumulative_upper_bound" in reaction_name or "cumulative_lower_bound" in reaction_name:
            return {"linewidth": 0.1, "linestyle": "-", "color": "grey"}
        elif "cumulative_coeffs" in reaction_name:
            return {"linewidth": 1, "linestyle": "dotted"}
        elif "upper_bound_coeffs" in reaction_name or "lower_bound_coeffs" in reaction_name:
            return {"linewidth": 1.25, "linestyle": "-."}
        else:
            return {}

    def update_fill_between(self):
        """
        Update the fill_between regions if both upper and lower bound lines are present.
        This adds a shaded area between upper and lower bounds to visually indicate the range.
        """
        if "cumulative_upper_bound_coeffs" in self.lines and "cumulative_lower_bound_coeffs" in self.lines:
            x = self.lines["cumulative_upper_bound_coeffs"].get_xdata()
            upper_y = self.lines["cumulative_upper_bound_coeffs"].get_ydata()
            lower_y = self.lines["cumulative_lower_bound_coeffs"].get_ydata()
            logger.debug("Filling area between cumulative bounds.")
            self.axes.fill_between(x, lower_y, upper_y, color="grey", alpha=0.1)

        if "upper_bound_coeffs" in self.lines and "lower_bound_coeffs" in self.lines:
            x = self.lines["upper_bound_coeffs"].get_xdata()
            upper_y = self.lines["upper_bound_coeffs"].get_ydata()
            lower_y = self.lines["lower_bound_coeffs"].get_ydata()
            logger.debug("Filling area between direct bounds.")
            self.axes.fill_between(x, lower_y, upper_y, color="grey", alpha=0.1)

    @pyqtSlot(tuple, list)
    def plot_reaction(self, keys, values):
        """
        Slot to plot reaction data. If the reaction line already exists, it will be
        removed and re-plotted with new data.

        Args:
            keys: A tuple containing (file_name, reaction_name).
            values: A list containing [x_values, y_values]."""
        file_name, reaction_name = keys
        x, y = values

        if reaction_name in self.lines:
            logger.debug(f"Removing existing line '{reaction_name}' before replotting.")
            line = self.lines[reaction_name]
            line.remove()
            del self.lines[reaction_name]

        line_properties = self.determine_line_properties(reaction_name)
        logger.debug(f"Plotting reaction '{reaction_name}' with provided data.")
        self.add_or_update_line(reaction_name, x, y, **line_properties)

    @pyqtSlot(dict)
    def add_anchors(self, reaction_data: dict):
        """
        Slot to add anchors to the plot based on given reaction data.
        Delegates to anchor manager.

        Args:
            reaction_data: A dictionary containing reaction coefficients and bounds.
        """
        self.anchor_manager.add_anchors(reaction_data)
        self.canvas.draw_idle()
        self.figure.tight_layout()  # Removed methods that are now handled by PlotControls:

    # - find_dragging_anchor()  -> moved to PlotControls
    # - log_anchor_positions()  -> moved to AnchorManager
    # - update_anchor_position() -> moved to PlotControls
    # - on_click() -> moved to PlotControls
    # - on_release() -> moved to PlotControls
    # - on_motion() -> moved to PlotControls

    def on_click(self, event):
        """
        Handle mouse button press events. Check if an anchor was clicked and
        initiate dragging if so.

        Args:
            event: Matplotlib mouse event.
        """
        logger.debug(f"Mouse button pressed at x={event.xdata}, y={event.ydata}")
        if event.inaxes != self.axes:
            return

        self.dragging_anchor = self.find_dragging_anchor(event, self.position_anchor_group)
        if self.dragging_anchor:
            self.dragging_anchor_group = "position"
        else:
            self.dragging_anchor = self.find_dragging_anchor(event, self.height_anchor_group)
            if self.dragging_anchor:
                self.dragging_anchor_group = "height"

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
        Handle mouse button release events. When an anchor drag finishes, this method
        calculates the updated positions of bounds and center, emits signals, and logs
        the final positions.

        Args:
            event: Matplotlib mouse event.
        """
        logger.debug(f"Mouse button released at x={event.xdata}, y={event.ydata}")

        if self.dragging_anchor_group:
            logger.debug(f"Anchor group being updated: {self.dragging_anchor_group}")

            positions = (
                self.position_anchor_group if self.dragging_anchor_group == "position" else self.height_anchor_group
            ).get_bound_positions()
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

        self.dragging_anchor = None
        self.dragging_anchor_group = None

        # Log final anchor positions for both groups
        self.log_anchor_positions(self.position_anchor_group)
        self.log_anchor_positions(self.height_anchor_group)

    def on_motion(self, event):
        """
        Handle mouse motion events. If an anchor is currently being dragged,
        update its position accordingly. This method updates position and height
        anchors on separate axes.

        Args:
            event: Matplotlib mouse event.
        """
        if self.dragging_anchor is None or event.inaxes != self.axes:
            return

        # Update horizontal position anchors
        self.update_anchor_position(event, self.position_anchor_group, "x")

        # Update vertical height anchors
        self.update_anchor_position(event, self.height_anchor_group, "y")

        self.canvas.draw_idle()
        self.figure.tight_layout()
        logger.debug("Redrawing canvas after anchor motion.")

    def add_model_fit_annotation(self, annotation: str):
        annotation_core = annotation.strip("$")
        lines = annotation_core.split(r"\n")

        block_top = MODEL_FIT_ANNOTATION_CONFIG["block_top"]
        delta_y = MODEL_FIT_ANNOTATION_CONFIG["delta_y"]
        n_lines = len(lines)
        block_bottom = block_top - n_lines * delta_y
        block_left = MODEL_FIT_ANNOTATION_CONFIG["block_left"]
        block_right = MODEL_FIT_ANNOTATION_CONFIG["block_right"]
        rect_width = block_right - block_left

        rect = patches.Rectangle(
            (block_left, block_bottom),
            rect_width,
            block_top - block_bottom,
            transform=self.axes.transAxes,
            facecolor=MODEL_FIT_ANNOTATION_CONFIG["facecolor"],
            edgecolor=MODEL_FIT_ANNOTATION_CONFIG["edgecolor"],
            alpha=MODEL_FIT_ANNOTATION_CONFIG["alpha"],
            zorder=11,
        )
        self.axes.add_patch(rect)

        for i, line in enumerate(lines):
            y_pos = block_top - i * delta_y - delta_y / 2
            self.axes.text(
                0.5,
                y_pos,
                f"${line.strip()}$",
                transform=self.axes.transAxes,
                ha="center",
                va="center",
                fontsize=MODEL_FIT_ANNOTATION_CONFIG["fontsize"],
                zorder=11,
            )

    def add_model_free_annotation(self, annotation: str):
        annotation_core = annotation.strip("$")
        lines = annotation_core.split(r"\n")

        block_top = MODEL_FREE_ANNOTATION_CONFIG["block_top"]
        delta_y = MODEL_FREE_ANNOTATION_CONFIG["delta_y"]
        n_lines = len(lines)
        block_bottom = block_top - n_lines * delta_y
        block_left = MODEL_FREE_ANNOTATION_CONFIG["block_left"]
        block_right = MODEL_FREE_ANNOTATION_CONFIG["block_right"]
        rect_width = block_right - block_left

        rect = patches.Rectangle(
            (block_left, block_bottom),
            rect_width,
            block_top - block_bottom,
            transform=self.axes.transAxes,
            facecolor=MODEL_FREE_ANNOTATION_CONFIG["facecolor"],
            edgecolor=MODEL_FREE_ANNOTATION_CONFIG["edgecolor"],
            alpha=MODEL_FREE_ANNOTATION_CONFIG["alpha"],
            zorder=11,
        )
        self.axes.add_patch(rect)

        for i, line in enumerate(lines):
            y_pos = block_top - i * delta_y - delta_y / 2
            self.axes.text(
                0.5,
                y_pos,
                f"${line.strip()}$",
                transform=self.axes.transAxes,
                ha="center",
                va="center",
                fontsize=MODEL_FIT_ANNOTATION_CONFIG["fontsize"],
                zorder=11,
            )

    def plot_model_fit_result(self, plot_data_and_kwargs):
        plot_df = plot_data_and_kwargs[0]["plot_df"]
        plot_kwargs = plot_data_and_kwargs[0]["plot_kwargs"]

        title = plot_kwargs.pop("title", "Model Plot")
        xlabel = plot_kwargs.pop("xlabel", "Reverse Temperature")
        ylabel = plot_kwargs.pop("ylabel", "Value")
        annotation = plot_kwargs.pop("annotation", None)

        self.axes.clear()
        self.lines = {}
        self.add_or_update_line("lhs_clean", plot_df["reverse_temperature"], plot_df["lhs_clean"], label="lhs_clean")
        self.add_or_update_line("y", plot_df["reverse_temperature"], plot_df["y"], label="y")

        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)

        self.canvas.draw_idle()
        self.figure.tight_layout()

        if annotation:
            self.add_model_fit_annotation(annotation)

    def plot_model_free_result(self, plot_data_and_kwargs):
        plot_df = plot_data_and_kwargs[0]["plot_df"]
        plot_kwargs = plot_data_and_kwargs[0]["plot_kwargs"]

        title = plot_kwargs.pop("title", "Model Free Plot")
        xlabel = plot_kwargs.pop("xlabel", "Conversion")
        ylabel = plot_kwargs.pop("ylabel", "Value")
        annotation = plot_kwargs.pop("annotation", None)

        self.axes.clear()
        self.lines = {}

        x = plot_df["conversion"]

        for col in plot_df.columns:
            if col != "conversion":
                self.add_or_update_line(col, x, plot_df[col], label=col)

        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.legend()

        self.canvas.draw_idle()
        self.figure.tight_layout()

        if annotation:
            self.add_model_free_annotation(annotation)
