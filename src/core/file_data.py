import enum
import os
from functools import wraps
from io import StringIO

import chardet
import pandas as pd
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


def detect_encoding(func):
    """Decorator to automatically detect file encoding using chardet."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with open(self.file_path, "rb") as f:
            result = chardet.detect(f.read(100_000))
        kwargs["encoding"] = result["encoding"]
        return func(self, *args, **kwargs)

    return wrapper


def detect_decimal(func):
    """Decorator to automatically detect decimal separator from file content."""

    @wraps(func)
    def wrapper(self, **kwargs):
        encoding = kwargs.get("encoding", "utf-8")
        with open(self.file_path, "r", encoding=encoding) as f:
            sample_lines = [next(f) for _ in range(100)]
        sample_text = "".join(sample_lines)

        decimal_sep = "," if sample_text.count(",") > sample_text.count(".") else "."
        kwargs["decimal"] = decimal_sep
        return func(self, **kwargs)

    return wrapper


class FileData(BaseSlots):
    """
    Manages experimental data files with loading, modification tracking, and persistence.

    Provides functionality to load CSV/TXT files, maintain operation history,
    and manage multiple dataframe copies for non-destructive data transformations.
    Supports automatic encoding/decimal detection and experimental data preprocessing.

    Attributes
    ----------
    data : pd.DataFrame or None
        Currently loaded DataFrame from file.
    original_data : dict[str, pd.DataFrame]
        Immutable original dataframes keyed by filename.
    dataframe_copies : dict[str, pd.DataFrame]
        Working copies for modifications without altering originals.
    operations_history : dict[str, list]
        Complete modification history per file for traceability.
    loaded_files : set[str]
        Loaded file paths to prevent duplicate loading.
    """

    data_loaded_signal = pyqtSignal(pd.DataFrame)

    def __init__(self, signals):
        super().__init__(actor_name="file_data", signals=signals)
        self.data = None
        self.original_data = {}
        self.dataframe_copies = {}
        self.file_path = None
        self.delimiter = ","
        self.skip_rows = 0
        self.columns_names = None
        self.operations_history = {}
        self.loaded_files = set()

    def log_operation(self, params: dict):
        """Log operation to history for traceability."""
        file_name = params.pop("file_name")
        if file_name not in self.operations_history:
            self.operations_history[file_name] = []
        self.operations_history[file_name].append({"params": params})
        logger.debug(f"Updated operations history: {self.operations_history}")

    def check_operation_executed(self, file_name: str, operation: enum) -> bool:
        """Check if specific operation was already executed on file."""
        if file_name in self.operations_history:
            for operation_record in self.operations_history[file_name]:
                if operation_record["params"]["operation"] == operation:
                    return True
        return False

    @pyqtSlot(tuple)
    def load_file(self, file_info):
        """
        Load experimental data file with automatic format detection and validation.

        Supports CSV and TXT formats with configurable delimiters, column names,
        and skip rows. Prevents duplicate loading and maintains original copies.
        Automatically detects encoding and decimal separators for robust parsing.

        Parameters
        ----------
        file_info : tuple
            (file_path, delimiter, skip_rows, columns_names) configuration tuple.
        """
        self.file_path, self.delimiter, self.skip_rows, columns_names = file_info

        if self.file_path in self.loaded_files:
            console.log(f"\n\nThe file '{self.file_path}' is already loaded.")
            return

        if columns_names:
            column_delimiter = "," if "," in columns_names else " "
            self.columns_names = [name.strip() for name in columns_names.split(column_delimiter)]
            logger.debug(
                "Loading file: path=%s, delimiter=%s, skip_rows=%s, columns_names=%s",
                self.file_path,
                self.delimiter,
                self.skip_rows,
                columns_names,
            )
        else:
            logger.debug(
                "Loading file: path=%s, delimiter=%s, skip_rows=%s, columns_names=none",
                self.file_path,
                self.delimiter,
                self.skip_rows,
            )

        _, file_extension = os.path.splitext(self.file_path)
        console.log(f"\n\nAttempting to load the file: {self.file_path}")

        if file_extension == ".csv":
            self.load_csv()
        elif file_extension == ".txt":
            self.load_txt()
        else:
            console.log(f"\n\nFile extension '{file_extension}' is not supported.")

        self.loaded_files.add(self.file_path)
        console.log(f"\n\nFile '{self.file_path}' has been successfully loaded.")

    @detect_encoding
    @detect_decimal
    def load_csv(self, **kwargs):
        """Load CSV file with flexible parsing and error handling."""
        try:
            self.data = pd.read_csv(
                self.file_path,
                sep=self.delimiter,
                engine="python",
                on_bad_lines="skip",
                skiprows=self.skip_rows,
                header=0,
                **kwargs,
            )
            self._fetch_data()
        except Exception as e:
            logger.error(f"Error while loading CSV file: {e}")
            console.log("\n\nError: Unable to load the CSV file.")

    @detect_encoding
    @detect_decimal
    def load_txt(self, **kwargs):
        """Load TXT file with configurable delimiter and encoding detection."""
        try:
            self.data = pd.read_table(
                self.file_path,
                sep=self.delimiter,
                skiprows=self.skip_rows,
                header=0,
                **kwargs,
            )
            self._fetch_data()
        except Exception as e:
            logger.error(f"Error while loading TXT file: {e}")
            console.log("\n\nError: Unable to load the TXT file.")

    def _fetch_data(self):
        """Finalize data loading with column processing and signal emission."""
        file_basename = os.path.basename(self.file_path)

        if self.columns_names is not None:
            if len(self.columns_names) != len(self.data.columns):
                logger.warning("The number of user-provided column names does not match the dataset columns.")
            self.data = self.data.apply(pd.to_numeric, errors="coerce")
            self.data.columns = [name.strip() for name in self.columns_names]
        else:
            logger.debug("No custom column names provided; using file's header row as column names.")

        self.original_data[file_basename] = self.data.copy()
        self.dataframe_copies[file_basename] = self.data.copy()

        buffer = StringIO()
        self.dataframe_copies[file_basename].info(buf=buffer)
        file_info = buffer.getvalue()
        console.log(f"\n\nFile loaded:\n{file_info}")

        logger.debug(f"dataframe_copies keys: {self.dataframe_copies.keys()}")
        self.data_loaded_signal.emit(self.data)

    @pyqtSlot(str)
    def plot_dataframe_copy(self, key):
        """Request plotting of dataframe copy by key."""
        if key in self.dataframe_copies:
            _ = self.handle_request_cycle("main_window", OperationType.PLOT_DF, df=self.dataframe_copies[key])
            console.log(f"\n\nPlotting the DataFrame with key: {key}")
        else:
            logger.error(f"Key '{key}' not found in dataframe_copies.")

    def reset_dataframe_copy(self, key):
        """Reset dataframe copy to original state and clear operation history."""
        if key in self.original_data:
            self.dataframe_copies[key] = self.original_data[key].copy()
            if key in self.operations_history:
                del self.operations_history[key]
            logger.debug(f"Reset data for key '{key}' and cleared operations history.")
            console.log(f"\n\nData reset for '{key}'. Original state restored.")

    def modify_data(self, func, params):
        """
        Apply transformation function to experimental data with operation logging.

        Modifies all numeric columns except 'temperature', preserving original data
        integrity. Logs operations for traceability and supports chained transformations
        like smoothing, background subtraction, and derivative calculations.

        Parameters
        ----------
        func : callable
            Transformation function applied to each data column.
        params : dict
            Operation parameters including file_name for tracking.
        """
        file_name = params.get("file_name")
        if not callable(func):
            logger.error("The provided 'func' is not callable.")
            console.log("\n\nError: Provided function is not callable.")
            return

        if file_name not in self.dataframe_copies:
            logger.error(f"Key '{file_name}' not found in dataframe_copies.")
            console.log("\n\nError: Cannot modify data as the file was not found in memory.")
            return

        try:
            dataframe = self.dataframe_copies[file_name]
            for column in dataframe.columns:
                if column != "temperature":
                    dataframe[column] = func(dataframe[column])

            self.log_operation(params)
            logger.info("Data has been successfully modified.")

        except Exception as e:
            logger.error(f"Error modifying data for file '{file_name}': {e}")

    def process_request(self, params: dict):  # noqa: C901
        """
        Central request dispatcher for file operations and data access.

        Handles loading, modification, reset, and data retrieval operations.
        Maintains operation history and prevents duplicate transformations.
        Supports LOAD_FILE, GET_DF_DATA, RESET_FILE_DATA, and differential operations.

        Parameters
        ----------
        params : dict
            Request containing operation type, file_name, and optional function/parameters.
        """
        operation = params.get("operation")
        file_name = params.get("file_name")
        func = params.get("function")
        actor = params.get("actor")

        logger.debug(f"{self.actor_name} processing request '{operation}' from '{actor}'")

        if not file_name:
            logger.error("No 'file_name' specified in the request.")
            console.log("\n\nError: 'file_name' must be specified for the requested operation.")
            return

        if operation == OperationType.TO_A_T:
            if not self.check_operation_executed(file_name, OperationType.TO_A_T):
                self.modify_data(func, params)
            else:
                console.log("\nThe data has already been transformed to α(t).")
            params["data"] = True

        elif operation == OperationType.TO_DTG:
            if not self.check_operation_executed(file_name, OperationType.TO_A_T):
                console.log("\nBefore transforming to DTG, you need to transform to α(t).")
                params["data"] = True
                return
            if not self.check_operation_executed(file_name, OperationType.TO_DTG):
                self.modify_data(func, params)
            else:
                console.log("\n\nThe data has already been transformed (differential operation).")
            params["data"] = True

        elif operation == OperationType.CHECK_OPERATION:
            checked_operation: OperationType = params.get("checked_operation")
            if checked_operation is None or not isinstance(checked_operation, OperationType):
                logger.error("Invalid or missing 'checked_operation'.")
                return
            params["data"] = self.check_operation_executed(file_name, checked_operation)

        elif operation == OperationType.GET_DF_DATA:
            params["data"] = self.dataframe_copies.get(file_name)
            if params["data"] is None:
                console.log(f"\n\nNo data found for file '{file_name}'.")

        elif operation == OperationType.GET_ALL_DATA:
            params["data"] = self.dataframe_copies

        elif operation == OperationType.RESET_FILE_DATA:
            self.reset_dataframe_copy(file_name)
            params["data"] = True

        elif operation == OperationType.LOAD_FILE:
            self.load_file(file_name)
            params["data"] = True

        else:
            console.log(f"\n\nUnknown operation '{operation}'. No action taken.")
            return

        params["target"], params["actor"] = params.get("actor"), params.get("target")

        self.signals.response_signal.emit(params)
