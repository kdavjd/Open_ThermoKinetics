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
            "Coats-Redfern": CoatsRedfern,
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

        operations_map = {
            OperationType.MODEL_FIT_CALCULATION: self._handle_model_fit_calculation,
            OperationType.PLOT_MODEL_FIT_RESULT: self._handle_plot_model_fit_result,
        }

        handler = operations_map.get(operation)
        if handler is not None:
            handler(calculation_params, response)
        else:
            logger.error(f"Unknown operation '{operation}' received by {self.actor_name}")

        self.signals.response_signal.emit(response)

    def _handle_plot_model_fit_result(self, calculation_params: dict, response: dict) -> None:
        logger.info(f"{calculation_params=}")
        fit_method = calculation_params.get("fit_method")
        model_series = calculation_params.get("model_series")
        reaction_df = calculation_params.get("reaction_df")
        alpha_min = calculation_params.get("alpha_min", 0.01)
        alpha_max = calculation_params.get("alpha_max", 0.99)
        valid_proportion = calculation_params.get("valid_proportion", 0.8)

        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}")
            return

        strategy = FitMethod(alpha_min=alpha_min, alpha_max=alpha_max, valid_proportion=valid_proportion)

        plot_data = []
        for _, model_row in model_series.iterrows():
            plot_df, plot_kwargs = strategy.prepare_plot_data_for_model(model_row, reaction_df)
            plot_data.append({"plot_df": plot_df, "plot_kwargs": plot_kwargs})

        response["data"] = plot_data

    def _handle_model_fit_calculation(self, calculation_params: dict, response: dict) -> None:
        fit_method = calculation_params.get("fit_method")
        reaction_data = calculation_params.get("reaction_data")
        alpha_min = calculation_params.get("alpha_min", 0.005)
        alpha_max = calculation_params.get("alpha_max", 0.995)
        valid_proportion = calculation_params.get("valid_proportion", 0.8)

        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}")
            return

        strategy = FitMethod(alpha_min, alpha_max, valid_proportion)
        result_data = {}
        for reaction_name, data in reaction_data.items():
            temperature_K = data["temperature"] + 273.15
            reaction_results = {}

            for beta_column in data.columns:
                if beta_column == "temperature":
                    continue

                beta_value = int(beta_column)
                conversion = data[beta_column].cumsum() / data[beta_column].cumsum().max()
                reaction_results[str(beta_value)] = strategy.calculate(temperature_K, conversion, beta_value)

            result_data[reaction_name] = reaction_results

        response["data"] = result_data
        logger.debug(f"Calculation results for '{fit_method}': {result_data}")


