import numpy as np
import pandas as pd
from scipy.constants import R
from scipy.interpolate import interp1d

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger


class ModelFreeCalculation(BaseSlots):
    def __init__(self, actor_name: str = "model_free_calculation", signals=None):
        super().__init__(actor_name=actor_name, signals=signals)
        self.strategies = {
            "linear approximation": LinearApproximation,
            "Friedman": Friedman,
            "Kissinger": Kissinger,
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
            OperationType.MODEL_FREE_CALCULATION: self._handle_model_free_calculation,
            OperationType.PLOT_MODEL_FREE_RESULT: self._handle_plot_model_fit_result,
        }

        handler = operations_map.get(operation)
        if handler is not None:
            handler(calculation_params, response)
        else:
            logger.error(f"Unknown operation '{operation}' received by {self.actor_name}")

        self.signals.response_signal.emit(response)

    def _handle_model_free_calculation(self, calculation_params: dict, response: dict):
        fit_method = calculation_params.get("fit_method")
        reaction_data = calculation_params.get("reaction_data")
        alpha_min = calculation_params.get("alpha_min", 0.005)
        alpha_max = calculation_params.get("alpha_max", 0.995)

        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}")
            return

        strategy = FitMethod(alpha_min, alpha_max)
        result_data = {}
        for reaction_name, reaction_df in reaction_data.items():
            reaction_df["temperature"] = reaction_df["temperature"] + 273.15
            beta_columns = [col for col in reaction_df.columns if col != "temperature"]
            if len(beta_columns) < 2:
                logger.error("There are not enough beta columns for model free calculation")
                response["data"] = False
                return

            for beta_column in beta_columns:
                reaction_df[beta_column] = reaction_df[beta_column].cumsum() / reaction_df[beta_column].cumsum().max()

            reaction_results = strategy.calculate(reaction_df)
            result_data[reaction_name] = reaction_results

        response["data"] = result_data
        logger.debug(f"Calculation results for '{fit_method}': {result_data}")

    def _handle_plot_model_fit_result(self, calculation_params: dict, response: dict):
        fit_method = calculation_params.get("fit_method")
        result_df = calculation_params.get("result_df")
        alpha_min = calculation_params.get("alpha_min", 0.01)
        alpha_max = calculation_params.get("alpha_max", 0.99)

        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}")
            return

        strategy = FitMethod(alpha_min=alpha_min, alpha_max=alpha_max)

        plot_data = []

        plot_df, plot_kwargs = strategy.prepare_plot_data(result_df)
        plot_data.append({"plot_df": plot_df, "plot_kwargs": plot_kwargs})

        response["data"] = plot_data


