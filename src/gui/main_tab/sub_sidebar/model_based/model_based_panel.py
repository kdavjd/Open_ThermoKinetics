"""
Main model-based analysis panel orchestrator.
Contains the primary ModelBasedTab widget that coordinates all sub-components.
"""

import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget
from scipy.integrate import solve_ivp

from src.core.app_settings import NUC_MODELS_LIST, PARAMETER_BOUNDS, OperationType
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console
from src.core.model_based_calculation import model_based_objective_function, ode_function
from src.gui.main_tab.sub_sidebar.model_based.adjustment_controls import AdjustingSettingsBox
from src.gui.main_tab.sub_sidebar.model_based.calculation_controls import ModelCalcButtons, RangeAndCalculateWidget
from src.gui.main_tab.sub_sidebar.model_based.calculation_settings_dialogs import CalculationSettingsDialog
from src.gui.main_tab.sub_sidebar.model_based.config import MODEL_BASED_CONFIG
from src.gui.main_tab.sub_sidebar.model_based.models_scheme import ModelsScheme
from src.gui.main_tab.sub_sidebar.model_based.parameter_table import ReactionDefaults, ReactionTable


class ModelBasedTab(QWidget):
    """Main widget for model-based kinetic analysis."""

    model_params_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize model-based analysis interface."""
        super().__init__(parent)
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

        # Reaction selection
        self._setup_reaction_selection(main_layout)

        # Range and calculate controls
        self._setup_range_controls(main_layout)

        # Parameter table
        self._setup_parameter_table(main_layout)

        # Adjustment controls
        self._setup_adjustment_controls(main_layout)

        # Bottom section with scheme and buttons
        self._setup_bottom_section(main_layout)

    def _setup_reaction_selection(self, main_layout):
        """Setup reaction selection widgets."""
        config = MODEL_BASED_CONFIG.layout_settings
        # Reactions combo
        self.reactions_combo = QComboBox()
        self.reactions_combo.setMinimumSize(config.reactions_combo_min_width, config.reactions_combo_min_height)
        main_layout.addWidget(self.reactions_combo)

        # Reaction type selection
        reaction_type_layout = QHBoxLayout()
        reaction_type_label = QLabel("Reaction type:")
        self.reaction_type_combo = QComboBox()
        self.reaction_type_combo.setMinimumSize(
            config.reaction_type_combo_min_width, config.reaction_type_combo_min_height
        )
        self.reaction_type_combo.addItems(NUC_MODELS_LIST)

        reaction_type_layout.addWidget(reaction_type_label)
        reaction_type_layout.addWidget(self.reaction_type_combo)
        main_layout.addLayout(reaction_type_layout)

    def _setup_range_controls(self, main_layout):
        """Setup range and calculate control widgets."""
        config = MODEL_BASED_CONFIG.layout_settings

        self.range_calc_widget = RangeAndCalculateWidget()
        self.range_calc_widget.setMinimumHeight(config.range_calc_widget_min_height)
        main_layout.addWidget(self.range_calc_widget)

    def _setup_parameter_table(self, main_layout):
        """Setup parameter table widget."""
        config = MODEL_BASED_CONFIG.layout_settings

        self.reaction_table = ReactionTable()
        self.reaction_table.setMinimumHeight(config.reaction_table_min_height)
        main_layout.addWidget(self.reaction_table)

        # Set column widths and row heights
        for col, width in enumerate(config.reaction_table_column_widths):
            self.reaction_table.setColumnWidth(col, width)
        for row, height in enumerate(config.reaction_table_row_heights):
            self.reaction_table.setRowHeight(row, height)

    def _setup_adjustment_controls(self, main_layout):
        """Setup parameter adjustment controls."""
        config = MODEL_BASED_CONFIG.layout_settings

        self.adjusting_settings_box = AdjustingSettingsBox()
        self.adjusting_settings_box.setMinimumHeight(config.adjusting_settings_box_min_height)
        main_layout.addWidget(self.adjusting_settings_box)

    def _setup_bottom_section(self, main_layout):
        """Setup models scheme and calculation buttons."""
        config = MODEL_BASED_CONFIG.layout_settings

        bottom_layout = QVBoxLayout()

        # Models scheme
        self.models_scene = ModelsScheme(self)
        self.models_scene.setMinimumSize(config.models_scene_min_width, config.models_scene_min_height)
        bottom_layout.addWidget(self.models_scene)

        # Calculation buttons
        self.calc_buttons = ModelCalcButtons(self)
        self.calc_buttons.settings_button.setFixedSize(config.calc_buttons_width, config.calc_buttons_height)
        self.calc_buttons.start_button.setFixedSize(config.calc_buttons_width, config.calc_buttons_height)
        self.calc_buttons.stop_button.setFixedSize(config.calc_buttons_width, config.calc_buttons_height)
        bottom_layout.addWidget(self.calc_buttons)

        main_layout.addLayout(bottom_layout)

    def _connect_signals(self):
        """Connect all widget signals."""
        # Range and calculate controls
        self.range_calc_widget.showRangeToggled.connect(self.on_show_range_checkbox_changed)
        self.range_calc_widget.calculateToggled.connect(self.on_calculate_toggled)

        # Parameter table editing
        self.reaction_table.activation_energy_edit.editingFinished.connect(self._on_params_changed)
        self.reaction_table.log_a_edit.editingFinished.connect(self._on_params_changed)
        self.reaction_table.contribution_edit.editingFinished.connect(self._on_params_changed)
        self.reaction_table.ea_min_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.ea_max_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.log_a_min_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.log_a_max_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.contribution_min_item.editingFinished.connect(self._on_params_changed)
        self.reaction_table.contribution_max_item.editingFinished.connect(self._on_params_changed)

        # Reaction selection
        self.reaction_type_combo.currentIndexChanged.connect(self._on_params_changed)
        self.reactions_combo.currentIndexChanged.connect(self._on_reactions_combo_changed)

        # Adjustment controls
        self.adjusting_settings_box.ea_adjuster.valueChanged.connect(self.on_adjuster_value_changed)
        self.adjusting_settings_box.log_a_adjuster.valueChanged.connect(self.on_adjuster_value_changed)
        self.adjusting_settings_box.contrib_adjuster.valueChanged.connect(self.on_adjuster_value_changed)

    def update_best_values(self, best_values_data: dict):
        """Update cached best optimization values for reactions."""
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
                f"ModelBasedTab.update_best_values: Updating Value fields for current reaction {reaction_index}"
            )

            self.reaction_table.update_value_with_best(self._best_values_cache[reaction_index])
            self._on_params_changed()
        else:
            logger.debug(
                f"ModelBasedTab.update_best_values: Reaction {reaction_index} is not currently selected "
                f"(current: {current_index}), values cached for later display"
            )

    def on_adjuster_value_changed(self, parameter_name: str, new_value: float):
        """Handle parameter adjustment from sliders."""
        if parameter_name == "Ea":
            self.reaction_table.activation_energy_edit.setText(str(new_value))
        elif parameter_name == "log_A":
            self.reaction_table.log_a_edit.setText(str(new_value))
        elif parameter_name == "contribution":
            self.reaction_table.contribution_edit.setText(str(new_value))
        self._on_params_changed()

    def on_show_range_checkbox_changed(self, checked: bool):
        """Handle range visibility toggle."""
        self.reaction_table.set_ranges_visible(checked)

    def on_calculate_toggled(self, checked: bool):
        """Handle calculate checkbox toggle."""
        pass  # Placeholder for future functionality

    def update_scheme_data(self, scheme_data: dict):
        """Update reaction scheme data and refresh UI."""
        self._scheme_data = scheme_data
        self._reactions_list = scheme_data.get("reactions", [])

        current_label = self.reactions_combo.currentText() if self.reactions_combo.count() > 0 else None

        # Update reactions combo
        self.reactions_combo.clear()
        reaction_map = {}
        for i, reaction in enumerate(self._reactions_list):
            label = f"{reaction.get('from', '?')} -> {reaction.get('to', '?')}"
            self.reactions_combo.addItem(label)
            reaction_map[label] = i

        # Select appropriate reaction
        default_label = "A -> B"
        new_index = reaction_map.get(current_label, reaction_map.get(default_label, 0))

        if not self._reactions_list:
            self.reaction_table.update_table({})
        else:
            self.reactions_combo.setCurrentIndex(new_index)
            self._on_reactions_combo_changed(new_index)

        # Update models scheme
        self.models_scene.update_from_scheme(scheme_data, self._reactions_list)

    def update_calculation_settings(self, calculation_settings: dict):
        """Update calculation method and parameters."""
        self._calculation_method = calculation_settings.get("method")
        self._calculation_method_params = calculation_settings.get("method_parameters")

    def _on_reactions_combo_changed(self, index: int):
        """Handle reaction selection change."""
        if 0 <= index < len(self._reactions_list):
            reaction_data = self._reactions_list[index]
            self.reaction_table.update_table(reaction_data)

            # Apply cached best values if available
            if index in self._best_values_cache:
                logger.debug(
                    f"ModelBasedTab._on_reactions_combo_changed: Applying cached best values for reaction {index}"
                )
                self.reaction_table.update_value_with_best(self._best_values_cache[index])

            # Update adjustment controls
            self._update_adjustment_controls(reaction_data)

            # Update reaction type combo
            self._update_reaction_type_combo(reaction_data)
        else:
            self.reaction_table.update_table({})

    def _update_adjustment_controls(self, reaction_data):
        """Update adjustment control values."""
        default_reaction = ReactionDefaults()
        ea_value = reaction_data.get("Ea", default_reaction.Ea_default)
        log_a_value = reaction_data.get("log_A", default_reaction.log_A_default)
        contrib_value = reaction_data.get("contribution", default_reaction.contribution_default)

        # Update Ea adjuster
        self.adjusting_settings_box.ea_adjuster.base_value = ea_value
        self.adjusting_settings_box.ea_adjuster.slider.setValue(0)
        self.adjusting_settings_box.ea_adjuster.update_label()

        # Update log_A adjuster
        self.adjusting_settings_box.log_a_adjuster.base_value = log_a_value
        self.adjusting_settings_box.log_a_adjuster.slider.setValue(0)
        self.adjusting_settings_box.log_a_adjuster.update_label()

        # Update contribution adjuster
        self.adjusting_settings_box.contrib_adjuster.base_value = contrib_value
        self.adjusting_settings_box.contrib_adjuster.slider.setValue(0)
        self.adjusting_settings_box.contrib_adjuster.update_label()

    def _update_reaction_type_combo(self, reaction_data):
        """Update reaction type combo selection."""
        new_reaction_type = reaction_data.get("reaction_type", "F2")
        current_reaction_type = self.reaction_type_combo.currentText()
        if new_reaction_type != current_reaction_type:
            was_blocked = self.reaction_type_combo.blockSignals(True)
            self.reaction_type_combo.setCurrentText(new_reaction_type)
            self.reaction_type_combo.blockSignals(was_blocked)

    @pyqtSlot()
    def _on_params_changed(self):
        """Handle parameter changes and emit update signal."""
        current_index = self.reactions_combo.currentIndex()
        if not (0 <= current_index < len(self._reactions_list)):
            return

        from_comp = self._reactions_list[current_index].get("from")
        to_comp = self._reactions_list[current_index].get("to")
        reaction_type = self.reaction_type_combo.currentText()

        # Get parameter values with validation using centralized bounds
        bounds = PARAMETER_BOUNDS.model_based
        ea_val = self._get_float_value(self.reaction_table.activation_energy_edit.text(), bounds.ea_default)
        loga_val = self._get_float_value(self.reaction_table.log_a_edit.text(), bounds.log_a_default)
        contrib_val = self._get_float_value(self.reaction_table.contribution_edit.text(), bounds.contribution_default)

        # Get range values with defaults
        defaults = self.reaction_table.defaults
        ea_min_val = self._get_float_value(self.reaction_table.ea_min_item.text(), defaults.Ea_range[0])
        ea_max_val = self._get_float_value(self.reaction_table.ea_max_item.text(), defaults.Ea_range[1])
        loga_min_val = self._get_float_value(self.reaction_table.log_a_min_item.text(), defaults.log_A_range[0])
        loga_max_val = self._get_float_value(self.reaction_table.log_a_max_item.text(), defaults.log_A_range[1])
        contrib_min_val = self._get_float_value(
            self.reaction_table.contribution_min_item.text(), defaults.contribution_range[0]
        )
        contrib_max_val = self._get_float_value(
            self.reaction_table.contribution_max_item.text(), defaults.contribution_range[1]
        )

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

    def _get_float_value(self, text: str, default: float) -> float:
        """Get float value from text with fallback to default."""
        try:
            return float(text)
        except ValueError:
            return default

    def open_settings(self):
        """Open calculation settings dialog."""
        if not self._reactions_list:
            QMessageBox.information(self, "No Reactions", "There are no available reactions to configure.")
            return

        dialog = CalculationSettingsDialog(
            self._reactions_list, self._calculation_method, self._calculation_method_params, parent=self
        )

        if dialog.exec():
            new_calculation_settings, updated_reactions = dialog.get_data()

            self._reactions_list = updated_reactions

            # Update scheme data with new reactions
            if self._scheme_data and "reactions" in self._scheme_data:
                for i, r in enumerate(self._scheme_data["reactions"]):
                    if i < len(updated_reactions):
                        self._scheme_data["reactions"][i] = updated_reactions[i]  # Emit update signal
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
        Simulate reaction model using model_based_objective_function directly.

        This function uses the exact same function as ModelBasedTargetFunction.__call__
        to ensure consistent MSE calculation and avoid code duplication.
        """
        if not self._validate_simulation_inputs(experimental_data, reaction_scheme):
            return pd.DataFrame()

        sim_params = self._prepare_simulation_parameters(experimental_data, reaction_scheme)
        if not sim_params:
            console.log("\nFailed to prepare simulation parameters. Check reaction scheme configuration.\n")
            return pd.DataFrame()

        # Create parameters array in the format expected by model_based_objective_function
        core_params = self._create_core_compatible_params(
            sim_params["logA"], sim_params["Ea"], sim_params["contributions"]
        )

        # Use model_based_objective_function directly to calculate MSE
        total_mse = self._calculate_mse_using_core_function(experimental_data, sim_params, core_params)

        # Output MSE to console
        console.log(f"\nModel simulation MSE: {total_mse:.6f}\n")

        # Generate simulation data for visualization
        simulation_results = self._generate_simulation_curves(experimental_data, sim_params, core_params)

        return pd.DataFrame(simulation_results)

    def _calculate_mse_using_core_function(
        self, experimental_data: pd.DataFrame, sim_params: dict, core_params: np.ndarray
    ) -> float:
        """Calculate MSE using the same logic as ModelBasedTargetFunction."""
        try:
            # Extract data exactly as done in ModelBasedTargetFunction
            species_list = sim_params["species_list"]
            reactions = sim_params["reactions"]
            num_species = sim_params["num_species"]
            num_reactions = sim_params["num_reactions"]
            exp_temperature = sim_params["T_K"]  # Temperature in Kelvin

            # Extract betas and experimental masses exactly as in ModelBasedTargetFunction
            betas = [float(col) for col in experimental_data.columns if col.lower() != "temperature"]
            all_exp_masses = self._extract_experimental_masses(experimental_data, betas)

            # Create dummy stop_event for simulation (no stopping needed in UI)
            from threading import Event

            stop_event = Event()

            # Call model_based_objective_function directly - same logic as ModelBasedTargetFunction.__call__
            total_mse = model_based_objective_function(
                core_params,
                species_list,
                reactions,
                num_species,
                num_reactions,
                betas,
                all_exp_masses,
                exp_temperature,
                R=8.314,
                stop_event=stop_event,
            )

            return total_mse

        except Exception as e:
            logger.error(f"MSE calculation error: {e}")
            console.log(f"\nError calculating MSE: {str(e)}\n")
            return float("inf")

    def _generate_simulation_curves(
        self, experimental_data: pd.DataFrame, sim_params: dict, core_params: np.ndarray
    ) -> dict:
        """Generate simulation curves for each heating rate for visualization."""
        simulation_results = {"temperature": sim_params["T"]}

        betas = [float(col) for col in experimental_data.columns if col.lower() != "temperature"]
        all_exp_masses = self._extract_experimental_masses(experimental_data, betas)

        for beta, exp_mass in zip(betas, all_exp_masses):
            try:
                model_mass = self._get_mass_from_core_ode(beta, sim_params, core_params, exp_mass)
                simulation_results[str(beta)] = model_mass
            except Exception as e:
                logger.error(f"Simulation curve generation error for β={beta}: {e}")
                simulation_results[str(beta)] = exp_mass  # Fallback to experimental data

        return simulation_results

    def _validate_simulation_inputs(self, experimental_data: pd.DataFrame, reaction_scheme: dict) -> bool:
        """Validate inputs for simulation."""
        if experimental_data.empty:
            console.log("\nCannot simulate model: No experimental data available.\n")
            return False
        if not reaction_scheme:
            console.log("\nCannot simulate model: No reaction scheme defined.\n")
            return False
        return True

    def _extract_experimental_masses(self, experimental_data: pd.DataFrame, betas: list) -> list:
        """Extract experimental masses for each heating rate."""
        all_exp_masses = []
        for beta in betas:
            col_name = str(beta)
            if col_name not in experimental_data.columns:
                col_name = str(int(beta))
            if col_name not in experimental_data.columns:
                logger.error(f"Experimental data does not contain column for beta value {beta}")
                continue
            exp_mass = experimental_data[col_name].to_numpy()
            all_exp_masses.append(exp_mass)
        return all_exp_masses

    def _prepare_simulation_parameters(self, experimental_data: pd.DataFrame, reaction_scheme: dict) -> dict:
        """Prepare parameters for reaction simulation."""
        T = experimental_data["temperature"].values
        T_K = T + 273.15
        beta_columns = [col for col in experimental_data.columns if col.lower() != "temperature"]

        reactions = reaction_scheme.get("reactions", [])
        components = reaction_scheme.get("components", [])
        species_list = [comp["id"] for comp in components]
        num_species = len(species_list)
        num_reactions = len(reactions)

        logA = np.array([reaction.get("log_A", 8) for reaction in reactions])
        Ea = np.array([reaction.get("Ea", 120) for reaction in reactions])
        contributions = np.array([reaction.get("contribution", 0.5) for reaction in reactions])

        return {
            "T": T,
            "T_K": T_K,
            "beta_columns": beta_columns,
            "reactions": reactions,
            "species_list": species_list,
            "num_species": num_species,
            "num_reactions": num_reactions,
            "logA": logA,
            "Ea": Ea,
            "contributions": contributions,
        }

    def _create_core_compatible_params(self, logA: np.ndarray, Ea: np.ndarray, contributions: np.ndarray) -> np.ndarray:
        num_reactions = len(logA)
        model_indices = np.zeros(num_reactions)  # GUI uses fixed models
        return np.concatenate([logA, Ea, model_indices, contributions])

    def _get_mass_from_core_ode(
        self, beta_value: float, sim_params: dict, core_params: np.ndarray, exp_mass: np.ndarray
    ) -> np.ndarray:
        try:
            y0 = np.zeros(sim_params["num_species"] + sim_params["num_reactions"])
            if sim_params["num_species"] > 0:
                y0[0] = 1.0

            def ode_wrapper(T, y):
                return ode_function(
                    T,
                    y,
                    beta_value,  # Pass β directly (K/min)
                    core_params,
                    sim_params["species_list"],
                    sim_params["reactions"],
                    sim_params["num_species"],
                    sim_params["num_reactions"],
                    R=8.314,
                )

            T_K = sim_params["T_K"]
            sol = solve_ivp(ode_wrapper, [T_K[0], T_K[-1]], y0, t_eval=T_K, method="BDF")

            if not sol.success:
                logger.error(f"Core ODE solution failed for β = {beta_value}")
                console.log(
                    f"\nODE integration failed for heating rate {beta_value} K/min. Check reaction parameters.\n"
                )
                return exp_mass

            # Extract rates and calculate mass
            rates_int = sol.y[sim_params["num_species"] : sim_params["num_species"] + sim_params["num_reactions"], :]
            int_sum = np.sum(sim_params["contributions"][:, np.newaxis] * rates_int, axis=0)
            M0 = exp_mass[0]
            Mfin = exp_mass[-1]
            model_mass = M0 - (M0 - Mfin) * int_sum

            return model_mass

        except Exception as e:
            logger.error(f"Core ODE mass calculation failed for β = {beta_value}: {e}")
            console.log(
                f"\nMass calculation from ODE failed for {beta_value} K/min: {str(e)}\n"
                f"Check reaction scheme and parameters.\n"
            )
            return exp_mass
