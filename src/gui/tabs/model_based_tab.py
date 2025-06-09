"""
Model-Based Kinetics Analysis Tab

This module provides the main coordinator widget for model-based kinetics analysis,
integrating reaction scheme editor, parameter tables, calculation controls, and
optimization settings for multi-step kinetic modeling.
"""

import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget
from scipy.integrate import solve_ivp

from src.core.app_settings import NUC_MODELS_LIST, NUC_MODELS_TABLE, OperationType
from src.core.logger_config import logger
from src.gui.controls.adjustment_controls import AdjustingSettingsBox
from src.gui.controls.model_calculation_controls import ModelCalcButtons, RangeAndCalculateWidget
from src.gui.dialogs.model_dialogs import CalculationSettingsDialog
from src.gui.modeling.modeling_config import get_modeling_config
from src.gui.modeling.models_scheme import ModelsScheme
from src.gui.tables.reaction_table import ModelReactionTable


class ModelBasedTab(QWidget):
    """
    Main widget for model-based kinetics analysis.

    Provides integrated interface for defining reaction schemes, setting kinetic
    parameters, configuring optimization bounds, and running multi-step kinetic
    simulations with various nucleation and growth models.

    Signals:
        model_params_changed: Emitted when model parameters or settings change
    """

    model_params_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Initialize the model-based analysis tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Internal state
        self._scheme_data = {}
        self._reactions_list = []
        self._calculation_method = None
        self._calculation_method_params = {}
        self._best_values_cache = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface components."""
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Configuration
        config = get_modeling_config()

        # Reaction selection combo box
        self.reactions_combo = QComboBox()
        self.reactions_combo.setMinimumSize(
            config.model_based_tab.reactions_combo_min_width, config.model_based_tab.reactions_combo_min_height
        )
        main_layout.addWidget(self.reactions_combo)

        # Reaction type selection
        reaction_type_layout = QHBoxLayout()
        reaction_type_label = QLabel("Reaction type:")
        self.reaction_type_combo = QComboBox()
        self.reaction_type_combo.setMinimumSize(
            config.model_based_tab.reaction_type_combo_min_width, config.model_based_tab.reaction_type_combo_min_height
        )
        self.reaction_type_combo.addItems(NUC_MODELS_LIST)

        reaction_type_layout.addWidget(reaction_type_label)
        reaction_type_layout.addWidget(self.reaction_type_combo)
        main_layout.addLayout(reaction_type_layout)

        # Range and calculation controls
        self.range_calc_widget = RangeAndCalculateWidget()
        self.range_calc_widget.setMinimumHeight(config.model_based_tab.range_calc_widget_min_height)
        main_layout.addWidget(self.range_calc_widget)

        # Reaction parameters table
        self.reaction_table = ModelReactionTable()
        self.reaction_table.setMinimumHeight(config.model_based_tab.reaction_table_min_height)
        main_layout.addWidget(self.reaction_table)

        # Configure table layout
        for col in range(self.reaction_table.columnCount()):
            self.reaction_table.setColumnWidth(col, 80)
        for row in range(self.reaction_table.rowCount()):
            self.reaction_table.setRowHeight(row, 30)

        # Parameter adjustment controls
        self.adjusting_settings_box = AdjustingSettingsBox()
        self.adjusting_settings_box.setMinimumHeight(config.model_based_tab.adjusting_settings_box_min_height)
        main_layout.addWidget(self.adjusting_settings_box)

        # Bottom section layout
        bottom_layout = QVBoxLayout()

        # Models scheme editor
        self.models_scene = ModelsScheme(self)
        self.models_scene.setMinimumSize(
            config.model_based_tab.models_scene_min_width, config.model_based_tab.models_scene_min_height
        )
        bottom_layout.addWidget(self.models_scene)

        # Calculation buttons
        self.calc_buttons = ModelCalcButtons(self)
        self.calc_buttons.settings_button.setFixedSize(
            config.model_based_tab.calc_button_width, config.model_based_tab.calc_button_height
        )
        self.calc_buttons.start_button.setFixedSize(
            config.model_based_tab.calc_button_width, config.model_based_tab.calc_button_height
        )
        self.calc_buttons.stop_button.setFixedSize(
            config.model_based_tab.calc_button_width, config.model_based_tab.calc_button_height
        )
        bottom_layout.addWidget(self.calc_buttons)

        main_layout.addLayout(bottom_layout)

    def _connect_signals(self):
        """Connect widget signals to their handlers."""
        # Table parameter changes
        self.reaction_table.activation_energy_edit.editingFinished.connect(self._on_params_changed)
        self.reaction_table.log_a_edit.editingFinished.connect(self._on_params_changed)
        self.reaction_table.contribution_edit.editingFinished.connect(self._on_params_changed)
        self.reaction_table.ea_min_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.ea_max_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.log_a_min_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.log_a_max_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.contribution_min_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.contribution_max_item.editingFinished.connect(self._on_params_changed)

        # Combo box changes
        self.reaction_type_combo.currentIndexChanged.connect(self._on_params_changed)
        self.reactions_combo.currentIndexChanged.connect(self._on_reactions_combo_changed)

        # Adjustment controls
        self.adjusting_settings_box.ea_adjuster.valueChanged.connect(self.on_adjuster_value_changed)
        self.adjusting_settings_box.log_a_adjuster.valueChanged.connect(self.on_adjuster_value_changed)
        self.adjusting_settings_box.contrib_adjuster.valueChanged.connect(self.on_adjuster_value_changed)

        # Range and calculation controls
        self.range_calc_widget.showRangeToggled.connect(self.on_show_range_checkbox_changed)
        self.range_calc_widget.calculateToggled.connect(self.on_calculate_toggled)  # Calculation buttons
        self.calc_buttons.settings_button.clicked.connect(self.open_settings)

    def update_best_values(self, best_values_data: dict):
        """
        Update cached best optimization values for reactions.

        Args:
            best_values_data: Dictionary containing optimized parameter values
        """
        if not best_values_data:
            logger.debug("ModelBasedTab.update_best_values: No data provided")
            return

        reaction_index = best_values_data.get("reaction_index", 0)

        self._best_values_cache[reaction_index] = {
            "Ea": best_values_data.get("Ea"),
            "logA": best_values_data.get("logA"),
            "contribution": best_values_data.get("contribution"),
        }

        logger.debug(f"ModelBasedTab.update_best_values: Cached best values for reaction {reaction_index}")

        current_index = self.reactions_combo.currentIndex()
        if reaction_index == current_index:
            logger.debug(
                f"ModelBasedTab.update_best_values: " f"Updating Value fields for current reaction {reaction_index}"
            )
            self.reaction_table.update_value_with_best(self._best_values_cache[reaction_index])
            self._on_params_changed()
        else:
            logger.debug(
                f"ModelBasedTab.update_best_values: Reaction {reaction_index} is not currently selected "
                f"(current: {current_index}), values cached for later display"
            )

    def on_adjuster_value_changed(self, parameter_name: str, new_value: float):
        """
        Handle parameter adjustment through slider controls.

        Args:
            parameter_name: Name of the parameter being adjusted
            new_value: New parameter value
        """
        if parameter_name == "Ea":
            self.reaction_table.activation_energy_edit.setText(str(new_value))
        elif parameter_name == "log_A":
            self.reaction_table.log_a_edit.setText(str(new_value))
        elif parameter_name == "contribution":
            self.reaction_table.contribution_edit.setText(str(new_value))
        self._on_params_changed()

    def on_show_range_checkbox_changed(self, checked: bool):
        """
        Toggle visibility of parameter range columns.

        Args:
            checked: Whether range columns should be visible
        """
        self.reaction_table.set_ranges_visible(checked)

    def on_calculate_toggled(self, checked: bool):
        """
        Handle calculation toggle state changes.

        Args:
            checked: Whether calculation is enabled
        """
        pass  # Placeholder for future functionality

    def update_scheme_data(self, scheme_data: dict):
        """
        Update the reaction scheme data and refresh UI components.

        Args:
            scheme_data: Dictionary containing reaction scheme configuration
        """
        self._scheme_data = scheme_data
        self._reactions_list = scheme_data.get("reactions", [])

        # Save current selection
        current_label = self.reactions_combo.currentText() if self.reactions_combo.count() > 0 else None

        # Update reactions combo box
        self.reactions_combo.clear()
        reaction_map = {}
        for i, reaction in enumerate(self._reactions_list):
            label = f"{reaction.get('from', '?')} -> {reaction.get('to', '?')}"
            self.reactions_combo.addItem(label)
            reaction_map[label] = i

        # Restore selection or use default
        default_label = "A -> B"
        new_index = reaction_map.get(current_label, reaction_map.get(default_label, 0))

        if not self._reactions_list:
            self.reaction_table.update_table({})
        else:
            self.reactions_combo.setCurrentIndex(new_index)
            self._on_reactions_combo_changed(new_index)

        # Update scheme visualization
        self.models_scene.update_from_scheme(scheme_data, self._reactions_list)

    def update_calculation_settings(self, calculation_settings: dict):
        """
        Update calculation method and parameters.

        Args:
            calculation_settings: Dictionary containing method and parameters
        """
        self._calculation_method = calculation_settings.get("method")
        self._calculation_method_params = calculation_settings.get("method_parameters")

    def _on_reactions_combo_changed(self, index: int):
        """
        Handle reaction selection changes.

        Args:
            index: Index of selected reaction
        """
        if 0 <= index < len(self._reactions_list):
            reaction_data = self._reactions_list[index]
            self.reaction_table.update_table(reaction_data)

            # Apply cached best values if available
            if index in self._best_values_cache:
                logger.debug(
                    f"ModelBasedTab._on_reactions_combo_changed: " f"Applying cached best values for reaction {index}"
                )
                self.reaction_table.update_value_with_best(self._best_values_cache[index])

            # Update adjustment controls
            config = get_modeling_config()
            defaults = config.reaction_defaults

            ea_value = reaction_data.get("Ea", defaults.ea_default)
            log_a_value = reaction_data.get("log_A", defaults.log_a_default)
            contrib_value = reaction_data.get("contribution", defaults.contribution_default)

            # Update adjusters
            self.adjusting_settings_box.ea_adjuster.base_value = ea_value
            self.adjusting_settings_box.ea_adjuster.slider.setValue(0)
            self.adjusting_settings_box.ea_adjuster.update_label()

            self.adjusting_settings_box.log_a_adjuster.base_value = log_a_value
            self.adjusting_settings_box.log_a_adjuster.slider.setValue(0)
            self.adjusting_settings_box.log_a_adjuster.update_label()

            self.adjusting_settings_box.contrib_adjuster.base_value = contrib_value
            self.adjusting_settings_box.contrib_adjuster.slider.setValue(0)
            self.adjusting_settings_box.contrib_adjuster.update_label()

            # Update reaction type combo
            new_reaction_type = reaction_data.get("reaction_type", "F2")
            current_reaction_type = self.reaction_type_combo.currentText()
            if new_reaction_type != current_reaction_type:
                was_blocked = self.reaction_type_combo.blockSignals(True)
                self.reaction_type_combo.setCurrentText(new_reaction_type)
                self.reaction_type_combo.blockSignals(was_blocked)
        else:
            self.reaction_table.update_table({})

    @pyqtSlot()
    def _on_params_changed(self):  # noqa: C901
        """Handle parameter changes and emit update signals."""
        current_index = self.reactions_combo.currentIndex()
        if not (0 <= current_index < len(self._reactions_list)):
            return

        from_comp = self._reactions_list[current_index].get("from")
        to_comp = self._reactions_list[current_index].get("to")
        reaction_type = self.reaction_type_combo.currentText()

        # Parse parameter values with fallbacks
        try:
            ea_val = float(self.reaction_table.activation_energy_edit.text())
        except ValueError:
            ea_val = 120

        try:
            loga_val = float(self.reaction_table.log_a_edit.text())
        except ValueError:
            loga_val = 8

        try:
            contrib_val = float(self.reaction_table.contribution_edit.text())
        except ValueError:
            contrib_val = 0.5

        try:
            ea_min_val = float(self.reaction_table.ea_min_item.text())
        except ValueError:
            ea_min_val = self.reaction_table.defaults.ea_range[0]

        try:
            ea_max_val = float(self.reaction_table.ea_max_item.text())
        except ValueError:
            ea_max_val = self.reaction_table.defaults.ea_range[1]

        try:
            loga_min_val = float(self.reaction_table.log_a_min_item.text())
        except ValueError:
            loga_min_val = self.reaction_table.defaults.log_a_range[0]

        try:
            loga_max_val = float(self.reaction_table.log_a_max_item.text())
        except ValueError:
            loga_max_val = self.reaction_table.defaults.log_a_range[1]

        try:
            contrib_min_val = float(self.reaction_table.contribution_min_item.text())
        except ValueError:
            contrib_min_val = self.reaction_table.defaults.contribution_range[0]

        try:
            contrib_max_val = float(self.reaction_table.contribution_max_item.text())
        except ValueError:
            contrib_max_val = self.reaction_table.defaults.contribution_range[1]

        # Update scheme data
        new_scheme = self._scheme_data.copy()

        for r in new_scheme.get("reactions", []):
            if r.get("from") == from_comp and r.get("to") == to_comp:
                r["reaction_type"] = reaction_type
                r["Ea"] = ea_val
                r["log_A"] = loga_val
                r["contribution"] = contrib_val
                r["Ea_min"] = ea_min_val
                r["Ea_max"] = ea_max_val
                r["log_A_min"] = loga_min_val
                r["log_A_max"] = loga_max_val
                r["contribution_min"] = contrib_min_val
                r["contribution_max"] = contrib_max_val
                break

        # Emit update signal
        update_data = {
            "operation": OperationType.MODEL_PARAMS_CHANGE,
            "reaction_scheme": new_scheme,
            "is_calculate": True if self.range_calc_widget.calculateCheckbox.isChecked() else None,
        }
        self.model_params_changed.emit(update_data)

    def open_settings(self):
        """Open the calculation settings dialog."""
        if not self._reactions_list:
            QMessageBox.information(self, "No Reactions", "There are no available reactions to configure.")
            return

        dialog = CalculationSettingsDialog(
            self._reactions_list, self._calculation_method, self._calculation_method_params, parent=self
        )

        if dialog.exec():
            new_calculation_settings, updated_reactions = dialog.get_data()

            self._reactions_list = updated_reactions

            # Update scheme data with new reaction parameters
            if self._scheme_data and "reactions" in self._scheme_data:
                for i, r in enumerate(self._scheme_data["reactions"]):
                    if i < len(updated_reactions):
                        self._scheme_data["reactions"][i] = updated_reactions[i]

            # Emit update signal
            update_data = {
                "operation": OperationType.MODEL_PARAMS_CHANGE,
                "reaction_scheme": self._scheme_data,
                "calculation_settings": new_calculation_settings,
                "is_calculate": True if self.range_calc_widget.calculateCheckbox.isChecked() else None,
            }
            self.model_params_changed.emit(update_data)

            QMessageBox.information(self, "Settings Saved", "The settings have been updated successfully.")

    def _simulate_reaction_model(self, experimental_data: pd.DataFrame, reaction_scheme: dict):
        """
        Simulate reaction kinetics based on experimental data and scheme.

        Args:
            experimental_data: DataFrame with temperature and heating rate data
            reaction_scheme: Dictionary containing reaction scheme configuration

        Returns:
            DataFrame: Simulated mass loss data for each heating rate
        """
        T = experimental_data["temperature"].values
        T_K = T + 273.15

        beta_columns = [col for col in experimental_data.columns if col.lower() != "temperature"]

        reactions = reaction_scheme.get("reactions", [])
        components = reaction_scheme.get("components", [])

        species_list = [comp["id"] for comp in components]
        num_species = len(species_list)
        num_reactions = len(reactions)

        # Extract kinetic parameters
        logA = np.array([reaction.get("log_A", 0) for reaction in reactions])
        Ea = np.array([reaction.get("Ea", 0) for reaction in reactions])
        contributions = np.array([reaction.get("contribution", 0) for reaction in reactions])
        R = 8.314  # Gas constant

        simulation_results = {"temperature": T}

        # Simulate for each heating rate
        for beta_col in beta_columns:
            beta_value = float(beta_col)

            def ode_func(T_val, X):
                """ODE system for reaction kinetics."""
                dXdt = np.zeros(num_species + num_reactions)
                conc = X[:num_species]
                beta_SI = beta_value / 60.0  # Convert K/min to K/s

                for i, reaction in enumerate(reactions):
                    src = reaction.get("from")
                    tgt = reaction.get("to")
                    if src not in species_list or tgt not in species_list:
                        continue

                    src_index = species_list.index(src)
                    tgt_index = species_list.index(tgt)
                    e_value = conc[src_index]

                    # Get reaction model
                    reaction_type = reaction.get("reaction_type")
                    model = NUC_MODELS_TABLE.get(reaction_type)
                    f_e = model["differential_form"](e_value)

                    # Calculate rate constant (Arrhenius equation)
                    k_i = (10 ** logA[i]) * np.exp(-Ea[i] * 1000 / (R * T_val))
                    k_i /= beta_SI

                    rate = k_i * f_e
                    dXdt[src_index] -= rate
                    dXdt[tgt_index] += rate
                    dXdt[num_species + i] = rate

                return dXdt

            # Initial conditions
            X0 = np.zeros(num_species + num_reactions)
            if num_species > 0:
                X0[0] = 1.0  # Start with first component

            # Solve ODE system
            sol = solve_ivp(ode_func, [T_K[0], T_K[-1]], X0, t_eval=T_K, method="RK45")

            if not sol.success:
                logger.error(f"ODE failed for β = {beta_value}.")
                continue

            # Calculate mass loss
            rates_int = sol.y[num_species : num_species + num_reactions, :]
            int_sum = np.sum(contributions[:, np.newaxis] * rates_int, axis=0)

            exp_mass = experimental_data[beta_col].values
            M0 = exp_mass[0]
            Mfin = exp_mass[-1]

            model_mass = M0 - (M0 - Mfin) * int_sum
            simulation_results[beta_col] = model_mass

        return pd.DataFrame(simulation_results)
