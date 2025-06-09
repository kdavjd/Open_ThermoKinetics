"""
Model-Based Analysis Dialog Components

This module contains dialog components for model-based kinetics analysis including
calculation settings configuration and model selection dialogs.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import NUC_MODELS_LIST


class CalculationSettingsDialog(QDialog):
    """
    Dialog for configuring model-based calculation settings.

    Provides interface for setting differential evolution parameters and reaction
    constraints including energy activation bounds, pre-exponential factors, and
    contribution limits for each reaction in the scheme.
    """

    def __init__(
        self, reactions_data: list[dict], calculation_method: str, calculation_method_params: dict, parent=None
    ):
        """
        Initialize the calculation settings dialog.

        Args:
            reactions_data: List of reaction configuration dictionaries
            calculation_method: Selected calculation method name
            calculation_method_params: Method-specific parameters
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculation_method = calculation_method
        self.calculation_method_params = calculation_method_params
        self.setWindowTitle("Calculation Settings")

        self.reactions_data = reactions_data or []
        self.de_params_edits = {}

        # Main layout setup
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Left panel for method parameters
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        # Method selection
        method_label = QLabel("Calculation method:")
        self.calculation_method_combo = QComboBox()
        self.calculation_method_combo.addItems(["differential_evolution", "another_method"])
        self.calculation_method_combo.setCurrentText("differential_evolution")
        self.calculation_method_combo.currentTextChanged.connect(self.update_method_parameters)
        left_layout.addWidget(method_label)
        left_layout.addWidget(self.calculation_method_combo)

        # Differential evolution parameters
        self.de_group = QGroupBox("Differential Evolution Settings")
        self.de_layout = QFormLayout()
        self.de_group.setLayout(self.de_layout)
        left_layout.addWidget(self.de_group, stretch=0)

        # Create parameter widgets
        for param_name, default_value in self.calculation_method_params.items():
            label = QLabel(param_name)
            label.setToolTip(self.get_tooltip_for_parameter(param_name))

            if isinstance(default_value, bool):
                edit_widget = QCheckBox()
                edit_widget.setChecked(default_value)
            elif param_name in ["strategy", "init", "updating"]:
                edit_widget = QComboBox()
                edit_widget.addItems(self.get_options_for_parameter(param_name))
                edit_widget.setCurrentText(str(default_value))
            else:
                text_val = str(default_value) if default_value is not None else "None"
                edit_widget = QLineEdit(text_val)

            self.de_params_edits[param_name] = edit_widget
            self.de_layout.addRow(label, edit_widget)

        left_layout.addStretch(1)

        # Right panel for reaction parameters
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, stretch=1)

        # Scrollable area for reactions
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        self.reactions_grid = QGridLayout(scroll_content)
        scroll_content.setLayout(self.reactions_grid)

        self.reaction_boxes = []
        self._setup_reaction_widgets()

        # Dialog buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.addWidget(btn_box)

        self.update_method_parameters()

    def _setup_reaction_widgets(self):
        """Create widgets for each reaction configuration."""
        for i, reaction in enumerate(self.reactions_data):
            row = i % 2
            col = i // 2

            box_widget = QWidget()
            box_layout = QVBoxLayout(box_widget)
            box_widget.setLayout(box_layout)

            # Reaction header with model selection
            top_line_widget = QWidget()
            top_line_layout = QHBoxLayout(top_line_widget)
            top_line_widget.setLayout(top_line_layout)

            reaction_label = QLabel(f"{reaction.get('from', '?')} -> {reaction.get('to', '?')}")
            top_line_layout.addWidget(reaction_label)

            combo_type = QComboBox()
            combo_type.addItems(NUC_MODELS_LIST)
            current_type = reaction.get("reaction_type", "F2")
            if current_type in NUC_MODELS_LIST:
                combo_type.setCurrentText(current_type)
            top_line_layout.addWidget(combo_type)

            box_layout.addWidget(top_line_widget)

            # Multi-model selection
            models_selection_widget = QWidget()
            models_selection_layout = QHBoxLayout(models_selection_widget)
            models_selection_widget.setLayout(models_selection_layout)

            many_models_checkbox = QCheckBox("Many models")
            add_models_button = QPushButton("Add models")
            add_models_button.setEnabled(False)
            add_models_button.selected_models = []

            models_selection_layout.addWidget(many_models_checkbox)
            models_selection_layout.addWidget(add_models_button)
            box_layout.addWidget(models_selection_widget)

            # Enable/disable models button based on checkbox
            many_models_checkbox.stateChanged.connect(
                lambda state, btn=add_models_button: btn.setEnabled(state == Qt.CheckState.Checked.value)
            )

            # Models selection dialog connection
            def open_models_dialog(checked, btn=add_models_button):
                dialog = ModelsSelectionDialog(NUC_MODELS_LIST, parent=self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected = dialog.get_selected_models()
                    btn.selected_models = selected
                    btn.setText(f"Add models ({len(selected)})")

            add_models_button.clicked.connect(open_models_dialog)

            # Parameter bounds table
            table = QTableWidget(3, 2, self)
            table.setHorizontalHeaderLabels(["Min", "Max"])
            table.setVerticalHeaderLabels(["Ea", "log(A)", "contribution"])
            table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
            table.verticalHeader().setVisible(True)
            table.horizontalHeader().setVisible(True)
            table.setStyleSheet("""
                QTableWidget::item:selected {
                    background-color: lightgray;
                    color: black;
                }
                QTableWidget::item:focus {
                    background-color: lightgray;
                    color: black;
                }
            """)
            box_layout.addWidget(table)

            # Populate table with reaction bounds
            ea_min = str(reaction.get("Ea_min", 1))
            ea_max = str(reaction.get("Ea_max", 2000))
            table.setItem(0, 0, QTableWidgetItem(ea_min))
            table.setItem(0, 1, QTableWidgetItem(ea_max))

            log_a_min = str(reaction.get("log_A_min", 0.1))
            log_a_max = str(reaction.get("log_A_max", 100))
            table.setItem(1, 0, QTableWidgetItem(log_a_min))
            table.setItem(1, 1, QTableWidgetItem(log_a_max))

            contrib_min = str(reaction.get("contribution_min", 0.01))
            contrib_max = str(reaction.get("contribution_max", 1.0))
            table.setItem(2, 0, QTableWidgetItem(contrib_min))
            table.setItem(2, 1, QTableWidgetItem(contrib_max))

            self.reactions_grid.addWidget(box_widget, row, col)
            self.reaction_boxes.append((combo_type, many_models_checkbox, add_models_button, table, reaction_label))

    def update_method_parameters(self):
        """Update visibility of method-specific parameter groups."""
        selected_method = self.calculation_method_combo.currentText()
        if selected_method == "differential_evolution":
            self.de_group.setVisible(True)
        else:
            self.de_group.setVisible(False)

    def get_data(self):  # noqa: C901
        """
        Extract and validate all dialog data.

        Returns:
            tuple: (calculation_settings_dict, updated_reactions_list) or (None, None) if validation fails
        """
        selected_method = self.calculation_method_combo.currentText()
        errors = []
        method_params = {}

        # Extract method parameters
        if selected_method == "differential_evolution":
            for key, widget in self.de_params_edits.items():
                if isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                else:
                    text = widget.text().strip()
                    default_value = self.calculation_method_params[key]
                    value = self.convert_to_type(text, default_value)

                is_valid, error_msg = self.validate_parameter(key, value)
                if not is_valid:
                    errors.append(f"Parameter '{key}': {error_msg}")
                method_params[key] = value
        elif selected_method == "another_method":
            method_params = {"info": "No additional params set for another_method"}

        if errors:
            QMessageBox.warning(self, "Invalid DE parameters", "\n".join(errors))
            return None, None

        # Extract reaction parameters
        updated_reactions = []
        for (combo_type, many_models_checkbox, add_models_button, table, label_reaction), old_reaction in zip(
            self.reaction_boxes, self.reactions_data
        ):
            # Get table values with safe conversion
            ea_min_str = table.item(0, 0).text().strip()
            ea_max_str = table.item(0, 1).text().strip()
            loga_min_str = table.item(1, 0).text().strip()
            loga_max_str = table.item(1, 1).text().strip()
            contrib_min_str = table.item(2, 0).text().strip()
            contrib_max_str = table.item(2, 1).text().strip()

            def safe_cast(s, default):
                try:
                    return float(s)
                except ValueError:
                    return default

            # Build updated reaction dictionary
            new_r = dict(old_reaction)
            new_r["reaction_type"] = combo_type.currentText()
            new_r["Ea_min"] = safe_cast(ea_min_str, old_reaction.get("Ea_min", 1))
            new_r["Ea_max"] = safe_cast(ea_max_str, old_reaction.get("Ea_max", 2000))
            new_r["log_A_min"] = safe_cast(loga_min_str, old_reaction.get("log_A_min", 0.1))
            new_r["log_A_max"] = safe_cast(loga_max_str, old_reaction.get("log_A_max", 100))
            new_r["contribution_min"] = safe_cast(contrib_min_str, old_reaction.get("contribution_min", 0.01))
            new_r["contribution_max"] = safe_cast(contrib_max_str, old_reaction.get("contribution_max", 1.0))

            # Handle model selection
            many_models_value = many_models_checkbox.isChecked()
            if many_models_value:
                selected_models = add_models_button.selected_models
            else:
                selected_models = [combo_type.currentText()]
            new_r["allowed_models"] = selected_models

            updated_reactions.append(new_r)

        return {"method": selected_method, "method_parameters": method_params}, updated_reactions

    def accept(self):
        """Validate data before accepting dialog."""
        data_result, reactions = self.get_data()
        if data_result is None or reactions is None:
            return
        super().accept()

    def convert_to_type(self, text, default_value):
        """Convert string input to appropriate type based on default value."""
        if text.lower() == "none":
            return None

        try:
            if isinstance(default_value, int):
                return int(text)
            elif isinstance(default_value, float):
                return float(text)
            elif isinstance(default_value, tuple):
                values = text.strip("() ").split(",")
                return tuple(float(v.strip()) for v in values)
            elif isinstance(default_value, str):
                return text
            elif default_value is None:
                if "." in text:
                    return float(text)
                else:
                    return int(text)
            else:
                return text
        except (ValueError, TypeError):
            return default_value

    def validate_parameter(self, key, value):  # noqa: C901
        """
        Validate differential evolution parameter values.

        Args:
            key: Parameter name
            value: Parameter value to validate

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        try:
            if key == "strategy":
                strategies = self.get_options_for_parameter("strategy")
                if value not in strategies:
                    return False, f"Invalid strategy. Choose from {strategies}."
            elif key == "maxiter":
                if not isinstance(value, int) or value < 1:
                    return False, "Must be an integer >= 1."
            elif key == "popsize":
                if not isinstance(value, int) or value < 1:
                    return False, "Must be an integer >= 1."
            elif key == "tol":
                if not isinstance(value, (int, float)) or value < 0:
                    return False, "Must be non-negative."
            elif key == "mutation":
                if isinstance(value, tuple):
                    if len(value) != 2 or not all(0 <= v <= 2 for v in value):
                        return False, "Must be a tuple of two numbers in [0, 2]."
                elif isinstance(value, (int, float)):
                    if not 0 <= value <= 2:
                        return False, "Must be in [0, 2]."
                else:
                    return False, "Invalid format."
            elif key == "recombination":
                if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                    return False, "Must be in [0, 1]."
            elif key == "seed":
                if not (isinstance(value, int) or value is None):
                    return False, "Must be an integer or None."
            elif key == "atol":
                if not isinstance(value, (int, float)) or value < 0:
                    return False, "Must be non-negative."
            elif key == "updating":
                options = self.get_options_for_parameter("updating")
                if value not in options:
                    return False, f"Must be one of {options}."
            elif key == "workers":
                if not isinstance(value, int) or value < 1 or value > 4:
                    return False, "Must be an integer = 1. Parallel processing is not supported. Up to 4 for test"
            return True, ""
        except Exception as e:
            return False, f"Error validating parameter: {str(e)}"

    def get_tooltip_for_parameter(self, param_name):
        """Get tooltip text for differential evolution parameters."""
        tooltips = {
            "strategy": "The strategy for differential evolution.",
            "maxiter": "Maximum number of iterations. Must be >= 1.",
            "popsize": "Population size. Must be >= 1.",
            "tol": "Tolerance. Must be non-negative.",
            "mutation": "Mutation factor in [0, 2] or tuple of two values.",
            "recombination": "Recombination factor in [0, 1].",
            "workers": "Number of processes. Must be 1.",
        }
        return tooltips.get(param_name, "")

    def get_options_for_parameter(self, param_name):
        """Get available options for enumerated parameters."""
        options = {
            "strategy": [
                "best1bin",
                "best1exp",
                "rand1exp",
                "randtobest1exp",
                "currenttobest1exp",
                "best2exp",
                "rand2exp",
                "randtobest1bin",
                "currenttobest1bin",
                "best2bin",
                "rand2bin",
                "rand1bin",
            ],
            "init": ["latinhypercube", "random"],
            "updating": ["immediate", "deferred"],
        }
        return options.get(param_name, [])


class ModelsSelectionDialog(QDialog):
    """
    Dialog for selecting multiple kinetic models.

    Provides a grid of checkboxes for selecting from available nucleation
    and growth models (F1/3, F2, A2, etc.) for multi-model optimization.
    """

    def __init__(self, models_list, parent=None):
        """
        Initialize the models selection dialog.

        Args:
            models_list: List of available model names
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Models")
        self.models_list = models_list
        self.selected_models = []

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create grid of model checkboxes
        grid = QGridLayout()
        layout.addLayout(grid)

        self.checkboxes = []
        col_count = 6

        for index, model in enumerate(models_list):
            checkbox = QCheckBox(model)
            self.checkboxes.append(checkbox)
            row = index // col_count
            col = index % col_count
            grid.addWidget(checkbox, row, col)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_models(self):
        """
        Get list of selected model names.

        Returns:
            list: Names of selected models
        """
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
