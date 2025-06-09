"""
Calculation Dialogs Component

This module provides dialog components for configuring calculation and deconvolution settings
for kinetic analysis reactions.
"""

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from src.core.app_settings import MODEL_FREE_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS


class CalculationSettingsDialog(QDialog):
    """
    Dialog for configuring calculation and deconvolution settings.

    Allows users to select functions for reactions and configure deconvolution parameters
    including method selection and parameter validation.
    """

    def __init__(self, reactions, initial_settings, initial_deconvolution_settings, parent=None):
        """
        Initialize the calculation settings dialog.

        Args:
            reactions (dict): Dictionary of reaction names to ComboBox widgets
            initial_settings (dict): Initial function settings for reactions
            initial_deconvolution_settings (dict): Initial deconvolution method settings
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("calculation settings")
        self.reactions = reactions
        self.initial_settings = initial_settings
        self.initial_deconvolution_settings = initial_deconvolution_settings

        self.checkboxes = {}
        self.de_parameters = {}

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)

        # Create reactions group
        reactions_group_box = QGroupBox("functions")
        reactions_layout = QGridLayout()
        reactions_group_box.setLayout(reactions_layout)

        self.checkboxes = {}
        row = 0

        for reaction_name, combo in self.reactions.items():
            functions = [combo.itemText(i) for i in range(combo.count())]
            self.checkboxes[reaction_name] = []
            col = 0

            reaction_label = QLabel(reaction_name)
            reactions_layout.addWidget(reaction_label, row, col)
            col += 1

            for function in functions:
                checkbox = QCheckBox(function)
                checkbox.setChecked(function in self.initial_settings.get(reaction_name, []))
                self.checkboxes[reaction_name].append(checkbox)
                reactions_layout.addWidget(checkbox, row, col)
                col += 1
            row += 1

        main_layout.addWidget(reactions_group_box)

        # Create deconvolution parameters group
        deconvolution_group_box = QGroupBox("deconvolution parameters")
        deconvolution_layout = QVBoxLayout()
        deconvolution_group_box.setLayout(deconvolution_layout)

        method_layout = QHBoxLayout()
        method_label = QLabel("deconvolution method:")
        self.deconvolution_method_combo = QComboBox()
        self.deconvolution_method_combo.addItems(["differential_evolution", "another_method"])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.deconvolution_method_combo)
        deconvolution_layout.addLayout(method_layout)

        self.method_parameters_layout = QGridLayout()
        deconvolution_layout.addLayout(self.method_parameters_layout)

        main_layout.addWidget(deconvolution_group_box)

        # Set initial method if available
        if self.initial_deconvolution_settings:
            initial_method = self.initial_deconvolution_settings.get("method", "differential_evolution")
            index = self.deconvolution_method_combo.findText(initial_method)
            if index >= 0:
                self.deconvolution_method_combo.setCurrentIndex(index)
        else:
            self.deconvolution_method_combo.setCurrentText("differential_evolution")

        self._update_method_parameters()
        self.deconvolution_method_combo.currentIndexChanged.connect(self._update_method_parameters)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _update_method_parameters(self):
        """Update the displayed parameters for the selected deconvolution method."""
        # Clear previous parameters
        while self.method_parameters_layout.count():
            item = self.method_parameters_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        selected_method = self.deconvolution_method_combo.currentText()

        if selected_method == "differential_evolution":
            self.de_parameters = {}
            initial_params = {}

            if (
                self.initial_deconvolution_settings
                and self.initial_deconvolution_settings.get("method") == selected_method
            ):
                initial_params = self.initial_deconvolution_settings.get("method_parameters", {})

            row = 0
            for key, value in MODEL_FREE_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS.items():
                label = QLabel(key)
                tooltip = self._get_tooltip_for_parameter(key)
                label.setToolTip(tooltip)

                # Choose widget type based on parameter type
                if isinstance(value, bool):
                    field = QCheckBox()
                    field.setChecked(initial_params.get(key, value))
                    field.setToolTip(tooltip)
                elif key in ["strategy", "init", "updating"]:
                    field = QComboBox()
                    options = self._get_options_for_parameter(key)
                    field.addItems(options)
                    field.setCurrentText(initial_params.get(key, value))
                    field.setToolTip(tooltip)
                else:
                    field = QLineEdit(str(initial_params.get(key, value)))
                    field.setToolTip(tooltip)

                self.de_parameters[key] = field
                self.method_parameters_layout.addWidget(label, row, 0)
                self.method_parameters_layout.addWidget(field, row, 1)
                row += 1

    def _get_tooltip_for_parameter(self, param_name: str) -> str:
        """Get tooltip text for a parameter."""
        tooltips = {
            "strategy": "The strategy for differential evolution. Choose one of the available options.",
            "maxiter": "Maximum number of iterations. An integer >= 1.",
            "popsize": "Population size. An integer >= 1.",
            "tol": "Relative tolerance for stop criteria. A non-negative number.",
            "mutation": "Mutation factor. A number or tuple of two numbers in [0, 2].",
            "recombination": "Recombination factor in [0, 1].",
            "seed": "Random seed. An integer or None.",
            "callback": "Callback function. Leave empty if not required.",
            "disp": "Display status during optimization.",
            "polish": "Perform a final polish optimization after differential evolution is done.",
            "init": "Population initialization method.",
            "atol": "Absolute tolerance for stop criteria. A non-negative number.",
            "updating": "Population updating mode: immediate or deferred.",
            "workers": "Number of processes for parallel computing. Must be 1 here.",
            "constraints": "Constraints for the optimization. Leave empty if not required.",
        }
        return tooltips.get(param_name, "")

    def _get_options_for_parameter(self, param_name: str) -> list:
        """Get valid options for a parameter."""
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

    def get_selected_functions(self):
        """
        Get the selected functions for each reaction and the chosen deconvolution method and parameters.

        Returns:
            tuple: (selected_functions (dict), selected_method (str), deconvolution_parameters (dict))
        """
        selected_functions = {}
        for reaction_name, checkboxes in self.checkboxes.items():
            selected_functions[reaction_name] = [cb.text() for cb in checkboxes if cb.isChecked()]

        selected_method, deconvolution_parameters = self._get_deconvolution_parameters()
        return selected_functions, selected_method, deconvolution_parameters

    def _get_deconvolution_parameters(self):
        """
        Validate and retrieve deconvolution parameters for the selected method.

        Returns:
            tuple: (selected_method (str), parameters (dict))
        """
        selected_method = self.deconvolution_method_combo.currentText()
        parameters = {}
        errors = []

        if selected_method == "differential_evolution":
            for key, field in self.de_parameters.items():
                if isinstance(field, QCheckBox):
                    parameters[key] = field.isChecked()
                elif isinstance(field, QComboBox):
                    parameters[key] = field.currentText()
                else:
                    text = field.text()
                    default_value = MODEL_FREE_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS[key]
                    value = self._convert_to_type(text, default_value)

                    is_valid, error_msg = self._validate_parameter(key, value)
                    if not is_valid:
                        errors.append(f"Parameter '{key}': {error_msg}")
                    parameters[key] = value

            if errors:
                error_message = "\n".join(errors)
                QMessageBox.warning(self, "Error entering parameters", error_message)
                return None, None

        elif selected_method == "another_method":
            parameters = {}

        return selected_method, parameters

    def _convert_to_type(self, text: str, default_value):
        """
        Convert text input into the appropriate type based on the default value type.

        Args:
            text (str): The string to convert
            default_value: The default value to infer type

        Returns:
            Converted value or the default value if conversion fails
        """
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
                if text == "" or text.lower() == "none":
                    return None
                else:
                    return text
            else:
                return text
        except ValueError:
            return default_value

    def _validate_parameter(self, key: str, value):
        """Validate a parameter's value according to differential evolution rules."""
        # Simple validation for commonly used parameters
        validators = {
            "strategy": self._validate_strategy,
            "maxiter": self._validate_positive_int,
            "popsize": self._validate_positive_int,
            "tol": self._validate_non_negative_number,
            "atol": self._validate_non_negative_number,
            "workers": self._validate_positive_int,
        }

        if key in validators:
            return validators[key](value)
        return True, ""

    def _validate_strategy(self, value):
        """Validate strategy parameter."""
        valid_strategies = self._get_options_for_parameter("strategy")
        if value not in valid_strategies:
            return False, f"Invalid strategy. Choose from {valid_strategies}."
        return True, ""

    def _validate_positive_int(self, value):
        """Validate positive integer parameters."""
        if not isinstance(value, int) or value < 1:
            return False, "Must be an integer >= 1."
        return True, ""

    def _validate_non_negative_number(self, value):
        """Validate non-negative numeric parameters."""
        if not isinstance(value, (int, float)) or value < 0:
            return False, "Must be a number >= 0."
        return True, ""

    def accept(self):
        """Validate settings before closing the dialog."""
        selected_functions = {}
        for reaction_name, checkboxes in self.checkboxes.items():
            selected = [cb.text() for cb in checkboxes if cb.isChecked()]
            if not selected:
                QMessageBox.warning(
                    self, "Settings error", f"Reaction '{reaction_name}' must have at least one function."
                )
                return
            selected_functions[reaction_name] = selected

        selected_method, deconvolution_parameters = self._get_deconvolution_parameters()
        if deconvolution_parameters is None:
            # Error in parameters, do not close the dialog
            return

        self.selected_functions = selected_functions
        self.selected_method = selected_method
        self.deconvolution_parameters = deconvolution_parameters
        super().accept()

    def get_results(self):
        """Get the results selected in the dialog."""
        return self.selected_functions, self.selected_method, self.deconvolution_parameters
