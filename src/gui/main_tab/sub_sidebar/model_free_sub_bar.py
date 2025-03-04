from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import MODEL_FREE_METHODS, OperationType


class ModelFreeSubBar(QWidget):
    model_free_calculation_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.model_combobox = QComboBox(self)
        self.model_combobox.addItems(MODEL_FREE_METHODS)
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

        self.layout.addLayout(self.form_layout)

        # Calculate button
        self.calculate_button = QPushButton("calculate", self)
        self.calculate_button.clicked.connect(self.on_calculate_clicked)
        self.layout.addWidget(self.calculate_button)

        self.reaction_layout = QHBoxLayout()
        self.reaction_combobox = QComboBox(self)
        self.reaction_combobox.addItems(["select reaction"])
        self.reaction_layout.addWidget(self.reaction_combobox)

        self.layout.addLayout(self.reaction_layout)

        # self.beta_combobox.currentTextChanged.connect()
        # self.reaction_combobox.currentTextChanged.connect()

        self.results_table = QTableWidget(self)
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Model", "R2_score", "Ea", "A"])
        self.layout.addWidget(self.results_table)

        # Drop-down for NUC models, plot button and settings button
        self.plot_layout = QHBoxLayout()
        self.plot_button = QPushButton("plot", self)
        # self.plot_button.clicked.connect()
        self.settings_button = QPushButton("settings", self)
        # self.settings_button.clicked.connect()
        self.plot_layout.addWidget(self.plot_button)
        self.plot_layout.addWidget(self.settings_button)
        self.plot_layout.setStretchFactor(self.plot_button, 4)
        self.plot_layout.setStretchFactor(self.settings_button, 4)

        self.layout.addLayout(self.plot_layout)
        self.setLayout(self.layout)

        self.last_selected_reaction = None
        self.last_selected_beta = None

    def on_calculate_clicked(self):
        try:
            alpha_min = float(self.alpha_min_input.text())
            alpha_max = float(self.alpha_max_input.text())
            fit_method = self.model_combobox.currentText()

            if not (0 <= alpha_min <= 0.999):
                raise ValueError("alpha_min must be between 0 and 0.999")
            if not (0 <= alpha_max <= 1):
                raise ValueError("alpha_max must be between 0 and 1")
            if alpha_min > alpha_max:
                raise ValueError("alpha_min cannot be greater than alpha_max")

            self.model_free_calculation_signal.emit(
                {
                    "fit_method": fit_method,
                    "alpha_min": alpha_min,
                    "alpha_max": alpha_max,
                    "operation": OperationType.MODEL_FREE_CALCULATION,
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
