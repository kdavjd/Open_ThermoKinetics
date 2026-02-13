"""Tests for file_operations module - data transformation functions."""

import numpy as np
import pandas as pd
import pytest

from src.core.app_settings import OperationType
from src.core.file_operations import ActiveFileOperations


@pytest.fixture
def file_operations(mock_signals):
    """Create ActiveFileOperations instance with mocked signals."""
    return ActiveFileOperations(mock_signals)


class TestDiffFunction:
    """Tests for derivative calculation (DTG)."""

    def test_diff_function_basic(self, file_operations):
        """Should calculate differences between consecutive elements."""
        series = pd.Series([1.0, 2.0, 4.0, 7.0])
        result = file_operations.diff_function(series)

        expected = pd.Series([np.nan, 1.0, 2.0, 3.0])
        pd.testing.assert_series_equal(result, expected)

    def test_diff_function_constant(self, file_operations):
        """Should return zeros for constant series."""
        series = pd.Series([5.0, 5.0, 5.0, 5.0])
        result = file_operations.diff_function(series)

        expected = pd.Series([np.nan, 0.0, 0.0, 0.0])
        pd.testing.assert_series_equal(result, expected)

    def test_diff_function_single_element(self, file_operations):
        """Should handle single element series."""
        series = pd.Series([5.0])
        result = file_operations.diff_function(series)

        assert len(result) == 1
        assert pd.isna(result.iloc[0])

    def test_diff_function_preserves_index(self, file_operations):
        """Should preserve series index."""
        series = pd.Series([1.0, 3.0, 6.0], index=["a", "b", "c"])
        result = file_operations.diff_function(series)

        assert list(result.index) == ["a", "b", "c"]


class TestToATFunction:
    """Tests for conversion to α(t) function."""

    def test_to_a_t_basic(self, file_operations):
        """Should convert mass loss to conversion α(t)."""
        # Linear mass loss: 100 -> 80 over 5 points
        series = pd.Series([100.0, 95.0, 90.0, 85.0, 80.0])
        result = file_operations.to_a_t_function(series)

        # α = (m0 - m) / (m0 - mf)
        # α at start = (100 - 100) / 20 = 0
        # α at end = (100 - 80) / 20 = 1
        assert result.iloc[0] == pytest.approx(0.0)
        assert result.iloc[-1] == pytest.approx(1.0)

    def test_to_a_t_linear_progression(self, file_operations):
        """Should produce linear α progression for linear mass loss."""
        series = pd.Series([100.0, 90.0, 80.0, 70.0, 60.0])
        result = file_operations.to_a_t_function(series)

        # Each step should increase α by 0.25
        expected = pd.Series([0.0, 0.25, 0.5, 0.75, 1.0])
        pd.testing.assert_series_equal(result, expected)

    def test_to_a_t_equal_masses(self, file_operations):
        """Should return zeros when m0 equals mf."""
        series = pd.Series([50.0, 50.0, 50.0, 50.0])
        result = file_operations.to_a_t_function(series)

        # Function returns Series with int dtype for zeros
        assert len(result) == 4
        assert (result == 0).all()

    def test_to_a_t_empty_series(self, file_operations):
        """Should return empty series unchanged."""
        series = pd.Series([], dtype=float)
        result = file_operations.to_a_t_function(series)

        assert len(result) == 0

    def test_to_a_t_increasing_mass(self, file_operations):
        """Should handle mass gain (increasing series)."""
        # Mass gain: 80 -> 100
        series = pd.Series([80.0, 85.0, 90.0, 95.0, 100.0])
        result = file_operations.to_a_t_function(series)

        # α = (m0 - m) / (m0 - mf) = (80 - m) / (80 - 100) = (80 - m) / -20
        # α at start = 0 / -20 = 0
        # α at end = -20 / -20 = 1
        assert result.iloc[0] == pytest.approx(0.0)
        assert result.iloc[-1] == pytest.approx(1.0)

    def test_to_a_t_preserves_index(self, file_operations):
        """Should preserve series index."""
        series = pd.Series([100.0, 90.0, 80.0], index=[0, 5, 10])
        result = file_operations.to_a_t_function(series)

        assert list(result.index) == [0, 5, 10]


class TestProcessRequest:
    """Tests for request processing dispatcher."""

    def test_process_request_to_dtg(self, file_operations, mock_signals):
        """Should return diff_function for TO_DTG operation."""
        params = {
            "operation": OperationType.TO_DTG,
            "actor": "test_actor",
            "target": "active_file_operations",
        }

        file_operations.process_request(params)

        # Check that emit was called with the response containing data
        mock_signals.response_signal.emit.assert_called_once()
        emitted_response = mock_signals.response_signal.emit.call_args[0][0]
        assert "data" in emitted_response
        assert callable(emitted_response["data"])

    def test_process_request_to_a_t(self, file_operations, mock_signals):
        """Should return to_a_t_function for TO_A_T operation."""
        params = {
            "operation": OperationType.TO_A_T,
            "actor": "test_actor",
            "target": "active_file_operations",
        }

        file_operations.process_request(params)

        # Check that emit was called with the response containing data
        mock_signals.response_signal.emit.assert_called_once()
        emitted_response = mock_signals.response_signal.emit.call_args[0][0]
        assert "data" in emitted_response
        assert callable(emitted_response["data"])

    def test_process_request_swaps_actor_target(self, file_operations, mock_signals):
        """Should swap actor and target in response."""
        params = {
            "operation": OperationType.TO_A_T,
            "actor": "test_actor",
            "target": "active_file_operations",
        }

        file_operations.process_request(params)

        emitted_response = mock_signals.response_signal.emit.call_args[0][0]
        assert emitted_response["actor"] == "active_file_operations"
        assert emitted_response["target"] == "test_actor"

    def test_process_request_emits_response(self, file_operations, mock_signals):
        """Should emit response signal."""
        params = {
            "operation": OperationType.TO_A_T,
            "actor": "test_actor",
            "target": "active_file_operations",
        }

        file_operations.process_request(params)

        mock_signals.response_signal.emit.assert_called_once()
