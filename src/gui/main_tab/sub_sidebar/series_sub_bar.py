import json

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import OperationType
from src.core.logger_config import logger


class DialogDimensions:
    MIN_WINDOW_WIDTH = 300
    FIELD_WIDTH = 290
    HEATING_RATE_WIDTH = 80
    FILE_IMPUT_ROW_HEIGHT = 50
    ADD_BUTTON_HEIGHT = 40
    WINDOW_PADDING = 50


class DeconvolutionResultsLoadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Load Deconvolution Results")
        self.setMinimumWidth(DialogDimensions.MIN_WINDOW_WIDTH)

        self.layout = QVBoxLayout(self)

        self.form_layout = QVBoxLayout()

        self.file_inputs = []
        self.file_count = 1

        self.add_button = QPushButton("Add File", self)
        self.add_button.clicked.connect(self.add_file_input)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.add_button)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self
        )
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.add_file_input()

    def add_file_input(self):
        file_input = QPushButton(f"Select File {self.file_count}", self)
        heating_rate_input = QLineEdit(self)
        heating_rate_input.setPlaceholderText("heating rate:")

        file_input.clicked.connect(lambda: self.select_file(file_input))

        file_layout = QHBoxLayout()
        file_layout.addWidget(file_input)
        file_layout.addWidget(heating_rate_input)

        heating_rate_input.setFixedWidth(DialogDimensions.HEATING_RATE_WIDTH)
        file_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        file_layout.setStretch(0, DialogDimensions.FIELD_WIDTH - DialogDimensions.HEATING_RATE_WIDTH)
        file_layout.setStretch(1, DialogDimensions.HEATING_RATE_WIDTH)

        self.form_layout.addLayout(file_layout)

        self.file_inputs.append((file_input, heating_rate_input))
        self.file_count += 1

        new_height = (
            (self.file_count - 1) * DialogDimensions.FILE_IMPUT_ROW_HEIGHT
            + DialogDimensions.ADD_BUTTON_HEIGHT
            + DialogDimensions.WINDOW_PADDING
        )
        self.setFixedHeight(new_height)

    def select_file(self, file_input):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if file_path:
            file_name = file_path.split("/")[-1]
            file_input.setText(file_name)
            file_input.file_path = file_path

    def get_files_data(self):
        files_data = {}
        for file_input, heating_rate_input in self.file_inputs:
            file_name = file_input.text()
            file_path = getattr(file_input, "file_path", None)
            try:
                heating_rate = int(heating_rate_input.text())
                if file_path and file_name:
                    files_data[heating_rate] = file_path
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    f"Invalid heating rate value for file {file_name}. Please enter a valid integer.",
                )
                logger.warning(f"Invalid heating rate value for file {file_name}. Please enter a valid integer.")
                return {}  # If heating rate is invalid, return an empty dict to prevent proceeding
        return files_data

    def on_accept(self):
        files_data = self.get_files_data()
        if not files_data:
            logger.error("Error: Heating rate is not filled or invalid.")
            return
        logger.debug(f"Loaded files and heating rates: {files_data}")
        self.accept()


class SeriesSubBar(QWidget):
    load_deconvolution_results_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.load_button_deconvolution_results_button = QPushButton("Load Deconvolution Results", self)
        self.layout.addWidget(self.load_button_deconvolution_results_button)

        self.results_combobox = QComboBox(self)
        self.results_combobox.setPlaceholderText("Select Reaction")
        self.layout.addWidget(self.results_combobox)

        self.load_button_deconvolution_results_button.clicked.connect(self.load_deconvolution_results_dialog)

    def load_deconvolution_results_dialog(self):
        dialog = DeconvolutionResultsLoadDialog(self)
        if dialog.exec():
            files_data = dialog.get_files_data()
            if files_data:
                self.load_reactions_from_files(files_data)

    def load_reactions_from_files(self, files_data: dict):
        for heating_rate, file_path in files_data.items():
            data = self.load_reactions(file_path, str(heating_rate))
            if data:
                self.results_combobox.addItem(f"Heating Rate: {heating_rate}", data)
                self.load_deconvolution_results_signal.emit(
                    {
                        "deconvolution_results": {heating_rate: data},
                        "operation": OperationType.LOAD_DECONVOLUTION_RESULTS,
                    }
                )
            else:
                logger.warning(f"Failed to load data from {file_path}")

    def load_reactions(self, load_file_name: str, file_name: str):
        try:
            with open(load_file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

            for reaction_key, reaction_data in data.items():
                if "x" in reaction_data:
                    reaction_data["x"] = np.array(reaction_data["x"])

            logger.debug(f"Loaded data for {file_name}: {data}")

            return data
        except IOError as e:
            logger.error(f"Error loading file {load_file_name}: {e}")
            return {}
