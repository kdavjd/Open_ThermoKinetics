"""Tests for file_data module - CSV/TXT file loading and data management."""

import os

import pandas as pd
import pytest

from src.core.app_settings import OperationType
from src.core.file_data import FileData


@pytest.fixture
def file_data(mock_signals):
    """Create FileData instance with mocked signals."""
    return FileData(mock_signals)


class TestFileDataInit:
    """Tests for FileData initialization."""

    def test_init_attributes(self, file_data):
        """Should initialize with empty data structures."""
        assert file_data.data is None
        assert file_data.original_data == {}
        assert file_data.dataframe_copies == {}
        assert file_data.operations_history == {}
        assert file_data.loaded_files == set()


class TestLoadFile:
    """Tests for file loading functionality."""

    def test_load_csv_file(self, file_data, sample_csv_path):
        """Should successfully load CSV file with experimental data."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)

        assert file_data.data is not None
        assert "temperature" in file_data.data.columns

    def test_prevent_duplicate_loading(self, file_data, sample_csv_path):
        """Should prevent loading same file twice."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        initial_loaded = len(file_data.loaded_files)

        file_data.load_file(file_info)  # Try to load again

        assert len(file_data.loaded_files) == initial_loaded

    def test_loaded_file_added_to_set(self, file_data, sample_csv_path):
        """Should add loaded file path to loaded_files set."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)

        assert str(sample_csv_path) in file_data.loaded_files

    def test_original_data_stored(self, file_data, sample_csv_path):
        """Should store original data copy by filename."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)

        file_basename = os.path.basename(sample_csv_path)
        assert file_basename in file_data.original_data
        assert isinstance(file_data.original_data[file_basename], pd.DataFrame)

    def test_dataframe_copy_created(self, file_data, sample_csv_path):
        """Should create working copy of data."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)

        file_basename = os.path.basename(sample_csv_path)
        assert file_basename in file_data.dataframe_copies


class TestOperationsHistory:
    """Tests for operations history tracking."""

    def test_log_operation(self, file_data):
        """Should log operation to history."""
        file_data.operations_history["test_file"] = []
        params = {"file_name": "test_file", "operation": "test_op"}

        file_data.log_operation(params)

        assert len(file_data.operations_history["test_file"]) == 1

    def test_check_operation_executed_true(self, file_data):
        """Should return True when operation was executed."""
        file_data.operations_history["test_file"] = [{"params": {"operation": OperationType.TO_A_T}}]

        result = file_data.check_operation_executed("test_file", OperationType.TO_A_T)

        assert result is True

    def test_check_operation_executed_false(self, file_data):
        """Should return False when operation was not executed."""
        result = file_data.check_operation_executed("test_file", OperationType.TO_A_T)

        assert result is False


class TestResetDataFrame:
    """Tests for dataframe reset functionality."""

    def test_reset_dataframe_copy(self, file_data, sample_csv_path):
        """Should reset dataframe copy to original state."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        file_basename = os.path.basename(sample_csv_path)

        # Modify the copy
        original = file_data.dataframe_copies[file_basename].copy()
        file_data.dataframe_copies[file_basename].iloc[0, 0] = 999

        # Reset
        file_data.reset_dataframe_copy(file_basename)

        pd.testing.assert_frame_equal(file_data.dataframe_copies[file_basename], original)

    def test_reset_clears_operations_history(self, file_data, sample_csv_path):
        """Should clear operations history on reset."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        file_basename = os.path.basename(sample_csv_path)

        file_data.operations_history[file_basename] = [{"params": {"operation": "test"}}]
        file_data.reset_dataframe_copy(file_basename)

        assert file_basename not in file_data.operations_history


class TestModifyData:
    """Tests for data modification functionality."""

    def test_modify_data_applies_function(self, file_data, sample_csv_path):
        """Should apply function to all columns except temperature."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        file_basename = os.path.basename(sample_csv_path)

        # Multiply all columns by 2
        def multiply_by_2(series):
            return series * 2

        params = {"file_name": file_basename}
        original = file_data.dataframe_copies[file_basename].copy()

        file_data.modify_data(multiply_by_2, params)

        # Temperature should be unchanged
        pd.testing.assert_series_equal(
            file_data.dataframe_copies[file_basename]["temperature"], original["temperature"]
        )

    def test_modify_data_logs_operation(self, file_data, sample_csv_path):
        """Should log modification to operations history."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        file_basename = os.path.basename(sample_csv_path)

        def identity(x):
            return x

        params = {"file_name": file_basename, "operation": "test_modify"}

        file_data.modify_data(identity, params)

        assert file_basename in file_data.operations_history

    def test_modify_data_nonexistent_file(self, file_data):
        """Should handle missing file gracefully."""

        def identity(x):
            return x

        params = {"file_name": "nonexistent_file"}

        file_data.modify_data(identity, params)  # Should not raise

        assert "nonexistent_file" not in file_data.dataframe_copies


class TestProcessRequest:
    """Tests for request processing dispatcher."""

    def test_process_request_get_df_data(self, file_data, sample_csv_path, mock_signals):
        """Should return dataframe copy for GET_DF_DATA operation."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        file_basename = os.path.basename(sample_csv_path)

        params = {
            "operation": OperationType.GET_DF_DATA,
            "file_name": file_basename,
            "actor": "test_actor",
            "target": "file_data",
        }

        file_data.process_request(params)

        assert "data" in params
        assert isinstance(params["data"], pd.DataFrame)

    def test_process_request_get_all_data(self, file_data, sample_csv_path, mock_signals):
        """Should return all dataframe copies for GET_ALL_DATA operation."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)

        params = {
            "operation": OperationType.GET_ALL_DATA,
            "file_name": "any",
            "actor": "test_actor",
            "target": "file_data",
        }

        file_data.process_request(params)

        assert "data" in params
        assert isinstance(params["data"], dict)

    def test_process_request_resets_swaps_actor_target(self, file_data, sample_csv_path, mock_signals):
        """Should swap actor and target in response."""
        file_info = (str(sample_csv_path), ",", 0, None)
        file_data.load_file(file_info)
        file_basename = os.path.basename(sample_csv_path)

        params = {
            "operation": OperationType.GET_DF_DATA,
            "file_name": file_basename,
            "actor": "test_actor",
            "target": "file_data",
        }

        file_data.process_request(params)

        assert params["actor"] == "file_data"
        assert params["target"] == "test_actor"
