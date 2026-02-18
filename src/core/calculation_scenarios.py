"""Calculation scenarios for optimization using Strategy pattern."""

from typing import Callable, Dict

import numpy as np

from src.core.curve_fitting import CurveFitting as cft
from src.core.logger_config import logger
from src.core.model_based_calculation import ModelBasedScenario


class BaseCalculationScenario:
    """Base class for defining optimization scenarios."""

    def __init__(self, params: Dict, calculations):
        self.params = params
        self.calculations = calculations

    def get_bounds(self) -> list[tuple]:
        """Return optimization parameter bounds."""
        raise NotImplementedError

    def get_target_function(self, **kwargs) -> Callable:
        """Return objective function for optimization."""
        raise NotImplementedError

    def get_optimization_method(self) -> str:
        """Return optimization algorithm name."""
        return "differential_evolution"

    def get_result_strategy_type(self) -> str:
        """Return result handling strategy type."""
        raise NotImplementedError

    def get_constraints(self) -> list:
        """Return optimization constraints."""
        return []


class DeconvolutionScenario(BaseCalculationScenario):
    """Scenario for peak deconvolution optimization."""

    def get_bounds(self) -> list[tuple]:
        """Return deconvolution parameter bounds."""
        return self.params["bounds"]

    def get_optimization_method(self) -> str:
        """Return deconvolution optimization method."""
        deconv_settings = self.params.get("deconvolution_settings", {})
        return deconv_settings.pop("method", "differential_evolution")

    def get_result_strategy_type(self) -> str:
        return "deconvolution"

    def get_target_function(self, **kwargs) -> Callable:
        reaction_variables = self.params["reaction_variables"]
        reaction_combinations = self.params["reaction_combinations"]
        experimental_data = self.params["experimental_data"]

        def target_function(params_array: np.ndarray) -> float:
            if not self.calculations.calculation_active:
                return float("inf")

            best_mse = float("inf")
            best_combination = None

            for combination in reaction_combinations:
                cumulative_function = np.zeros(len(experimental_data["temperature"]))
                param_idx_local = 0

                for (reaction, coeffs), func in zip(reaction_variables.items(), combination):
                    coeff_count = len(coeffs)
                    func_params = params_array[param_idx_local : param_idx_local + coeff_count]
                    param_idx_local += coeff_count

                    x = experimental_data["temperature"]
                    if len(func_params) < 3:
                        raise ValueError("Not enough parameters for the function.")
                    h, z, w = func_params[0:3]

                    if func == "gauss":
                        reaction_values = cft.gaussian(x, h, z, w)
                    elif func == "fraser":
                        fr = func_params[3]  # fraser_suzuki
                        reaction_values = cft.fraser_suzuki(x, h, z, w, fr)
                    elif func == "ads":
                        ads1 = func_params[3]
                        ads2 = func_params[4]
                        reaction_values = cft.asymmetric_double_sigmoid(x, h, z, w, ads1, ads2)
                    else:
                        logger.warning(f"Unknown function type: {func}")
                        reaction_values = 0

                    cumulative_function += reaction_values

                y_true = experimental_data.iloc[:, 1].to_numpy()
                mse = np.mean((y_true - cumulative_function) ** 2)
                if mse < best_mse:
                    best_mse = mse
                    best_combination = combination
                    self.calculations.new_best_result.emit(
                        {
                            "best_mse": best_mse,
                            "best_combination": best_combination,
                            "params": params_array,
                            "reaction_variables": reaction_variables,
                        }
                    )
            return best_mse

        return target_function


SCENARIO_REGISTRY = {
    "deconvolution": DeconvolutionScenario,
    "model_based_calculation": ModelBasedScenario,
}
