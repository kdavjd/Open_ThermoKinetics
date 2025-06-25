"""
Settings dialog for configuring deconvolution calculation parameters.

This module provides a comprehensive dialog for setting up calculation
and deconvolution parameters for reactions, including differential evolution
optimization settings.
"""

from typing import Any, Dict, Optional, Tuple

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

from src.core.app_settings import DECONVOLUTION_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS

from .config import DeconvolutionConfig


class CalculationSettingsDialog(QDialog):
    """
    Dialog for configuring calculation and deconvolution settings.

    This dialog allows users to:
    - Select which functions to use for each reaction
    - Choose deconvolution method and parameters
    - Configure differential evolution optimization settings
    """

    def __init__(
        self,
        reactions: Dict[str, Any],
        initial_settings: Dict[str, Any],
        initial_deconvolution_settings: Dict[str, Any],
        parent=None,
    ):
        """
        Initialize the settings dialog.

        Args:
            reactions: Dictionary mapping reaction names to ComboBox widgets
            initial_settings: Previously selected function settings
            initial_deconvolution_settings: Previously selected deconvolution settings
            parent: Parent widget
        """
        super().__init__(parent)

        self.config = DeconvolutionConfig()
        self.setWindowTitle(self.config.labels.calculation_settings_title)

        self.reactions = reactions
        self.initial_settings = initial_settings
        self.initial_deconvolution_settings = initial_deconvolution_settings

        # Initialize result storage
        self.selected_functions = {}
        self.selected_method = ""
        self.deconvolution_parameters = {}

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)

        # Create reactions group box
        self._create_reactions_group(main_layout)

        # Create deconvolution parameters group box
        self._create_deconvolution_group(main_layout)

        # Create button box
        self._create_button_box(main_layout)

        # Initialize method parameters
        self._set_initial_method()
        self.update_method_parameters()
        self.deconvolution_method_combo.currentIndexChanged.connect(self.update_method_parameters)

    def _create_reactions_group(self, main_layout: QVBoxLayout):
        """Create the reactions function selection group."""
        reactions_group_box = QGroupBox(self.config.dialog_layout.reactions_groupbox_title)
        reactions_layout = QGridLayout()
        reactions_group_box.setLayout(reactions_layout)

        self.checkboxes = {}
        row = 0

        for reaction_name, combo in self.reactions.items():
            # Get available functions from combo box
            functions = [combo.itemText(i) for i in range(combo.count())]
            self.checkboxes[reaction_name] = []

            # Add reaction name label
            col = 0
            reaction_label = QLabel(reaction_name)
            reactions_layout.addWidget(reaction_label, row, col)
            col += 1

            # Add function checkboxes
            for function in functions:
                checkbox = QCheckBox(function)
                # Set initial state from previous settings
                checkbox.setChecked(function in self.initial_settings.get(reaction_name, []))
                self.checkboxes[reaction_name].append(checkbox)
                reactions_layout.addWidget(checkbox, row, col)
                col += 1

            row += 1

        main_layout.addWidget(reactions_group_box)

    def _create_deconvolution_group(self, main_layout: QVBoxLayout):
        """Create the deconvolution parameters group."""
        deconvolution_group_box = QGroupBox(self.config.dialog_layout.deconvolution_groupbox_title)
        deconvolution_layout = QVBoxLayout()
        deconvolution_group_box.setLayout(deconvolution_layout)

        # Method selection
        method_layout = QHBoxLayout()
        method_label = QLabel(self.config.labels.deconvolution_method_label)
        self.deconvolution_method_combo = QComboBox()
        self.deconvolution_method_combo.addItems(self.config.defaults.method_options)

        method_layout.addWidget(method_label)
        method_layout.addWidget(self.deconvolution_method_combo)
        deconvolution_layout.addLayout(method_layout)

        # Method parameters layout (will be populated dynamically)
        self.method_parameters_layout = QGridLayout()
        deconvolution_layout.addLayout(self.method_parameters_layout)

        main_layout.addWidget(deconvolution_group_box)

    def _create_button_box(self, main_layout: QVBoxLayout):
        """Create the dialog button box."""
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _set_initial_method(self):
        """Set the initial deconvolution method from previous settings."""
        if self.initial_deconvolution_settings:
            initial_method = self.initial_deconvolution_settings.get("method", self.config.defaults.default_method)
            index = self.deconvolution_method_combo.findText(initial_method)
            if index >= 0:
                self.deconvolution_method_combo.setCurrentIndex(index)
        else:
            self.deconvolution_method_combo.setCurrentText(self.config.defaults.default_method)

    def update_method_parameters(self):
        """
        Update the displayed parameters for the selected deconvolution method.
        Clears previous parameters and populates the layout with fields for the current method.
        """
        # Clear existing parameters
        while self.method_parameters_layout.count():
            item = self.method_parameters_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        selected_method = self.deconvolution_method_combo.currentText()

        if selected_method == "differential_evolution":
            self._create_differential_evolution_parameters()
        elif selected_method == "another_method":
            # No parameters defined for this method
            pass

    def _create_differential_evolution_parameters(self):
        """Create parameter input fields for differential evolution method."""
        self.de_parameters = {}

        # Get initial parameters if available
        initial_params = {}
        if (
            self.initial_deconvolution_settings
            and self.initial_deconvolution_settings.get("method") == "differential_evolution"
        ):
            initial_params = self.initial_deconvolution_settings.get("method_parameters", {})

        row = 0
        for key, default_value in DECONVOLUTION_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS.items():
            # Create label with tooltip
            label = QLabel(key)
            tooltip = self._get_tooltip_for_parameter(key)
            label.setToolTip(tooltip)  # Create appropriate input widget based on parameter type
            if isinstance(default_value, bool):
                field = QCheckBox()
                field.setChecked(initial_params.get(key, default_value))
                field.setToolTip(tooltip)
            elif key in ["strategy", "init", "updating"]:
                field = QComboBox()
                options = self._get_options_for_parameter(key)
                field.addItems(options)
                field.setCurrentText(str(initial_params.get(key, default_value)))
                field.setToolTip(tooltip)
            else:
                field = QLineEdit(str(initial_params.get(key, default_value)))
                field.setToolTip(tooltip)

            # Store field reference and add to layout
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
        if param_name == "strategy":
            return self.config.calculation_settings.strategy_options
        elif param_name == "init":
            return self.config.calculation_settings.init_options
        elif param_name == "updating":
            return self.config.calculation_settings.updating_options
        return []

    def get_selected_functions(self) -> Tuple[Dict[str, list], str, Dict[str, Any]]:
        """
        Get the selected functions for each reaction and deconvolution parameters.

        Returns:
            Tuple containing:
            - selected_functions: Dict mapping reaction names to selected function lists
            - selected_method: Name of selected deconvolution method
            - deconvolution_parameters: Dict of method parameters
        """
        # Get selected functions
        selected_functions = {}
        for reaction_name, checkboxes in self.checkboxes.items():
            selected_functions[reaction_name] = [cb.text() for cb in checkboxes if cb.isChecked()]

        # Get deconvolution parameters
        selected_method, deconvolution_parameters = self.get_deconvolution_parameters()

        return selected_functions, selected_method, deconvolution_parameters

    def get_deconvolution_parameters(self) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate and retrieve deconvolution parameters for the selected method.

        Returns:
            Tuple containing:
            - selected_method: Name of selected method (None if validation failed)
            - parameters: Dict of validated parameters (None if validation failed)
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
                    default_value = DECONVOLUTION_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS[key]
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

    def _convert_to_type(self, text: str, default_value: Any) -> Any:
        """
        Convert text input into the appropriate type based on the default value type.

        Args:
            text: The string to convert
            default_value: The default value to infer type from

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

    def _validate_parameter(self, key: str, value: Any) -> Tuple[bool, str]:  # noqa: C901
        """
        Validate a parameter's value according to differential evolution rules.

        Args:
            key: Parameter name
            value: Parameter value

        Returns:
            Tuple containing:
            - is_valid: True if value is valid
            - error_message: Error description if not valid, empty string if valid
        """
        try:
            if key == "strategy":
                strategies = self._get_options_for_parameter("strategy")
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
                    return False, "Must be a non-negative number."
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
                    return False, "Must be a non-negative number."
            elif key == "updating":
                options = self._get_options_for_parameter("updating")
                if value not in options:
                    return False, f"Must be one of {options}."
            elif key == "workers":
                # The code currently does not support parallel processes other than 1
                if not isinstance(value, int) or value < 1 or value > 1:
                    return False, "Must be an integer = 1. Parallel processing is not supported."

            return True, ""

        except Exception as e:
            return False, f"Error validating parameter: {str(e)}"

    def accept(self):
        """
        Validate settings before closing the dialog.
        Ensures each reaction has at least one function selected and parameters are valid.
        """
        # Validate function selections
        selected_functions = {}
        for reaction_name, checkboxes in self.checkboxes.items():
            selected = [cb.text() for cb in checkboxes if cb.isChecked()]
            if not selected:
                QMessageBox.warning(
                    self, "Settings error", f"Reaction '{reaction_name}' must have at least one function."
                )
                return
            selected_functions[reaction_name] = selected

        # Validate deconvolution parameters
        selected_method, deconvolution_parameters = self.get_deconvolution_parameters()
        if deconvolution_parameters is None:
            # Error in parameters, do not close the dialog
            return

        # Store results
        self.selected_functions = selected_functions
        self.selected_method = selected_method
        self.deconvolution_parameters = deconvolution_parameters

        super().accept()

    def get_results(self) -> Tuple[Dict[str, list], str, Dict[str, Any]]:
        """
        Get the results selected in the dialog.

        Returns:
            Tuple containing selected functions, method, and parameters
        """
        return self.selected_functions, self.selected_method, self.deconvolution_parameters
