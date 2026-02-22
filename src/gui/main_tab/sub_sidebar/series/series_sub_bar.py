"""
Series analysis panel for multi-heating-rate experiments.

Provides interface for loading deconvolution results from multiple heating rates,
performing model-fit and model-free analysis, and visualizing kinetic parameters.
"""

import json

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, pyqtSignal
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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import MODEL_FIT_METHODS, OperationType, SideBarNames
from src.core.curve_fitting import CurveFitting as cft
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console
from src.gui.main_tab.sub_sidebar.series.config import SeriesConfig


class DeconvolutionResultsLoadDialog(QDialog):
    """
    Dialog for loading deconvolution results from multiple heating rate files.

    Allows user to specify files and their corresponding heating rates
    for series analysis.
    """

    def __init__(self, parent=None):
        """Initialize dialog with dynamic file input capability."""
        super().__init__(parent)

        self.config = SeriesConfig()

        self.setWindowTitle(self.config.dialog.deconvolution_results_title)
        self.setMinimumWidth(self.config.dialog.min_window_width)

        self.layout = QVBoxLayout(self)

        self.form_layout = QVBoxLayout()

        self.file_inputs = []
        self.file_count = 1

        self.add_button = QPushButton(self.config.dialog.add_file_button_text, self)
        self.add_button.setObjectName("btn_secondary")
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
        file_input = QPushButton(f"select file {self.file_count}", self)
        file_input.setObjectName("btn_secondary")
        heating_rate_input = QLineEdit(self)
        heating_rate_input.setPlaceholderText(self.config.dialog.heating_rate_placeholder)

        file_input.clicked.connect(lambda: self.select_file(file_input))

        file_layout = QHBoxLayout()
        file_layout.addWidget(file_input)
        file_layout.addWidget(heating_rate_input)

        heating_rate_input.setFixedWidth(self.config.dialog.heating_rate_width)
        file_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        file_layout.setStretch(0, self.config.dialog.field_width - self.config.dialog.heating_rate_width)
        file_layout.setStretch(1, self.config.dialog.heating_rate_width)

        self.form_layout.addLayout(file_layout)

        self.file_inputs.append((file_input, heating_rate_input))
        self.file_count += 1

        new_height = (
            (self.file_count - 1) * self.config.dialog.file_input_row_height
            + self.config.dialog.add_button_height
            + self.config.dialog.window_padding
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


class CalculationButtonsBlock(QWidget):
    """
    Widget providing calculation action buttons for series analysis.

    Emits signals for switching to model-fit, model-free, and model-based panels.
    """

    calculation_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize calculation buttons with signal connections."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.model_fit_button = QPushButton("MODEL FIT")
        self.model_fit_button.setObjectName("btn_secondary")
        self.model_free_button = QPushButton("MODEL FREE")
        self.model_free_button.setObjectName("btn_secondary")
        self.model_based_button = QPushButton("MODEL BASED")
        self.model_based_button.setObjectName("btn_secondary")

        self.model_fit_button.clicked.connect(self.emit_model_fit)
        self.model_free_button.clicked.connect(self.emit_model_free)
        self.model_based_button.clicked.connect(self.emit_model_based)

        layout.addWidget(self.model_fit_button)
        layout.addWidget(self.model_free_button)
        layout.addWidget(self.model_based_button)

    def emit_model_fit(self):
        """Emit signal to switch to model-fit panel."""
        self.calculation_clicked.emit(SideBarNames.MODEL_FIT.value)

    def emit_model_free(self):
        """Emit signal to switch to model-free panel."""
        self.calculation_clicked.emit(SideBarNames.MODEL_FREE.value)

    def emit_model_based(self):
        """Emit signal to switch to model-based panel."""
        self.calculation_clicked.emit(SideBarNames.MODEL_BASED.value)


class SeriesSubBar(QWidget):
    """
    Series analysis panel for multi-heating-rate kinetic studies.

    Provides interface for loading deconvolution results from multiple files,
    performing model-fit/model-free analysis, and displaying kinetic parameters
    in tabular format with export functionality.
    """

    load_deconvolution_results_signal = pyqtSignal(dict)
    results_combobox_text_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize series analysis panel with load button, combo boxes, and results table."""
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.load_button_deconvolution_results_button = QPushButton("LOAD DECONVOLUTION RESULTS", self)
        self.load_button_deconvolution_results_button.setObjectName("btn_secondary")
        self.layout.addWidget(self.load_button_deconvolution_results_button)

        self.results_combobox = QComboBox(self)
        self.results_combobox.setPlaceholderText("select reaction")
        self.layout.addWidget(self.results_combobox)

        self.model_free_method_combobox = QComboBox(self)
        self.model_free_method_combobox.addItems(MODEL_FIT_METHODS)
        self.layout.addWidget(self.model_free_method_combobox)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)  # Adjust based on expected columns
        self.table.setHorizontalHeaderLabels(["reactions", "Ea", "A"])
        self.layout.addWidget(self.table)

        self.export_button = QPushButton("EXPORT RESULTS", self)
        self.export_button.setObjectName("btn_small")
        self.layout.addWidget(self.export_button)

        self.calculation_buttons_block = CalculationButtonsBlock(self)
        self.layout.addWidget(self.calculation_buttons_block)

        self.load_button_deconvolution_results_button.clicked.connect(self.load_deconvolution_results_dialog)
        self.results_combobox.currentTextChanged.connect(self.emit_combobox_text)

        self.last_selected_reaction = None

    def emit_combobox_text(self, text):
        self.last_selected_reaction = text
        self.results_combobox_text_changed_signal.emit(text)

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

    def check_missing_reactions(self, experimental_data: pd.DataFrame, deconvolution_results: dict):
        experimental_columns = experimental_data.columns.tolist()
        experimental_columns = [col for col in experimental_columns if col != "temperature"]
        reactions_per_key = {}

        for key in deconvolution_results:
            key_float = float(key)

            if key_float not in [float(x) for x in experimental_columns]:
                logger.error(f"Missing corresponding data for key: {key_float} in {experimental_columns=}")
                console.log(f"Missing corresponding data for key: {key_float} in {experimental_columns=}")
                continue

            reaction_data = deconvolution_results[key]
            reaction_keys = list(reaction_data.keys())

            reactions_for_this_key = set()
            for reaction in reaction_keys:
                reactions_for_this_key.add(reaction)

            reactions_per_key[key] = reactions_for_this_key

        common_reactions = set.intersection(*reactions_per_key.values()) if reactions_per_key else set()
        logger.debug(f"common_reactions: {common_reactions}")
        all_reactions = {reaction for reactions_set in reactions_per_key.values() for reaction in reactions_set}
        missing_reactions = all_reactions - common_reactions

        if missing_reactions:
            logger.error(f"The following reactions do not appear in all keys: {missing_reactions}")
            console.log(f"The following reactions do not appear in all keys: {missing_reactions}")

        sorted_common_reactions = list(common_reactions)
        sorted_common_reactions.sort(key=lambda x: int(x.split("_")[1]))
        return sorted_common_reactions, missing_reactions

    def _update_table_with_reactions(self, common_reactions):
        self.results_combobox.blockSignals(True)
        self.results_combobox.clear()
        self.table.setRowCount(0)

        selected_reaction = self.last_selected_reaction if self.last_selected_reaction in common_reactions else None

        for reaction in common_reactions:
            self.results_combobox.addItem(f"{reaction}")
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(reaction))
            self.table.setItem(row_position, 1, QTableWidgetItem(""))
            self.table.setItem(row_position, 2, QTableWidgetItem(""))

        if selected_reaction:
            self.results_combobox.setCurrentText(selected_reaction)
        else:
            self.last_selected_reaction = None

        self.results_combobox.blockSignals(False)

    def get_reaction_dataframe(
        self, experimental_data: pd.DataFrame, deconvolution_results: dict, reaction_n="reaction_0"
    ) -> pd.DataFrame:
        temperatures = experimental_data["temperature"]
        fitted_data = {}
        for key, result in deconvolution_results.items():
            reaction_data = result.get(reaction_n)
            if reaction_data:
                function_type = reaction_data.get("function")
                coeffs = reaction_data.get("coeffs", {})

                if function_type == "gauss":
                    fitted_values = cft.calculate_reaction(
                        (
                            (np.min(temperatures), np.max(temperatures)),
                            function_type,
                            (coeffs.get("h", 0), coeffs.get("z", 0), coeffs.get("w", 0)),
                        )
                    )
                elif function_type == "fraser":
                    fitted_values = cft.calculate_reaction(
                        (
                            (np.min(temperatures), np.max(temperatures)),
                            function_type,
                            (coeffs.get("h", 0), coeffs.get("z", 0), coeffs.get("w", 0), coeffs.get("fr", 0)),
                        )
                    )
                elif function_type == "ads":
                    fitted_values = cft.calculate_reaction(
                        (
                            (np.min(temperatures), np.max(temperatures)),
                            function_type,
                            (
                                coeffs.get("h", 0),
                                coeffs.get("z", 0),
                                coeffs.get("w", 0),
                                coeffs.get("ads1", 0),
                                coeffs.get("ads2", 0),
                            ),
                        )
                    )
                else:
                    fitted_values = np.zeros_like(temperatures)

                fitted_data[key] = fitted_values

        # 250 depends on cft.calculate_reaction
        fitted_data["temperature"] = np.linspace(np.min(temperatures), np.max(temperatures), 250)
        reaction_df = pd.DataFrame(fitted_data)
        return reaction_df

    def update_series_ui(self, experimental_data: pd.DataFrame, deconvolution_results: dict):
        reactions, _ = self.check_missing_reactions(experimental_data, deconvolution_results)
        self._update_table_with_reactions(reactions)
