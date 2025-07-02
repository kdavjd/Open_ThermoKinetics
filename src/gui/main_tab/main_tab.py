from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from src.core.app_settings import OperationType, SideBarNames
from src.core.logger_config import logger
from src.gui.console_widget import ConsoleWidget
from src.gui.main_tab.plot_canvas.plot_canvas import PlotCanvas
from src.gui.main_tab.sidebar import SideBar
from src.gui.main_tab.sub_sidebar.sub_side_hub import SubSideHub

MIN_WIDTH_SIDEBAR = 220
MIN_WIDTH_SUBSIDEBAR = 220
MIN_WIDTH_CONSOLE = 150
MIN_WIDTH_PLOTCANVAS = 500
SPLITTER_WIDTH = 100
MIN_HEIGHT_MAINTAB = 700
COMPONENTS_MIN_WIDTH = (
    MIN_WIDTH_SIDEBAR + MIN_WIDTH_SUBSIDEBAR + MIN_WIDTH_CONSOLE + MIN_WIDTH_PLOTCANVAS + SPLITTER_WIDTH
)


class MainTab(QWidget):
    """
    Main tab widget implementing 4-panel responsive layout for thermal analysis GUI.

    Central component managing sidebar navigation, sub-sidebar panels, plot canvas,
    and console with proportional resizing and dynamic visibility control.
    Coordinates signal routing between GUI components and core logic modules.
    """

    to_main_window_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize main tab with 4-panel splitter layout and signal connections."""
        QWidget.__init__(self, parent)

        self.layout = QVBoxLayout(self)
        self.setMinimumHeight(MIN_HEIGHT_MAINTAB)
        self.setMinimumWidth(COMPONENTS_MIN_WIDTH + SPLITTER_WIDTH)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.layout.addWidget(self.splitter)

        self.sidebar = SideBar(self)
        self.sidebar.setMinimumWidth(MIN_WIDTH_SIDEBAR)
        self.splitter.addWidget(self.sidebar)

        self.sub_sidebar = SubSideHub(self)
        self.sub_sidebar.setMinimumWidth(MIN_WIDTH_SUBSIDEBAR)
        self.sub_sidebar.hide()
        self.splitter.addWidget(self.sub_sidebar)

        self.plot_canvas = PlotCanvas(self)
        self.plot_canvas.setMinimumWidth(MIN_WIDTH_PLOTCANVAS)
        self.splitter.addWidget(self.plot_canvas)

        self.console_widget = ConsoleWidget(self)
        self.console_widget.setMinimumWidth(MIN_WIDTH_CONSOLE)
        self.splitter.addWidget(self.console_widget)

        self.sidebar.sub_side_bar_needed.connect(self.toggle_sub_sidebar)
        self.sidebar.console_show_signal.connect(self.toggle_console_visibility)
        self.sub_sidebar.experiment_sub_bar.action_buttons_block.cancel_changes_clicked.connect(self.to_main_window)
        self.sub_sidebar.experiment_sub_bar.action_buttons_block.DTG_clicked.connect(self.to_main_window)
        self.sub_sidebar.experiment_sub_bar.action_buttons_block.conversion_clicked.connect(self.to_main_window)
        self.sub_sidebar.experiment_sub_bar.action_buttons_block.deconvolution_clicked.connect(self.toggle_sub_sidebar)
        self.sub_sidebar.deconvolution_sub_bar.reactions_table.reaction_added.connect(self.to_main_window)
        self.sub_sidebar.deconvolution_sub_bar.reactions_table.reaction_removed.connect(self.to_main_window)
        self.sub_sidebar.deconvolution_sub_bar.reactions_table.reaction_chosed.connect(self.to_main_window)
        self.sub_sidebar.deconvolution_sub_bar.update_value.connect(self.to_main_window)
        self.sidebar.active_file_selected.connect(self.sub_sidebar.deconvolution_sub_bar.reactions_table.switch_file)
        self.sidebar.active_series_selected.connect(self.select_series)
        self.plot_canvas.update_value.connect(self.update_anchors_slot)
        self.sub_sidebar.deconvolution_sub_bar.calc_buttons.calculation_started.connect(self.to_main_window)
        self.sub_sidebar.model_fit_sub_bar.model_fit_calculation.connect(self.to_main_window)
        self.sub_sidebar.deconvolution_sub_bar.file_transfer_buttons.import_reactions_signal.connect(
            self.to_main_window
        )
        self.sub_sidebar.deconvolution_sub_bar.file_transfer_buttons.export_reactions_signal.connect(
            self.to_main_window
        )
        self.sub_sidebar.deconvolution_sub_bar.calc_buttons.calculation_stopped.connect(self.to_main_window)
        self.sub_sidebar.model_based.models_scene.scheme_change_signal.connect(self.to_main_window)
        self.sub_sidebar.model_based.calc_buttons.simulation_started.connect(self.to_main_window)
        self.sub_sidebar.model_based.calc_buttons.simulation_stopped.connect(self.to_main_window)
        self.sub_sidebar.model_based.model_params_changed.connect(self.to_main_window)
        self.sub_sidebar.series_sub_bar.load_deconvolution_results_signal.connect(self.to_main_window)
        self.sub_sidebar.series_sub_bar.results_combobox_text_changed_signal.connect(self.select_series_reaction)
        self.sub_sidebar.model_fit_sub_bar.table_combobox_text_changed_signal.connect(self.to_main_window)
        self.sub_sidebar.model_fit_sub_bar.plot_model_fit_signal.connect(self.to_main_window)
        self.sub_sidebar.model_free_sub_bar.model_free_calculation_signal.connect(self.to_main_window)
        self.sub_sidebar.model_free_sub_bar.table_combobox_text_changed_signal.connect(self.to_main_window)
        self.sub_sidebar.model_free_sub_bar.plot_model_free_signal.connect(self.to_main_window)

    def initialize_sizes(self):
        """Calculate and apply proportional panel sizes based on total width."""
        total_width = self.width()

        sidebar_ratio = MIN_WIDTH_SIDEBAR / COMPONENTS_MIN_WIDTH
        subsidebar_ratio = MIN_WIDTH_SUBSIDEBAR / COMPONENTS_MIN_WIDTH
        console_ratio = MIN_WIDTH_CONSOLE / COMPONENTS_MIN_WIDTH

        sidebar_width = int(total_width * sidebar_ratio)
        console_width = int(total_width * console_ratio) if self.console_widget.isVisible() else 0
        sub_sidebar_width = int(total_width * subsidebar_ratio) if self.sub_sidebar.isVisible() else 0
        canvas_width = total_width - (sidebar_width + sub_sidebar_width + console_width)
        self.splitter.setSizes([sidebar_width, sub_sidebar_width, canvas_width, console_width])

    def showEvent(self, event):
        """Handle widget show event by initializing panel sizes."""
        super().showEvent(event)
        self.initialize_sizes()

    def toggle_sub_sidebar(self, content_type):
        """
        Toggle sub-sidebar visibility and update content based on analysis type.

        Args:
            content_type: Analysis panel type or None to hide
        """
        logger.debug(f"totoggle_sub_sidebar: {content_type=}")
        if content_type:
            canvas_connects = True if content_type == SideBarNames.DECONVOLUTION.value else False
            self.plot_canvas.toggle_event_connections(canvas_connects)

            if content_type in self.sidebar.get_experiment_files_names():
                self.sub_sidebar.update_content(SideBarNames.EXPERIMENTS.value)
            else:
                self.sub_sidebar.update_content(content_type)
            self.sub_sidebar.setVisible(True)
        else:
            self.sub_sidebar.setVisible(False)
        self.initialize_sizes()

    def toggle_console_visibility(self, visible):
        """Toggle console widget visibility and recalculate layout sizes."""
        self.console_widget.setVisible(visible)
        self.initialize_sizes()

    def select_series(self, series_name):
        """Emit series selection signal if series exists."""
        if series_name in self.sidebar.get_series_names():
            self.to_main_window_signal.emit({"operation": OperationType.SELECT_SERIES, "series_name": series_name})

    @pyqtSlot(str)
    def select_series_reaction(self, reaction_name):
        """Select specific reaction within active series for visualization."""
        series_name = self.sidebar.active_series_item.text() if self.sidebar.active_series_item else None
        params = {
            "operation": OperationType.SELECT_SERIES,
            "series_name": series_name,
            "reaction_n": reaction_name,
        }
        self.to_main_window_signal.emit(params)

    @pyqtSlot(dict)
    def to_main_window(self, params: dict):
        """
        Route operation signals to main window with active file/series context.

        Args:
            params: Operation parameters dict to be enhanced with context
        """
        file_name = self.sidebar.active_file_item.text() if self.sidebar.active_file_item else "no_file"
        series_name = self.sidebar.active_series_item.text() if self.sidebar.active_series_item else None
        params["file_name"] = file_name
        params["series_name"] = series_name
        params.setdefault("path_keys", []).insert(0, file_name)
        self.to_main_window_signal.emit(params)

    @pyqtSlot(list)
    def update_anchors_slot(self, params_list: list):
        """
        Handle interactive anchor updates from plot canvas.

        Args:
            params_list: List of parameter update dictionaries from draggable anchors
        """
        for i, params in enumerate(params_list):
            params["path_keys"].insert(
                0,
                self.sub_sidebar.deconvolution_sub_bar.reactions_table.active_reaction,
            )
            params["is_chain"] = True
            self.to_main_window(params)
        params["operation"] = OperationType.HIGHLIGHT_REACTION
        self.to_main_window(params)

    def update_reactions_table(self, data: dict):
        """
        Update reactions table UI with loaded reaction configuration data.

        Args:
            data: Dict mapping reaction names to reaction info with function types
        """
        active_file_name = self.sidebar.active_file_item.text() if self.sidebar.active_file_item else None
        if not active_file_name:
            logger.error("There is no active file to update the UI.")
            return

        reaction_table = self.sub_sidebar.deconvolution_sub_bar.reactions_table
        reaction_table.switch_file(active_file_name)
        table = reaction_table.reactions_tables[active_file_name]
        table.setRowCount(0)
        reaction_table.reactions_counters[active_file_name] = 0

        for reaction_name, reaction_info in data.items():
            function_name = reaction_info.get("function", "gauss")
            reaction_table.add_reaction(reaction_name=reaction_name, function_name=function_name, emit_signal=False)
        logger.debug("The UI has been successfully updated with loaded reactions.")

    def response_slot(self, params: dict):
        """Handle response signals with debug logging."""
        logger.debug(f"response_slot handle {params}")
