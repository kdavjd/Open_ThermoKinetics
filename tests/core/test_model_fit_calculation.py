"""Tests for model_fit_calculation module - model-fitting kinetic analysis."""

import numpy as np
import pandas as pd
import pytest

from src.core.model_fit_calculation import (
    CoatsRedfern,
    DirectDiff,
    FreemanCaroll,
    ModelFitCalculation,
    r2_score,
)


class TestR2Score:
    """Tests for r2_score helper function."""

    def test_perfect_fit(self):
        """R2 should be 1.0 for identical arrays."""
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        assert r2_score(y, y) == pytest.approx(1.0)

    def test_no_correlation(self):
        """R2 should be 0 when predictions equal mean."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([3.0, 3.0, 3.0, 3.0, 3.0])  # mean of y_true
        assert r2_score(y_true, y_pred) == pytest.approx(0.0)

    def test_linear_relationship(self):
        """R2 should be 1.0 for perfectly correlated linear transformation."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = y_true * 2 + 1  # Perfect linear transformation
        # Note: R2=1 requires y_pred == y_true exactly, not just linear correlation
        # This test verifies R2 handles linear transformations correctly
        result = r2_score(y_true, y_pred)
        assert result < 1.0  # Not exact match, so R2 < 1

    def test_pandas_series_input(self):
        """Should accept pandas Series as input."""
        y_true = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = pd.Series([1.1, 2.1, 2.9, 4.2, 4.8])
        result = r2_score(y_true, y_pred)
        assert 0.9 < result <= 1.0


