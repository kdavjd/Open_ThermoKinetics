"""Tests for calculation_scenarios module — optimization scenarios."""

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.core.calculation_scenarios import (
    SCENARIO_REGISTRY,
    BaseCalculationScenario,
    DeconvolutionScenario,
    ModelBasedScenario,
    constraint_fun,
    extract_chains,
    get_core_params_format_info,
    make_de_callback,
)


class TestBaseCalculationScenario:
    """Tests for BaseCalculationScenario base class."""

    def test_base_scenario_initialization(self, mock_signals):
        """BaseCalculationScenario should initialize with params and calculations."""
        mock_calcs = MagicMock()
        scenario = BaseCalculationScenario({"test": "params"}, mock_calcs)

        assert scenario.params == {"test": "params"}
        assert scenario.calculations == mock_calcs

    def test_get_bounds_raises_not_implemented(self, mock_signals):
        """get_bounds should raise NotImplementedError in base class."""
        mock_calcs = MagicMock()
        scenario = BaseCalculationScenario({}, mock_calcs)

        with pytest.raises(NotImplementedError):
            scenario.get_bounds()

    def test_get_target_function_raises_not_implemented(self, mock_signals):
        """get_target_function should raise NotImplementedError in base class."""
        mock_calcs = MagicMock()
        scenario = BaseCalculationScenario({}, mock_calcs)

        with pytest.raises(NotImplementedError):
            scenario.get_target_function()

    def test_get_optimization_method_default(self, mock_signals):
        """get_optimization_method should return 'differential_evolution' by default."""
        mock_calcs = MagicMock()
        scenario = BaseCalculationScenario({}, mock_calcs)

        assert scenario.get_optimization_method() == "differential_evolution"

    def test_get_result_strategy_type_raises_not_implemented(self, mock_signals):
        """get_result_strategy_type should raise NotImplementedError in base class."""
        mock_calcs = MagicMock()
        scenario = BaseCalculationScenario({}, mock_calcs)

        with pytest.raises(NotImplementedError):
            scenario.get_result_strategy_type()

    def test_get_constraints_default_empty(self, mock_signals):
        """get_constraints should return empty list by default."""
        mock_calcs = MagicMock()
        scenario = BaseCalculationScenario({}, mock_calcs)

        assert scenario.get_constraints() == []


class TestDeconvolutionScenario:
    """Tests for DeconvolutionScenario."""

    def test_get_bounds(self, mock_signals):
        """get_bounds should return params bounds."""
        mock_calcs = MagicMock()
        params = {"bounds": [(0, 1), (100, 200)]}
        scenario = DeconvolutionScenario(params, mock_calcs)

        bounds = scenario.get_bounds()

        assert bounds == [(0, 1), (100, 200)]

    def test_get_result_strategy_type(self, mock_signals):
        """get_result_strategy_type should return 'deconvolution'."""
        mock_calcs = MagicMock()
        scenario = DeconvolutionScenario({}, mock_calcs)

        assert scenario.get_result_strategy_type() == "deconvolution"

    def test_get_optimization_method_default(self, mock_signals):
        """get_optimization_method should return default method."""
        mock_calcs = MagicMock()
        scenario = DeconvolutionScenario({}, mock_calcs)

        assert scenario.get_optimization_method() == "differential_evolution"

    def test_get_optimization_method_custom(self, mock_signals):
        """get_optimization_method should return custom method from settings."""
        mock_calcs = MagicMock()
        params = {"deconvolution_settings": {"method": "optuna"}}
        scenario = DeconvolutionScenario(params, mock_calcs)

        assert scenario.get_optimization_method() == "optuna"

    def test_get_target_function(self, mock_signals):
        """get_target_function should return callable."""
        mock_calcs = MagicMock()
        mock_calcs.calculation_active = True

        temperature = np.linspace(300, 600, 100)
        intensity = np.exp(-((temperature - 450) ** 2) / (2 * 30**2))
        df = pd.DataFrame({"temperature": temperature, "intensity": intensity})

        params = {
            "reaction_variables": {"r1": [0.8, 450, 30]},
            "reaction_combinations": [["gauss"]],
            "experimental_data": df,
        }
        scenario = DeconvolutionScenario(params, mock_calcs)

        target_func = scenario.get_target_function(calculations_instance=mock_calcs)

        assert callable(target_func)


