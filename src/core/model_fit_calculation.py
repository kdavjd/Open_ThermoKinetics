import numpy as np
import pandas as pd
from scipy.constants import R

from src.core.app_settings import NUC_MODELS_LIST, NUC_MODELS_TABLE, OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger


def r2_score(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot


class ModelFitCalculation(BaseSlots):
    def __init__(self, actor_name: str = "model_fit_calculation", signals=None):
        super().__init__(actor_name=actor_name, signals=signals)
        self.strategies = {
            "direct-diff": DirectDiff,
            "Coats-Redfern": CoatsRedfern,
            "Freeman-Carroll": FreemanCaroll,
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

        try:
            x = reverse_temperature[valid_mask]
            y = lhs[valid_mask]
            slope, intercept = np.polyfit(x, y, 1)
            y_pred = slope * x + intercept
            r_value = r2_score(y, y_pred)
        except (ValueError, TypeError):
            return pd.DataFrame(
                {
                    "Model": [model_key],
                    "R2_score": [None],
                    "Ea": [None],
                    "A": [None],
                }
            )

        Ea, A = self._calculate_direct_diff_params(slope, intercept, beta)

        return pd.DataFrame(
            {
                "Model": [model_key],
                "R2_score": [r_value],
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
        conversion = da_dT.cumsum() / da_dT.cumsum().max()
        trimmed_temperature, trimmed_conversion = self._trim_conversion(temperature_K, conversion)
        da_dT = trimmed_conversion.diff()

        model_func = NUC_MODELS_TABLE[model_row["Model"]]["differential_form"]
        f_a_val = model_func(1 - trimmed_conversion)

        lhs = self._calculate_direct_diff_lhs(da_dT, f_a_val)
        temperature_clean, lhs_clean = self._filter_inf_data(lhs, trimmed_temperature)
        reverse_temperature = 1 / temperature_clean

        try:
            _x = reverse_temperature
            _y = lhs_clean
            slope, intercept = np.polyfit(_x, _y, 1)
            y = reverse_temperature * slope + intercept
        except (ValueError, TypeError):
            plot_df = pd.DataFrame({"reverse_temperature": [], "lhs_clean": [], "y": []})
            plot_kwargs = {
                "title": f"Model: {model_row['Model']} - Error",
                "xlabel": "1/T",
                "ylabel": r"$\ln\left(\frac{da}{dT}\dot \frac{1}{f(a)}\right)$",
                "annotation": "Error in polyfit calculation",
            }
            return plot_df, plot_kwargs

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
        epsilon = 1e-8
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.log(g_a_val / ((temperature**2) + epsilon))
            result[~np.isfinite(result)] = np.inf
        return result

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
            x = reverse_temperature
            y = lhs_clean
            slope, intercept = np.polyfit(x, y, 1)
            y_pred = slope * x + intercept
            r_value = r2_score(y, y_pred)
        except (ValueError, TypeError):
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
                "R2_score": [r_value],
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

        valid_results = [
            df.dropna(axis=1, how="all")
            for df in result_list
            if not df.empty and not df.dropna(axis=1, how="all").empty
        ]

        if valid_results:
            coats_redfern = pd.concat(valid_results, ignore_index=True)
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
        conversion = da_dT.cumsum() / da_dT.cumsum().max()
        model_func = NUC_MODELS_TABLE[model_row["Model"]]["integral_form"]

        g_a_val = model_func(1 - conversion)
        lhs = self.calculate_coats_redfern_lhs(g_a_val, temperature_K)
        temperature_clean, lhs_clean = self._filter_inf_data(lhs, temperature_K)
        reverse_temperature = 1 / temperature_clean

        try:
            _x = reverse_temperature
            _y = lhs_clean
            slope, intercept = np.polyfit(_x, _y, 1)
            y = reverse_temperature * slope + intercept
        except (ValueError, TypeError):
            plot_df = pd.DataFrame({"reverse_temperature": [], "lhs_clean": [], "y": []})
            plot_kwargs = {
                "title": f"Model: {model_row['Model']} - Error",
                "xlabel": "1/T",
                "ylabel": r"$\ln \frac{g(a)}{T^2}$",
                "annotation": "Error in polyfit calculation",
            }
            return plot_df, plot_kwargs

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


class FreemanCaroll:
    def __init__(self, alpha_min: float, alpha_max: float, valid_proportion: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.valid_proportion = valid_proportion

    def _process_freeman_carr_model(self, conversion, temperature, model_func, model_name, beta, DEBUG=False):
        conversion_series = pd.Series(conversion)
        da_dT = conversion_series.diff().astype(float)
        epsilon = 1e-8
        da_dT = da_dT.replace(0, epsilon)
        ln_da_dT = np.log(da_dT.values)
        ln_f_a = np.log(model_func(conversion_series) + epsilon)
        m = len(temperature)
        x = []
        y = []

        for j in range(2, m - 1):
            delta_ln_da_dT = ln_da_dT[j] - ln_da_dT[j - 1]
            delta_1_T = 1 / temperature[j + 1] - 1 / temperature[j]
            delta_ln_f_a = ln_f_a[j + 1] - ln_f_a[j]
            if np.isnan(delta_ln_da_dT) or np.isnan(delta_ln_f_a):
                continue
            if np.abs(delta_1_T) > epsilon:
                x_val = delta_ln_f_a / delta_1_T
                y_val = delta_ln_da_dT / delta_1_T
                x.append(x_val)
                y.append(y_val)
            else:
                continue

        if len(x) < 2 or len(x) != len(y) or np.std(x) < epsilon:
            return pd.DataFrame(
                {
                    "Model": [model_name],
                    "R2_score": [None],
                    "Ea": [None],
                    "A": [None],
                }
            )

        x_arr = np.array(x)
        y_arr = np.array(y)

        try:
            slope, intercept = np.polyfit(x_arr, y_arr, 1)
            y_pred = x_arr * slope + intercept
            r_value = r2_score(y, y_pred)
        except (ValueError, TypeError):
            return pd.DataFrame(
                {
                    "Model": [model_name],
                    "R2_score": [None],
                    "Ea": [None],
                    "A": [None],
                }
            )

        Ea = R * intercept

        temperature_array = np.array(temperature[1:])
        ln_A_over_beta = ln_da_dT[1:] + Ea / (R * temperature_array) - ln_f_a[1:]
        average_ln_A_over_beta = np.mean(ln_A_over_beta)
        A = beta * np.exp(average_ln_A_over_beta)
        return pd.DataFrame(
            {
                "Model": [model_name],
                "R2_score": [r_value],
                "Ea": [Ea],
                "A": [A],
            }
        )

    # TODO: RuntimeWarning: invalid value encountered in log
    def calculate(self, temperature: pd.Series, conversion: pd.Series, beta: int) -> pd.DataFrame:
        result_list = []

        for model_key in NUC_MODELS_LIST:
            model_func = NUC_MODELS_TABLE[model_key]["differential_form"]
            temp_df = self._process_freeman_carr_model(conversion, temperature, model_func, model_key, beta)
            result_list.append(temp_df)

        valid_results = [
            df.dropna(axis=1, how="all")
            for df in result_list
            if not df.empty and not df.dropna(axis=1, how="all").empty
        ]

        if valid_results:
            freeman_carr = pd.concat(valid_results, ignore_index=True)
            freeman_carr["R2_score"] = freeman_carr["R2_score"].round(4)
            freeman_carr["Ea"] = freeman_carr["Ea"].round()
            freeman_carr["A"] = freeman_carr["A"].apply(lambda x: f"{x:.3e}" if pd.notnull(x) else x)
            freeman_carr = freeman_carr.sort_values(by="R2_score", ascending=False)
        else:
            freeman_carr = pd.DataFrame(columns=["Model", "R2_score", "Ea", "A"])
        return freeman_carr

    def prepare_plot_data_for_model(self, model_row: pd.DataFrame, reaction_df: pd.DataFrame):
        """
        x-axes: Δln(f(a))/Δ(1/T)
        y-axes: Δln(da/dT)/Δ(1/T)
        """
        temperature_K = reaction_df["temperature"] + 273.15
        beta_column = [col for col in reaction_df.columns if col != "temperature"][0]
        da_dT = reaction_df[beta_column]
        conversion = da_dT.cumsum() / da_dT.cumsum().max()
        conversion_series = pd.Series(conversion)
        da_dT_series = conversion_series.diff().astype(float)
        epsilon = 1e-8
        da_dT_series = da_dT_series.replace(0, epsilon)
        ln_da_dT = np.log(da_dT_series.values)
        model_func = NUC_MODELS_TABLE[model_row["Model"]]["differential_form"]
        ln_f_a = np.log(model_func(conversion_series) + epsilon)
        m = len(temperature_K)
        x_vals = []
        y_vals = []

        for j in range(2, m - 1):
            delta_ln_da_dT = ln_da_dT[j] - ln_da_dT[j - 1]
            delta_1_T = 1 / temperature_K.iloc[j + 1] - 1 / temperature_K.iloc[j]
            delta_ln_f_a = ln_f_a[j + 1] - ln_f_a[j]
            if np.isnan(delta_ln_da_dT) or np.isnan(delta_ln_f_a):
                continue
            if np.abs(delta_1_T) > epsilon:
                x_val = delta_ln_f_a / delta_1_T
                y_val = delta_ln_da_dT / delta_1_T
                x_vals.append(x_val)
                y_vals.append(y_val)
        if len(x_vals) < 2 or np.std(x_vals) < epsilon:
            plot_df = pd.DataFrame({"reverse_temperature": [], "lhs_clean": []})
            plot_kwargs = {
                "title": f"Model: {model_row['Model']}",
                "xlabel": r"$\Delta \ln(f(a)) / \Delta(1/T)$",
                "ylabel": r"$\Delta \ln(da/dT) / \Delta(1/T)$",
                "annotation": "",
            }
            return plot_df, plot_kwargs

        x_arr = np.array(x_vals)
        y_arr = np.array(y_vals)

        try:
            slope, intercept = np.polyfit(x_arr, y_arr, 1)
            y_fit = slope * x_arr + intercept
        except (ValueError, TypeError):
            plot_df = pd.DataFrame({"reverse_temperature": [], "lhs_clean": [], "y": []})
            plot_kwargs = {
                "title": f"Model: {model_row['Model']} - Error",
                "xlabel": r"$\Delta \ln(f(a)) / \Delta(1/T)$",
                "ylabel": r"$\Delta \ln(da/dT) / \Delta(1/T)$",
                "annotation": "Error in polyfit calculation",
            }
            return plot_df, plot_kwargs

        plot_df = pd.DataFrame({"reverse_temperature": x_arr, "lhs_clean": y_arr, "y": y_fit})

        model_name = model_row["Model"]
        Ea = float(model_row["Ea"]) if pd.notna(model_row["Ea"]) else 0.0
        try:
            A_val = float(model_row["A"])
        except (ValueError, TypeError):
            A_val = 0.0
        R2 = float(model_row["R2_score"]) if pd.notna(model_row["R2_score"]) else 0.0
        annotation = r"$ E_a = {:.2f} \n A = {:.2e} \n R^2 = {:.4f}$".format(Ea, A_val, R2)
        plot_kwargs = {
            "title": f"Model: {model_name}",
            "xlabel": r"$\Delta \ln(f(a)) / \Delta(1/T)$",
            "ylabel": r"$\Delta \ln(da/dT) / \Delta(1/T)$",
            "annotation": annotation,
        }
        return plot_df, plot_kwargs
