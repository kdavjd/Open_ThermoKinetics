"""Tests for curve_fitting module - mathematical peak functions."""

import numpy as np
import pandas as pd
import pytest

from src.core.curve_fitting import CurveFitting


class TestGaussian:
    """Tests for Gaussian peak function."""

    def test_gaussian_max_at_center(self, sample_x_array, sample_gaussian_params):
        """Peak maximum should be at center position z."""
        result = CurveFitting.gaussian(
            sample_x_array,
            sample_gaussian_params["h"],
            sample_gaussian_params["z"],
            sample_gaussian_params["w"],
        )
        max_idx = np.argmax(result)
        assert sample_x_array[max_idx] == pytest.approx(sample_gaussian_params["z"], rel=1e-2)

    def test_gaussian_max_value(self, sample_x_array, sample_gaussian_params):
        """Peak height should approximately equal h parameter."""
        result = CurveFitting.gaussian(
            sample_x_array,
            sample_gaussian_params["h"],
            sample_gaussian_params["z"],
            sample_gaussian_params["w"],
        )
        # Allow small tolerance due to discrete x sampling
        assert np.max(result) == pytest.approx(sample_gaussian_params["h"], rel=0.001)

    def test_gaussian_symmetric(self, sample_gaussian_params):
        """Gaussian should be symmetric around center."""
        z = sample_gaussian_params["z"]
        offset = 20.0
        x_left = z - offset
        x_right = z + offset

        result_left = CurveFitting.gaussian(x_left, **sample_gaussian_params)
        result_right = CurveFitting.gaussian(x_right, **sample_gaussian_params)

        assert result_left == pytest.approx(result_right, rel=1e-10)

    def test_gaussian_positive(self, sample_x_array, sample_gaussian_params):
        """Gaussian should produce only positive values for positive h."""
        result = CurveFitting.gaussian(
            sample_x_array,
            sample_gaussian_params["h"],
            sample_gaussian_params["z"],
            sample_gaussian_params["w"],
        )
        assert np.all(result >= 0)

    def test_gaussian_zero_height(self, sample_x_array, sample_gaussian_params):
        """Zero height should produce zero output."""
        result = CurveFitting.gaussian(sample_x_array, 0.0, sample_gaussian_params["z"], sample_gaussian_params["w"])
        assert np.allclose(result, 0.0)


class TestFraserSuzuki:
    """Tests for Fraser-Suzuki asymmetric peak function."""

    def test_fraser_suzuki_returns_array(self, sample_x_array, sample_fraser_params):
        """Should return numpy array of same length as input."""
        result = CurveFitting.fraser_suzuki(
            sample_x_array,
            sample_fraser_params["h"],
            sample_fraser_params["z"],
            sample_fraser_params["w"],
            sample_fraser_params["fs"],
        )
        assert isinstance(result, np.ndarray)
        assert len(result) == len(sample_x_array)

    def test_fraser_suzuki_max_approximately_at_z(self, sample_x_array, sample_fraser_params):
        """Peak maximum should be approximately near center for small asymmetry."""
        result = CurveFitting.fraser_suzuki(
            sample_x_array,
            sample_fraser_params["h"],
            sample_fraser_params["z"],
            sample_fraser_params["w"],
            sample_fraser_params["fs"],
        )
        max_idx = np.argmax(result)
        # Allow some deviation for asymmetric peaks
        assert abs(sample_x_array[max_idx] - sample_fraser_params["z"]) < sample_fraser_params["w"]

    def test_fraser_suzuki_handles_invalid_input(self):
        """Should handle edge cases without crashing (NaN becomes 0)."""
        x = np.array([100.0, 200.0, 300.0])
        result = CurveFitting.fraser_suzuki(x, 1.0, 200.0, 30.0, 10.0)  # Large fs
        assert isinstance(result, np.ndarray)
        assert not np.any(np.isnan(result))


class TestAsymmetricDoubleSigmoid:
    """Tests for Asymmetric Double Sigmoid peak function."""

    def test_ads_returns_array(self, sample_x_array, sample_ads_params):
        """Should return numpy array of same length as input."""
        result = CurveFitting.asymmetric_double_sigmoid(
            sample_x_array,
            sample_ads_params["h"],
            sample_ads_params["z"],
            sample_ads_params["w"],
            sample_ads_params["ads1"],
            sample_ads_params["ads2"],
        )
        assert isinstance(result, np.ndarray)
        assert len(result) == len(sample_x_array)

    def test_ads_max_value(self, sample_x_array, sample_ads_params):
        """Peak height should be positive and bounded by h."""
        result = CurveFitting.asymmetric_double_sigmoid(
            sample_x_array,
            sample_ads_params["h"],
            sample_ads_params["z"],
            sample_ads_params["w"],
            sample_ads_params["ads1"],
            sample_ads_params["ads2"],
        )
        # ADS function is bounded by h but actual max depends on parameter relationships
        assert np.max(result) > 0
        assert np.max(result) <= sample_ads_params["h"] * 1.01  # Allow small numerical tolerance

    def test_ads_positive(self, sample_x_array, sample_ads_params):
        """ADS should produce only positive values for positive h."""
        result = CurveFitting.asymmetric_double_sigmoid(
            sample_x_array,
            sample_ads_params["h"],
            sample_ads_params["z"],
            sample_ads_params["w"],
            sample_ads_params["ads1"],
            sample_ads_params["ads2"],
        )
        assert np.all(result >= 0)


