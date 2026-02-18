"""Tests for calculation_data module - hierarchical data storage for reactions."""

import json

import numpy as np
import pytest

from src.core.app_settings import OperationType
from src.core.calculation_data import CalculationsData


class TestCalculationsDataGetSetValue:
    """Tests for get_value and set_value hierarchical operations."""

    @pytest.fixture
    def calc_data(self, mock_signals):
        """Create CalculationsData instance with mock signals."""
        return CalculationsData(signals=mock_signals)

    def test_set_and_get_simple_value(self, calc_data):
        """Should set and retrieve a simple value."""
        calc_data.set_value(["file_name"], "test.csv")
        assert calc_data.get_value(["file_name"]) == "test.csv"

    def test_set_and_get_nested_value(self, calc_data):
        """Should set and retrieve nested values."""
        calc_data.set_value(["file_name", "reaction_0", "coeffs", "h"], 1.0)
        result = calc_data.get_value(["file_name", "reaction_0", "coeffs"])
        assert result == {"h": 1.0}

    def test_get_nonexistent_path_returns_empty_dict(self, calc_data):
        """Should return empty dict for non-existent path."""
        result = calc_data.get_value(["nonexistent", "path"])
        assert result == {}

    def test_set_multiple_nested_values(self, calc_data):
        """Should handle multiple nested set operations."""
        calc_data.set_value(["file", "reaction_0", "h"], 1.0)
        calc_data.set_value(["file", "reaction_0", "z"], 450.0)
        calc_data.set_value(["file", "reaction_1", "h"], 0.8)

        assert calc_data.get_value(["file", "reaction_0"]) == {"h": 1.0, "z": 450.0}
        assert calc_data.get_value(["file", "reaction_1"]) == {"h": 0.8}

    def test_set_value_empty_keys_does_nothing(self, calc_data):
        """Empty keys list should not modify data."""
        calc_data.set_value([], "value")
        assert calc_data.get_value([]) == {}


class TestCalculationsDataExists:
    """Tests for exists method."""

    @pytest.fixture
    def calc_data(self, mock_signals):
        """Create CalculationsData instance."""
        cd = CalculationsData(signals=mock_signals)
        cd.set_value(["file", "reaction_0", "h"], 1.0)
        return cd

    def test_exists_returns_true_for_existing_path(self, calc_data):
        """Should return True for existing path."""
        assert calc_data.exists(["file"]) is True
        assert calc_data.exists(["file", "reaction_0"]) is True
        assert calc_data.exists(["file", "reaction_0", "h"]) is True

    def test_exists_returns_false_for_nonexistent_path(self, calc_data):
        """Should return False for non-existent path."""
        assert calc_data.exists(["nonexistent"]) is False
        assert calc_data.exists(["file", "nonexistent"]) is False


class TestCalculationsDataRemoveValue:
    """Tests for remove_value method."""

    @pytest.fixture
    def calc_data(self, mock_signals):
        """Create CalculationsData with test data."""
        cd = CalculationsData(signals=mock_signals)
        cd.set_value(["file", "reaction_0", "h"], 1.0)
        cd.set_value(["file", "reaction_0", "z"], 450.0)
        cd.set_value(["file", "reaction_1", "h"], 0.8)
        return cd

    def test_remove_existing_value(self, calc_data):
        """Should remove existing value."""
        calc_data.remove_value(["file", "reaction_0", "h"])
        assert calc_data.exists(["file", "reaction_0", "h"]) is False
        assert calc_data.exists(["file", "reaction_0", "z"]) is True

    def test_remove_nested_dict(self, calc_data):
        """Should remove entire nested dict."""
        calc_data.remove_value(["file", "reaction_0"])
        assert calc_data.exists(["file", "reaction_0"]) is False
        assert calc_data.exists(["file", "reaction_1"]) is True

    def test_remove_nonexistent_does_not_raise(self, calc_data):
        """Should not raise for non-existent path."""
        calc_data.remove_value(["nonexistent", "path"])  # Should not raise

    def test_remove_empty_keys_does_nothing(self, calc_data):
        """Empty keys list should do nothing."""
        calc_data.remove_value([])
        assert calc_data.exists(["file"]) is True


class TestCalculationsDataLoadReactions:
    """Tests for load_reactions JSON import."""

    @pytest.fixture
    def calc_data(self, mock_signals):
        """Create CalculationsData instance."""
        return CalculationsData(signals=mock_signals)

    @pytest.fixture
    def sample_json_file(self, tmp_path):
        """Create sample JSON file with reaction data."""
        data = {
            "reaction_0": {
                "function": "gauss",
                "x": [300, 350, 400, 450, 500],
                "coeffs": {"h": 1.0, "z": 450.0, "w": 30.0},
            }
        }
        json_path = tmp_path / "reactions.json"
        with open(json_path, "w") as f:
            json.dump(data, f)
        return json_path

    def test_load_reactions_success(self, calc_data, sample_json_file):
        """Should load reactions from JSON file."""
        result = calc_data.load_reactions(str(sample_json_file), "test_file")

        assert "reaction_0" in result
        assert result["reaction_0"]["function"] == "gauss"
        assert calc_data.exists(["test_file", "reaction_0"])

    def test_load_reactions_converts_x_to_numpy(self, calc_data, sample_json_file):
        """Should convert 'x' field to numpy array."""
        result = calc_data.load_reactions(str(sample_json_file), "test_file")

        assert isinstance(result["reaction_0"]["x"], np.ndarray)
        assert len(result["reaction_0"]["x"]) == 5

    def test_load_reactions_nonexistent_file(self, calc_data):
        """Should return empty dict for non-existent file."""
        result = calc_data.load_reactions("/nonexistent/file.json", "test_file")
        assert result == {}


class TestCalculationsDataProcessRequest:
    """Tests for process_request signal handling."""

    @pytest.fixture
    def calc_data(self, mock_signals):
        """Create CalculationsData instance."""
        return CalculationsData(signals=mock_signals)

    def test_process_get_value_request(self, calc_data, mock_signals):
        """Should handle GET_VALUE operation."""
        calc_data.set_value(["test_key"], "test_value")

        params = {
            "operation": OperationType.GET_VALUE,
            "actor": "test_actor",
            "request_id": "req-1",
            "path_keys": ["test_key"],
        }

        calc_data.process_request(params)

        # Check that response_signal.emit was called
        mock_signals.response_signal.emit.assert_called_once()
        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] == "test_value"

    def test_process_set_value_request(self, calc_data, mock_signals):
        """Should handle SET_VALUE operation."""
        params = {
            "operation": OperationType.SET_VALUE,
            "actor": "test_actor",
            "request_id": "req-2",
            "path_keys": ["new_key"],
            "value": "new_value",
        }

        calc_data.process_request(params)

        assert calc_data.get_value(["new_key"]) == "new_value"
        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True

    def test_process_get_full_data_request(self, calc_data, mock_signals):
        """Should handle GET_FULL_DATA operation."""
        calc_data.set_value(["key1"], "value1")

        params = {
            "operation": OperationType.GET_FULL_DATA,
            "actor": "test_actor",
            "request_id": "req-3",
        }

        calc_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert "key1" in response["data"]

    def test_process_invalid_path_keys(self, calc_data, mock_signals):
        """Should handle invalid path_keys gracefully."""
        params = {
            "operation": OperationType.GET_VALUE,
            "actor": "test_actor",
            "request_id": "req-4",
            "path_keys": "not_a_list",  # Invalid
        }

        calc_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] == {}
