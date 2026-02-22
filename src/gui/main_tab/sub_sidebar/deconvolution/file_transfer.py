"""
File transfer operations for importing and exporting reaction configurations.

This module handles the import/export functionality for deconvolution reactions,
including JSON file operations and filename generation.
"""

import json
import os
from typing import Any, Dict

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console

from .config import DeconvolutionConfig


class NumpyArrayEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that converts NumPy arrays to lists for JSON serialization.
    """

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyArrayEncoder, self).default(obj)


class FileTransferButtons(QWidget):
    """
    Widget for handling import and export operations of reaction configurations.

    This component provides buttons and functionality for importing reaction
    configurations from JSON files and exporting current configurations.
    """

    import_reactions_signal = pyqtSignal(dict)
    export_reactions_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the file transfer buttons widget."""
        super().__init__(parent)

        self.config = DeconvolutionConfig()
        self.layout = QVBoxLayout(self)

        # Create buttons
        self.load_reactions_button = QPushButton(self.config.labels.import_button)
        self.load_reactions_button.setObjectName("btn_small")
        self.export_reactions_button = QPushButton(self.config.labels.export_button)
        self.export_reactions_button.setObjectName("btn_small")

        # Setup layout
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.load_reactions_button)
        self.buttons_layout.addWidget(self.export_reactions_button)

        self.layout.addLayout(self.buttons_layout)

        # Connect signals
        self.load_reactions_button.clicked.connect(self._import_reactions)
        self.export_reactions_button.clicked.connect(self._export_reactions)

    def _import_reactions(self):
        """
        Open file dialog to select JSON file for importing reaction configurations.
        """
        import_file_name, _ = QFileDialog.getOpenFileName(
            self, "Select the JSON file to import the data", "", self.config.file_transfer.file_extensions
        )

        if import_file_name:
            self.import_reactions_signal.emit(
                {"import_file_name": import_file_name, "operation": OperationType.IMPORT_REACTIONS}
            )

    def _export_reactions(self):
        """
        Emit signal to start export process with filename generation function.
        """
        self.export_reactions_signal.emit(
            {"function": self._generate_suggested_file_name, "operation": OperationType.EXPORT_REACTIONS}
        )

    def _generate_suggested_file_name(self, file_name: str, data: Dict[str, Any]) -> str:
        """
        Generate a suggested file name for exporting reactions based on reaction data.

        Args:
            file_name (str): Base file name.
            data (dict): Reaction data dictionary.

        Returns:
            str: Suggested file name incorporating reaction count and types.
        """
        n_reactions = len(data)
        reaction_types = []

        for reaction_key, reaction_data in data.items():
            function = reaction_data.get("function", "")
            if function == "gauss":
                reaction_types.append("gs")
            elif function == "fraser":
                reaction_types.append("fr")
            elif function == "ads":
                reaction_types.append("ads")

        reaction_codes = "_".join(reaction_types) if reaction_types else "unknown"
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        suggested_file_name = f"{base_name}_{n_reactions}_rcts_{reaction_codes}.json"

        return suggested_file_name

    def export_reactions(self, data: Dict[str, Any], suggested_file_name: str):
        """
        Export the provided reaction data to a JSON file chosen by the user.

        Args:
            data (dict): Reaction data to export.
            suggested_file_name (str): Suggested file name for saving.
        """
        save_file_name, _ = QFileDialog.getSaveFileName(
            self, "Select a location to save JSON", suggested_file_name, self.config.file_transfer.file_extensions
        )

        if save_file_name:
            try:
                with open(save_file_name, "w", encoding=self.config.file_transfer.encoding) as file:
                    json.dump(
                        data,
                        file,
                        ensure_ascii=False,
                        indent=self.config.file_transfer.export_indent,
                        cls=NumpyArrayEncoder,
                    )
                    console.log(f"Data successfully exported to file:\n\n{save_file_name}")
                    logger.info(f"Data successfully exported to file: {save_file_name}")
            except Exception as e:
                logger.error(f"Failed to export data to {save_file_name}: {e}")
                console.log(f"Export failed: {e}")
