"""
Model-fit analysis panel for kinetic parameter determination.

Provides interface for direct-differential and Coats-Redfern methods
to determine kinetic parameters from deconvoluted reaction data.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import MODEL_FIT_ANNOTATION_CONFIG, MODEL_FIT_METHODS, NUC_MODELS_LIST, OperationType
from src.gui.main_tab.sub_sidebar.model_fit.config import ModelFitConfig


class ModelFitSubBar(QWidget):
    """
    Model-fit analysis panel for determining kinetic parameters.

    Provides interface for direct-differential and Coats-Redfern methods
    with conversion range selection and nucleation model configuration.
    """

    model_fit_calculation = pyqtSignal(dict)
    table_combobox_text_changed_signal = pyqtSignal(dict)
    plot_model_fit_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize model-fit panel with method selection and parameter inputs."""
        super().__init__(parent)

        self.config = ModelFitConfig()

        self.layout = QVBoxLayout(self)

        self.model_combobox = QComboBox(self)
        self.model_combobox.addItems(MODEL_FIT_METHODS)
        self.layout.addWidget(self.model_combobox)

        self.form_layout = QFormLayout()
        self.alpha_min_input = QLineEdit(self)
        self.alpha_min_input.setText(self.config.defaults.alpha_min)
        self.alpha_min_input.setToolTip(self.config.ui.alpha_min_tooltip)
        self.form_layout.addRow(self.config.ui.alpha_min_label, self.alpha_min_input)

        self.alpha_max_input = QLineEdit(self)
        self.alpha_max_input.setText(self.config.defaults.alpha_max)
        self.alpha_max_input.setToolTip(self.config.ui.alpha_max_tooltip)
        self.form_layout.addRow(self.config.ui.alpha_max_label, self.alpha_max_input)

        self.valid_proportion_input = QLineEdit(self)
        self.valid_proportion_input.setText(self.config.defaults.valid_proportion)
        self.valid_proportion_input.setToolTip(self.config.ui.valid_proportion_tooltip)
        self.form_layout.addRow(self.config.ui.valid_proportion_label, self.valid_proportion_input)

        self.layout.addLayout(self.form_layout)

        # Calculate button
        self.calculate_button = QPushButton(self.config.ui.calculate_button_text, self)
        self.calculate_button.setObjectName("btn_primary")
        self.calculate_button.clicked.connect(self.on_calculate_clicked)
        self.layout.addWidget(self.calculate_button)

        self.reaction_layout = QHBoxLayout()

        # β combobox
        self.beta_combobox = QComboBox(self)
        self.beta_combobox.addItems(["β"])
        self.reaction_layout.addWidget(self.beta_combobox)

        # Reaction combobox
        self.reaction_combobox = QComboBox(self)
        self.reaction_combobox.addItems(["select reaction"])
        self.reaction_layout.addWidget(self.reaction_combobox)

        self.layout.addLayout(self.reaction_layout)

        self.beta_combobox.currentTextChanged.connect(self.emit_combobox_text)
        self.reaction_combobox.currentTextChanged.connect(self.emit_combobox_text)

        self.results_table = QTableWidget(self)
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(self.config.ui.table_headers)
        self.layout.addWidget(self.results_table)

        # Drop-down for NUC models, plot button and settings button
        self.plot_layout = QHBoxLayout()
        self.plot_model_combobox = QComboBox(self)
        self.plot_model_combobox.addItems(NUC_MODELS_LIST)
        self.plot_button = QPushButton(self.config.ui.plot_button_text, self)
        self.plot_button.setObjectName("btn_secondary")
        self.plot_button.clicked.connect(self.on_plot_clicked)
        self.settings_button = QPushButton(self.config.ui.settings_button_text, self)
        self.settings_button.setObjectName("btn_secondary")
        self.settings_button.clicked.connect(self.on_settings_clicked)
        self.plot_layout.addWidget(self.plot_model_combobox)
        self.plot_layout.addWidget(self.plot_button)
        self.plot_layout.addWidget(self.settings_button)
        self.plot_layout.setStretchFactor(self.plot_model_combobox, 2)
        self.plot_layout.setStretchFactor(self.plot_button, 4)
        self.plot_layout.setStretchFactor(self.settings_button, 4)

        self.layout.addLayout(self.plot_layout)
        self.setLayout(self.layout)

        self.last_selected_reaction = None
        self.last_selected_beta = None

        self.is_annotate = True
        self.annotation_config = MODEL_FIT_ANNOTATION_CONFIG.copy()

    def emit_combobox_text(self, _=None):
        reaction = self.reaction_combobox.currentText()
        beta = self.beta_combobox.currentText()

        self.last_selected_reaction = reaction
        self.last_selected_beta = beta

        self.table_combobox_text_changed_signal.emit(
            {
                "operation": OperationType.GET_MODEL_FIT_REACTION_DF,
                "fit_method": self.model_combobox.currentText(),
                "reaction_n": reaction,
                "beta": beta,
            }
        )

    def on_calculate_clicked(self):
        try:
            alpha_min = float(self.alpha_min_input.text())
            alpha_max = float(self.alpha_max_input.text())
            valid_proportion = float(self.valid_proportion_input.text())
            fit_method = self.model_combobox.currentText()

            if not (0 <= alpha_min <= 0.999):
                raise ValueError("alpha_min must be between 0 and 0.999")
            if not (0 <= alpha_max <= 1):
                raise ValueError("alpha_max must be between 0 and 1")
            if alpha_min > alpha_max:
                raise ValueError("alpha_min cannot be greater than alpha_max")
            if not (0.001 <= valid_proportion <= 1):
                raise ValueError("valid proportion must be between 0.001 and 1")

            self.model_fit_calculation.emit(
                {
                    "fit_method": fit_method,
                    "alpha_min": alpha_min,
                    "alpha_max": alpha_max,
                    "valid_proportion": valid_proportion,
                    "operation": OperationType.MODEL_FIT_CALCULATION,
                }
            )

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def update_combobox_with_reactions(self, common_reactions: list[str]):
        self.reaction_combobox.blockSignals(True)
        self.reaction_combobox.clear()

        selected_reaction = self.last_selected_reaction if self.last_selected_reaction in common_reactions else None

        for reaction in common_reactions:
            self.reaction_combobox.addItem(reaction)

        if selected_reaction:
            self.reaction_combobox.setCurrentText(selected_reaction)
        else:
            self.last_selected_reaction = None

        self.reaction_combobox.blockSignals(False)

    def update_beta_combobox(self, beta_values: list[str]):
        self.beta_combobox.blockSignals(True)
        self.beta_combobox.clear()
        self.beta_combobox.addItems(beta_values)
        self.beta_combobox.blockSignals(False)

    def update_results_table(self, result_df):
        self.results_table.setRowCount(0)
        for row in result_df.itertuples(index=False):
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            for col, value in enumerate(row):
                self.results_table.setItem(row_position, col, QTableWidgetItem(str(value)))

    def update_fit_results(self, fit_results: dict):
        reaction_keys = list(fit_results.keys())
        self.update_combobox_with_reactions(reaction_keys)
        selected_reaction = (
            self.last_selected_reaction if self.last_selected_reaction in reaction_keys else reaction_keys[0]
        )

        beta_dict = fit_results[selected_reaction]
        beta_values = list(beta_dict.keys())
        self.update_beta_combobox(beta_values)

        selected_beta = beta_values[0] if beta_values else None

        if selected_beta:
            result_df = beta_dict[selected_beta]
            self.update_results_table(result_df)

    def on_plot_clicked(self):
        try:
            alpha_min = float(self.alpha_min_input.text())
            alpha_max = float(self.alpha_max_input.text())
            valid_proportion = float(self.valid_proportion_input.text())

            if not (0 <= alpha_min <= 0.999):
                raise ValueError("alpha_min must be between 0 and 0.999")
            if not (0 <= alpha_max <= 1):
                raise ValueError("alpha_max must be between 0 and 1")
            if alpha_min > alpha_max:
                raise ValueError("alpha_min cannot be greater than alpha_max")
            if not (0.001 <= valid_proportion <= 1):
                raise ValueError("valid proportion must be between 0.001 and 1")

            self.plot_model_fit_signal.emit(
                {
                    "operation": OperationType.PLOT_MODEL_FIT_RESULT,
                    "beta": self.beta_combobox.currentText(),
                    "reaction_n": self.reaction_combobox.currentText(),
                    "model": self.plot_model_combobox.currentText(),
                    "fit_method": self.model_combobox.currentText(),
                    "alpha_min": alpha_min,
                    "alpha_max": alpha_max,
                    "valid_proportion": valid_proportion,
                    "is_annotate": self.is_annotate,
                }
            )
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

    def on_settings_clicked(self):
        dialog = ModelFitAnnotationSettingsDialog(self, self.is_annotate, self.annotation_config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.is_annotate, self.annotation_config = dialog.get_settings()
            MODEL_FIT_ANNOTATION_CONFIG.clear()
            MODEL_FIT_ANNOTATION_CONFIG.update(self.annotation_config)


class ModelFitAnnotationSettingsDialog(QDialog):
    """
    Dialog for configuring model-fit plot annotation settings.

    Allows configuration of annotation positioning, styling, and enable/disable state
    for displaying kinetic parameters on model-fit analysis plots.
    """

    def __init__(self, parent, is_annotate, config):
        """Initialize annotation settings dialog with current configuration."""
        super().__init__(parent)
        self.config = config
        self.setWindowTitle(self.config.dialog.annotation_settings_title)
        self.resize(self.config.dialog.annotation_settings_width, self.config.dialog.annotation_settings_height)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Checkbox to enable annotations
        self.annotate_checkbox = QCheckBox("annotation")
        self.annotate_checkbox.setChecked(is_annotate)
        form_layout.addRow(self.annotate_checkbox)

        # Configuration parameters
        self.block_top_spin = QDoubleSpinBox()
        self.block_top_spin.setRange(0.0, 1.0)
        self.block_top_spin.setDecimals(2)
        self.block_top_spin.setSingleStep(0.01)
        self.block_top_spin.setValue(config.get("block_top", 0.98))
        form_layout.addRow("block Top:", self.block_top_spin)

        self.block_left_spin = QDoubleSpinBox()
        self.block_left_spin.setRange(0.0, 1.0)
        self.block_left_spin.setDecimals(2)
        self.block_left_spin.setSingleStep(0.01)
        self.block_left_spin.setValue(config.get("block_left", 0.4))
        form_layout.addRow("block Left:", self.block_left_spin)

        self.block_right_spin = QDoubleSpinBox()
        self.block_right_spin.setRange(0.0, 1.0)
        self.block_right_spin.setDecimals(2)
        self.block_right_spin.setSingleStep(0.01)
        self.block_right_spin.setValue(config.get("block_right", 0.6))
        form_layout.addRow("block Right:", self.block_right_spin)

        self.delta_y_spin = QDoubleSpinBox()
        self.delta_y_spin.setRange(0.0, 1.0)
        self.delta_y_spin.setDecimals(2)
        self.delta_y_spin.setSingleStep(0.01)
        self.delta_y_spin.setValue(config.get("delta_y", 0.03))
        form_layout.addRow("delta Y:", self.delta_y_spin)

        self.fontsize_spin = QSpinBox()
        self.fontsize_spin.setRange(1, 100)
        self.fontsize_spin.setValue(config.get("fontsize", 8))
        form_layout.addRow("font size:", self.fontsize_spin)

        self.facecolor_edit = QLineEdit()
        self.facecolor_edit.setText(config.get("facecolor", "white"))
        form_layout.addRow("face color:", self.facecolor_edit)

        self.edgecolor_edit = QLineEdit()
        self.edgecolor_edit.setText(config.get("edgecolor", "black"))
        form_layout.addRow("edge color:", self.edgecolor_edit)

        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1.0)
        self.alpha_spin.setDecimals(2)
        self.alpha_spin.setSingleStep(0.1)
        self.alpha_spin.setValue(config.get("alpha", 1.0))
        form_layout.addRow("alpha:", self.alpha_spin)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_settings(self):
        config = {
            "block_top": self.block_top_spin.value(),
            "block_left": self.block_left_spin.value(),
            "block_right": self.block_right_spin.value(),
            "delta_y": self.delta_y_spin.value(),
            "fontsize": self.fontsize_spin.value(),
            "facecolor": self.facecolor_edit.text(),
            "edgecolor": self.edgecolor_edit.text(),
            "alpha": self.alpha_spin.value(),
        }
        return self.annotate_checkbox.isChecked(), config