class TestParseReactionParams:
    """Tests for parse_reaction_params utility."""

    def test_parse_gaussian_params(self, sample_gaussian_reaction_params):
        """Should correctly parse Gaussian reaction parameters."""
        result = CurveFitting.parse_reaction_params(sample_gaussian_reaction_params)

        assert "coeffs" in result
        assert "upper_bound_coeffs" in result
        assert "lower_bound_coeffs" in result

        x_range, func_type, coeffs = result["coeffs"]
        assert func_type == "gauss"
        assert len(coeffs) == 3  # h, z, w

    def test_parse_fraser_params(self, sample_fraser_reaction_params):
        """Should correctly parse Fraser-Suzuki reaction parameters."""
        result = CurveFitting.parse_reaction_params(sample_fraser_reaction_params)

        x_range, func_type, coeffs = result["coeffs"]
        assert func_type == "fraser"
        assert len(coeffs) == 4  # h, z, w, fr

    def test_parse_ads_params(self, sample_ads_reaction_params):
        """Should correctly parse ADS reaction parameters."""
        result = CurveFitting.parse_reaction_params(sample_ads_reaction_params)

        x_range, func_type, coeffs = result["coeffs"]
        assert func_type == "ads"
        assert len(coeffs) == 5  # h, z, w, ads1, ads2

    def test_parse_empty_x_range(self):
        """Should handle empty x array gracefully."""
        params = {"x": np.array([]), "function": "gauss", "coeffs": {"h": 1.0, "z": 450.0, "w": 30.0}}
        result = CurveFitting.parse_reaction_params(params)

        x_range, _, _ = result["coeffs"]
        assert x_range == (0.0, 0.0)


class TestGenerateDefaultFunctionData:
    """Tests for generate_default_function_data utility."""

    def test_generate_default_data(self, sample_dataframe):
        """Should generate default reaction parameters from DataFrame."""
        result = CurveFitting.generate_default_function_data(sample_dataframe)

        assert result["function"] == "gauss"
        assert "coeffs" in result
        assert "h" in result["coeffs"]
        assert "z" in result["coeffs"]
        assert "w" in result["coeffs"]

    def test_generate_default_data_bounds(self, sample_dataframe):
        """Should include upper and lower bound coefficients."""
        result = CurveFitting.generate_default_function_data(sample_dataframe)

        assert "upper_bound_coeffs" in result
        assert "lower_bound_coeffs" in result

    def test_generate_default_data_empty_dataframe(self):
        """Should return empty dict for DataFrame without y columns."""
        df = pd.DataFrame({"temperature": np.linspace(300, 600, 100)})
        result = CurveFitting.generate_default_function_data(df)

        assert result == {}


class TestCalculateReaction:
    """Tests for calculate_reaction cached calculation."""

    def test_calculate_gaussian_reaction(self, sample_gaussian_reaction_params):
        """Should calculate Gaussian reaction curve."""
        parsed = CurveFitting.parse_reaction_params(sample_gaussian_reaction_params)
        result = CurveFitting.calculate_reaction(parsed["coeffs"])

        assert isinstance(result, np.ndarray)
        assert len(result) == 250  # Default linspace points

    def test_calculate_fraser_reaction(self, sample_fraser_reaction_params):
        """Should calculate Fraser-Suzuki reaction curve."""
        parsed = CurveFitting.parse_reaction_params(sample_fraser_reaction_params)
        result = CurveFitting.calculate_reaction(parsed["coeffs"])

        assert isinstance(result, np.ndarray)
        assert len(result) == 250

    def test_calculate_ads_reaction(self, sample_ads_reaction_params):
        """Should calculate ADS reaction curve."""
        parsed = CurveFitting.parse_reaction_params(sample_ads_reaction_params)
        result = CurveFitting.calculate_reaction(parsed["coeffs"])

        assert isinstance(result, np.ndarray)
        assert len(result) == 250
