from functools import lru_cache
from typing import Any, Dict, List, Tuple

import numpy as np

from src.core.app_settings import PARAMETER_BOUNDS


class CurveFitting:
    """Mathematical functions and utilities for reaction curve fitting and deconvolution.

    Provides core mathematical functions (Gaussian, Fraser-Suzuki, ADS) for reaction
    modeling, parameter parsing, and default data generation. Used extensively
    throughout deconvolution and visualization processes.
    """

    @staticmethod
    def parse_reaction_params(
        reaction_params: dict,
    ) -> Dict[str, Tuple[Tuple[float, float], str, Tuple[Any, ...]]]:
        """Convert reaction dictionary to tuple format for calculation functions.

        Transforms stored reaction parameters into the optimized tuple format required
        by mathematical calculation functions. Handles coefficient extraction based
        on function types and creates proper x-range tuples.

        Args:
            reaction_params (dict): Raw reaction data with coeffs, bounds, and metadata.

        Returns:
            Dict containing structured tuples for coeffs, upper_bound_coeffs, lower_bound_coeffs.
        """
        x: np.ndarray = reaction_params.get("x", np.array([]))
        function_type: str = reaction_params.get("function", "")
        coeffs: dict = reaction_params.get("coeffs", {})
        upper_coeffs: dict = reaction_params.get("upper_bound_coeffs", {})
        lower_coeffs: dict = reaction_params.get("lower_bound_coeffs", {})

        x_range = (np.min(x), np.max(x)) if x.size > 0 else (0.0, 0.0)

        allowed_keys = CurveFitting._get_allowed_keys_for_type(function_type)

        coeffs_tuple = tuple(coeffs.get(key, None) for key in allowed_keys if key in coeffs)
        upper_coeffs_tuple = tuple(upper_coeffs.get(key, None) for key in allowed_keys if key in upper_coeffs)
        lower_coeffs_tuple = tuple(lower_coeffs.get(key, None) for key in allowed_keys if key in lower_coeffs)

        return {
            "coeffs": (x_range, function_type, coeffs_tuple),
            "upper_bound_coeffs": (x_range, function_type, upper_coeffs_tuple),
            "lower_bound_coeffs": (x_range, function_type, lower_coeffs_tuple),
        }

    @staticmethod
    def _get_allowed_keys_for_type(function_type: str) -> List[str]:
        """Return valid parameter names for the specified function type."""
        default_keys = ["h", "z", "w"]
        function_specific_keys = {
            "fraser": default_keys + ["fr"],
            "ads": default_keys + ["ads1", "ads2"],
        }
        return function_specific_keys.get(function_type, default_keys)

    @staticmethod
    def generate_default_function_data(df) -> dict:
        """Create default reaction parameters based on experimental data characteristics.

        Analyzes the input DataFrame to generate physically reasonable initial
        parameters for curve fitting. Used when adding new reactions to provide
        intelligent starting points for optimization.

        Args:
            df: DataFrame containing temperature and intensity data.

        Returns:
            dict: Complete reaction configuration with coeffs and bounds.
        """
        x = df["temperature"].copy()
        y_columns = [col for col in df.columns if col != "temperature"]
        if y_columns:
            bounds = PARAMETER_BOUNDS.deconvolution
            y = df[y_columns[0]]

            h = 0.3 * y.max()
            z = x.mean()
            w = 0.1 * (x.max() - x.min())

            h = max(bounds.h_min, min(h, bounds.h_max))
            z = max(bounds.z_min, min(z, bounds.z_max))
            w = max(bounds.w_min, min(w, bounds.w_max))

            h_lower, h_upper = h * 0.99, h * 1.01
            w_lower, w_upper = w * 0.99, w * 1.01

            fr = bounds.fr_default
            ads1 = bounds.ads1_default
            ads2 = bounds.ads2_default

            result_dict = {
                "function": "gauss",
                "x": x.to_numpy(),
                "coeffs": {
                    "h": h,
                    "z": z,
                    "w": w,
                    "fr": fr,
                    "ads1": ads1,
                    "ads2": ads2,
                },
                "upper_bound_coeffs": {
                    "h": h_upper,
                    "z": z,
                    "w": w_upper,
                    "fr": fr,
                    "ads1": ads1,
                    "ads2": ads2,
                },
                "lower_bound_coeffs": {
                    "h": h_lower,
                    "z": z,
                    "w": w_lower,
                    "fr": fr,
                    "ads1": ads1,
                    "ads2": ads2,
                },
            }
            return result_dict
        return {}

    @lru_cache(maxsize=128)
    @staticmethod
    def calculate_reaction(reaction_params: tuple):
        """Calculate reaction curve using cached computation for performance.

        Core calculation function that generates y-values for reaction curves
        based on function type and parameters. Heavily optimized with LRU caching
        for real-time GUI updates and deconvolution processes.

        Args:
            reaction_params (tuple): (x_range, function_type, coeffs) format.

        Returns:
            np.ndarray: Calculated y-values for the reaction curve.
        """
        x_range, function_type, coeffs = reaction_params
        x = np.linspace(x_range[0], x_range[1], 250)
        result = None
        if function_type == "gauss":
            result = CurveFitting.gaussian(x, *coeffs)
        elif function_type == "fraser":
            result = CurveFitting.fraser_suzuki(x, *coeffs)
        elif function_type == "ads":
            result = CurveFitting.asymmetric_double_sigmoid(x, *coeffs)
        return result

    @staticmethod
    def gaussian(x: np.ndarray, h: float, z: float, w: float) -> np.ndarray:
        """Standard Gaussian peak function."""
        return h * np.exp(-((x - z) ** 2) / (2 * w**2))

    @staticmethod
    def fraser_suzuki(x: np.ndarray, h: float, z: float, w: float, fs: float) -> np.ndarray:
        """Fraser-Suzuki asymmetric peak function with tail parameter."""
        with np.errstate(divide="ignore", invalid="ignore"):
            result = h * np.exp(-np.log(2) * ((np.log(1 + 2 * fs * ((x - z) / w)) / fs) ** 2))
        result = np.nan_to_num(result, nan=0)
        return result

    @staticmethod
    def asymmetric_double_sigmoid(x: np.ndarray, h: float, z: float, w: float, ads1: float, ads2: float) -> np.ndarray:
        """Asymmetric Double Sigmoid function for complex peak shapes."""
        exp_arg = -((x - z + w / 2) / ads1)
        left_term = (1 + np.exp(exp_arg)) ** -1

        _exp_arg = -((x - z - w / 2) / ads2)
        inner_term = (1 + np.exp(_exp_arg)) ** -1
        right_term = 1 - inner_term
        return h * left_term * right_term
