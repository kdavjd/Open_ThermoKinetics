"""Tests for series_data module - experimental series management."""

import numpy as np
import pandas as pd
import pytest

from src.core.app_settings import OperationType
from src.core.series_data import SeriesData


class TestSeriesDataAddSeries:
    """Tests for add_series method."""

    @pytest.fixture
    def series_data(self, mock_signals):
        """Create SeriesData instance."""
        return SeriesData(signals=mock_signals)

    @pytest.fixture
    def sample_experimental_data(self):
        """Create sample experimental DataFrame."""
        temperature = np.linspace(400, 600, 50)
        return pd.DataFrame(
            {
                "temperature": temperature,
                "rate_10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
            }
        )

    def test_add_series_with_name(self, series_data, sample_experimental_data):
        """Should add series with specified name."""
        success, name = series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0],
            name="Test Series",
        )

        assert success is True
        assert name == "Test Series"
        assert "Test Series" in series_data.series

    def test_add_series_auto_name(self, series_data, sample_experimental_data):
        """Should auto-generate name if not provided."""
        success, name = series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0],
            name=None,
        )

        assert success is True
        assert name == "Series 1"

        # Add another series
        success2, name2 = series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0],
            name=None,
        )
        assert name2 == "Series 2"

    def test_add_series_duplicate_name_fails(self, series_data, sample_experimental_data):
        """Should fail to add series with duplicate name."""
        series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0],
            name="Duplicate",
        )

        success, name = series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0],
            name="Duplicate",
        )

        assert success is False
        assert name is None

    def test_add_series_creates_default_scheme(self, series_data, sample_experimental_data):
        """Should create default A→B reaction scheme."""
        series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0],
            name="Test",
        )

        series_entry = series_data.series["Test"]
        assert "reaction_scheme" in series_entry
        assert "components" in series_entry["reaction_scheme"]
        assert "reactions" in series_entry["reaction_scheme"]

    def test_add_series_stores_experimental_data(self, series_data, sample_experimental_data):
        """Should store experimental data and masses."""
        series_data.add_series(
            data=sample_experimental_data,
            experimental_masses=[1.0, 2.0],
            name="Test",
        )

        series_entry = series_data.series["Test"]
        assert "experimental_data" in series_entry
        assert series_entry["experimental_masses"] == [1.0, 2.0]


class TestSeriesDataUpdateSeries:
    """Tests for update_series method."""

    @pytest.fixture
    def series_data_with_series(self, mock_signals):
        """Create SeriesData with a test series."""
        sd = SeriesData(signals=mock_signals)
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})
        sd.add_series(data=df, experimental_masses=[1.0], name="Test")
        return sd

    def test_update_series_adds_new_field(self, series_data_with_series):
        """Should add new field to existing series."""
        series_data_with_series.update_series("Test", {"new_field": "new_value"})

        assert series_data_with_series.series["Test"]["new_field"] == "new_value"

    def test_update_series_modifies_existing_field(self, series_data_with_series):
        """Should modify existing field."""
        series_data_with_series.update_series("Test", {"experimental_masses": [2.0, 3.0]})

        assert series_data_with_series.series["Test"]["experimental_masses"] == [2.0, 3.0]

    def test_update_nonexistent_series_fails(self, series_data_with_series):
        """Should return False for non-existent series."""
        result = series_data_with_series.update_series("NonExistent", {"field": "value"})
        assert result is False

    def test_update_merges_nested_dicts(self, series_data_with_series):
        """Should merge nested dictionaries."""
        series_data_with_series.update_series(
            "Test",
            {"calculation_settings": {"maxiter": 500}},
        )

        settings = series_data_with_series.series["Test"]["calculation_settings"]
        assert "maxiter" in settings
        assert "method" in settings  # Original field preserved

    def test_update_reaction_scheme_preserves_params(self, series_data_with_series):
        """Should preserve old reaction params when updating scheme."""
        # First update to set some params
        series_data_with_series.update_series(
            "Test",
            {"reaction_scheme": {"reactions": [{"from": "A", "to": "B", "Ea": 100.0}]}},
        )

        # Second update should preserve Ea
        series_data_with_series.update_series(
            "Test",
            {"reaction_scheme": {"reactions": [{"from": "A", "to": "B", "log_A": 10.0}]}},
        )

        reactions = series_data_with_series.series["Test"]["reaction_scheme"]["reactions"]
        assert reactions[0]["Ea"] == 100.0  # Preserved
        assert reactions[0]["log_A"] == 10.0  # New value

    def test_update_replaces_non_dict_values(self, series_data_with_series):
        """Should replace non-dict values instead of merging."""
        series_data_with_series.update_series("Test", {"experimental_masses": [5.0]})
        assert series_data_with_series.series["Test"]["experimental_masses"] == [5.0]