class LinearApproximation:
    def __init__(self, alpha_min: float, alpha_max: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max

    def calculate(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        return self.fetch_linear_approx_Ea(reaction_df)

    def fetch_linear_approx_Ea(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        rate_cols = [col for col in reaction_df.columns if col != "temperature"]

        conv = reaction_df[rate_cols].cumsum() / reaction_df[rate_cols].cumsum().max()
        temperature = reaction_df["temperature"]

        valid = temperature.notna() & conv.notna().all(axis=1)
        conv, temperature = conv[valid], temperature[valid]

        f = {
            rate: interp1d(conv[rate], temperature, bounds_error=False, fill_value="extrapolate") for rate in rate_cols
        }

        lower_bound = max(conv.min().min(), self.alpha_min)
        upper_bound = min(conv.max().max(), self.alpha_max)
        conv_grid = np.linspace(lower_bound, upper_bound, 100)

        T = np.column_stack([f[rate](conv_grid) for rate in rate_cols])
        X = 1.0 / T
        x_mean = X.mean(axis=1, keepdims=True)
        denom = ((X - x_mean) ** 2).sum(axis=1)

        rates = np.array([float(rate) for rate in rate_cols])
        log_rates = np.log(rates)

        # OFW: y = ln(β)
        Y_OFW = np.tile(log_rates, (100, 1))
        slope_OFW = ((X - x_mean) * (Y_OFW - Y_OFW.mean(axis=1, keepdims=True))).sum(axis=1) / denom

        # KAS: y = ln(β) - 2·ln(T)
        Y_KAS = log_rates - 2 * np.log(T)
        slope_KAS = ((X - x_mean) * (Y_KAS - Y_KAS.mean(axis=1, keepdims=True))).sum(axis=1) / denom

        # Starink: y = ln(β) - 1.92·ln(T)
        Y_Starink = log_rates - 1.92 * np.log(T)
        slope_Starink = ((X - x_mean) * (Y_Starink - Y_Starink.mean(axis=1, keepdims=True))).sum(axis=1) / denom

        Ea_OFW = slope_OFW * R / -1.052
        Ea_KAS = slope_KAS * R / -1.0
        Ea_Starink = slope_Starink * R / -1.008

        return pd.DataFrame({"conversion": conv_grid, "OFW": Ea_OFW, "KAS": Ea_KAS, "Starink": Ea_Starink})

    def prepare_plot_data(self, df: pd.DataFrame):
        mean_ofw = df["OFW"].mean()
        std_ofw = df["OFW"].std()
        mean_kas = df["KAS"].mean()
        std_kas = df["KAS"].std()
        mean_starink = df["Starink"].mean()
        std_starink = df["Starink"].std()

        annotation = (
            f"OFW: {mean_ofw:.0f}, std {std_ofw:.0f}\n"
            f"KAS: {mean_kas:.0f}, std {std_kas:.0f}\n"
            f"Starink: {mean_starink:.0f}, std {std_starink:.0f}"
        )
        annotation = (
            r"$ OFW = {:.0f}, std =  {:.0f} \n KAS = {:.0f}, std = {:.0f} \n Starink = {:.0f}, std = {:.0f}$".format(
                mean_ofw, std_ofw, mean_kas, std_kas, mean_starink, std_starink
            )
        )

        plot_kwargs = {
            "title": "Ea(α) for linear approximations of varying accuracy",
            "xlabel": "α",
            "ylabel": r"$E_{a}$, J/Mole",
            "annotation": annotation,
        }

        return df, plot_kwargs


class Friedman:
    def __init__(self, alpha_min: float, alpha_max: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max

    def calculate(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        return self.fetch_friedman_Ea(reaction_df)

    def fetch_friedman_Ea(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        rate_cols = [col for col in reaction_df.columns if col != "temperature"]

        conv = reaction_df[rate_cols].cumsum() / reaction_df[rate_cols].cumsum().max()
        temperature = reaction_df["temperature"]

        valid = temperature.notna() & conv.notna().all(axis=1)
        conv, temperature = conv[valid], temperature[valid]

        f = {
            rate: interp1d(conv[rate], temperature, bounds_error=False, fill_value="extrapolate") for rate in rate_cols
        }

        lower_bound = max(conv.min().min(), self.alpha_min)
        upper_bound = min(conv.max().max(), self.alpha_max)
        conv_grid = np.linspace(lower_bound, upper_bound, 100)

        T = np.column_stack([f[rate](conv_grid) for rate in rate_cols])
        X = 1.0 / T

        x_mean = X.mean(axis=1, keepdims=True)
        denom = ((X - x_mean) ** 2).sum(axis=1)

        rates = np.array([float(rate) for rate in rate_cols])
        log_rates = np.log(rates)  # ln(β)

        # ln(dα/dT) = ln(β) - ln(T)
        Y_Friedman = np.tile(log_rates, (len(conv_grid), 1)) - np.log(T)
        slope_Friedman = ((X - x_mean) * (Y_Friedman - Y_Friedman.mean(axis=1, keepdims=True))).sum(axis=1) / denom

        Ea_Friedman = -slope_Friedman * R

        return pd.DataFrame({"conversion": conv_grid, "Friedman": Ea_Friedman})


class Kissinger:
    def __init__(self, alpha_min: float, alpha_max: float):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max

    def calculate(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        return self.fetch_kissinger_Ea(reaction_df)

    def fetch_kissinger_Ea(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        rate_cols = [col for col in reaction_df.columns if col != "temperature"]

        temperature_K = reaction_df["temperature"]

        peak_points = []
        for col in rate_cols:
            series = reaction_df[col]

            valid = series.notna() & temperature_K.notna()
            if valid.sum() == 0:
                continue

            cum = series[valid].cumsum()
            conv = cum / cum.iloc[-1]

            idx_peak = series.idxmax()
            T_peak = temperature_K.loc[idx_peak]
            alpha_peak = conv.loc[idx_peak]
            beta_val = float(col)
            peak_points.append((beta_val, T_peak, alpha_peak))

        peak_points.sort(key=lambda x: x[2])

        beta_vals = np.array([pt[0] for pt in peak_points], dtype=float)
        T_peaks = np.array([pt[1] for pt in peak_points], dtype=float)
        alphas = np.array([pt[2] for pt in peak_points], dtype=float)

        # X = 1/Tₚ, Y = ln(β / Tₚ²)
        X = 1.0 / T_peaks
        Y = np.log(beta_vals / (T_peaks**2))
        slope, intercept = np.polyfit(X, Y, 1)
        E_a = -slope * R

        result_df = pd.DataFrame({"conversion": alphas, "Kissinger_Ea": [E_a] * len(alphas)})
        return result_df
