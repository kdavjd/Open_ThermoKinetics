"""Tests for SideBar GUI component.

Tests flat list navigation, file/series management, and signal emission.
"""

from PyQt6.QtWidgets import QListWidgetItem

from src.gui.main_tab.sidebar import SideBar


class TestSideBarCreation:
    """Tests for SideBar initialization."""

    def test_sidebar_creates_without_error(self, qtbot):
        """SideBar should initialize without exceptions."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar is not None

    def test_sidebar_has_list_widgets(self, qtbot):
        """SideBar should contain QListWidget for FILES and SERIES."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar.files_list is not None
        assert sidebar.series_list is not None

    def test_sidebar_lists_start_empty(self, qtbot):
        """FILES and SERIES lists should be empty initially."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar.files_list.count() == 0
        assert sidebar.series_list.count() == 0

    def test_sidebar_active_items_initialized_as_none(self, qtbot):
        """Active file and series items should be None initially."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar.active_file_item is None
        assert sidebar.active_series_item is None


class TestSideBarItemManagement:
    """Tests for SideBar item addition and removal."""

    def test_add_series_adds_item_to_list(self, qtbot):
        """add_series should add new series item to list."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        initial_count = sidebar.series_list.count()
        sidebar.add_series("Test Series")

        assert sidebar.series_list.count() == initial_count + 1

    def test_add_series_empty_name_does_not_add(self, qtbot):
        """add_series should not add item with empty name."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        initial_count = sidebar.series_list.count()
        sidebar.add_series("")

        assert sidebar.series_list.count() == initial_count

    def test_get_experiment_files_names_returns_list(self, qtbot):
        """get_experiment_files_names should return a list."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        files = sidebar.get_experiment_files_names()
        assert isinstance(files, list)

    def test_get_series_names_returns_list(self, qtbot):
        """get_series_names should return a list."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        series = sidebar.get_series_names()
        assert isinstance(series, list)

    def test_add_series_name_appears_in_get_series_names(self, qtbot):
        """Added series name should be returned by get_series_names."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        sidebar.add_series("MySeries")
        assert "MySeries" in sidebar.get_series_names()


class TestSideBarActiveState:
    """Tests for SideBar active item marking."""

    def test_mark_as_active_sets_bold(self, qtbot):
        """mark_as_active should set font bold on item."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        item = QListWidgetItem("Test File")
        sidebar.mark_as_active(item, is_series=False)

        assert item.font().bold()
        assert sidebar.active_file_item == item

    def test_mark_as_active_emits_signal(self, qtbot):
        """mark_as_active should emit active_file_selected signal."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        item = QListWidgetItem("Test File")

        with qtbot.waitSignal(sidebar.active_file_selected) as blocker:
            sidebar.mark_as_active(item, is_series=False)

        assert blocker.args == ["Test File"]

    def test_unmark_active_state_removes_bold(self, qtbot):
        """unmark_active_state should remove bold from font."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        item = QListWidgetItem("Test File")
        sidebar.mark_active_state(item)
        sidebar.unmark_active_state(item)

        assert not item.font().bold()


class TestSideBarSignals:
    """Tests for SideBar signal emissions."""

    def test_sub_side_bar_needed_signal_exists(self, qtbot):
        """SideBar should have sub_side_bar_needed signal."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert hasattr(sidebar, "sub_side_bar_needed")

    def test_to_main_window_signal_exists(self, qtbot):
        """SideBar should have to_main_window_signal."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert hasattr(sidebar, "to_main_window_signal")
