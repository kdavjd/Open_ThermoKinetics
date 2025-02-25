import numpy as np
import pandas as pd
from scipy import stats
from scipy.constants import R

from src.core.app_settings import NUC_MODELS_LIST, NUC_MODELS_TABLE, OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger


class ModelFitCalculation(BaseSlots):
    def __init__(self, actor_name: str = "model_fit_calculation", signals=None):
        super().__init__(actor_name=actor_name, signals=signals)
        self.strategies = {
            "direct-diff": DirectDiff,
        }

    def process_request(self, params: dict) -> None:
        operation = params.get("operation")
        calculation_params = params.get("calculation_params")
        logger.debug(f"{self.actor_name} processing operation: {operation}")

        response = {
            "actor": self.actor_name,
            "target": params.get("actor"),
            "request_id": params.get("request_id"),
            "data": None,
            "operation": operation,
        }

        if operation == OperationType.MODEL_FIT_CALCULATION:
            self._handle_model_fit_calculation(calculation_params, response)

        else:
            logger.warning(f"Unknown operation '{operation}' received by {self.actor_name} with {params=}")

        self.signals.response_signal.emit(response)

    def _handle_model_fit_calculation(self, calculation_params: dict, response: dict) -> None:
        fit_method = calculation_params.get("fit_method")
        reaction_data = calculation_params.get("reaction_data")
        alpha_min = calculation_params.get("alpha_min", 0.005)
        alpha_max = calculation_params.get("alpha_max", 0.995)
        valid_proportion = calculation_params.get("valid_proportion", 0.99)

        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}")
            return

        strategy = FitMethod(alpha_min, alpha_max, valid_proportion)
        result_data = {}
        for reaction_name, data in reaction_data.items():
            temperature = data["temperature"]
            reaction_results = {}

            for beta_column in data.columns:
                if beta_column == "temperature":
                    continue

                beta_value = float(beta_column)
                conversion = data[beta_column].cumsum() / data[beta_column].cumsum().max()
                reaction_results[str(beta_value)] = strategy.calculate(temperature, conversion, beta_value)

            result_data[reaction_name] = reaction_results

        response["data"] = result_data
        logger.debug(f"Calculation results for '{fit_method}': {result_data}")


class DirectDiff:
    def __init__(self, alpha_min: float, alpha_max: float, valid_proportion: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.valid_proportion = valid_proportion

    def calculate(self, temperature: pd.Series, conversion: pd.Series, beta: float) -> pd.DataFrame:
        def calculate_direct_diff_lhs(da_dT, f_a_val):
            with np.errstate(divide="ignore", invalid="ignore"):
                result = np.log(da_dT / f_a_val)
                result[~np.isfinite(result)] = np.inf
            return result

        def calculate_direct_diff_params(slope, intercept, beta):
            Ea = -slope * R
            A = np.exp(intercept) * beta
            return Ea, A

        def process_model(temperature, conversion, model_key, beta):
            da_dT = conversion.diff()
            model_func = NUC_MODELS_TABLE[model_key]["differential_form"]
            f_a_val = model_func(1 - conversion)

            lhs = calculate_direct_diff_lhs(da_dT, f_a_val)

            reverse_temperature = 1 / temperature
            valid_mask = np.isfinite(lhs) & np.isfinite(reverse_temperature)

            if np.sum(valid_mask) < len(temperature) * self.valid_proportion:
                return pd.DataFrame(
                    {
                        "Model": [model_key],
                        "R2_score": [np.nan],
                        "Ea": [np.nan],
                        "A": [np.nan],
                    }
                )

            slope, intercept, r_value, p_value, std_err = stats.linregress(
                reverse_temperature[valid_mask], lhs[valid_mask]
            )
            Ea, A = calculate_direct_diff_params(slope, intercept, beta)

            return pd.DataFrame(
                {
                    "Model": [model_key],
                    "R2_score": [r_value**2],
                    "Ea": [Ea],
                    "A": [A],
                }
            )

        def trim_conversion(temperature, conversion):
            valid_mask = (conversion >= self.alpha_min) & (conversion <= self.alpha_max)
            trimmed_conversion = conversion[valid_mask]
            trimmed_temperature = temperature[valid_mask]
            return trimmed_temperature, trimmed_conversion

        result_list = []
        trimmed_temperature, trimmed_conversion = trim_conversion(temperature, conversion)

        for model_key in NUC_MODELS_LIST:
            temp_df = process_model(trimmed_temperature, trimmed_conversion, model_key, beta)

            if not temp_df[["R2_score", "Ea", "A"]].isna().all(axis=1).all():
                result_list.append(temp_df)

        if result_list:
            direct_diff = pd.concat(result_list, ignore_index=True)
            direct_diff["R2_score"] = direct_diff["R2_score"].round(4)
            direct_diff["Ea"] = direct_diff["Ea"].round()
            direct_diff["A"] = direct_diff["A"].apply(lambda x: f"{x:.3e}")
            direct_diff = direct_diff.sort_values(by="R2_score", ascending=False)

        else:
            direct_diff = pd.DataFrame(columns=["Model", "R2_score", "Ea", "A"])

        return direct_diff