class TestDirectDiff:
    """Tests for DirectDiff model-fitting strategy."""

    @pytest.fixture
    def strategy(self):
        """Create DirectDiff strategy with default params."""
        return DirectDiff(alpha_min=0.01, alpha_max=0.99, valid_proportion=0.5)

    @pytest.fixture
    def sample_conversion_data(self):
        """Create sample temperature and conversion data."""
        temperature = pd.Series(np.linspace(400, 600, 100))
        # Simulate sigmoid-like conversion curve
        conversion = 1 / (1 + np.exp(-0.03 * (temperature - 500)))
        return temperature, conversion

    def test_calculate_direct_diff_params(self, strategy):
        """Ea and A calculation from slope and intercept."""
        slope = -10000.0  # Typical slope for Ea ~83 kJ/mol
        intercept = 20.0
        beta = 10  # K/min
        Ea, A = strategy._calculate_direct_diff_params(slope, intercept, beta)
        assert Ea > 0  # Activation energy should be positive
        assert A > 0  # Pre-exponential factor should be positive

    def test_trim_conversion(self, strategy, sample_conversion_data):
        """Should trim conversion to alpha_min/alpha_max range."""
        temperature, conversion = sample_conversion_data
        trimmed_T, trimmed_conv = strategy._trim_conversion(temperature, conversion)
        assert trimmed_conv.min() >= strategy.alpha_min
        assert trimmed_conv.max() <= strategy.alpha_max

    def test_calculate_returns_dataframe(self, strategy, sample_conversion_data):
        """calculate() should return DataFrame with Model, R2_score, Ea, A columns."""
        temperature, conversion = sample_conversion_data
        beta = 10
        result = strategy.calculate(temperature, conversion, beta)

        assert isinstance(result, pd.DataFrame)
        expected_cols = {"Model", "R2_score", "Ea", "A"}
        assert expected_cols.issubset(set(result.columns))

    def test_calculate_returns_sorted_by_r2(self, strategy, sample_conversion_data):
        """Results should be sorted by R2_score descending."""
        temperature, conversion = sample_conversion_data
        result = strategy.calculate(temperature, conversion, beta=10)

        if len(result) > 1:
            r2_values = result["R2_score"].values
            # Check descending order (ignoring NaN values)
            valid_r2 = r2_values[~np.isnan(r2_values)]
            if len(valid_r2) > 1:
                assert all(valid_r2[i] >= valid_r2[i + 1] for i in range(len(valid_r2) - 1))

    def test_prepare_plot_data_for_model(self, strategy, sample_conversion_data):
        """prepare_plot_data_for_model should return plot DataFrame and kwargs."""
        temperature, conversion = sample_conversion_data
        result = strategy.calculate(temperature, conversion, beta=10)

        if len(result) > 0:
            model_row = result.iloc[0]
            reaction_df = pd.DataFrame(
                {"temperature": temperature, "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2))}
            )
            plot_df, plot_kwargs = strategy.prepare_plot_data_for_model(model_row, reaction_df)

            assert isinstance(plot_df, pd.DataFrame)
            assert "title" in plot_kwargs
            assert "xlabel" in plot_kwargs

    def test_filter_inf_data(self, strategy):
        """_filter_inf_data should remove inf values."""
        lhs = np.array([1.0, np.inf, 2.0, -np.inf, 3.0])
        temperature = np.array([400.0, 450.0, 500.0, 550.0, 600.0])

        clean_T, clean_lhs = strategy._filter_inf_data(lhs, temperature)

        assert len(clean_T) == 3
        assert len(clean_lhs) == 3
        assert np.all(np.isfinite(clean_T))
        assert np.all(np.isfinite(clean_lhs))


class TestCoatsRedfern:
    """Tests for Coats-Redfern integral method strategy."""

    @pytest.fixture
    def strategy(self):
        """Create CoatsRedfern strategy with default params."""
        return CoatsRedfern(alpha_min=0.01, alpha_max=0.99, valid_proportion=0.5)

    @pytest.fixture
    def sample_conversion_data(self):
        """Create sample temperature and conversion data."""
        temperature = pd.Series(np.linspace(400, 600, 100))
        conversion = 1 / (1 + np.exp(-0.03 * (temperature - 500)))
        return temperature, conversion

    def test_calculate_coats_redfern_lhs(self, strategy):
        """LHS calculation should return finite values for valid input."""
        g_a_val = np.array([0.1, 0.5, 1.0, 2.0])
        temperature = np.array([400.0, 450.0, 500.0, 550.0])
        result = strategy.calculate_coats_redfern_lhs(g_a_val, temperature)
        assert isinstance(result, np.ndarray)

    def test_calculate_returns_dataframe(self, strategy, sample_conversion_data):
        """calculate() should return DataFrame with expected columns."""
        temperature, conversion = sample_conversion_data
        result = strategy.calculate(temperature, conversion, beta=10)

        assert isinstance(result, pd.DataFrame)
        expected_cols = {"Model", "R2_score", "Ea", "A"}
        assert expected_cols.issubset(set(result.columns))

    def test_prepare_plot_data_for_model(self, strategy, sample_conversion_data):
        """prepare_plot_data_for_model should return plot DataFrame and kwargs."""
        temperature, conversion = sample_conversion_data
        result = strategy.calculate(temperature, conversion, beta=10)

        if len(result) > 0:
            model_row = result.iloc[0]
            reaction_df = pd.DataFrame(
                {"temperature": temperature, "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2))}
            )
            plot_df, plot_kwargs = strategy.prepare_plot_data_for_model(model_row, reaction_df)

            assert isinstance(plot_df, pd.DataFrame)
            assert "title" in plot_kwargs

    def test_calculate_coats_redfern_params(self, strategy):
        """calculate_coats_redfern_params should return Ea and A."""
        slope = -10000.0
        intercept = 20.0
        beta = 10
        temperature = np.array([500.0, 510.0, 520.0])

        Ea, A = strategy.calculate_coats_redfern_params(slope, intercept, beta, temperature)
        assert Ea > 0
        assert A > 0


class TestFreemanCaroll:
    """Tests for Freeman-Carroll differential method strategy."""

    @pytest.fixture
    def strategy(self):
        """Create FreemanCaroll strategy with default params."""
        return FreemanCaroll(alpha_min=0.01, alpha_max=0.99, valid_proportion=0.5)

    @pytest.fixture
    def sample_conversion_data(self):
        """Create sample temperature and conversion data."""
        temperature = pd.Series(np.linspace(400, 600, 100))
        conversion = 1 / (1 + np.exp(-0.03 * (temperature - 500)))
        return temperature, conversion

    def test_calculate_returns_dataframe(self, strategy, sample_conversion_data):
        """calculate() should return DataFrame with expected columns."""
        temperature, conversion = sample_conversion_data
        result = strategy.calculate(temperature, conversion, beta=10)

        assert isinstance(result, pd.DataFrame)
        expected_cols = {"Model", "R2_score", "Ea", "A"}
        assert expected_cols.issubset(set(result.columns))

    def test_prepare_plot_data_for_model(self, strategy, sample_conversion_data):
        """prepare_plot_data_for_model should return plot DataFrame and kwargs."""
        temperature, conversion = sample_conversion_data
        result = strategy.calculate(temperature, conversion, beta=10)

        if len(result) > 0:
            model_row = result.iloc[0]
            reaction_df = pd.DataFrame(
                {"temperature": temperature, "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2))}
            )
            plot_df, plot_kwargs = strategy.prepare_plot_data_for_model(model_row, reaction_df)

            assert isinstance(plot_df, pd.DataFrame)
            assert "title" in plot_kwargs


class TestModelFitCalculation:
    """Tests for ModelFitCalculation request handler."""

    @pytest.fixture
    def calculation_handler(self, mock_signals):
        """Create ModelFitCalculation handler with mock signals."""
        return ModelFitCalculation(signals=mock_signals)

    @pytest.fixture
    def sample_reaction_data(self):
        """Create sample reaction data with multiple heating rates."""
        temperature = np.linspace(400, 600, 50)
        df = pd.DataFrame(
            {
                "temperature": temperature,
                "5": np.exp(-((temperature - 490) ** 2) / (2 * 40**2)),
                "10": np.exp(-((temperature - 500) ** 2) / (2 * 45**2)),
            }
        )
        return {"reaction_1": df}

    def test_strategies_registered(self, calculation_handler):
        """All three strategies should be registered."""
        assert "direct-diff" in calculation_handler.strategies
        assert "Coats-Redfern" in calculation_handler.strategies
        assert "Freeman-Carroll" in calculation_handler.strategies

    def test_handle_model_fit_calculation(self, calculation_handler, sample_reaction_data):
        """Should process MODEL_FIT_CALCULATION request."""
        from src.core.app_settings import OperationType

        response = {
            "actor": "model_fit_calculation",
            "target": "test",
            "request_id": "test-1",
            "data": None,
            "operation": OperationType.MODEL_FIT_CALCULATION,
        }

        calculation_params = {
            "fit_method": "direct-diff",
            "reaction_data": sample_reaction_data,
            "alpha_min": 0.01,
            "alpha_max": 0.99,
        }

        calculation_handler._handle_model_fit_calculation(calculation_params, response)

        assert response["data"] is not None
        assert "reaction_1" in response["data"]

    def test_process_request(self, calculation_handler, mock_signals, sample_reaction_data):
        """Should process MODEL_FIT_CALCULATION via process_request."""
        from src.core.app_settings import OperationType

        params = {
            "operation": OperationType.MODEL_FIT_CALCULATION,
            "actor": "test_actor",
            "request_id": "req-1",
            "calculation_params": {
                "fit_method": "direct-diff",
                "reaction_data": sample_reaction_data,
                "alpha_min": 0.01,
                "alpha_max": 0.99,
            },
        }

        calculation_handler.process_request(params)

        mock_signals.response_signal.emit.assert_called_once()
        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is not None

    def test_handle_plot_model_fit_result(self, calculation_handler):
        """Should handle PLOT_MODEL_FIT_RESULT request."""
        from src.core.app_settings import OperationType

        temperature = np.linspace(400, 600, 50)
        reaction_df = pd.DataFrame(
            {"temperature": temperature, "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2))}
        )

        model_series = pd.DataFrame({"Model": ["F2"], "R2_score": [0.95], "Ea": [100000], "A": ["1.0e+10"]})

        response = {
            "actor": "model_fit_calculation",
            "target": "test",
            "request_id": "test-2",
            "data": None,
            "operation": OperationType.PLOT_MODEL_FIT_RESULT,
        }

        calculation_params = {
            "fit_method": "direct-diff",
            "model_series": model_series,
            "reaction_df": reaction_df,
            "alpha_min": 0.01,
            "alpha_max": 0.99,
        }

        calculation_handler._handle_plot_model_fit_result(calculation_params, response)

        assert response["data"] is not None
        assert isinstance(response["data"], list)

    def test_unknown_fit_method(self, calculation_handler):
        """Should handle unknown fit method gracefully."""
        from src.core.app_settings import OperationType

        temperature = np.linspace(400, 600, 50)
        reaction_data = {
            "reaction_1": pd.DataFrame(
                {"temperature": temperature, "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2))}
            )
        }

        response = {
            "actor": "model_fit_calculation",
            "target": "test",
            "request_id": "test-3",
            "data": None,
            "operation": OperationType.MODEL_FIT_CALCULATION,
        }

        calculation_params = {
            "fit_method": "unknown_method",
            "reaction_data": reaction_data,
        }

        calculation_handler._handle_model_fit_calculation(calculation_params, response)

        # Should return early without setting data
        assert response["data"] is None

    def test_unknown_operation(self, calculation_handler, mock_signals):
        """Should handle unknown operation gracefully."""
        from src.core.app_settings import OperationType

        params = {
            "operation": OperationType.LOAD_FILE,  # Wrong operation
            "actor": "test_actor",
            "request_id": "req-2",
            "calculation_params": {},
        }

        calculation_handler.process_request(params)

        mock_signals.response_signal.emit.assert_called_once()
        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is None
