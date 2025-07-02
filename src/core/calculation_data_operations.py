import time
from itertools import product

import numpy as np
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSlots
from src.core.curve_fitting import CurveFitting as cft
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class CalculationsDataOperations(BaseSlots):
    """High-level operations coordinator for reaction data management and visualization.

    Handles complex reaction operations including parameter updates, plotting, deconvolution
    preparation, and real-time GUI feedback. Coordinates between CalculationsData storage
    and visual components through signal-slot architecture.
    """

    deconvolution_signal = pyqtSignal(dict)
    plot_reaction = pyqtSignal(tuple, list)
    reaction_params_to_gui = pyqtSignal(dict)

    def __init__(self, signals):
        super().__init__(actor_name="calculations_data_operations", signals=signals)
        self.last_plot_time = 0
        self.calculations_in_progress = False
        self.reaction_variables: dict = {}
        self.reaction_chosen_functions: dict[str, list] = {}

    @pyqtSlot(dict)
    def process_request(self, params: dict):
        """Route incoming operation requests to appropriate handler methods."""
        path_keys = params.get("path_keys")
        operation = params.get("operation")

        if not path_keys or not isinstance(path_keys, list):
            logger.error("Invalid or empty path_keys list.")
            return

        operations = {
            OperationType.ADD_REACTION: self.add_reaction,
            OperationType.REMOVE_REACTION: self.remove_reaction,
            OperationType.HIGHLIGHT_REACTION: self.highlight_reaction,
            OperationType.UPDATE_VALUE: self.update_value,
            OperationType.DECONVOLUTION: self.deconvolution,
            OperationType.UPDATE_REACTIONS_PARAMS: self.update_reactions_params,
        }

        if operation in operations:
            params["data"] = True
            logger.debug(f"Processing operation '{operation}' with path_keys: {path_keys}")
            answer = operations[operation](path_keys, params)

            if answer:
                if operation == OperationType.UPDATE_VALUE:
                    self._protected_plot_update_curves(path_keys, params)
                if operation == OperationType.DECONVOLUTION:
                    self.deconvolution_signal.emit(answer)

            params["target"], params["actor"] = params["actor"], params["target"]
            self.signals.response_signal.emit(params)
        else:
            logger.warning("Unknown or missing data operation.")

    def _protected_plot_update_curves(self, path_keys, params):
        """Throttle plot updates to prevent excessive redrawing during rapid parameter changes."""
        if self.calculations_in_progress:
            logger.debug("Skipping plot update as calculations are in progress.")
            return
        current_time = time.time()
        if current_time - self.last_plot_time >= 0.1:
            self.last_plot_time = current_time
            logger.debug("Updating reaction curves based on updated values.")
            self.highlight_reaction(path_keys, params)

    def _extract_reaction_params(self, path_keys: list):
        """Get reaction parameters from storage and parse them for curve fitting."""
        reaction_params = self.handle_request_cycle("calculations_data", OperationType.GET_VALUE, path_keys=path_keys)
        return cft.parse_reaction_params(reaction_params)

    def _plot_reaction_curve(self, file_name, reaction_name, bound_label, params):
        """Calculate and emit reaction curve data for visualization."""
        if not params:
            logger.warning(f"No parameters found for {reaction_name} with bound {bound_label}. Skipping plot.")
            return
        x_min, x_max = params[0]
        x = np.linspace(x_min, x_max, 250)
        y = cft.calculate_reaction(params)
        curve_name = f"{reaction_name}_{bound_label}"
        logger.debug(f"Emitting plot signal for curve: {curve_name} in file: {file_name}.")
        self.plot_reaction.emit((file_name, curve_name), [x, y])

    def update_reactions_params(self, path_keys: list, params: dict):
        """Apply optimized parameters from deconvolution results to all reaction bounds.

        Takes the best combination of functions and their optimized coefficients,
        distributes them to appropriate reactions, and updates storage with proper bounds.

        Args:
            path_keys (list): Location keys, typically [file_name].
            params (dict): Contains 'best_combination' and 'reactions_params' from optimization.
        """
        file_name = path_keys[0]
        reaction_functions: tuple[str] = params.get("best_combination", None)
        reactions_params = params.get("reactions_params", None)
        if reaction_functions is None or reactions_params is None:
            logger.error("Missing 'best_combination' or 'reactions_params' for update.")
            console.log("Error: Unable to update reaction parameters due to missing required data.")
            return

        n_reactions_coeffs = [len(self.reaction_variables[key]) for key in self.reaction_variables]
        reactions_dict = {}
        start = 0
        for key, count in zip(self.reaction_variables.keys(), n_reactions_coeffs):
            reactions_dict[key] = reactions_params[start : start + count]
            start += count

        ordered_vars = ["h", "z", "w", "fr", "ads1", "ads2"]
        sorted_reactions = sorted(reactions_dict.keys(), key=lambda x: int(x.split("_")[1]))

        for i, reaction in enumerate(sorted_reactions):
            variables = self.reaction_variables[reaction]
            values = reactions_dict[reaction]
            function_type = reaction_functions[i]
            allowed_keys = cft._get_allowed_keys_for_type(function_type)
            var_list = [var for var in ordered_vars if var in variables and var in allowed_keys]

            for var, value in zip(var_list, values):
                for bound in ["lower_bound_coeffs", "coeffs", "upper_bound_coeffs"]:
                    pk = [file_name, reaction, bound, var]
                    pr = {"value": value, "is_chain": True}
                    self.update_value(pk, pr)

        logger.info("Reaction parameters updated successfully.")
        console.log("Reaction parameters have been updated based on the best combination found.")

    def add_reaction(self, path_keys: list, _params: dict):
        """Create new reaction with default parameters and plot initial curves."""
        file_name, reaction_name = path_keys
        is_executed = self.handle_request_cycle(
            "file_data", OperationType.CHECK_OPERATION, file_name=file_name, checked_operation=OperationType.TO_DTG
        )

        if is_executed:
            df = self.handle_request_cycle("file_data", OperationType.GET_DF_DATA, file_name=file_name)
            data = cft.generate_default_function_data(df)
            is_exist = self.handle_request_cycle(
                "calculations_data", OperationType.SET_VALUE, path_keys=path_keys.copy(), value=data
            )
            if is_exist:
                logger.warning(f"Data already exists at path: {path_keys.copy()} - overwriting not performed.")

            reaction_params = self._extract_reaction_params(path_keys)
            for bound_label, params in reaction_params.items():
                self._plot_reaction_curve(file_name, reaction_name, bound_label, params)
            console.log(f"Reaction '{reaction_name}' has been successfully added to file '{file_name}'.")
        else:
            _params["data"] = False
            logger.error(f"Differential data check failed for file: {file_name}. Cannot add reaction.")
            console.log(f"Failed to add reaction '{reaction_name}' due to missing differential data in '{file_name}'.")

    def remove_reaction(self, path_keys: list, _params: dict):
        """Delete reaction from data storage."""
        if len(path_keys) < 2:
            logger.error("Insufficient path_keys information to remove reaction.")
            return
        file_name, reaction_name = path_keys
        is_exist = self.handle_request_cycle("calculations_data", OperationType.REMOVE_VALUE, path_keys=path_keys)
        if not is_exist:
            logger.warning(f"Reaction {reaction_name} not found in data.")
            console.log(f"Reaction '{reaction_name}' could not be found for removal.")
        else:
            logger.debug(f"Removed reaction {reaction_name} for file {file_name}.")
            console.log(f"Reaction '{reaction_name}' was successfully removed from file '{file_name}'.")

    def highlight_reaction(self, path_keys: list, _params: dict):
        """Plot individual and cumulative reaction curves for visualization.

        Generates curves for all reactions in a file, with special highlighting
        for the selected reaction. Emits both individual curves and cumulative
        sums for comparison visualization.

        Args:
            path_keys (list): Keys specifying file and optionally selected reaction.
            _params (dict): Additional parameters (unused).
        """
        file_name = path_keys[0]
        data = self.handle_request_cycle("calculations_data", OperationType.GET_VALUE, path_keys=[file_name])

        if not data:
            logger.warning(f"No data found for file '{file_name}' when highlighting reaction.")
            console.log(f"No data available for highlighting reactions in file '{file_name}'.")
            return

        reactions = data.keys()

        cumulative_y = {
            "upper_bound_coeffs": np.array([]),
            "lower_bound_coeffs": np.array([]),
            "coeffs": np.array([]),
        }
        x = None

        for reaction_name in reactions:
            reaction_params = self._extract_reaction_params([file_name, reaction_name])
            for bound_label, params in reaction_params.items():
                if bound_label in cumulative_y:
                    y = cft.calculate_reaction(reaction_params.get(bound_label, []))
                    if x is None:
                        x_min, x_max = params[0]
                        x = np.linspace(x_min, x_max, 250)
                    cumulative_y[bound_label] = cumulative_y[bound_label] + y if cumulative_y[bound_label].size else y

            if reaction_name in path_keys:
                self.reaction_params_to_gui.emit(reaction_params)
                logger.debug(f"Highlighting reaction: {reaction_name}")
                self._plot_reaction_curve(
                    file_name, reaction_name, "upper_bound_coeffs", reaction_params.get("upper_bound_coeffs", [])
                )
                self._plot_reaction_curve(
                    file_name, reaction_name, "lower_bound_coeffs", reaction_params.get("lower_bound_coeffs", [])
                )
            else:
                self._plot_reaction_curve(file_name, reaction_name, "coeffs", reaction_params.get("coeffs", []))

        if x is not None:
            for bound_label, y in cumulative_y.items():
                self.plot_reaction.emit((file_name, f"cumulative_{bound_label}"), [x, y])
            logger.info("Cumulative curves have been plotted.")

    def _update_coeffs_value(self, path_keys: list[str], new_value):
        """Maintain coefficient consistency by averaging upper and lower bounds."""
        bound_keys = ["upper_bound_coeffs", "lower_bound_coeffs"]
        for key in bound_keys:
            if key in path_keys:
                opposite_key = bound_keys[1 - bound_keys.index(key)]
                new_keys = path_keys.copy()
                new_keys[new_keys.index(key)] = opposite_key

                opposite_value = self.handle_request_cycle(
                    "calculations_data", OperationType.GET_VALUE, path_keys=new_keys
                )

                if opposite_value is None:
                    logger.warning(f"Opposite bound data not found at {new_keys}. Cannot update coeffs.")
                    return

                average_value = (new_value + opposite_value) / 2
                new_keys[new_keys.index(opposite_key)] = "coeffs"
                is_exist = self.handle_request_cycle(
                    "calculations_data", OperationType.SET_VALUE, path_keys=new_keys, value=average_value
                )
                if is_exist:
                    logger.info(f"Data at {new_keys} updated to {average_value}.")
                else:
                    logger.error(f"No data found at {new_keys} for updating coeffs.")

    def update_value(self, path_keys: list[str], params: dict):
        """Update reaction parameter and maintain coefficient consistency.

        Handles individual parameter updates from GUI interactions, automatically
        maintaining bound consistency when applicable. Used extensively for
        real-time parameter adjustments.

        Args:
            path_keys (list[str]): Location of parameter to update.
            params (dict): Contains 'value' to set and optional 'is_chain' bool.

        Returns:
            dict or None: Operation result if successful and not part of chain.
        """
        try:
            new_value = params.get("value")
            is_chain = params.get("is_chain", None)
            is_ok = self.handle_request_cycle(
                "calculations_data", OperationType.SET_VALUE, path_keys=path_keys.copy(), value=new_value
            )
            if is_ok:
                logger.debug(f"Data at {path_keys} updated to {new_value}.")
                if not is_chain:
                    self._update_coeffs_value(path_keys.copy(), new_value)
                    return {"operation": OperationType.UPDATE_VALUE, "data": None}
            else:
                logger.error(f"No data found at {path_keys} for updating.")
        except ValueError as e:
            logger.error(f"Unexpected error updating data at {path_keys}: {str(e)}")

    def deconvolution(self, path_keys: list[str], params: dict):
        """Prepare comprehensive deconvolution configuration for optimization.

        Assembles all necessary data for reaction deconvolution including function
        combinations, parameter bounds, experimental data, and optimization settings.
        Generates exhaustive function combinations for global optimization.

        Args:
            path_keys (list[str]): Location keys, typically [file_name].
            params (dict): Must contain 'deconvolution_settings' and 'chosen_functions'.

        Returns:
            dict: Complete deconvolution configuration ready for optimization.
        """
        deconvolution_settings = params.get("deconvolution_settings", {})
        reaction_variables = {}
        num_coefficients = {}
        bounds = []
        check_keys = ["h", "z", "w", "fr", "ads1", "ads2"]
        file_name = path_keys[0]
        reaction_chosen_functions: dict = params.get("chosen_functions", {})

        if not reaction_chosen_functions:
            raise ValueError("chosen_functions is None or empty")

        functions_data = self.handle_request_cycle("calculations_data", OperationType.GET_VALUE, path_keys=[file_name])
        if not functions_data:
            raise ValueError(f"No functions data found for file: {file_name}")

        reaction_combinations = list(product(*reaction_chosen_functions.values()))

        for reaction_name in reaction_chosen_functions:
            function_vars = set()
            reaction_params = functions_data[reaction_name]
            if not reaction_params:
                raise ValueError(f"No reaction params found for reaction: {reaction_name}")
            for reaction_type in reaction_chosen_functions[reaction_name]:
                allowed_keys = cft._get_allowed_keys_for_type(reaction_type)
                function_vars.update(allowed_keys)
            reaction_variables[reaction_name] = function_vars

            lower_coeffs = reaction_params["lower_bound_coeffs"].values()
            upper_coeffs = reaction_params["upper_bound_coeffs"].values()
            filtered_pairs = [
                (lc, uc) for lc, uc, key in zip(lower_coeffs, upper_coeffs, check_keys) if key in function_vars
            ]
            bounds.extend(filtered_pairs)
            num_coefficients[reaction_name] = len(function_vars)

        df = self.handle_request_cycle("file_data", OperationType.GET_DF_DATA, file_name=file_name)
        self.reaction_variables = reaction_variables.copy()
        self.reaction_chosen_functions = reaction_chosen_functions.copy()

        logger.info(f"Preparing for deconvolution with reaction_variables: {reaction_variables}")
        console.log("Preparing reaction data for deconvolution. Please wait...")

        return {
            "reaction_variables": reaction_variables,
            "calculation_settings": deconvolution_settings,
            "bounds": bounds,
            "reaction_combinations": reaction_combinations,
            "experimental_data": df,
            "calculation_scenario": "deconvolution",
        }
