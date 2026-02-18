"""Tests for model_free_calculation module - isoconversional kinetic methods."""

import numpy as np
import pandas as pd
import pytest

from src.core.model_free_calculation import (
    Friedman,
    Kissinger,
    LinearApproximation,
    MasterPlots,
    ModelFreeCalculation,
    Vyazovkin,
)


class TestLinearApproximation:
    """Tests for Linear Approximation (OFW, KAS, Starink) method."""

    @pytest.fixture
    def strategy(self):
        """Create LinearApproximation strategy."""
        return LinearApproximation(alpha_min=0.1, alpha_max=0.9)

    @pytest.fixture
    def sample_reaction_df(self):
        """Create sample reaction DataFrame with multiple heating rates."""
        temperature = np.linspace(400, 600, 100)
        return pd.DataFrame(
            {
                "temperature": temperature,
                "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
                "20": np.exp(-((temperature - 520) ** 2) / (2 * 45**2)),
            }
        )

    def test_calculate_returns_dataframe(self, strategy, sample_reaction_df):
        """calculate() should return DataFrame with OFW, KAS, Starink columns."""
        result = strategy.calculate(sample_reaction_df)

        assert isinstance(result, pd.DataFrame)
        assert "conversion" in result.columns
        assert "OFW" in result.columns
        assert "KAS" in result.columns
        assert "Starink" in result.columns

    def test_ea_values_positive(self, strategy, sample_reaction_df):
        """Activation energies should be positive."""
        result = strategy.calculate(sample_reaction_df)

        assert np.all(result["OFW"] > 0)
        assert np.all(result["KAS"] > 0)
        assert np.all(result["Starink"] > 0)

    def test_prepare_plot_data(self, strategy, sample_reaction_df):
        """prepare_plot_data should return DataFrame and kwargs."""
        df = strategy.calculate(sample_reaction_df)
        plot_df, plot_kwargs = strategy.prepare_plot_data(df)

        assert isinstance(plot_df, pd.DataFrame)
        assert "title" in plot_kwargs
        assert "xlabel" in plot_kwargs
        assert "ylabel" in plot_kwargs


class TestFriedman:
    """Tests for Friedman differential isoconversional method."""

    @pytest.fixture
    def strategy(self):
        """Create Friedman strategy."""
        return Friedman(alpha_min=0.1, alpha_max=0.9)

    @pytest.fixture
    def sample_reaction_df(self):
        """Create sample reaction DataFrame."""
        temperature = np.linspace(400, 600, 100)
        return pd.DataFrame(
            {
                "temperature": temperature,
                "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
            }
        )

    def test_calculate_returns_dataframe(self, strategy, sample_reaction_df):
        """calculate() should return DataFrame with Friedman column."""
        result = strategy.calculate(sample_reaction_df)

        assert isinstance(result, pd.DataFrame)
        assert "conversion" in result.columns
        assert "Friedman" in result.columns

    def test_ea_values_positive(self, strategy, sample_reaction_df):
        """Friedman activation energies should be positive."""
        result = strategy.calculate(sample_reaction_df)
        assert np.all(result["Friedman"] > 0)

    def test_prepare_plot_data(self, strategy, sample_reaction_df):
        """prepare_plot_data should return DataFrame and kwargs."""
        df = strategy.calculate(sample_reaction_df)
        plot_df, plot_kwargs = strategy.prepare_plot_data(df)

        assert isinstance(plot_df, pd.DataFrame)
        assert "title" in plot_kwargs
        assert "Friedman" in plot_kwargs["title"]


class TestKissinger:
    """Tests for Kissinger peak method."""

    @pytest.fixture
    def strategy(self):
        """Create Kissinger strategy."""
        return Kissinger(alpha_min=0.1, alpha_max=0.9)

    @pytest.fixture
    def sample_reaction_df(self):
        """Create sample reaction DataFrame with clear peaks."""
        temperature = np.linspace(400, 600, 100)
        return pd.DataFrame(
            {
                "temperature": temperature,
                "5": np.exp(-((temperature - 480) ** 2) / (2 * 30**2)),
                "10": np.exp(-((temperature - 500) ** 2) / (2 * 35**2)),
                "20": np.exp(-((temperature - 520) ** 2) / (2 * 40**2)),
            }
        )

    def test_calculate_returns_dataframe(self, strategy, sample_reaction_df):
        """calculate() should return DataFrame with Kissinger_Ea column."""
        result = strategy.calculate(sample_reaction_df)

        assert isinstance(result, pd.DataFrame)
        assert "conversion" in result.columns
        assert "Kissinger_Ea" in result.columns

    def test_single_ea_value(self, strategy, sample_reaction_df):
        """Kissinger returns single Ea value for all conversion points."""
        result = strategy.calculate(sample_reaction_df)

        if len(result) > 1:
            # All Ea values should be identical (method characteristic)
            assert result["Kissinger_Ea"].nunique() == 1

    def test_prepare_plot_data(self, strategy, sample_reaction_df):
        """prepare_plot_data should return DataFrame and kwargs."""
        df = strategy.calculate(sample_reaction_df)
        plot_df, plot_kwargs = strategy.prepare_plot_data(df)

        assert isinstance(plot_df, pd.DataFrame)
        assert "title" in plot_kwargs
        assert "Kissinger" in plot_kwargs["title"]


