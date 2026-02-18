"""Tests for MainWindow GUI component.

Tests main window creation, tab management, and signal routing.
"""

from PyQt6.QtWidgets import QTabWidget

from src.gui.main_window import MainWindow


class TestMainWindowCreation:
    """Tests for MainWindow initialization."""

    def test_main_window_creates_without_error(self, gui_signals, qtbot):
        """MainWindow should initialize without exceptions."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        assert window is not None
        assert window.windowTitle() == "Open ThermoKinetics"

    def test_main_window_has_tab_widget(self, gui_signals, qtbot):
        """MainWindow should contain QTabWidget as central widget."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        assert isinstance(window.tabs, QTabWidget)
        assert window.tabs is window.centralWidget()

    def test_main_window_has_two_tabs(self, gui_signals, qtbot):
        """MainWindow should have Main and User Guide tabs."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        assert window.tabs.count() == 2
        assert window.tabs.tabText(0) == "Main"
        assert window.tabs.tabText(1) == "User Guide"

    def test_main_window_registers_with_signals(self, gui_signals, qtbot):
        """MainWindow should register itself with BaseSignals."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        assert "main_window" in gui_signals.components


class TestMainWindowTabs:
    """Tests for MainWindow tab switching."""

    def test_tabs_are_switchable(self, gui_signals, qtbot):
        """Tab switching should work without errors."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)
        window.show()

        window.tabs.setCurrentIndex(1)
        assert window.tabs.currentIndex() == 1

        window.tabs.setCurrentIndex(0)
        assert window.tabs.currentIndex() == 0


class TestMainWindowSignalRouting:
    """Tests for MainWindow signal routing."""

    def test_main_tab_signal_exists(self, gui_signals, qtbot):
        """MainTab should have to_main_window_signal for routing."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        assert hasattr(window.main_tab, "to_main_window_signal")
        assert window.main_tab.to_main_window_signal is not None

    def test_process_request_handles_unknown_operation(self, gui_signals, qtbot):
        """process_request should handle unknown operations gracefully."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        params = {"operation": "UNKNOWN_OPERATION", "actor": "test", "target": "main_window"}
        window.process_request(params)


class TestMainWindowOperationHandlers:
    """Tests for MainWindow operation handler methods."""

    def test_handle_plot_df_returns_false_without_df(self, gui_signals, qtbot):
        """_handle_plot_df should return False when df is None."""
        window = MainWindow(gui_signals)
        qtbot.addWidget(window)

        result = window._handle_plot_df({})
        assert result is False
