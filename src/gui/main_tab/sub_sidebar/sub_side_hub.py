from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.app_settings import SideBarNames
from src.gui.analysis.panels.deconvolution_panel import DeconvolutionPanel
from src.gui.analysis.panels.model_fit_panel import ModelFitPanel
from src.gui.analysis.panels.model_free_panel import ModelFreePanel
from src.gui.main_tab.sub_sidebar.experiment_sub_bar import ExperimentSubBar
from src.gui.main_tab.sub_sidebar.series_sub_bar import SeriesSubBar
from src.gui.tabs.model_based_tab import ModelBasedTab


class SubSideHub(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.deconvolution_sub_bar = DeconvolutionPanel(self)
        self.model_fit_sub_bar = ModelFitPanel(self)
        self.experiment_sub_bar = ExperimentSubBar(self)
        self.model_based = ModelBasedTab(self)
        self.series_sub_bar = SeriesSubBar(self)
        self.model_free_sub_bar = ModelFreePanel(self)

        self.deconvolution_sub_bar.hide()
        self.model_fit_sub_bar.hide()
        self.model_free_sub_bar.hide()
        self.experiment_sub_bar.hide()
        self.model_based.hide()
        self.series_sub_bar.hide()

        self.current_widget = None

    def update_content(self, content_type):
        if self.current_widget is not None:
            self.layout.removeWidget(self.current_widget)
            self.current_widget.hide()

        if content_type == SideBarNames.DECONVOLUTION.value:
            self.current_widget = self.deconvolution_sub_bar
        elif content_type == SideBarNames.MODEL_FREE.value:
            self.current_widget = self.model_free_sub_bar
        elif content_type == SideBarNames.MODEL_FIT.value:
            self.current_widget = self.model_fit_sub_bar
        elif content_type == SideBarNames.MODEL_BASED.value:
            self.current_widget = self.model_based
        elif content_type == SideBarNames.EXPERIMENTS.value:
            self.current_widget = self.experiment_sub_bar
        elif content_type == SideBarNames.SERIES.value:
            self.current_widget = self.series_sub_bar
        else:
            self.current_widget = QLabel("unknown content", self)

        self.current_widget.show()
        self.layout.addWidget(self.current_widget)