class TestModelBasedScenario:
    """Tests for ModelBasedScenario."""

    @pytest.fixture
    def model_based_params(self):
        """Sample params for ModelBasedScenario."""
        temperature = np.linspace(300, 600, 50)
        return {
            "reaction_scheme": {
                "components": [{"id": "A"}, {"id": "B"}],
                "reactions": [
                    {"from": "A", "to": "B", "allowed_models": ["F1", "F2"]},
                ],
            },
            "experimental_data": pd.DataFrame(
                {
                    "temperature": temperature,
                    "5.0": np.exp(-((temperature - 450) ** 2) / (2 * 30**2)),
                }
            ),
            "calculation_settings": {"method": "differential_evolution"},
        }

    def test_get_result_strategy_type(self, mock_signals):
        """get_result_strategy_type should return 'model_based_calculation'."""
        mock_calcs = MagicMock()
        scenario = ModelBasedScenario({}, mock_calcs)

        assert scenario.get_result_strategy_type() == "model_based_calculation"

    def test_get_bounds(self, mock_signals, model_based_params):
        """get_bounds should return correct bounds structure."""
        mock_calcs = MagicMock()
        scenario = ModelBasedScenario(model_based_params, mock_calcs)

        bounds = scenario.get_bounds()

        # 1 reaction: logA (1), Ea (1), model_index (1), contribution (1) = 4 bounds
        assert len(bounds) == 4
        # logA bounds
        assert bounds[0][0] == -50.0
        assert bounds[0][1] == 50.0
        # Ea bounds
        assert bounds[1][0] == 1.0
        assert bounds[1][1] == 250.0
        # model index bounds
        assert bounds[2][0] == 0
        assert bounds[2][1] == 1  # 2 allowed_models - 1

    def test_get_bounds_missing_scheme_raises(self, mock_signals):
        """get_bounds should raise if no reaction_scheme."""
        mock_calcs = MagicMock()
        scenario = ModelBasedScenario({}, mock_calcs)

        with pytest.raises(ValueError, match="No 'reaction_scheme'"):
            scenario.get_bounds()

    def test_get_bounds_missing_reactions_raises(self, mock_signals):
        """get_bounds should raise if no reactions in scheme."""
        mock_calcs = MagicMock()
        params = {"reaction_scheme": {"components": []}}
        scenario = ModelBasedScenario(params, mock_calcs)

        with pytest.raises(ValueError, match="No 'reactions'"):
            scenario.get_bounds()

    def test_get_constraints(self, mock_signals, model_based_params):
        """get_constraints should return NonlinearConstraint list."""
        mock_calcs = MagicMock()
        scenario = ModelBasedScenario(model_based_params, mock_calcs)

        constraints = scenario.get_constraints()

        assert isinstance(constraints, list)

    def test_get_constraints_single_chain(self, mock_signals):
        """get_constraints should handle single chain scheme."""
        mock_calcs = MagicMock()
        params = {
            "reaction_scheme": {
                "components": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
                "reactions": [
                    {"from": "A", "to": "B", "allowed_models": ["F1"]},
                    {"from": "B", "to": "C", "allowed_models": ["F2"]},
                ],
            },
        }
        scenario = ModelBasedScenario(params, mock_calcs)

        constraints = scenario.get_constraints()

        assert len(constraints) == 1


