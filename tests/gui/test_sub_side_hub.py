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

    def test_init_all_panels_hidden(self, qtbot):
        """All panels should be hidden by default."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.deconvolution_sub_bar.isHidden()
        assert hub.model_fit_sub_bar.isHidden()
        assert hub.experiment_sub_bar.isHidden()
        assert hub.model_based.isHidden()
        assert hub.series_sub_bar.isHidden()
        assert hub.model_free_sub_bar.isHidden()

    def test_init_current_widget_is_none(self, qtbot):
        """Current widget should be None initially."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        assert hub.current_widget is None


class TestSubSideHubUpdateContent:
    """Tests for SubSideHub.update_content method."""

    def test_update_content_deconvolution(self, qtbot):
        """Switching to deconvolution panel shows DeconvolutionSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.DECONVOLUTION.value)

        assert hub.current_widget == hub.deconvolution_sub_bar
        assert not hub.deconvolution_sub_bar.isHidden()

    def test_update_content_model_free(self, qtbot):
        """Switching to model free panel shows ModelFreeSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.MODEL_FREE.value)

        assert hub.current_widget == hub.model_free_sub_bar
        assert not hub.model_free_sub_bar.isHidden()

    def test_update_content_model_fit(self, qtbot):
        """Switching to model fit panel shows ModelFitSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.MODEL_FIT.value)

        assert hub.current_widget == hub.model_fit_sub_bar
        assert not hub.model_fit_sub_bar.isHidden()

    def test_update_content_model_based(self, qtbot):
        """Switching to model based panel shows ModelBasedTab."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.MODEL_BASED.value)

        assert hub.current_widget == hub.model_based
        assert not hub.model_based.isHidden()

    def test_update_content_experiments(self, qtbot):
        """Switching to experiments panel shows ExperimentSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)

        assert hub.current_widget == hub.experiment_sub_bar
        assert not hub.experiment_sub_bar.isHidden()

    def test_update_content_series(self, qtbot):
        """Switching to series panel shows SeriesSubBar."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.SERIES.value)

        assert hub.current_widget == hub.series_sub_bar
        assert not hub.series_sub_bar.isHidden()

    def test_update_content_unknown_shows_label(self, qtbot):
        """Unknown content type shows 'unknown content' label."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content("unknown_type")

        assert hub.current_widget.text() == "unknown content"

    def test_update_content_hides_previous_widget(self, qtbot):
        """Switching panels hides the previously shown widget."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)
        assert not hub.experiment_sub_bar.isHidden()

        hub.update_content(SideBarNames.DECONVOLUTION.value)
        assert hub.experiment_sub_bar.isHidden()
        assert not hub.deconvolution_sub_bar.isHidden()

    def test_update_content_multiple_switches(self, qtbot):
        """Multiple panel switches work correctly."""
        hub = SubSideHub()
        qtbot.add_widget(hub)

        hub.update_content(SideBarNames.EXPERIMENTS.value)
        assert hub.current_widget == hub.experiment_sub_bar

        hub.update_content(SideBarNames.MODEL_FIT.value)
        assert hub.current_widget == hub.model_fit_sub_bar

        hub.update_content(SideBarNames.MODEL_FREE.value)
        assert hub.current_widget == hub.model_free_sub_bar

        hub.update_content(SideBarNames.DECONVOLUTION.value)
        assert hub.current_widget == hub.deconvolution_sub_bar
