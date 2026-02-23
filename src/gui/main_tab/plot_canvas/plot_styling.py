"""
Styling and appearance management for PlotCanvas.
Handles annotations, line properties, fill areas, and visual formatting.
"""

import random
from typing import Dict

import matplotlib
import matplotlib.patches as patches
import numpy as np
from cycler import cycler

from src.core.app_settings import MODEL_FIT_ANNOTATION_CONFIG, MODEL_FREE_ANNOTATION_CONFIG, NUC_MODELS_TABLE
from src.core.logger_config import logger
from src.gui.main_tab.plot_canvas.config import PLOT_CANVAS_CONFIG


class PlotStylingMixin:
    """
    Mixin class providing styling and appearance functionality for PlotCanvas.
    Handles line properties, annotations, mock plots, and visual formatting.
    """

    def determine_line_properties(self, reaction_name: str) -> Dict[str, object]:
        """
        Determine line properties (such as linewidth, linestyle, color)
        based on the given reaction name patterns.

        Args:
            reaction_name: A string identifying the reaction line.

        Returns:
            dict: Line properties for Matplotlib.
        """
        config = PLOT_CANVAS_CONFIG.BOUND_LINE_CONFIG

        if "cumulative_upper_bound" in reaction_name or "cumulative_lower_bound" in reaction_name:
            return config["cumulative_upper_bound"]
        elif "cumulative_coeffs" in reaction_name:
            return PLOT_CANVAS_CONFIG.CUMULATIVE_LINE_CONFIG
        elif "upper_bound_coeffs" in reaction_name or "lower_bound_coeffs" in reaction_name:
            return config["upper_bound_coeffs"]
        else:
            return PLOT_CANVAS_CONFIG.DEFAULT_LINE_CONFIG

    def update_fill_between(self):
        """
        Update the fill_between regions if both upper and lower bound lines are present.
        This adds a shaded area between upper and lower bounds to visually indicate the range.
        """
        # Fill between cumulative bounds
        if "cumulative_upper_bound_coeffs" in self.lines and "cumulative_lower_bound_coeffs" in self.lines:
            x = self.lines["cumulative_upper_bound_coeffs"].get_xdata()
            upper_y = self.lines["cumulative_upper_bound_coeffs"].get_ydata()
            lower_y = self.lines["cumulative_lower_bound_coeffs"].get_ydata()
            logger.debug("Filling area between cumulative bounds.")
            self.axes.fill_between(
                x, lower_y, upper_y, color=PLOT_CANVAS_CONFIG.FILL_COLOR, alpha=PLOT_CANVAS_CONFIG.FILL_ALPHA
            )

        # Fill between direct bounds
        if "upper_bound_coeffs" in self.lines and "lower_bound_coeffs" in self.lines:
            x = self.lines["upper_bound_coeffs"].get_xdata()
            upper_y = self.lines["upper_bound_coeffs"].get_ydata()
            lower_y = self.lines["lower_bound_coeffs"].get_ydata()
            logger.debug("Filling area between direct bounds.")
            self.axes.fill_between(
                x, lower_y, upper_y, color=PLOT_CANVAS_CONFIG.FILL_COLOR, alpha=PLOT_CANVAS_CONFIG.FILL_ALPHA
            )

    def _get_random_line_style_and_width(self):
        """Get random line style and width for mock plots."""
        line_styles = PLOT_CANVAS_CONFIG.MOCK_PLOT_LINE_STYLES
        line_widths = PLOT_CANVAS_CONFIG.MOCK_PLOT_LINE_WIDTHS
        return np.random.choice(line_styles), np.random.choice(line_widths)

    def _normalize_data(self, data):
        """Normalize data for mock plots."""
        if np.isinf(np.max(data)) or np.isnan(np.max(data)):
            data_max = np.nanmax(data[~np.isinf(data) & ~np.isnan(data)])
        else:
            data_max = np.max(data)
        if np.isinf(np.min(data)) or np.isnan(np.min(data)):
            data_min = np.nanmin(data[~np.isinf(data) & ~np.isnan(data)])
        else:
            data_min = np.min(data)
        return (data - data_min) / (data_max - data_min)

    def mock_plot(self, data=None):
        """
        Generate a mock plot with random kinetic model functions for demonstration.

        Args:
            data: Optional data parameter (not currently used)
        """
        a = np.linspace(0.001, 1, 100)
        e = 1 - a

        function_type = random.choice(PLOT_CANVAS_CONFIG.MOCK_PLOT_FUNCTION_TYPES)

        self.axes.clear()
        self.lines.clear()

        for model_key, funcs in NUC_MODELS_TABLE.items():
            try:
                if function_type == "y":
                    values = self._normalize_data(funcs["differential_form"](e))
                elif function_type == "g":
                    values = self._normalize_data(funcs["integral_form"](e))
                elif function_type == "z":
                    y_values = funcs["differential_form"](e)
                    g_values = funcs["integral_form"](e)
                    values = self._normalize_data(y_values * g_values)
                else:
                    continue

                line_style, line_width = self._get_random_line_style_and_width()

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
            self.axes.set_ylabel(ylabel)
            self.axes.set_title(title, loc="left")

        self.axes.tick_params(axis="both", which="major", labelsize=8)
        self.canvas.draw_idle()

    def apply_theme(self, theme: str):
        """
        Apply the given theme ('light' or 'dark') to all existing matplotlib artists.
        Updates rcParams for future plot calls and explicitly re-colors current content.
        Does NOT clear data — existing lines, annotations, and axes content are preserved.
        """
        params = PLOT_CANVAS_CONFIG.THEME_PARAMS[theme]

        matplotlib.rcParams.update(params)
        matplotlib.rcParams["axes.prop_cycle"] = cycler(color=PLOT_CANVAS_CONFIG.NPG_PALETTE)

        self.figure.set_facecolor(params["figure.facecolor"])
        self.axes.set_facecolor(params["axes.facecolor"])

        for spine in self.axes.spines.values():
            spine.set_edgecolor(params["axes.edgecolor"])

        self.axes.tick_params(colors=params["xtick.color"], which="both")
        self.axes.xaxis.label.set_color(params["axes.labelcolor"])
        self.axes.yaxis.label.set_color(params["axes.labelcolor"])
        self.axes.title.set_color(params["text.color"])
        self.axes.grid(color=params["grid.color"])

        legend = self.axes.get_legend()
        if legend:
            legend.get_frame().set_facecolor(params["legend.facecolor"])
            legend.get_frame().set_edgecolor(params["legend.edgecolor"])
            for text in legend.get_texts():
                text.set_color(params["text.color"])

        ann_params = PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS[theme]
        for patch in self.axes.patches:
            patch.set_facecolor(ann_params["facecolor"])
            patch.set_edgecolor(ann_params["edgecolor"])
        for text in self.axes.texts:
            text.set_color(ann_params["text_color"])

        self._current_theme = theme
        self.canvas.draw_idle()

    def add_model_fit_annotation(self, annotation: str):
        """
        Add a formatted annotation box for model fit results.

        Args:
            annotation: The annotation text to display
        """
        annotation_core = annotation.strip("$")
        lines = annotation_core.split(r"\n")

        block_top = MODEL_FIT_ANNOTATION_CONFIG["block_top"]
        delta_y = MODEL_FIT_ANNOTATION_CONFIG["delta_y"]
        n_lines = len(lines)
        block_bottom = block_top - n_lines * delta_y
        block_left = MODEL_FIT_ANNOTATION_CONFIG["block_left"]
        block_right = MODEL_FIT_ANNOTATION_CONFIG["block_right"]
        rect_width = block_right - block_left

        ann_params = PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS[getattr(self, "_current_theme", "light")]
        rect = patches.Rectangle(
            (block_left, block_bottom),
            rect_width,
            block_top - block_bottom,
            transform=self.axes.transAxes,
            facecolor=ann_params["facecolor"],
            edgecolor=ann_params["edgecolor"],
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
                color=ann_params["text_color"],
                zorder=11,
            )

    def plot_model_fit_result(self, plot_data_and_kwargs):
        """
        Plot model fit results with annotations.

        Args:
            plot_data_and_kwargs: Data and configuration for plotting
        """
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
        self.axes.legend()

        self.canvas.draw_idle()
        self.figure.tight_layout()

        if annotation:
            self.add_model_fit_annotation(annotation)

    def add_model_free_annotation(self, annotation: str):
        """
        Add a formatted annotation box for model free results.

        Args:
            annotation: The annotation text to display
        """
        annotation_core = annotation.strip("$")
        lines = annotation_core.split(r"\n")

        block_top = MODEL_FREE_ANNOTATION_CONFIG["block_top"]
        delta_y = MODEL_FREE_ANNOTATION_CONFIG["delta_y"]
        n_lines = len(lines)
        block_bottom = block_top - n_lines * delta_y
        block_left = MODEL_FREE_ANNOTATION_CONFIG["block_left"]
        block_right = MODEL_FREE_ANNOTATION_CONFIG["block_right"]
        rect_width = block_right - block_left

        ann_params = PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS[getattr(self, "_current_theme", "light")]
        rect = patches.Rectangle(
            (block_left, block_bottom),
            rect_width,
            block_top - block_bottom,
            transform=self.axes.transAxes,
            facecolor=ann_params["facecolor"],
            edgecolor=ann_params["edgecolor"],
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
                fontsize=MODEL_FREE_ANNOTATION_CONFIG["fontsize"],
                color=ann_params["text_color"],
                zorder=11,
            )

    def plot_model_free_result(self, plot_data_and_kwargs):
        """
        Plot model free results with annotations.

        Args:
            plot_data_and_kwargs: Data and configuration for plotting
        """
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
