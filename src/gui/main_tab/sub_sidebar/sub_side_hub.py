from PyQt6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from src.core.app_settings import SideBarNames
from src.gui.main_tab.sub_sidebar.deconvolution import DeconvolutionSubBar
from src.gui.main_tab.sub_sidebar.experiment.experiment_sub_bar import ExperimentSubBar
from src.gui.main_tab.sub_sidebar.model_based import ModelBasedTab
from src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar import ModelFitSubBar
from src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar import ModelFreeSubBar
from src.gui.main_tab.sub_sidebar.series.series_sub_bar import SeriesSubBar

_FILE_TAB_INDEX = {
    SideBarNames.EXPERIMENTS.value: 0,
    SideBarNames.DECONVOLUTION.value: 1,
    SideBarNames.MODEL_FIT.value: 2,
}


class SubSideHub(QWidget):
    """
    Dynamic content manager for analysis panels in sub-sidebar.

    Manages switching between different analysis interfaces (deconvolution,
    model-based, experiments, etc.) based on sidebar navigation selection.
    """

    def __init__(self, parent=None):
        """Initialize all analysis panels and hide them by default."""
        super().__init__(parent)
        self.setObjectName("sub_sidebar_panel")
        self.layout = QVBoxLayout(self)

        # File-level analysis tabs: Experiment / Deconvolution / Model Fit
        self.experiment_sub_bar = ExperimentSubBar(self)
        self.deconvolution_sub_bar = DeconvolutionSubBar(self)
        self.model_fit_sub_bar = ModelFitSubBar(self)

        self.file_tabs = QTabWidget(self)
        self.file_tabs.setObjectName("file_tabs")
        self.file_tabs.addTab(self.experiment_sub_bar, "Experiment")
        self.file_tabs.addTab(self.deconvolution_sub_bar, "Deconvolution")
        self.file_tabs.addTab(self.model_fit_sub_bar, "Model Fit")
        self.file_tabs.hide()
        self.file_tabs.tabBar().hide()

        # Standalone panels
        self.model_based = ModelBasedTab(self)
        self.series_sub_bar = SeriesSubBar(self)
        self.model_free_sub_bar = ModelFreeSubBar(self)

        self.model_based.hide()
        self.series_sub_bar.hide()
        self.model_free_sub_bar.hide()

        self.current_widget = None

    def update_content(self, content_type):
        """
        Switch displayed panel based on content type from sidebar navigation.

        Args:
            content_type: Analysis panel identifier from SideBarNames enum
        """
        if content_type in _FILE_TAB_INDEX:
            if self.current_widget is not self.file_tabs:
                if self.current_widget is not None:
                    self.layout.removeWidget(self.current_widget)
                    self.current_widget.hide()
                self.current_widget = self.file_tabs
                self.layout.addWidget(self.file_tabs)
                self.file_tabs.show()
            self.file_tabs.setCurrentIndex(_FILE_TAB_INDEX[content_type])
            return

        widget_map = {
            SideBarNames.SERIES.value: self.series_sub_bar,
            SideBarNames.MODEL_FREE.value: self.model_free_sub_bar,
            SideBarNames.MODEL_BASED.value: self.model_based,
        }
        new_widget = widget_map.get(content_type, QLabel("unknown content", self))
        if self.current_widget is not new_widget:
            if self.current_widget is not None:
                self.layout.removeWidget(self.current_widget)
                self.current_widget.hide()
            self.current_widget = new_widget
            self.layout.addWidget(new_widget)
            new_widget.show()
