from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.app_settings import SideBarNames
from src.gui.main_tab.sub_sidebar.deconvolution import DeconvolutionSubBar
from src.gui.main_tab.sub_sidebar.experiment.experiment_sub_bar import ExperimentSubBar
from src.gui.main_tab.sub_sidebar.model_based import ModelBasedTab
from src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar import ModelFitSubBar
from src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar import ModelFreeSubBar
from src.gui.main_tab.sub_sidebar.series.series_sub_bar import SeriesSubBar


class SubSideHub(QWidget):
    """
    Dynamic content manager for analysis panels in sub-sidebar.

    Manages switching between different analysis interfaces (deconvolution,
    model-based, experiments, etc.) based on sidebar navigation selection.
    """

    def __init__(self, parent=None):
        """Initialize all analysis panels and hide them by default."""
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.deconvolution_sub_bar = DeconvolutionSubBar(self)
        self.model_fit_sub_bar = ModelFitSubBar(self)
        self.experiment_sub_bar = ExperimentSubBar(self)
        self.model_based = ModelBasedTab(self)
        self.series_sub_bar = SeriesSubBar(self)
        self.model_free_sub_bar = ModelFreeSubBar(self)

        self.deconvolution_sub_bar.hide()
        self.model_fit_sub_bar.hide()
        self.model_free_sub_bar.hide()
        self.experiment_sub_bar.hide()
        self.model_based.hide()
        self.series_sub_bar.hide()

        self.current_widget = None

    def update_content(self, content_type):
        """
        Switch displayed panel based on content type from sidebar navigation.

        Args:
            content_type: Analysis panel identifier from SideBarNames enum
        """
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
