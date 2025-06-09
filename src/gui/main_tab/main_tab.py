from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from src.core.app_settings import OperationType, SideBarNames
from src.core.logger_config import logger
from src.gui.config import get_app_config
from src.gui.console_widget import ConsoleWidget
from src.gui.main_tab.plot_canvas.plot_canvas import PlotCanvas
from src.gui.main_tab.sidebar import SideBar
from src.gui.main_tab.sub_sidebar.sub_side_hub import SubSideHub


class MainTab(QWidget):
    to_main_window_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Get configuration for layout dimensions
        config = get_app_config()
        splitter_config = config.splitter

        self.layout = QVBoxLayout(self)
        self.setMinimumHeight(splitter_config.min_height_maintab)
        self.setMinimumWidth(
            splitter_config.min_width_sidebar
            + splitter_config.min_width_subsidebar
            + splitter_config.min_width_console
            + splitter_config.min_width_plotcanvas
        )

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.layout.addWidget(self.splitter)

        self.sidebar = SideBar(self)
        self.sidebar.setMinimumWidth(splitter_config.min_width_sidebar)
        self.splitter.addWidget(self.sidebar)

        self.sub_sidebar = SubSideHub(self)
        self.sub_sidebar.setMinimumWidth(splitter_config.min_width_subsidebar)
        self.sub_sidebar.hide()
        self.splitter.addWidget(self.sub_sidebar)

        self.plot_canvas = PlotCanvas(self)
        self.plot_canvas.setMinimumWidth(splitter_config.min_width_plotcanvas)
        self.splitter.addWidget(self.plot_canvas)

        self.console_widget = ConsoleWidget(self)
        self.console_widget.setMinimumWidth(splitter_config.min_width_console)
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
        total_width = self.width()

        # Get configuration for layout dimensions
        config = get_app_config()
        splitter_config = config.splitter

        sidebar_width = int(total_width * splitter_config.sidebar_ratio)
        console_width = int(total_width * splitter_config.console_ratio) if self.console_widget.isVisible() else 0
        sub_sidebar_width = int(total_width * splitter_config.sub_sidebar_ratio) if self.sub_sidebar.isVisible() else 0
        canvas_width = total_width - (sidebar_width + sub_sidebar_width + console_width)
        self.splitter.setSizes([sidebar_width, sub_sidebar_width, canvas_width, console_width])

    def showEvent(self, event):
        super().showEvent(event)
        self.initialize_sizes()

    def toggle_sub_sidebar(self, content_type):
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
        self.console_widget.setVisible(visible)
        self.initialize_sizes()

    def select_series(self, series_name):
        if series_name in self.sidebar.get_series_names():
            self.to_main_window_signal.emit({"operation": OperationType.SELECT_SERIES, "series_name": series_name})

    @pyqtSlot(str)
    def select_series_reaction(self, reaction_name):
        series_name = self.sidebar.active_series_item.text() if self.sidebar.active_series_item else None
        params = {
            "operation": OperationType.SELECT_SERIES,
            "series_name": series_name,
            "reaction_n": reaction_name,
        }
        self.to_main_window_signal.emit(params)

    @pyqtSlot(dict)
    def to_main_window(self, params: dict):
        file_name = self.sidebar.active_file_item.text() if self.sidebar.active_file_item else "no_file"
        series_name = self.sidebar.active_series_item.text() if self.sidebar.active_series_item else None
        params["file_name"] = file_name
        params["series_name"] = series_name
        params.setdefault("path_keys", []).insert(0, file_name)
        self.to_main_window_signal.emit(params)

    @pyqtSlot(list)
    def update_anchors_slot(self, params_list: list):
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
        logger.debug(f"response_slot handle {params}")
