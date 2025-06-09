import warnings

import numpy as np
import pandas as pd
from scipy import integrate
from scipy.constants import R
from scipy.interpolate import interp1d

from src.core.app_settings import NUC_MODELS_TABLE, OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger


class ModelFreeCalculation(BaseSlots):
    def __init__(self, actor_name: str = "model_free_calculation", signals=None):
        super().__init__(actor_name=actor_name, signals=signals)
        self.strategies = {
            "linear approximation": LinearApproximation,
            "Friedman": Friedman,
            "Kissinger": Kissinger,
            "Vyazovkin": Vyazovkin,
            "master plots": MasterPlots,
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
        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}, \n\n{calculation_params=}")
            return

        kwargs = {
            "alpha_min": calculation_params.get("alpha_min", 0.005),
            "alpha_max": calculation_params.get("alpha_max", 0.995),
        }
        if calculation_params.get("ea_mean") is not None:
            kwargs["ea_mean"] = calculation_params["ea_mean"] * 1000  #  kJ/mol to J/mol
        elif calculation_params.get("ea_min") is not None and calculation_params.get("ea_max") is not None:
            kwargs["ea_min"] = calculation_params["ea_min"] * 1000
            kwargs["ea_max"] = calculation_params["ea_max"] * 1000

        strategy = FitMethod(**kwargs)

        result_data = {}
        for reaction_name, reaction_df in reaction_data.items():
            if fit_method == "master plots":
                if reaction_name != calculation_params.get("reaction_n"):
                    continue

            reaction_df["temperature"] = reaction_df["temperature"] + 273.15
            beta_columns = [col for col in reaction_df.columns if col != "temperature"]
            if len(beta_columns) < 2:
                logger.error("There are not enough beta columns for model free calculation.")
                response["data"] = False
                return

            # if fit_method != "master plots":
            #     for beta_column in beta_columns:
            #         reaction_df[beta_column] = (
            #             reaction_df[beta_column].cumsum() / reaction_df[beta_column].cumsum().max()
            #         )

            reaction_results = strategy.calculate(reaction_df)
            result_data[reaction_name] = reaction_results

        response["data"] = result_data
        logger.debug(f"Calculation results for '{fit_method}': {result_data}")

    def _handle_plot_model_fit_result(self, calculation_params: dict, response: dict):
        fit_method = calculation_params.get("fit_method")
        result_df = calculation_params.get("result_df")
        FitMethod = self.strategies.get(fit_method)
        if FitMethod is None:
            logger.error(f"Unknown fit method: {fit_method}")
            return

        kwargs = {
            "alpha_min": calculation_params.get("alpha_min", 0.01),
            "alpha_max": calculation_params.get("alpha_max", 0.99),
        }
        strategy = FitMethod(**kwargs)

        plot_df, plot_kwargs = strategy.prepare_plot_data(result_df)
        response["data"] = [{"plot_df": plot_df, "plot_kwargs": plot_kwargs}]


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
            r"$ OFW = {:.0f}, std =  {:.0f} \n KAS = {:.0f}, std = {:.0f} \n Starink = {:.0f}, std = {:.0f}$".format(
                mean_ofw, std_ofw, mean_kas, std_kas, mean_starink, std_starink
            )
        )

        plot_kwargs = {
            "title": "Ea vs α for linear approximations of varying accuracy",
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

    def prepare_plot_data(self, df: pd.DataFrame):
        mean_friedman = df["Friedman"].mean()
        std_friedman = df["Friedman"].std()
        annotation = r"$Friedman = {:.0f}, std = {:.0f}$".format(mean_friedman, std_friedman)
        plot_kwargs = {
            "title": "Friedman Method: Ea vs α",
            "xlabel": "α",
            "ylabel": r"$E_{a}$, J/Mole",
            "annotation": annotation,
        }
        return df, plot_kwargs


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

    def prepare_plot_data(self, df: pd.DataFrame):
        mean_kissinger = df["Kissinger_Ea"].mean()
        std_kissinger = df["Kissinger_Ea"].std()
        annotation = r"$Kissinger = {:.0f}, std = {:.0f}$".format(mean_kissinger, std_kissinger)
        plot_kwargs = {
            "title": "Kissinger Method: Ea vs Conversion",
            "xlabel": "α",
            "ylabel": r"$E_{a}$, J/Mole",
            "annotation": annotation,
        }
        return df, plot_kwargs


class Vyazovkin:
    def __init__(self, alpha_min: float, alpha_max: float, ea_min: float = 10000, ea_max: float = 300000):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.ea_min = ea_min
        self.ea_max = ea_max

    def calculate(self, reaction_df: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
        beta_cols = [col for col in reaction_df.columns if col != "temperature"]

        conv_df = pd.DataFrame()
        for col in beta_cols:
            cum = reaction_df[col].cumsum()
            conv_df[col] = cum / cum.iloc[-1]

        temperature = reaction_df["temperature"]

        f_funcs = {
            col: interp1d(conv_df[col], temperature, bounds_error=False, fill_value="extrapolate") for col in beta_cols
        }

        conv_grid = np.linspace(self.alpha_min, self.alpha_max, 100)

        T_matrix = {}
        for col in beta_cols:
            T_matrix[col] = f_funcs[col](conv_grid)

        beta_vals = {col: float(col) for col in beta_cols}

        dT = reaction_df["temperature"].diff().mean()

        def integrand(T, Ea):
            return np.exp(-Ea / (R * T))

        def I_func(Ea, T, dT):
            integral, _ = integrate.quad(integrand, T - dT, T, args=(Ea,))
            return integral

        def vyazovkin_lhs(Ea, dT, pairs):
            n = len(pairs)
            sum_ratio = 0.0
            for i in range(n):
                T_i, beta_i = pairs[i]
                for j in range(n):
                    if i != j:
                        T_j, beta_j = pairs[j]
                        I_i = I_func(Ea, T_i, dT)
                        I_j = I_func(Ea, T_j, dT)
                        sum_ratio += (beta_j / beta_i) * (I_i / I_j)
            result = (n * (n - 1) - sum_ratio) * -1
            return result

        candidate_Ea = np.arange(self.ea_min, self.ea_max + 1, 1000)
        estimated_Ea = []

        for idx, alpha in enumerate(conv_grid):
            pairs = []
            for col in beta_cols:
                pairs.append((T_matrix[col][idx], beta_vals[col]))
            f_vals = [abs(vyazovkin_lhs(Ea, dT, pairs)) for Ea in candidate_Ea]
            best_index = np.argmin(f_vals)
            best_Ea = candidate_Ea[best_index]
            estimated_Ea.append(best_Ea)

        result_df = pd.DataFrame({"conversion": conv_grid, "Vyazovkin": estimated_Ea})
        return result_df

    def prepare_plot_data(self, df: pd.DataFrame):
        mean_vyazovkin = df["Vyazovkin"].mean()
        std_vyazovkin = df["Vyazovkin"].std()
        annotation = r"$Vyazovkin = {:.0f}, std = {:.0f}$".format(mean_vyazovkin, std_vyazovkin)
        plot_kwargs = {
            "title": "Vyazovkin Method: Ea vs α",
            "xlabel": "α",
            "ylabel": r"$E_{a}$, J/Mole",
            "annotation": annotation,
        }
        return df, plot_kwargs


class MasterPlots:
    def __init__(self, alpha_min, alpha_max, ea_mean=0, master_plot="y(α)"):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.Ea_mean = ea_mean
        self.master_plot = master_plot

    @staticmethod
    def normalize_data(arr):
        arr = np.array(arr)
        finite_mask = np.isfinite(arr)
        if not finite_mask.any():
            return arr
        arr_min = np.min(arr[finite_mask])
        arr_max = np.max(arr[finite_mask])
        if arr_max - arr_min != 0:
            return (arr - arr_min) / (arr_max - arr_min)
        else:
            return arr

    @staticmethod
    def r2_score(y_true, y_pred):
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - ss_res / ss_tot

    def get_exp_term(self, temperature):
        return np.exp(self.Ea_mean / (R * temperature))

    def calculate_y_master_plot(self, da_dt, exp_term):
        y_a = da_dt * exp_term
        y_a_norm = (y_a - y_a.min()) / (y_a.max() - y_a.min())
        return y_a_norm

    def calculate_g_master_plot(self, temperature_a: np.ndarray):
        def integrand(T):
            return np.exp(-self.Ea_mean / (R * T))

        N = len(temperature_a)
        g_values = []
        for i in range(N):
            if i == 0:
                lower_bound = temperature_a[i]
                upper_bound = (temperature_a[i] + temperature_a[i + 1]) / 2
            elif i == N - 1:
                lower_bound = (temperature_a[i - 1] + temperature_a[i]) / 2
                upper_bound = temperature_a[i]
            else:
                lower_bound = (temperature_a[i - 1] + temperature_a[i]) / 2
                upper_bound = (temperature_a[i] + temperature_a[i + 1]) / 2

            integral_value, _ = integrate.quad(integrand, lower_bound, upper_bound)
            g_values.append(integral_value)

        g_a = np.array(g_values)
        g_norm = (g_a - g_a.min()) / (g_a.max() - g_a.min())
        return g_norm

    def model_r2_scores(self, experiment_norm, conversion, model_form, z_a=False):
        e = 1 - conversion
        r2_scores = {}
        model_predictions = {}
        for model, funcs in NUC_MODELS_TABLE.items():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    raw_model = (
                        funcs[model_form](e) if not z_a else funcs["differential_form"](e) * funcs["integral_form"](e)
                    )
                    model_norm = self.normalize_data(raw_model)
                    score = self.r2_score(experiment_norm, model_norm)
                    r2_scores[model] = score
                    model_predictions[model] = model_norm
            except Exception as exception:
                print(f"Проблема с моделью {model}: {exception}")

        top_models = sorted(r2_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        df_dict = {"conversion": conversion, "experiment": experiment_norm}
        for model, score in top_models:
            df_dict[model] = model_predictions[model]
        return pd.DataFrame(df_dict)

    def calculate_z_master_plot(self, da_dt, temperature_a):
        z = da_dt * temperature_a**2
        z_norm = (z - z.min()) / (z.max() - z.min())
        return z_norm

    def calculate(self, reaction_df: pd.DataFrame) -> pd.DataFrame:
        rate_cols = [col for col in reaction_df.columns if col != "temperature"]
        temperature = reaction_df["temperature"].values
        y_a_results = {}
        g_a_results = {}
        z_a_results = {}
        for beta in rate_cols:
            da_dT = reaction_df[beta].values

            valid = ~np.isnan(temperature) & ~np.isnan(da_dT)
            da_dT, temperature_valid = da_dT[valid], temperature[valid]
            conversion = da_dT.cumsum() / da_dT.cumsum().max()

            exp_term = self.get_exp_term(temperature_valid)
            y_a_norm = self.calculate_y_master_plot(da_dT, exp_term)
            g_a_norm = self.calculate_g_master_plot(temperature_valid)
            z_a_norm = self.calculate_z_master_plot(da_dT, temperature_valid)
            sorted_ya_r2 = self.model_r2_scores(y_a_norm, conversion, "differential_form")
            sorted_ga_r2 = self.model_r2_scores(g_a_norm, conversion, "integral_form")
            sorted_za_r2 = self.model_r2_scores(z_a_norm, conversion, "_", z_a=True)
            y_a_results[beta] = sorted_ya_r2
            g_a_results[beta] = sorted_ga_r2
            z_a_results[beta] = sorted_za_r2

        return {
            "y(α)": y_a_results,
            "g(α)": g_a_results,
            "z(α)": z_a_results,
        }

    def prepare_plot_data(self, df: pd.DataFrame):
        annotation_parts = []
        for col in df.columns:
            if col not in ["conversion", "experiment"]:
                r2 = self.r2_score(df["experiment"], df[col])
                annotation_parts.append(f"{col} = {r2:.2f}")

        annotation = "\n".join(annotation_parts)

        plot_kwargs = {
            "title": "Master Plot: Model R2 Scores",
            "xlabel": "α",
            "ylabel": "R2 Score",
            "annotation": annotation,
        }

        return df, plot_kwargs
