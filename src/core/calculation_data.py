import json
from functools import reduce
from typing import Any, Dict, List

import numpy as np
from PyQt6.QtCore import pyqtSignal

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class CalculationsData(BaseSlots):
    """Central data storage for reaction configurations and parameters.

    Manages hierarchical storage of reaction data using path_keys system for nested access.
    Provides CRUD operations, import/export functionality, and automatic persistence.
    Used extensively for deconvolution parameters, function coefficients, and optimization bounds.
    """

    dataChanged = pyqtSignal(dict)

    def __init__(self, signals):
        super().__init__(actor_name="calculations_data", signals=signals)
        self._data: Dict[str, Any] = {}
        self._filename: str = ""

    def load_reactions(self, load_file_name: str, file_name: str) -> Dict[str, Any]:
        """Load and import reaction configurations from JSON file.

        Automatically converts serialized numpy arrays back to proper format and stores
        under the specified file_name key. Used for importing pre-configured reactions
        with all parameters, bounds, and function types preserved.

        Args:
            load_file_name (str): Path to the JSON file containing reaction data.
            file_name (str): Key name under which data will be stored in the hierarchy.

        Returns:
            Dict[str, Any]: The loaded reaction data if successful, otherwise empty dict.
        """
        try:
            with open(load_file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

            for reaction_key, reaction_data in data.items():
                if "x" in reaction_data:
                    reaction_data["x"] = np.array(reaction_data["x"])

            self.set_value([file_name], data)
            console.log(f"Data successfully imported from file:\n\n{load_file_name}")
            return data
        except IOError as e:
            logger.error(f"{e}")
            return {}

    def save_data(self) -> None:
        """Save current data to JSON file."""
        try:
            with open(self._filename, "w") as file:
                json.dump(self._data, file, indent=4)
        except IOError as e:
            logger.error(f"{e}")

    def get_value(self, keys: List[str]) -> Dict[str, Any]:
        """Navigate nested dictionary using path_keys system.

        Core method for hierarchical data access used throughout the application.
        Supports path structures like ['file_name', 'reaction_0', 'coeffs', 'h']
        for accessing deeply nested reaction parameters.

        Args:
            keys (List[str]): List of keys representing the nested path.

        Returns:
            Dict[str, Any]: Retrieved data or empty dict if path not found.
        """
        return reduce(lambda data, key: data.get(key, {}), keys, self._data)

    def set_value(self, keys: List[str], value: Any) -> None:
        """Store value at specified path_keys location.

        Creates intermediate dictionaries as needed for nested storage.
        Extensively used for updating reaction parameters, bounds, and configurations.

        Args:
            keys (List[str]): List of keys defining the nested storage path.
            value (Any): Value to store at the specified location.
        """
        if not keys:
            return
        last_key = keys.pop()
        nested_dict = reduce(lambda data, key: data.setdefault(key, {}), keys, self._data)
        nested_dict[last_key] = value

    def exists(self, keys: List[str]) -> bool:
        """Check if path exists in the hierarchical data structure."""
        try:
            _ = reduce(lambda data, key: data[key], keys, self._data)
            return True
        except KeyError:
            return False

    def remove_value(self, keys: List[str]) -> None:
        """Delete value from specified path_keys location."""
        if not keys:
            return
        if self.exists(keys):
            last_key = keys.pop()
            parent_dict = reduce(lambda data, key: data.get(key, {}), keys, self._data)
            if last_key in parent_dict:
                del parent_dict[last_key]
                logger.debug({"operation": "remove_reaction", "keys": keys + [last_key]})

    def process_request(self, params: dict) -> None:
        """Handle incoming data operation requests through signal-slot system.

        Processes various operations including GET_VALUE, SET_VALUE, REMOVE_VALUE,
        IMPORT_REACTIONS, and GET_FULL_DATA. Validates parameters and emits responses
        back through the centralized signal system.

        Args:
            params (dict): Request parameters containing 'operation', 'path_keys', 'value', etc.
        """
        operation = params.get("operation")
        actor = params.get("actor")
        logger.debug(f"{self.actor_name} processing request '{operation}' from '{actor}'")

        if operation == OperationType.GET_VALUE:
            path_keys = params.get("path_keys", [])
            if not isinstance(path_keys, list) or any(not isinstance(k, str) for k in path_keys):
                logger.error("Invalid path_keys provided for get_value.")
                params["data"] = {}
            else:
                params["data"] = self.get_value(path_keys)

        elif operation == OperationType.SET_VALUE:
            path_keys = params.get("path_keys", [])
            value = params.get("value")
            if not isinstance(path_keys, list) or any(not isinstance(k, str) for k in path_keys):
                logger.error("Invalid path_keys provided for set_value.")
                params["data"] = False
            else:
                self.set_value(path_keys, value)
                params["data"] = True

        elif operation == OperationType.REMOVE_VALUE:
            path_keys = params.get("path_keys", [])
            if not isinstance(path_keys, list) or any(not isinstance(k, str) for k in path_keys):
                logger.error("Invalid path_keys provided for remove_value.")
                params["data"] = False
            else:
                self.remove_value(path_keys)
                params["data"] = True

        elif operation == OperationType.IMPORT_REACTIONS:
            load_file_name = params.get("import_file_name")
            file_name = params.get("file_name")
            if isinstance(load_file_name, str) and isinstance(file_name, str):
                params["data"] = self.load_reactions(load_file_name, file_name)
            else:
                logger.error("Invalid import file name or target file name provided.")
                params["data"] = None

        elif operation == OperationType.GET_FULL_DATA:
            params["data"] = self._data.copy()

        else:
            logger.debug(f"Unknown operation: {operation}")
            params["data"] = None

        response = {
            "actor": self.actor_name,
            "target": actor,
            "operation": operation,
            "request_id": params["request_id"],
            "data": params["data"],
        }
        self.signals.response_signal.emit(response)
