"""
Series management and calculation settings dialogs.
Contains dialogs for configuring calculation parameters and model selection.
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
    """Dialog for configuring calculation settings and reaction parameters."""

    def __init__(
        self, reactions_data: list[dict], calculation_method: str, calculation_method_params: dict, parent=None
    ):
        """Initialize calculation settings dialog.

        Args:
            reactions_data: List of reaction configurations
            calculation_method: Current calculation method
            calculation_method_params: Method-specific parameters
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculation_method = calculation_method
        self.calculation_method_params = calculation_method_params
        self.setWindowTitle("Calculation Settings")

        self.reactions_data = reactions_data or []
        self.de_params_edits = {}

        self._setup_ui()
        self.update_method_parameters()

    def _setup_ui(self):
        """Setup the dialog user interface."""
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Left panel - method settings
        left_widget = self._create_left_panel()
        main_layout.addWidget(left_widget)

        # Right panel - reaction settings
        right_widget = self._create_right_panel()
        main_layout.addWidget(right_widget, stretch=1)

    def _create_left_panel(self):
        """Create left panel with method configuration."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Method selection
        method_label = QLabel("Calculation method:")
        self.calculation_method_combo = QComboBox()
        self.calculation_method_combo.addItems(["differential_evolution", "another_method"])
        self.calculation_method_combo.setCurrentText("differential_evolution")
        self.calculation_method_combo.currentTextChanged.connect(self.update_method_parameters)

        left_layout.addWidget(method_label)
        left_layout.addWidget(self.calculation_method_combo)

        # Differential evolution settings
        self.de_group = QGroupBox("Differential Evolution Settings")
        self.de_layout = QFormLayout()
        self.de_group.setLayout(self.de_layout)
        left_layout.addWidget(self.de_group, stretch=0)

        self._setup_de_parameters()
        left_layout.addStretch(1)

        return left_widget

    def _setup_de_parameters(self):
        """Setup differential evolution parameter inputs."""
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

    def _create_right_panel(self):
        """Create right panel with reaction configurations."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Scroll area for reactions
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        self.reactions_grid = QGridLayout(scroll_content)
        scroll_content.setLayout(self.reactions_grid)

        self.reaction_boxes = []
        self._setup_reaction_boxes()

        # Dialog buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        right_layout.addWidget(btn_box)

        return right_widget

    def _setup_reaction_boxes(self):
        """Setup individual reaction configuration boxes."""
        for i, reaction in enumerate(self.reactions_data):
            row = i % 2
            col = i // 2

            box_widget = self._create_reaction_box(reaction)
            self.reactions_grid.addWidget(box_widget, row, col)

    def _create_reaction_box(self, reaction):
        """Create configuration box for a single reaction."""
        box_widget = QWidget()
        box_layout = QVBoxLayout(box_widget)

        # Reaction header
        top_line_widget = QWidget()
        top_line_layout = QHBoxLayout(top_line_widget)

        reaction_label = QLabel(f"{reaction.get('from', '?')} -> {reaction.get('to', '?')}")
        top_line_layout.addWidget(reaction_label)

        combo_type = QComboBox()
        combo_type.addItems(NUC_MODELS_LIST)
        current_type = reaction.get("reaction_type", "F2")
        if current_type in NUC_MODELS_LIST:
            combo_type.setCurrentText(current_type)
        top_line_layout.addWidget(combo_type)

        box_layout.addWidget(top_line_widget)

        # Model selection
        models_selection_widget = self._create_models_selection(reaction)
        box_layout.addWidget(models_selection_widget)

        # Parameter table
        table = self._create_parameter_table(reaction)
        box_layout.addWidget(table)

        # Store components for later retrieval
        many_models_checkbox = models_selection_widget.findChild(QCheckBox)
        add_models_button = models_selection_widget.findChild(QPushButton)

        self.reaction_boxes.append((combo_type, many_models_checkbox, add_models_button, table, reaction_label))

        return box_widget

    def _create_models_selection(self, reaction):
        """Create model selection widgets."""
        models_selection_widget = QWidget()
        models_selection_layout = QHBoxLayout(models_selection_widget)

        many_models_checkbox = QCheckBox("Many models")
        add_models_button = QPushButton("Add models")
        add_models_button.setEnabled(False)
        add_models_button.selected_models = []

        models_selection_layout.addWidget(many_models_checkbox)
        models_selection_layout.addWidget(add_models_button)

        # Connect signals
        many_models_checkbox.stateChanged.connect(
            lambda state, btn=add_models_button: btn.setEnabled(state == Qt.CheckState.Checked.value)
        )

        def open_models_dialog(checked, btn=add_models_button):
            dialog = ModelsSelectionDialog(NUC_MODELS_LIST, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected = dialog.get_selected_models()
                btn.selected_models = selected
                btn.setText(f"Add models ({len(selected)})")

        add_models_button.clicked.connect(open_models_dialog)

        return models_selection_widget

    def _create_parameter_table(self, reaction):
        """Create parameter range table for a reaction."""
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

        # Fill with reaction data
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

        return table

    def update_method_parameters(self):
        """Update parameter visibility based on selected method."""
        selected_method = self.calculation_method_combo.currentText()
        self.de_group.setVisible(selected_method == "differential_evolution")

    def get_data(self):
        """Get dialog data - calculation settings and updated reactions."""
        selected_method = self.calculation_method_combo.currentText()
        errors = []
        method_params = {}

        # Validate and collect method parameters
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
        else:
            method_params = {"info": "No additional params set for another_method"}

        if errors:
            QMessageBox.warning(self, "Invalid DE parameters", "\n".join(errors))
            return None, None

        # Collect updated reaction data
        updated_reactions = self._collect_reaction_data()

        return {"method": selected_method, "method_parameters": method_params}, updated_reactions

    def _collect_reaction_data(self):
        """Collect reaction configuration data from UI."""
        updated_reactions = []

        for (combo_type, many_models_checkbox, add_models_button, table, label_reaction), old_reaction in zip(
            self.reaction_boxes, self.reactions_data
        ):
            # Get table values
            ea_min_str = table.item(0, 0).text().strip()
            ea_max_str = table.item(0, 1).text().strip()
            loga_min_str = table.item(1, 0).text().strip()
            loga_max_str = table.item(1, 1).text().strip()
            contrib_min_str = table.item(2, 0).text().strip()
            contrib_max_str = table.item(2, 1).text().strip()

            # Create updated reaction
            updated_reaction = old_reaction.copy()
            updated_reaction["reaction_type"] = combo_type.currentText()

            # Update range values with validation
            try:
                updated_reaction["Ea_min"] = float(ea_min_str)
                updated_reaction["Ea_max"] = float(ea_max_str)
                updated_reaction["log_A_min"] = float(loga_min_str)
                updated_reaction["log_A_max"] = float(loga_max_str)
                updated_reaction["contribution_min"] = float(contrib_min_str)
                updated_reaction["contribution_max"] = float(contrib_max_str)
            except ValueError:
                # Keep original values if conversion fails
                pass

            # Handle multiple models if selected
            if many_models_checkbox.isChecked():
                selected_models = getattr(add_models_button, "selected_models", [])
                if selected_models:
                    updated_reaction["allowed_models"] = selected_models

            updated_reactions.append(updated_reaction)

        return updated_reactions

    # Helper methods for parameter validation and tooltips
    def get_tooltip_for_parameter(self, param_name):
        """Get tooltip text for a parameter."""
        tooltips = {
            "strategy": "Differential evolution strategy to use",
            "maxiter": "Maximum number of iterations",
            "popsize": "Population size multiplier",
            "workers": "Number of parallel workers",
            "polish": "Whether to polish final result",
        }
        return tooltips.get(param_name, f"Parameter: {param_name}")

    def get_options_for_parameter(self, param_name):
        """Get valid options for choice parameters."""
        options = {
            "strategy": ["best1bin", "best1exp", "rand1exp", "randtobest1exp", "currenttobest1exp"],
            "init": ["latinhypercube", "random"],
            "updating": ["immediate", "deferred"],
        }
        return options.get(param_name, ["default"])

    def convert_to_type(self, text, default_value):
        """Convert text input to appropriate type with tuple support."""
        if default_value is None:
            return text if text != "None" else None

        if isinstance(default_value, int):
            return int(text)
        elif isinstance(default_value, float):
            return float(text)
        elif isinstance(default_value, bool):
            return text.lower() in ("true", "1", "yes")
        elif isinstance(default_value, tuple):
            # Handle tuple conversion from string representation
            if text.strip() == "()":
                return ()
            try:
                # Safe evaluation of tuple literals like "(0.5, 1)"
                import ast

                result = ast.literal_eval(text)
                if isinstance(result, tuple):
                    return result
                elif isinstance(result, (int, float)):
                    return (result,)  # Convert single number to single-element tuple
                else:
                    return default_value
            except (ValueError, SyntaxError):
                return default_value
        else:
            return text

    def validate_parameter(self, param_name, value):
        """Validate parameter value with support for tuple types."""
        # Basic numeric validations
        if param_name == "maxiter":
            return self._validate_positive_integer(value)
        if param_name == "popsize":
            return self._validate_positive_integer(value)
        if param_name == "workers":
            return self._validate_min_integer(value, 1)

        # Complex type validations
        if param_name == "mutation":
            return self._validate_mutation(value)
        if param_name == "constraints":
            return self._validate_constraints(value)

        return True, ""

    def _validate_positive_integer(self, value):
        """Validate that value is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            return False, "Must be a positive integer"
        return True, ""

    def _validate_min_integer(self, value, min_val):
        """Validate that value is an integer >= min_val."""
        if not isinstance(value, int) or value < min_val:
            return False, f"Must be an integer >= {min_val}"
        return True, ""

    def _validate_mutation(self, value):
        """Validate mutation parameter (number or tuple of two numbers)."""
        if isinstance(value, tuple):
            if len(value) != 2:
                return False, "Must be a tuple of two numbers"
            if not all(isinstance(x, (int, float)) for x in value):
                return False, "Must be a tuple of two numbers"
            if not all(0 <= x <= 2 for x in value):
                return False, "Values must be between 0 and 2"
        elif isinstance(value, (int, float)):
            if not (0 <= value <= 2):
                return False, "Value must be between 0 and 2"
        else:
            return False, "Must be a number or tuple of two numbers"
        return True, ""

    def _validate_constraints(self, value):
        """Validate constraints parameter (must be tuple)."""
        if not isinstance(value, tuple):
            return False, "Must be a tuple"
        return True, ""


class ModelsSelectionDialog(QDialog):
    """Dialog for selecting multiple models from a list."""

    def __init__(self, models_list, parent=None):
        """Initialize models selection dialog.

        Args:
            models_list: List of available model names
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Models")
        self.models_list = models_list
        self.selected_models = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog user interface."""
        layout = QVBoxLayout(self)

        # Create grid of checkboxes
        grid = QGridLayout()
        layout.addLayout(grid)

        self.checkboxes = []
        col_count = 6

        for index, model in enumerate(self.models_list):
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
        """Get list of selected model names."""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