class TestSeriesDataDeleteSeries:
    """Tests for delete_series method."""

    @pytest.fixture
    def series_data_with_series(self, mock_signals):
        """Create SeriesData with test series."""
        sd = SeriesData(signals=mock_signals)
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})
        sd.add_series(data=df, experimental_masses=[1.0], name="ToDelete")
        return sd

    def test_delete_existing_series(self, series_data_with_series):
        """Should delete existing series."""
        result = series_data_with_series.delete_series("ToDelete")
        assert result is True
        assert "ToDelete" not in series_data_with_series.series

    def test_delete_nonexistent_series(self, series_data_with_series):
        """Should return False for non-existent series."""
        result = series_data_with_series.delete_series("NonExistent")
        assert result is False


class TestSeriesDataRenameSeries:
    """Tests for rename_series method."""

    @pytest.fixture
    def series_data_with_series(self, mock_signals):
        """Create SeriesData with test series."""
        sd = SeriesData(signals=mock_signals)
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})
        sd.add_series(data=df, experimental_masses=[1.0], name="OldName")
        return sd

    def test_rename_series_success(self, series_data_with_series):
        """Should rename existing series."""
        result = series_data_with_series.rename_series("OldName", "NewName")
        assert result is True
        assert "NewName" in series_data_with_series.series
        assert "OldName" not in series_data_with_series.series

    def test_rename_nonexistent_series(self, series_data_with_series):
        """Should return False for non-existent old name."""
        result = series_data_with_series.rename_series("NonExistent", "NewName")
        assert result is False

    def test_rename_to_existing_name_fails(self, series_data_with_series):
        """Should fail if new name already exists."""
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})
        series_data_with_series.add_series(data=df, experimental_masses=[1.0], name="Existing")

        result = series_data_with_series.rename_series("OldName", "Existing")
        assert result is False


class TestSeriesDataGetSeries:
    """Tests for get_series method."""

    @pytest.fixture
    def series_data_with_series(self, mock_signals):
        """Create SeriesData with test series."""
        sd = SeriesData(signals=mock_signals)
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})
        sd.add_series(data=df, experimental_masses=[1.0], name="TestSeries")
        return sd

    def test_get_series_experimental(self, series_data_with_series):
        """Should get experimental data."""
        result = series_data_with_series.get_series("TestSeries", info_type="experimental")
        assert isinstance(result, pd.DataFrame)
        assert "temperature" in result.columns

    def test_get_series_scheme(self, series_data_with_series):
        """Should get reaction scheme."""
        result = series_data_with_series.get_series("TestSeries", info_type="scheme")
        assert "reactions" in result

    def test_get_series_all(self, series_data_with_series):
        """Should get all series data."""
        result = series_data_with_series.get_series("TestSeries", info_type="all")
        assert "experimental_data" in result
        assert "reaction_scheme" in result

    def test_get_nonexistent_series_returns_none(self, series_data_with_series):
        """Should return None for non-existent series."""
        result = series_data_with_series.get_series("NonExistent")
        assert result is None

    def test_get_all_series(self, series_data_with_series):
        """Should return copy of all series."""
        result = series_data_with_series.get_all_series()
        assert "TestSeries" in result


