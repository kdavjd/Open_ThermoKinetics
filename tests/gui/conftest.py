"""PyQt6 fixtures for GUI tests.

Provides fixtures for testing GUI components without real display.
Uses pytest-qt's qtbot for widget testing.
"""

from unittest.mock import MagicMock

import pytest

from src.core.base_signals import BaseSignals


@pytest.fixture
def gui_signals(qtbot):
    """Create real BaseSignals instance for GUI tests.

    Real signals are needed for Qt signal/slot connections in tests.
    Uses qtbot to ensure QApplication is available.
    """
    return BaseSignals()


@pytest.fixture
def mock_main_window_deps():
    """Mock dependencies for MainWindow that don't need real implementations.

    Returns dict of mocked core components.
    """
    return {
        "file_data": MagicMock(),
        "calculations": MagicMock(),
        "series_data": MagicMock(),
        "calculations_data_operations": MagicMock(),
    }
