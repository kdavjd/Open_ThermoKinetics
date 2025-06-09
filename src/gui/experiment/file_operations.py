"""
File Operations Component

This module provides file transfer operations for importing and exporting
reaction data in JSON format with proper encoding and error handling.
"""

import json
import os

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class NumpyArrayEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts NumPy arrays to lists for JSON serialization.

    This encoder handles NumPy arrays and other NumPy types to ensure proper
    JSON serialization of scientific data.
    """

    def default(self, obj):
        """
        Override default method to handle NumPy types.

        Args:
            obj: Object to serialize

        Returns:
            Serializable representation of the object
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        return super(NumpyArrayEncoder, self).default(obj)


class FileTransferButtons(QWidget):
    """
    Widget providing file import/export functionality for reaction data.

    Provides buttons for importing reaction configurations from JSON files
    and exporting current configurations with intelligent file naming.

    Signals:
        import_reactions_signal: Emitted when reaction data should be imported
        export_reactions_signal: Emitted when reaction data should be exported
    """

    import_reactions_signal = pyqtSignal(dict)
    export_reactions_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize the file transfer buttons widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface components."""
        self.layout = QVBoxLayout(self)

        # Create buttons
        self.load_reactions_button = QPushButton("import")
        self.export_reactions_button = QPushButton("export")

        # Layout buttons horizontally
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.load_reactions_button)
        self.buttons_layout.addWidget(self.export_reactions_button)
        self.layout.addLayout(self.buttons_layout)

    def _connect_signals(self):
        """Connect button signals to their handlers."""
        self.load_reactions_button.clicked.connect(self.load_reactions)
        self.export_reactions_button.clicked.connect(self._export_reactions)

    def load_reactions(self):
        """
        Open a file dialog to select a JSON file for importing reaction data.

        Emits the 'import_reactions_signal' upon successful file selection.
        """
        import_file_name, _ = QFileDialog.getOpenFileName(
            self, "Select the JSON file to import the data", "", "JSON Files (*.json)"
        )

        if import_file_name:
            self.import_reactions_signal.emit(
                {"import_file_name": import_file_name, "operation": OperationType.IMPORT_REACTIONS}
            )
            logger.info(f"Import request initiated for file: {import_file_name}")

    def _export_reactions(self):
        """
        Initiate the export process by emitting signal with filename generator function.

        The actual export will be handled by the parent component which has access
        to the reaction data needed for generating the suggested filename.
        """
        self.export_reactions_signal.emit(
            {"function": self._generate_suggested_file_name, "operation": OperationType.EXPORT_REACTIONS}
        )

    def _generate_suggested_file_name(self, file_name: str, data: dict) -> str:
        """
        Generate a suggested file name for exporting reactions.

        Creates an intelligent filename based on the number and types of reactions
        to provide meaningful file naming for exported configurations.

        Args:
            file_name (str): Base file name from the experiment
            data (dict): Reaction data dictionary

        Returns:
            str: Suggested file name incorporating reaction count and types
        """
        n_reactions = len(data)
        reaction_types = []

        # Extract function types from reaction data
        for reaction_key, reaction_data in data.items():
            function = reaction_data.get("function", "")
            if function == "gauss":
                reaction_types.append("gs")
            elif function == "fraser":
                reaction_types.append("fr")
            elif function == "ads":
                reaction_types.append("ads")
            else:
                reaction_types.append("unk")  # Unknown function type

        # Build filename components
        reaction_codes = "_".join(reaction_types)
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        suggested_file_name = f"{base_name}_{n_reactions}_rcts_{reaction_codes}.json"

        logger.debug(f"Generated suggested filename: {suggested_file_name}")
        return suggested_file_name

    def export_reactions(self, data: dict, suggested_file_name: str):
        """
        Export the provided reaction data to a JSON file chosen by the user.

        Opens a file save dialog with the suggested filename and saves the
        reaction data in properly formatted JSON with UTF-8 encoding.

        Args:
            data (dict): Reaction data to export
            suggested_file_name (str): Suggested file name for saving
        """
        save_file_name, _ = QFileDialog.getSaveFileName(
            self, "Select a location to save JSON", suggested_file_name, "JSON Files (*.json)"
        )

        if save_file_name:
            try:
                with open(save_file_name, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4, cls=NumpyArrayEncoder)

                console.log(f"Data successfully exported to file:\n\n{save_file_name}")
                logger.info(f"Data successfully exported to file: {save_file_name}")

            except Exception as e:
                error_msg = f"Failed to export data to {save_file_name}: {str(e)}"
                console.log(error_msg)
                logger.error(error_msg)
                raise
