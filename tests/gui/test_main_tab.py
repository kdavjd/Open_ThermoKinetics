"""Tests for MainTab GUI component.

Tests 4-panel layout, splitter management, and component visibility.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

from src.gui.main_tab.main_tab import (
    COMPONENTS_MIN_WIDTH,
    MIN_HEIGHT_MAINTAB,
    MIN_WIDTH_CONSOLE,
    MIN_WIDTH_PLOTCANVAS,
    MIN_WIDTH_SIDEBAR,
    MIN_WIDTH_SUBSIDEBAR,
    MainTab,
)


class TestMainTabCreation:
    """Tests for MainTab initialization."""

    def test_main_tab_creates_without_error(self, qtbot):
        """MainTab should initialize without exceptions."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)

        assert main_tab is not None

    def test_main_tab_has_splitter(self, qtbot):
        """MainTab should use QSplitter for 4-panel layout."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)

        assert isinstance(main_tab.splitter, QSplitter)
        assert main_tab.splitter.orientation() == Qt.Orientation.Horizontal

    def test_main_tab_has_four_components(self, qtbot):
        """MainTab should contain sidebar, sub_sidebar, plot_canvas, console."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)

        assert main_tab.splitter.count() == 4
        assert main_tab.sidebar is not None
        assert main_tab.sub_sidebar is not None
        assert main_tab.plot_canvas is not None
        assert main_tab.console_widget is not None

    def test_main_tab_minimum_dimensions(self, qtbot):
        """MainTab should have minimum dimensions set."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)

        assert main_tab.minimumHeight() == MIN_HEIGHT_MAINTAB
        assert main_tab.minimumWidth() >= COMPONENTS_MIN_WIDTH


class TestMainTabSubSidebar:
    """Tests for MainTab sub-sidebar visibility control."""

    def test_sub_sidebar_hidden_by_default(self, qtbot):
        """Sub-sidebar should be hidden initially."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)

        assert not main_tab.sub_sidebar.isVisible()

    def test_toggle_sub_sidebar_shows_panel(self, qtbot):
        """toggle_sub_sidebar should show panel when content_type provided."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)
        main_tab.show()

        main_tab.toggle_sub_sidebar("experiments")

        assert main_tab.sub_sidebar.isVisible()

    def test_toggle_sub_sidebar_hides_panel(self, qtbot):
        """toggle_sub_sidebar should hide panel when content_type is None/empty."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)
        main_tab.show()
        main_tab.sub_sidebar.setVisible(True)

        main_tab.toggle_sub_sidebar(None)

        assert not main_tab.sub_sidebar.isVisible()


class TestMainTabConsole:
    """Tests for MainTab console visibility control."""

    def test_toggle_console_visibility(self, qtbot):
        """toggle_console_visibility should toggle console widget."""
        main_tab = MainTab()
        qtbot.addWidget(main_tab)
        main_tab.show()

        main_tab.toggle_console_visibility(False)
        assert not main_tab.console_widget.isVisible()

        main_tab.toggle_console_visibility(True)
        assert main_tab.console_widget.isVisible()


class TestMainTabLayoutConstants:
    """Tests for MainTab layout constants."""

    def test_layout_constants_are_positive(self):
        """All layout constants should be positive integers."""
        assert MIN_WIDTH_SIDEBAR > 0
        assert MIN_WIDTH_SUBSIDEBAR > 0
        assert MIN_WIDTH_CONSOLE > 0
        assert MIN_WIDTH_PLOTCANVAS > 0
        assert MIN_HEIGHT_MAINTAB > 0
        assert COMPONENTS_MIN_WIDTH > 0

    def test_components_min_width_is_sum(self):
        """COMPONENTS_MIN_WIDTH should equal sum of component widths plus splitter."""
        expected = (
            MIN_WIDTH_SIDEBAR + MIN_WIDTH_SUBSIDEBAR + MIN_WIDTH_CONSOLE + MIN_WIDTH_PLOTCANVAS + 100  # SPLITTER_WIDTH
        )
        assert COMPONENTS_MIN_WIDTH == expected