class TestVyazovkin:
    """Tests for Vyazovkin nonlinear isoconversional method."""

    @pytest.fixture
    def strategy(self):
        """Create Vyazovkin strategy with narrow Ea range for fast tests."""
        return Vyazovkin(alpha_min=0.2, alpha_max=0.8, ea_min=50000, ea_max=150000)

    @pytest.fixture
    def sample_reaction_df(self):
        """Create sample reaction DataFrame."""
        temperature = np.linspace(400, 600, 50)
        return pd.DataFrame(
            {
                "temperature": temperature,
                "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
            }
        )

    def test_calculate_returns_dataframe(self, strategy, sample_reaction_df):
        """calculate() should return DataFrame with Vyazovkin column."""
        result = strategy.calculate(sample_reaction_df)

        assert isinstance(result, pd.DataFrame)
        assert "conversion" in result.columns
        assert "Vyazovkin" in result.columns

    def test_ea_within_bounds(self, strategy, sample_reaction_df):
        """Ea values should be within specified bounds."""
        result = strategy.calculate(sample_reaction_df)

        assert np.all(result["Vyazovkin"] >= strategy.ea_min)
        assert np.all(result["Vyazovkin"] <= strategy.ea_max)

    def test_prepare_plot_data(self, strategy, sample_reaction_df):
        """prepare_plot_data should return DataFrame and kwargs."""
        df = strategy.calculate(sample_reaction_df)
        plot_df, plot_kwargs = strategy.prepare_plot_data(df)

        assert isinstance(plot_df, pd.DataFrame)
        assert "title" in plot_kwargs
        assert "Vyazovkin" in plot_kwargs["title"]


class TestMasterPlots:
    """Tests for Master Plots method."""

    @pytest.fixture
    def strategy(self):
        """Create MasterPlots strategy."""
        return MasterPlots(alpha_min=0.1, alpha_max=0.9, ea_mean=100000)

    @pytest.fixture
    def sample_reaction_df(self):
        """Create sample reaction DataFrame."""
        temperature = np.linspace(400, 600, 50)
        return pd.DataFrame(
            {
                "temperature": temperature,
                "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
            }
        )

    def test_normalize_data(self, strategy):
        """normalize_data should scale array to [0, 1]."""
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = strategy.normalize_data(arr)

        assert result.min() == pytest.approx(0.0)
        assert result.max() == pytest.approx(1.0)

    def test_r2_score(self, strategy):
        """r2_score should return 1.0 for identical arrays."""
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        assert strategy.r2_score(arr, arr) == pytest.approx(1.0)

    def test_calculate_returns_dict(self, strategy, sample_reaction_df):
        """calculate() should return dict with y(α), g(α), z(α) keys."""
        result = strategy.calculate(sample_reaction_df)

        assert isinstance(result, dict)
        assert "y(α)" in result
        assert "g(α)" in result
        assert "z(α)" in result

    def test_get_exp_term(self, strategy):
        """get_exp_term should return exponential term."""
        temperature = np.array([500.0, 600.0])
        result = strategy.get_exp_term(temperature)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(temperature)

    def test_calculate_y_master_plot(self, strategy):
        """calculate_y_master_plot should return normalized array."""
        da_dt = np.array([0.1, 0.5, 1.0, 0.5, 0.1])
        exp_term = np.ones(5)
        result = strategy.calculate_y_master_plot(da_dt, exp_term)

        assert isinstance(result, np.ndarray)
        assert result.min() == pytest.approx(0.0)
        assert result.max() == pytest.approx(1.0)

    def test_calculate_z_master_plot(self, strategy):
        """calculate_z_master_plot should return normalized array."""
        da_dt = np.array([0.1, 0.5, 1.0, 0.5, 0.1])
        temperature = np.array([500.0, 520.0, 540.0, 560.0, 580.0])
        result = strategy.calculate_z_master_plot(da_dt, temperature)

        assert isinstance(result, np.ndarray)
        assert result.min() == pytest.approx(0.0)
        assert result.max() == pytest.approx(1.0)

    def test_prepare_plot_data(self, strategy, sample_reaction_df):
        """prepare_plot_data should return DataFrame and kwargs."""
        result = strategy.calculate(sample_reaction_df)
        # Get first DataFrame from y(α) results
        first_beta = list(result["y(α)"].keys())[0]
        df = result["y(α)"][first_beta]
        plot_df, plot_kwargs = strategy.prepare_plot_data(df)

        assert isinstance(plot_df, pd.DataFrame)
        assert "title" in plot_kwargs


