"""Common pytest fixtures for Open ThermoKinetics test suite.

Provides fixtures for:
- Sample data (numpy arrays, DataFrames)
- Test file paths
- Qt application for GUI tests
- Mock objects for BaseSlots-derived classes
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ============================================================================
# Mock fixtures for BaseSlots-derived classes (Qt-free testing)
# ============================================================================


@pytest.fixture
def mock_signals():
    """Create mock BaseSignals for testing BaseSlots-derived classes without Qt event loop.

    Usage:
        def test_something(mock_signals):
            component = FileData(mock_signals)
            # component.signals is a MagicMock with response_signal
    """
    signals = MagicMock()
    signals.response_signal = MagicMock()
    signals.response_signal.emit = MagicMock()
    signals.request_signal = MagicMock()
    signals.request_signal.emit = MagicMock()
    signals.register_component = MagicMock()
    return signals


@pytest.fixture
def mock_qapp(qtbot):
    """Provide QApplication instance for tests requiring real Qt event loop.

    Uses pytest-qt's qtbot fixture which handles QApplication lifecycle.
    Only use when you need actual signal/slot behavior with event processing.

    Usage:
        def test_with_real_qt(mock_qapp):
            from src.core.base_signals import BaseSignals
            signals = BaseSignals()
            # signals will work with real Qt event loop
    """
    return qtbot


# ============================================================================
# Path fixtures
# ============================================================================

TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def sample_csv_path() -> Path:
    """Path to sample experimental CSV file."""
    return FIXTURES_DIR / "NH4_rate_3.csv"


@pytest.fixture
def sample_preset_path() -> Path:
    """Path to sample deconvolution preset JSON file."""
    return FIXTURES_DIR / "NH4_rate_3_4_rcts_gs_fr_ads_ads.json"


# ============================================================================
# NumPy array fixtures (for curve_fitting tests)
# ============================================================================


@pytest.fixture
def sample_x_array() -> np.ndarray:
    """Sample x values (temperature range)."""
    return np.linspace(300, 600, 250)


@pytest.fixture
def sample_gaussian_params() -> dict:
    """Sample Gaussian peak parameters."""
    return {
        "h": 1.0,  # height
        "z": 450.0,  # center position
        "w": 30.0,  # width
    }


@pytest.fixture
def sample_fraser_params() -> dict:
    """Sample Fraser-Suzuki peak parameters."""
    return {
        "h": 1.0,  # height
        "z": 450.0,  # center position
        "w": 30.0,  # width
        "fs": 0.5,  # asymmetry
    }


@pytest.fixture
def sample_ads_params() -> dict:
    """Sample Asymmetric Double Sigmoid peak parameters."""
    return {
        "h": 1.0,  # height
        "z": 450.0,  # center position
        "w": 30.0,  # width
        "ads1": 10.0,  # left asymmetry
        "ads2": 15.0,  # right asymmetry
    }


# ============================================================================
# DataFrame fixtures (for file_data tests)
# ============================================================================


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Sample DataFrame with temperature and intensity data."""
    temperature = np.linspace(300, 600, 100)
    intensity = np.exp(-((temperature - 450) ** 2) / (2 * 30**2))
    return pd.DataFrame(
        {
            "temperature": temperature,
            "intensity": intensity,
        }
    )


@pytest.fixture
def sample_multi_heating_dataframe() -> pd.DataFrame:
    """Sample DataFrame with multiple heating rates."""
    temperature = np.linspace(300, 600, 100)
    return pd.DataFrame(
        {
            "temperature": temperature,
            "rate_3": np.exp(-((temperature - 440) ** 2) / (2 * 25**2)),
            "rate_5": np.exp(-((temperature - 450) ** 2) / (2 * 30**2)),
            "rate_10": np.exp(-((temperature - 465) ** 2) / (2 * 35**2)),
        }
    )


# ============================================================================
# Reaction params fixtures (for deconvolution tests)
# ============================================================================


@pytest.fixture
def sample_gaussian_reaction_params(sample_x_array) -> dict:
    """Sample reaction parameters for Gaussian function."""
    return {
        "function": "gauss",
        "x": sample_x_array,
        "coeffs": {"h": 0.8, "z": 450.0, "w": 25.0},
        "upper_bound_coeffs": {"h": 1.0, "z": 460.0, "w": 30.0},
        "lower_bound_coeffs": {"h": 0.6, "z": 440.0, "w": 20.0},
    }


@pytest.fixture
def sample_fraser_reaction_params(sample_x_array) -> dict:
    """Sample reaction parameters for Fraser-Suzuki function."""
    return {
        "function": "fraser",
        "x": sample_x_array,
        "coeffs": {"h": 0.8, "z": 450.0, "w": 25.0, "fr": 0.3},
        "upper_bound_coeffs": {"h": 1.0, "z": 460.0, "w": 30.0, "fr": 0.5},
        "lower_bound_coeffs": {"h": 0.6, "z": 440.0, "w": 20.0, "fr": 0.1},
    }


@pytest.fixture
def sample_ads_reaction_params(sample_x_array) -> dict:
    """Sample reaction parameters for ADS function."""
    return {
        "function": "ads",
        "x": sample_x_array,
        "coeffs": {"h": 0.8, "z": 450.0, "w": 25.0, "ads1": 8.0, "ads2": 12.0},
        "upper_bound_coeffs": {"h": 1.0, "z": 460.0, "w": 30.0, "ads1": 15.0, "ads2": 20.0},
        "lower_bound_coeffs": {"h": 0.6, "z": 440.0, "w": 20.0, "ads1": 5.0, "ads2": 8.0},
    }