class TestExtractChains:
    """Tests for extract_chains function."""

    def test_extract_chains_linear(self):
        """extract_chains should extract linear chain A→B→C."""
        scheme = {
            "components": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            "reactions": [
                {"from": "A", "to": "B"},
                {"from": "B", "to": "C"},
            ],
        }

        chains = extract_chains(scheme)

        assert len(chains) == 1
        assert chains[0] == [0, 1]  # indices of reactions

    def test_extract_chains_parallel(self):
        """extract_chains should extract parallel chains."""
        scheme = {
            "components": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            "reactions": [
                {"from": "A", "to": "B"},
                {"from": "A", "to": "C"},
            ],
        }

        chains = extract_chains(scheme)

        assert len(chains) == 2

    def test_extract_chains_single_reaction(self):
        """extract_chains should handle single reaction."""
        scheme = {
            "components": [{"id": "A"}, {"id": "B"}],
            "reactions": [{"from": "A", "to": "B"}],
        }

        chains = extract_chains(scheme)

        assert len(chains) == 1
        assert chains[0] == [0]


class TestConstraintFun:
    """Tests for constraint_fun function."""

    def test_constraint_fun_single_chain(self):
        """constraint_fun should compute sum constraint for chain."""
        # For 2 reactions, X layout: [logA*2, Ea*2, model_idx*2, contribution*2]
        # So contributions are at indices 6, 7 (3*2=6 to 4*2=8)
        X = np.array([1.0, 2.0, 100.0, 150.0, 0.0, 1.0, 0.5, 0.5])
        chains = [[0, 1]]  # chain uses both reactions
        num_reactions = 2

        result = constraint_fun(X, chains, num_reactions)

        # Sum of contributions [0.5, 0.5] should equal 1.0
        assert len(result) == 1
        assert result[0] == pytest.approx(0.0, rel=1e-8)

    def test_constraint_fun_invalid_sum(self):
        """constraint_fun should return non-zero for invalid sum."""
        X = np.array([1.0, 2.0, 100.0, 150.0, 0.0, 1.0, 0.3, 0.3])  # sum = 0.6 != 1.0
        chains = [[0, 1]]
        num_reactions = 2

        result = constraint_fun(X, chains, num_reactions)

        assert result[0] != pytest.approx(0.0)


class TestMakeDeCallback:
    """Tests for make_de_callback function."""

    def test_callback_returns_false_normally(self, mock_signals):
        """Callback should return False when stop_event not set."""
        mock_calcs = MagicMock()
        mock_calcs.stop_event.is_set.return_value = False
        mock_calcs.new_best_result = MagicMock()

        target_obj = MagicMock()
        target_obj.best_mse.value = 0.01
        target_obj.best_params = [1.0, 2.0]

        callback = make_de_callback(target_obj, mock_calcs)
        result = callback([1.0, 2.0], 0.5)

        assert result is False

    def test_callback_returns_true_when_stopped(self, mock_signals):
        """Callback should return True when stop_event is set."""
        mock_calcs = MagicMock()
        mock_calcs.stop_event.is_set.return_value = True
        mock_calcs.new_best_result = MagicMock()

        target_obj = MagicMock()
        target_obj.best_mse.value = 0.01
        target_obj.best_params = [1.0, 2.0]

        callback = make_de_callback(target_obj, mock_calcs)
        result = callback([1.0, 2.0], 0.5)

        assert result is True


class TestScenarioRegistry:
    """Tests for SCENARIO_REGISTRY."""

    def test_registry_has_deconvolution(self):
        """SCENARIO_REGISTRY should contain deconvolution."""
        assert "deconvolution" in SCENARIO_REGISTRY
        assert SCENARIO_REGISTRY["deconvolution"] == DeconvolutionScenario

    def test_registry_has_model_based(self):
        """SCENARIO_REGISTRY should contain model_based_calculation."""
        assert "model_based_calculation" in SCENARIO_REGISTRY
        assert SCENARIO_REGISTRY["model_based_calculation"] == ModelBasedScenario


class TestGetCoreParamsFormatInfo:
    """Tests for get_core_params_format_info function."""

    def test_returns_correct_structure(self):
        """Should return dict with params_order and expected_length."""
        info = get_core_params_format_info()

        assert isinstance(info, dict)
        assert "params_order" in info
        assert "expected_length_per_reaction" in info
        assert info["params_order"] == ["logA", "Ea", "model_indices", "contributions"]
        assert info["expected_length_per_reaction"] == 4
