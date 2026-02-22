"""Tests for SubSideHub - panel switcher for analysis sub-sidebars."""

from src.core.app_settings import SideBarNames
from src.gui.main_tab.sub_sidebar.sub_side_hub import SubSideHub


class TestSubSideHubInit:
    """Tests for SubSideHub initialization."""

    def test_init_creates_all_panels(self, qtbot):
        """SubSideHub should create all analysis panels on init."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.deconvolution_sub_bar is not None
        assert hub.model_fit_sub_bar is not None
        assert hub.experiment_sub_bar is not None
        assert hub.model_based is not None
        assert hub.series_sub_bar is not None
        assert hub.model_free_sub_bar is not None

    def test_init_file_tabs_hidden(self, qtbot):
        """File analysis tabs widget should be hidden by default."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.file_tabs.isHidden()

    def test_init_standalone_panels_hidden(self, qtbot):
        """Standalone panels (series, model free, model based) hidden by default."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.model_based.isHidden()
        assert hub.series_sub_bar.isHidden()
        assert hub.model_free_sub_bar.isHidden()

    def test_init_current_widget_is_none(self, qtbot):
        """Current widget should be None initially."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.current_widget is None

    def test_init_file_tabs_has_three_tabs(self, qtbot):
        """file_tabs should have Experiment, Deconvolution, Model Fit tabs."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.file_tabs.count() == 3
        assert hub.file_tabs.tabText(0) == "Experiment"
        assert hub.file_tabs.tabText(1) == "Deconvolution"
        assert hub.file_tabs.tabText(2) == "Model Fit"


class TestSubSideHubUpdateContent:
    """Tests for SubSideHub.update_content method."""

    def test_update_content_deconvolution(self, qtbot):
        """Switching to deconvolution shows file_tabs on Deconvolution tab."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.DECONVOLUTION.value)

        assert hub.current_widget is hub.file_tabs
        assert not hub.file_tabs.isHidden()
        assert hub.file_tabs.currentIndex() == 1

    def test_update_content_model_free(self, qtbot):
        """Switching to model free panel shows ModelFreeSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.MODEL_FREE.value)

        assert hub.current_widget is hub.model_free_sub_bar
        assert not hub.model_free_sub_bar.isHidden()

    def test_update_content_model_fit(self, qtbot):
        """Switching to model fit shows file_tabs on Model Fit tab."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.MODEL_FIT.value)

        assert hub.current_widget is hub.file_tabs
        assert not hub.file_tabs.isHidden()
        assert hub.file_tabs.currentIndex() == 2

    def test_update_content_model_based(self, qtbot):
        """Switching to model based panel shows ModelBasedTab."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.MODEL_BASED.value)

        assert hub.current_widget is hub.model_based
        assert not hub.model_based.isHidden()

    def test_update_content_experiments(self, qtbot):
        """Switching to experiments shows file_tabs on Experiment tab."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)

        assert hub.current_widget is hub.file_tabs
        assert not hub.file_tabs.isHidden()
        assert hub.file_tabs.currentIndex() == 0

    def test_update_content_series(self, qtbot):
        """Switching to series panel shows SeriesSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.SERIES.value)

        assert hub.current_widget is hub.series_sub_bar
        assert not hub.series_sub_bar.isHidden()

    def test_update_content_unknown_shows_label(self, qtbot):
        """Unknown content type shows 'unknown content' label."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content("unknown_type")

        assert hub.current_widget.text() == "unknown content"

    def test_update_content_file_to_standalone_hides_file_tabs(self, qtbot):
        """Switching from file tab to standalone panel hides file_tabs."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)
        assert not hub.file_tabs.isHidden()

        hub.update_content(SideBarNames.SERIES.value)
        assert hub.file_tabs.isHidden()
        assert not hub.series_sub_bar.isHidden()

    def test_update_content_experiments_to_deconvolution_switches_tab(self, qtbot):
        """Switching from Experiments to Deconvolution stays in file_tabs, switches tab."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)
        assert hub.file_tabs.currentIndex() == 0

        hub.update_content(SideBarNames.DECONVOLUTION.value)
        assert hub.current_widget is hub.file_tabs
        assert hub.file_tabs.currentIndex() == 1

    def test_update_content_multiple_switches(self, qtbot):
        """Multiple panel switches work correctly."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)
        assert hub.current_widget is hub.file_tabs
        assert hub.file_tabs.currentIndex() == 0

        hub.update_content(SideBarNames.MODEL_FIT.value)
        assert hub.current_widget is hub.file_tabs
        assert hub.file_tabs.currentIndex() == 2

        hub.update_content(SideBarNames.MODEL_FREE.value)
        assert hub.current_widget is hub.model_free_sub_bar

        hub.update_content(SideBarNames.DECONVOLUTION.value)
        assert hub.current_widget is hub.file_tabs
        assert hub.file_tabs.currentIndex() == 1