class DirectDiff:
    def __init__(self, alpha_min: float, alpha_max: float, valid_proportion: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.valid_proportion = valid_proportion

    def _calculate_direct_diff_lhs(self, da_dT, f_a_val):
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.log(da_dT / f_a_val)
            result[~np.isfinite(result)] = np.inf
        return result

    def _calculate_direct_diff_params(self, slope, intercept, beta):
        Ea = -slope * R
        A = np.exp(intercept) * beta
        return Ea, A

    def _trim_conversion(self, temperature, conversion):
        valid_mask = (conversion >= self.alpha_min) & (conversion <= self.alpha_max)
        trimmed_conversion = conversion[valid_mask]
        trimmed_temperature = temperature[valid_mask]
        return trimmed_temperature, trimmed_conversion

    def _process_model(self, temperature, conversion, model_key, beta):
        da_dT = conversion.diff()
        model_func = NUC_MODELS_TABLE[model_key]["differential_form"]
        f_a_val = model_func(1 - conversion)

        lhs = self._calculate_direct_diff_lhs(da_dT, f_a_val)
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

        slope, intercept, r_value, p_value, std_err = stats.linregress(reverse_temperature[valid_mask], lhs[valid_mask])
        Ea, A = self._calculate_direct_diff_params(slope, intercept, beta)

        return pd.DataFrame(
            {
                "Model": [model_key],
                "R2_score": [r_value**2],
                "Ea": [Ea],
                "A": [A],
            }
        )

    def calculate(self, temperature: pd.Series, conversion: pd.Series, beta: int) -> pd.DataFrame:
        result_list = []
        trimmed_temperature, trimmed_conversion = self._trim_conversion(temperature, conversion)

        for model_key in NUC_MODELS_LIST:
            temp_df = self._process_model(trimmed_temperature, trimmed_conversion, model_key, beta)
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

    def _filter_inf_data(self, lhs, temperature):
        mask = np.isfinite(lhs) & np.isfinite(temperature)
        return temperature[mask], lhs[mask]

    def prepare_plot_data_for_model(self, model_row: pd.DataFrame, reaction_df: pd.DataFrame):
        temperature_K = reaction_df["temperature"] + 273.15

        beta_column = [col for col in reaction_df.columns if col != "temperature"][0]
        da_dT = reaction_df[beta_column]
        conversion = da_dT.cumsum()
        trimmed_temperature, trimmed_conversion = self._trim_conversion(temperature_K, conversion)
        da_dT = trimmed_conversion.diff()

        model_func = NUC_MODELS_TABLE[model_row["Model"]]["differential_form"]
        f_a_val = model_func(1 - trimmed_conversion)

        lhs = self._calculate_direct_diff_lhs(da_dT, f_a_val)
        temperature_clean, lhs_clean = self._filter_inf_data(lhs, trimmed_temperature)
        reverse_temperature = 1 / temperature_clean
        slope, intercept, r_value, _, _ = stats.linregress(reverse_temperature, lhs_clean)
        y = reverse_temperature * slope + intercept

        plot_df = pd.DataFrame({"reverse_temperature": reverse_temperature, "lhs_clean": lhs_clean, "y": y})

        model_name = model_row["Model"]
        Ea = float(model_row["Ea"]) if isinstance(model_row["Ea"], str) else model_row["Ea"]
        A = float(model_row["A"]) if isinstance(model_row["A"], str) else model_row["A"]
        R2 = float(model_row["R2_score"]) if isinstance(model_row["R2_score"], str) else model_row["R2_score"]

        annotation = r"$ E_a = {:.2f} \n A = {:.2e} \n R^2 = {:.4f}$".format(Ea, A, R2)

        plot_kwargs = {
            "title": f"Model: {model_name}",
            "xlabel": "1/T",
            "ylabel": r"$\ln\left(\frac{da}{dT}\dot \frac{1}{f(a)}\right)$",
            "annotation": annotation,
        }

        return plot_df, plot_kwargs


class CoatsRedfern:
    def __init__(self, alpha_min: float, alpha_max: float, valid_proportion: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.valid_proportion = valid_proportion

    def calculate_coats_redfern_lhs(self, g_a_val, temperature):
        try:
            return np.log(g_a_val / (temperature**2))
        except ZeroDivisionError:
            return np.inf

    def calculate_coats_redfern_params(self, slope, intercept, beta, temperature):
        Ea = -slope * R
        t_mean = temperature.mean()
        A = np.exp(intercept) / (1 - t_mean * R * 2 / Ea) * beta * Ea / R
        return Ea, A

    def process_coats_redfern_model(self, conversion, temperature, model_func, model_name, beta):
        g_a_val = model_func(1 - conversion)
        lhs = self.calculate_coats_redfern_lhs(g_a_val, temperature)
        temperature_clean, lhs_clean = self._filter_inf_data(lhs, temperature)
        reverse_temperature = 1 / temperature_clean
        try:
            slope, intercept, r_value, _, _ = stats.linregress(reverse_temperature, lhs_clean)
        except ValueError:
            return pd.DataFrame(
                {
                    "Model": [model_name],
                    "R2_score": [None],
                    "Ea": [None],
                    "A": [None],
                }
            )

        Ea, A = self.calculate_coats_redfern_params(slope, intercept, beta, temperature)

        return pd.DataFrame(
            {
                "Model": [model_name],
                "R2_score": [r_value**2],
                "Ea": [Ea],
                "A": [A],
            }
        )

    def calculate(self, temperature: pd.Series, conversion: pd.Series, beta: int) -> pd.DataFrame:
        result_list = []
        for model_key in NUC_MODELS_LIST:
            model_func = NUC_MODELS_TABLE[model_key]["integral_form"]
            temp_df = self.process_coats_redfern_model(conversion, temperature, model_func, model_key, beta)
            result_list.append(temp_df)

        if result_list:
            coats_redfern = pd.concat(result_list, ignore_index=True)
            coats_redfern["R2_score"] = coats_redfern["R2_score"].round(4)
            coats_redfern["Ea"] = coats_redfern["Ea"].round()
            coats_redfern["A"] = coats_redfern["A"].apply(lambda x: f"{x:.3e}")
            coats_redfern = coats_redfern.sort_values(by="R2_score", ascending=False)
        else:
            coats_redfern = pd.DataFrame(columns=["Model", "Equation", "R2_score", "Ea", "A"])

        return coats_redfern

    def _filter_inf_data(self, lhs, temperature):
        mask = np.isfinite(lhs) & np.isfinite(temperature)
        return temperature[mask], lhs[mask]

    def prepare_plot_data_for_model(self, model_row: pd.DataFrame, reaction_df: pd.DataFrame):
        temperature_K = reaction_df["temperature"] + 273.15

        beta_column = [col for col in reaction_df.columns if col != "temperature"][0]
        da_dT = reaction_df[beta_column]
        conversion = da_dT.cumsum()
        model_func = NUC_MODELS_TABLE[model_row["Model"]]["integral_form"]

        g_a_val = model_func(1 - conversion)
        lhs = self.calculate_coats_redfern_lhs(g_a_val, temperature_K)
        temperature_clean, lhs_clean = self._filter_inf_data(lhs, temperature_K)
        reverse_temperature = 1 / temperature_clean
        slope, intercept, r_value, _, _ = stats.linregress(reverse_temperature, lhs_clean)
        y = reverse_temperature * slope + intercept

        plot_df = pd.DataFrame({"reverse_temperature": reverse_temperature, "lhs_clean": lhs_clean, "y": y})

        model_name = model_row["Model"]
        Ea = float(model_row["Ea"]) if isinstance(model_row["Ea"], str) else model_row["Ea"]
        A = float(model_row["A"]) if isinstance(model_row["A"], str) else model_row["A"]
        R2 = float(model_row["R2_score"]) if isinstance(model_row["R2_score"], str) else model_row["R2_score"]

        annotation = r"$ E_a = {:.2f} \n A = {:.2e} \n R^2 = {:.4f}$".format(Ea, A, R2)

        plot_kwargs = {
            "title": f"Model: {model_name}",
            "xlabel": "1/T",
            "ylabel": r"$\ln \frac{g(a)}{T^2}$",
            "annotation": annotation,
        }

        return plot_df, plot_kwargs
