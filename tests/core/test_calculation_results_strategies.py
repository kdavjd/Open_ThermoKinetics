"""Tests for calculation_results_strategies module."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.calculation_results_strategies import (
    BestResultStrategy,
    DeconvolutionStrategy,
    ModelBasedCalculationStrategy,
)


class TestBestResultStrategy:
    """Tests for abstract BestResultStrategy."""

    def test_is_abstract(self):
        """BestResultStrategy should be abstract."""
        with pytest.raises(TypeError):
            BestResultStrategy()

    def test_subclass_must_implement_handle(self):
        """Subclasses must implement handle method."""

        class IncompleteStrategy(BestResultStrategy):
            pass

        with pytest.raises(TypeError):
            IncompleteStrategy()


class TestDeconvolutionStrategy:
    """Tests for DeconvolutionStrategy."""

    def test_init(self):
        """DeconvolutionStrategy should store calculation instance."""
        mock_calc = MagicMock()
        strategy = DeconvolutionStrategy(mock_calc)
        assert strategy.calculation is mock_calc

    def test_handle_better_mse(self):
        """handle should update when better MSE found."""
        mock_calc = MagicMock()
        mock_calc.best_mse = 0.1
        mock_calc.mse_history = []
        mock_calc.handle_request_cycle.return_value = "test_file"

        strategy = DeconvolutionStrategy(mock_calc)

        result = {
            "best_mse": 0.05,
            "best_combination": ("gauss",),
            "params": [1.0, 450.0, 30.0],
            "reaction_variables": {"reaction_1": ["h", "z", "w"]},
        }

        with patch("src.core.calculation_results_strategies.console"):
            strategy.handle(result)

        assert mock_calc.best_mse == 0.05
        assert mock_calc.best_combination == ("gauss",)

    def test_handle_worse_mse(self):
        """handle should not update when worse MSE found."""
        mock_calc = MagicMock()
        mock_calc.best_mse = 0.01

        strategy = DeconvolutionStrategy(mock_calc)

        result = {
            "best_mse": 0.1,  # Worse than current
            "best_combination": ("gauss",),
            "params": [1.0, 450.0, 30.0],
            "reaction_variables": {"reaction_1": ["h", "z", "w"]},
        }

        strategy.handle(result)

        # best_mse should remain unchanged
        assert mock_calc.best_mse == 0.01

    def test_handle_gauss_function(self):
        """handle should correctly parse gauss function params."""
        mock_calc = MagicMock()
        mock_calc.best_mse = float("inf")
        mock_calc.mse_history = []
        mock_calc.handle_request_cycle.return_value = "test_file"

        strategy = DeconvolutionStrategy(mock_calc)

        result = {
            "best_mse": 0.01,
            "best_combination": ("gauss",),
            "params": [1.0, 450.0, 30.0],
            "reaction_variables": {"reaction_1": ["h", "z", "w"]},
        }

        with patch("src.core.calculation_results_strategies.console"):
            strategy.handle(result)

        mock_calc.handle_request_cycle.assert_called()

    def test_handle_fraser_function(self):
        """handle should correctly parse fraser function params."""
        mock_calc = MagicMock()
        mock_calc.best_mse = float("inf")
        mock_calc.mse_history = []
        mock_calc.handle_request_cycle.return_value = "test_file"

        strategy = DeconvolutionStrategy(mock_calc)

        result = {
            "best_mse": 0.01,
            "best_combination": ("fraser",),
            "params": [1.0, 450.0, 30.0, 0.3],
            "reaction_variables": {"reaction_1": ["h", "z", "w", "fr"]},
        }

        with patch("src.core.calculation_results_strategies.console"):
            strategy.handle(result)

        mock_calc.handle_request_cycle.assert_called()

    def test_handle_ads_function(self):
        """handle should correctly parse ads function params."""
        mock_calc = MagicMock()
        mock_calc.best_mse = float("inf")
        mock_calc.mse_history = []
        mock_calc.handle_request_cycle.return_value = "test_file"

        strategy = DeconvolutionStrategy(mock_calc)

        result = {
            "best_mse": 0.01,
            "best_combination": ("ads",),
            "params": [1.0, 450.0, 30.0, 10.0, 15.0],
            "reaction_variables": {"reaction_1": ["h", "z", "w", "ads1", "ads2"]},
        }

        with patch("src.core.calculation_results_strategies.console"):
            strategy.handle(result)

        mock_calc.handle_request_cycle.assert_called()


class TestModelBasedCalculationStrategy:
    """Tests for ModelBasedCalculationStrategy."""

    def test_init(self):
        """ModelBasedCalculationStrategy should store calculation instance."""
        mock_calc = MagicMock()
        strategy = ModelBasedCalculationStrategy(mock_calc)
        assert strategy.calculation is mock_calc

    def test_handle_missing_mse(self):
        """handle should handle missing MSE."""
        mock_calc = MagicMock()
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"params": [1.0, 2.0]}  # No mse/best_mse

        strategy.handle(result)
        # Should return early without error

    def test_handle_missing_params(self):
        """handle should handle missing params."""
        mock_calc = MagicMock()
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1}  # No params

        strategy.handle(result)
        # Should return early without error

    def test_handle_missing_calc_params(self):
        """handle should handle missing calc_params."""
        mock_calc = MagicMock()
        mock_calc.calc_params = None
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1, "params": [1.0]}

        strategy.handle(result)
        # Should return early without error

    def test_handle_missing_reaction_scheme(self):
        """handle should handle missing reaction_scheme."""
        mock_calc = MagicMock()
        mock_calc.calc_params = {}  # No reaction_scheme
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1, "params": [1.0]}

        strategy.handle(result)
        # Should return early without error

    def test_handle_missing_reactions(self):
        """handle should handle missing reactions."""
        mock_calc = MagicMock()
        mock_calc.calc_params = {"reaction_scheme": {}}
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1, "params": [1.0]}

        strategy.handle(result)
        # Should return early without error

    def test_handle_empty_reactions(self):
        """handle should handle empty reactions list."""
        mock_calc = MagicMock()
        mock_calc.calc_params = {"reaction_scheme": {"reactions": []}}
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1, "params": [1.0]}

        strategy.handle(result)
        # Should return early without error

    def test_handle_insufficient_params_length(self):
        """handle should handle insufficient params length."""
        mock_calc = MagicMock()
        mock_calc.calc_params = {"reaction_scheme": {"reactions": [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}]}}
        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1, "params": [1.0]}  # Too few params

        strategy.handle(result)
        # Should return early without error

    def test_handle_dict_params(self):
        """handle should convert dict params to list."""
        mock_calc = MagicMock()
        mock_calc.calc_params = {
            "reaction_scheme": {"reactions": [{"from": "A", "to": "B", "allowed_models": ["F1", "R2"]}]}
        }
        mock_calc.best_mse = float("inf")
        mock_calc.mse_history = []

        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {"mse": 0.1, "parameters": {"A -> B": {"log_A": 10, "Ea": 100, "contribution": 0.5}}}

        with patch("src.core.calculation_results_strategies.console"):
            strategy.handle(result)

    def test_convert_dict_params_to_list(self):
        """_convert_dict_params_to_list should work correctly."""
        mock_calc = MagicMock()
        strategy = ModelBasedCalculationStrategy(mock_calc)

        reactions = [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}]
        params_dict = {
            "A -> B": {"log_A": 10, "Ea": 100, "contribution": 0.5},
            "B -> C": {"log_A": 12, "Ea": 150, "contribution": 0.5},
        }

        result = strategy._convert_dict_params_to_list(params_dict, reactions)

        assert result is not None
        assert len(result) == 8  # 2 reactions * 4 params each

    def test_handle_better_mse(self):
        """handle should update when better MSE found."""
        mock_calc = MagicMock()
        mock_calc.calc_params = {
            "reaction_scheme": {"reactions": [{"from": "A", "to": "B", "allowed_models": ["F1", "R2"]}]}
        }
        mock_calc.best_mse = float("inf")
        mock_calc.mse_history = []

        strategy = ModelBasedCalculationStrategy(mock_calc)

        result = {
            "mse": 0.05,
            "params": [10.0, 100.0, 0, 0.5],  # logA, Ea, model_index, contribution
        }

        with patch("src.core.calculation_results_strategies.console"):
            strategy.handle(result)

        assert mock_calc.best_mse == 0.05