class TestSeriesDataProcessRequest:
    """Tests for process_request signal handling."""

    @pytest.fixture
    def series_data(self, mock_signals):
        """Create SeriesData instance."""
        sd = SeriesData(signals=mock_signals)
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})
        sd.add_series(data=df, experimental_masses=[1.0], name="Test")
        return sd

    def test_process_get_all_series_request(self, series_data, mock_signals):
        """Should handle GET_ALL_SERIES operation."""
        params = {
            "operation": OperationType.GET_ALL_SERIES,
            "actor": "test_actor",
            "request_id": "req-1",
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert "Test" in response["data"]

    def test_process_delete_series_request(self, series_data, mock_signals):
        """Should handle DELETE_SERIES operation."""
        params = {
            "operation": OperationType.DELETE_SERIES,
            "actor": "test_actor",
            "request_id": "req-2",
            "series_name": "Test",
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True
        assert "Test" not in series_data.series

    def test_process_get_series_request(self, series_data, mock_signals):
        """Should handle GET_SERIES operation."""
        params = {
            "operation": OperationType.GET_SERIES,
            "actor": "test_actor",
            "request_id": "req-3",
            "series_name": "Test",
            "info_type": "experimental",
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert isinstance(response["data"], pd.DataFrame)

    def test_process_add_series_request(self, mock_signals):
        """Should handle ADD_NEW_SERIES operation."""
        sd = SeriesData(signals=mock_signals)
        df = pd.DataFrame({"temperature": np.linspace(400, 600, 50), "rate_10": np.ones(50)})

        params = {
            "operation": OperationType.ADD_NEW_SERIES,
            "actor": "test_actor",
            "request_id": "req-4",
            "data": df,
            "experimental_masses": [1.0],
            "name": "NewSeries",
        }

        sd.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True
        assert "NewSeries" in sd.series

    def test_process_rename_series_request(self, series_data, mock_signals):
        """Should handle RENAME_SERIES operation."""
        params = {
            "operation": OperationType.RENAME_SERIES,
            "actor": "test_actor",
            "request_id": "req-5",
            "old_name": "Test",
            "new_name": "Renamed",
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True
        assert "Renamed" in series_data.series
        assert "Test" not in series_data.series

    def test_process_update_series_request(self, series_data, mock_signals):
        """Should handle UPDATE_SERIES operation."""
        params = {
            "operation": OperationType.UPDATE_SERIES,
            "actor": "test_actor",
            "request_id": "req-6",
            "series_name": "Test",
            "update_data": {"new_field": "new_value"},
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True
        assert series_data.series["Test"]["new_field"] == "new_value"

    def test_process_scheme_change_request(self, series_data, mock_signals):
        """Should handle SCHEME_CHANGE operation."""
        new_scheme = {
            "components": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            "reactions": [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}],
        }

        params = {
            "operation": OperationType.SCHEME_CHANGE,
            "actor": "test_actor",
            "request_id": "req-7",
            "series_name": "Test",
            "reaction_scheme": new_scheme,
            "calculation_settings": {"maxiter": 500},
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True
        assert len(series_data.series["Test"]["reaction_scheme"]["components"]) == 3

    def test_process_get_series_value_request(self, series_data, mock_signals):
        """Should handle GET_SERIES_VALUE operation."""
        params = {
            "operation": OperationType.GET_SERIES_VALUE,
            "actor": "test_actor",
            "request_id": "req-8",
            "keys": ["Test", "reaction_scheme"],
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert "reactions" in response["data"]

    def test_process_get_series_value_invalid_keys(self, series_data, mock_signals):
        """Should handle GET_SERIES_VALUE with invalid keys."""
        params = {
            "operation": OperationType.GET_SERIES_VALUE,
            "actor": "test_actor",
            "request_id": "req-9",
            "keys": "not_a_list",  # Invalid
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] == {}

    def test_process_unknown_operation(self, series_data, mock_signals):
        """Should handle unknown operation gracefully."""
        params = {
            "operation": OperationType.LOAD_FILE,  # Not handled by SeriesData
            "actor": "test_actor",
            "request_id": "req-10",
        }

        series_data.process_request(params)

        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is None

    def test_get_series_unknown_info_type(self, series_data):
        """Should return all data for unknown info_type."""
        result = series_data.get_series("Test", info_type="unknown_type")
        assert "experimental_data" in result  # Returns all by default
