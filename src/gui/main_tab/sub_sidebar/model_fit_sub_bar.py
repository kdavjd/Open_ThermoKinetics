from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import MODEL_FIT_METHODS, NUC_MODELS_LIST, OperationType


class ModelFitSubBar(QWidget):
    model_fit_calculation = pyqtSignal(dict)
    table_combobox_text_changed_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.model_combobox = QComboBox(self)
        self.model_combobox.addItems(MODEL_FIT_METHODS)
        self.layout.addWidget(self.model_combobox)

        self.form_layout = QFormLayout()
        self.alpha_min_input = QLineEdit(self)
        self.alpha_min_input.setText("0.005")
        self.alpha_min_input.setToolTip("alpha_min - minimum conversion value for calculation")
        self.form_layout.addRow("α_min:", self.alpha_min_input)

        self.alpha_max_input = QLineEdit(self)
        self.alpha_max_input.setText("0.995")
        self.alpha_max_input.setToolTip("alpha_max - maximum conversion value for calculation")
        self.form_layout.addRow("α_max:", self.alpha_max_input)

        self.valid_proportion_input = QLineEdit(self)
        self.valid_proportion_input.setText("0.8")
        self.valid_proportion_input.setToolTip(
            "valid proportion - the proportion of values in the model calculation that is not infinity or NaN. "
            "If it is smaller, the model is ignored."
        )
        self.form_layout.addRow("valid proportion:", self.valid_proportion_input)

        self.layout.addLayout(self.form_layout)

        # Calculate button
        self.calculate_button = QPushButton("Calculate", self)
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
        self.results_table.setHorizontalHeaderLabels(["Model", "R2_score", "Ea", "A"])
        self.layout.addWidget(self.results_table)

        # Drop-down for NUC models list and plot button
        self.plot_layout = QHBoxLayout()
        self.nuc_combobox = QComboBox(self)
        self.nuc_combobox.addItems(NUC_MODELS_LIST)
        self.plot_button = QPushButton("Plot result", self)
        self.plot_layout.addWidget(self.nuc_combobox)
        self.plot_layout.addWidget(self.plot_button)
        self.layout.addLayout(self.plot_layout)

        self.setLayout(self.layout)

        self.last_selected_reaction = None
        self.last_selected_beta = None

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

    def _update_combobox_with_reactions(self, common_reactions: list[str]):
        """Обновляет выпадающий список реакций."""
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

    def update_reaction_combobox(self, reactions: list[str]):
        self._update_combobox_with_reactions(reactions)

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
        self.update_reaction_combobox(reaction_keys)
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
