"""Tests for SideBar GUI component.

Tests tree navigation, file/series management, and signal emission.
"""

from PyQt6.QtGui import QStandardItem

from src.gui.main_tab.sidebar import SideBar


class TestSideBarCreation:
    """Tests for SideBar initialization."""

    def test_sidebar_creates_without_error(self, qtbot):
        """SideBar should initialize without exceptions."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar is not None

    def test_sidebar_has_tree_view(self, qtbot):
        """SideBar should contain QTreeView."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar.tree_view is not None
        assert sidebar.model is not None

    def test_sidebar_has_root_items(self, qtbot):
        """SideBar should have experiments, series, calculation, settings roots."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar.experiments_data_root is not None
        assert sidebar.series_root is not None
        assert sidebar.calculation_root is not None
        assert sidebar.settings_root is not None

    def test_sidebar_active_items_initialized_as_none(self, qtbot):
        """Active file and series items should be None initially."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert sidebar.active_file_item is None
        assert sidebar.active_series_item is None


class TestSideBarItemManagement:
    """Tests for SideBar item addition and removal."""

    def test_add_series_adds_item_to_tree(self, qtbot):
        """add_series should add new series item to tree."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        initial_count = sidebar.series_root.rowCount()
        sidebar.add_series("Test Series")

        assert sidebar.series_root.rowCount() == initial_count + 1

    def test_add_series_empty_name_does_not_add(self, qtbot):
        """add_series should not add item with empty name."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        initial_count = sidebar.series_root.rowCount()
        sidebar.add_series("")

        assert sidebar.series_root.rowCount() == initial_count

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


class TestSideBarActiveState:
    """Tests for SideBar active item marking."""

    def test_mark_as_active_sets_bold(self, qtbot):
        """mark_as_active should set font bold on item."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        item = QStandardItem("Test File")
        sidebar.mark_as_active(item, is_series=False)

        assert item.font().bold()
        assert sidebar.active_file_item == item

    def test_mark_as_active_emits_signal(self, qtbot):
        """mark_as_active should emit active_file_selected signal."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        item = QStandardItem("Test File")

        with qtbot.waitSignal(sidebar.active_file_selected) as blocker:
            sidebar.mark_as_active(item, is_series=False)

        assert blocker.args == ["Test File"]

    def test_unmark_active_state_removes_bold(self, qtbot):
        """unmark_active_state should remove bold from font."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        item = QStandardItem("Test File")
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

    def test_console_show_signal_exists(self, qtbot):
        """SideBar should have console_show_signal."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert hasattr(sidebar, "console_show_signal")

    def test_to_main_window_signal_exists(self, qtbot):
        """SideBar should have to_main_window_signal."""
        sidebar = SideBar()
        qtbot.addWidget(sidebar)

        assert hasattr(sidebar, "to_main_window_signal")
