from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import MODEL_FREE_METHODS


class ModelFreeSubBar(QWidget):
    model_fit_calculation = pyqtSignal(dict)
    table_combobox_text_changed_signal = pyqtSignal(dict)
    plot_model_fit_signal = pyqtSignal(dict)

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
        # self.calculate_button.clicked.connect()
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