class TestModelFreeCalculation:
    """Tests for ModelFreeCalculation request handler."""

    @pytest.fixture
    def calculation_handler(self, mock_signals):
        """Create ModelFreeCalculation handler with mock signals."""
        return ModelFreeCalculation(signals=mock_signals)

    def test_strategies_registered(self, calculation_handler):
        """All five strategies should be registered."""
        assert "linear approximation" in calculation_handler.strategies
        assert "Friedman" in calculation_handler.strategies
        assert "Kissinger" in calculation_handler.strategies
        assert "Vyazovkin" in calculation_handler.strategies
        assert "master plots" in calculation_handler.strategies

    def test_handle_model_free_calculation(self, calculation_handler):
        """Should process MODEL_FREE_CALCULATION request."""
        from src.core.app_settings import OperationType

        temperature = np.linspace(400, 600, 50)
        reaction_data = {
            "reaction_1": pd.DataFrame(
                {
                    "temperature": temperature,
                    "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                    "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
                }
            )
        }

        response = {
            "actor": "model_free_calculation",
            "target": "test",
            "request_id": "test-1",
            "data": None,
            "operation": OperationType.MODEL_FREE_CALCULATION,
        }

        calculation_params = {
            "fit_method": "Friedman",
            "reaction_data": reaction_data,
            "alpha_min": 0.1,
            "alpha_max": 0.9,
        }

        calculation_handler._handle_model_free_calculation(calculation_params, response)

        assert response["data"] is not None
        assert "reaction_1" in response["data"]

    def test_process_request(self, calculation_handler, mock_signals):
        """Should handle MODEL_FREE_CALCULATION via process_request."""
        from src.core.app_settings import OperationType

        temperature = np.linspace(400, 600, 50)
        reaction_data = {
            "reaction_1": pd.DataFrame(
                {
                    "temperature": temperature,
                    "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                    "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
                }
            )
        }

        params = {
            "operation": OperationType.MODEL_FREE_CALCULATION,
            "actor": "test_actor",
            "request_id": "req-1",
            "calculation_params": {
                "fit_method": "linear approximation",
                "reaction_data": reaction_data,
                "alpha_min": 0.1,
                "alpha_max": 0.9,
            },
        }

        calculation_handler.process_request(params)

        mock_signals.response_signal.emit.assert_called_once()
        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is not None

    def test_handle_plot_model_fit_result(self, calculation_handler, mock_signals):
        """Should handle PLOT_MODEL_FREE_RESULT request."""
        from src.core.app_settings import OperationType

        result_df = pd.DataFrame(
            {
                "conversion": np.linspace(0.1, 0.9, 50),
                "Friedman": np.ones(50) * 100000,
            }
        )

        response = {
            "actor": "model_free_calculation",
            "target": "test",
            "request_id": "test-2",
            "data": None,
            "operation": OperationType.PLOT_MODEL_FREE_RESULT,
        }

        calculation_params = {
            "fit_method": "Friedman",
            "result_df": result_df,
            "alpha_min": 0.1,
            "alpha_max": 0.9,
        }

        calculation_handler._handle_plot_model_fit_result(calculation_params, response)

        assert response["data"] is not None
        assert isinstance(response["data"], list)

    def test_handle_insufficient_beta_columns(self, calculation_handler, mock_signals):
        """Should return False when insufficient beta columns."""
        from src.core.app_settings import OperationType

        temperature = np.linspace(400, 600, 50)
        reaction_data = {
            "reaction_1": pd.DataFrame(
                {
                    "temperature": temperature,
                    "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                    # Only one beta column - insufficient for model-free
                }
            )
        }

        response = {
            "actor": "model_free_calculation",
            "target": "test",
            "request_id": "test-3",
            "data": None,
            "operation": OperationType.MODEL_FREE_CALCULATION,
        }

        calculation_params = {
            "fit_method": "Friedman",
            "reaction_data": reaction_data,
            "alpha_min": 0.1,
            "alpha_max": 0.9,
        }

        calculation_handler._handle_model_free_calculation(calculation_params, response)

        assert response["data"] is False

    def test_unknown_fit_method(self, calculation_handler, mock_signals):
        """Should handle unknown fit method gracefully."""
        from src.core.app_settings import OperationType

        temperature = np.linspace(400, 600, 50)
        reaction_data = {
            "reaction_1": pd.DataFrame(
                {
                    "temperature": temperature,
                    "5": np.exp(-((temperature - 480) ** 2) / (2 * 35**2)),
                    "10": np.exp(-((temperature - 500) ** 2) / (2 * 40**2)),
                }
            )
        }

        response = {
            "actor": "model_free_calculation",
            "target": "test",
            "request_id": "test-4",
            "data": None,
            "operation": OperationType.MODEL_FREE_CALCULATION,
        }

        calculation_params = {
            "fit_method": "unknown_method",
            "reaction_data": reaction_data,
        }

        calculation_handler._handle_model_free_calculation(calculation_params, response)

        # Should return early without setting data
        assert response["data"] is None
