"""Tests for app_settings module — configuration, models, bounds."""

import numpy as np
import pytest

from src.core.app_settings import (
    NUC_MODELS_LIST,
    NUC_MODELS_TABLE,
    OPTIMIZATION_CONFIG,
    PARAMETER_BOUNDS,
    DeconvolutionDifferentialEvolutionConfig,
    DeconvolutionParameterBounds,
    DifferentialEvolutionConfig,
    ModelBasedDifferentialEvolutionConfig,
    ModelBasedParameterBounds,
    ModelFreeParameterBounds,
    OperationType,
    SideBarNames,
    clip_fraction,
    ensure_array,
)


class TestParameterBounds:
    """Tests for parameter bounds dataclasses."""

    def test_model_based_bounds_defaults(self):
        """ModelBasedParameterBounds should have correct default values."""
        bounds = ModelBasedParameterBounds()
        assert bounds.ea_min == 1.0
        assert bounds.ea_max == 250.0
        assert bounds.ea_default == 120.0
        assert bounds.log_a_min == -15.0
        assert bounds.log_a_max == 30.0
        assert bounds.contribution_min == 0.01
        assert bounds.contribution_max == 1.0

    def test_model_free_bounds_defaults(self):
        """ModelFreeParameterBounds should have correct default values."""
        bounds = ModelFreeParameterBounds()
        assert bounds.ea_min == 10000.0
        assert bounds.ea_max == 300000.0
        assert bounds.alpha_min == 0.005
        assert bounds.alpha_max == 0.995

    def test_deconvolution_bounds_defaults(self):
        """DeconvolutionParameterBounds should have correct default values."""
        bounds = DeconvolutionParameterBounds()
        assert bounds.h_min == 0.0
        assert bounds.h_max == 1.0
        assert bounds.z_min == 0.0
        assert bounds.z_max == 1000.0
        assert bounds.w_min == 1.0
        assert bounds.w_max == 200.0

    def test_parameter_bounds_config_has_all_configs(self):
        """ParameterBoundsConfig should contain all bound types."""
        assert hasattr(PARAMETER_BOUNDS, "model_based")
        assert hasattr(PARAMETER_BOUNDS, "model_free")
        assert hasattr(PARAMETER_BOUNDS, "deconvolution")
        assert isinstance(PARAMETER_BOUNDS.model_based, ModelBasedParameterBounds)
        assert isinstance(PARAMETER_BOUNDS.model_free, ModelFreeParameterBounds)
        assert isinstance(PARAMETER_BOUNDS.deconvolution, DeconvolutionParameterBounds)


class TestDifferentialEvolutionConfig:
    """Tests for differential evolution configuration dataclasses."""

    def test_base_config_defaults(self):
        """DifferentialEvolutionConfig should have scipy defaults."""
        config = DifferentialEvolutionConfig()
        assert config.strategy == "best1bin"
        assert config.maxiter == 1000
        assert config.popsize == 15
        assert config.polish is True

    def test_base_config_to_dict(self):
        """to_dict should return all config parameters."""
        config = DifferentialEvolutionConfig()
        result = config.to_dict()
        assert isinstance(result, dict)
        assert "strategy" in result
        assert "maxiter" in result
        assert "popsize" in result
        assert result["strategy"] == "best1bin"

    def test_model_based_config_overrides(self):
        """ModelBasedDifferentialEvolutionConfig should override defaults."""
        config = ModelBasedDifferentialEvolutionConfig()
        assert config.workers == 6
        assert config.popsize == 50
        assert config.polish is False
        assert config.updating == "immediate"
        assert config.mutation == (0.4, 1.2)

    def test_deconvolution_config_defaults(self):
        """DeconvolutionDifferentialEvolutionConfig should have specific defaults."""
        config = DeconvolutionDifferentialEvolutionConfig()
        assert config.workers == 1
        assert config.maxiter == 1000
        assert config.polish is True

    def test_optimization_config_has_all_configs(self):
        """OptimizationConfig should contain all config types."""
        assert hasattr(OPTIMIZATION_CONFIG, "model_based")
        assert hasattr(OPTIMIZATION_CONFIG, "deconvolution")
        assert hasattr(OPTIMIZATION_CONFIG, "model_free")
        assert isinstance(OPTIMIZATION_CONFIG.model_based, ModelBasedDifferentialEvolutionConfig)
        assert isinstance(OPTIMIZATION_CONFIG.deconvolution, DeconvolutionDifferentialEvolutionConfig)


class TestOperationType:
    """Tests for OperationType enum."""

    def test_operation_type_values(self):
        """OperationType should have all expected operation values."""
        assert OperationType.LOAD_FILE.value == "load_file"
        assert OperationType.DECONVOLUTION.value == "deconvolution"
        assert OperationType.STOP_CALCULATION.value == "stop_calculation"
        assert OperationType.MODEL_BASED_CALCULATION.value == "model_based_calculation"
        assert OperationType.ADD_REACTION.value == "add_reaction"
        assert OperationType.REMOVE_REACTION.value == "remove_reaction"

    def test_operation_type_count(self):
        """Should have expected number of operations."""
        # Count all defined operations
        assert len(OperationType) >= 30


class TestSideBarNames:
    """Tests for SideBarNames enum."""

    def test_sidebar_names_values(self):
        """SideBarNames should have expected values."""
        assert SideBarNames.MODEL_BASED.value == "model based"
        assert SideBarNames.MODEL_FREE.value == "model free"
        assert SideBarNames.DECONVOLUTION.value == "deconvolution"
        assert SideBarNames.EXPERIMENTS.value == "experiments"
        assert SideBarNames.SERIES.value == "series"


class TestClipFraction:
    """Tests for clip_fraction numba function."""

    def test_clip_fraction_within_bounds(self):
        """Values within bounds should remain unchanged."""
        result = clip_fraction(np.array([0.5]))
        assert result[0] == pytest.approx(0.5, rel=1e-8)

    def test_clip_fraction_below_bound(self):
        """Values below epsilon should be clipped to epsilon."""
        result = clip_fraction(np.array([0.0]))
        assert result[0] > 0
        assert result[0] < 1e-7

    def test_clip_fraction_above_bound(self):
        """Values above 1-epsilon should be clipped to 1-epsilon."""
        result = clip_fraction(np.array([1.0]))
        assert result[0] < 1.0
        assert result[0] > 1 - 1e-7

    def test_clip_fraction_array(self):
        """Should handle arrays correctly."""
        arr = np.array([0.0, 0.5, 1.0])
        result = clip_fraction(arr)
        assert len(result) == 3
        assert result[0] > 0
        assert result[2] < 1.0


class TestEnsureArray:
    """Tests for ensure_array decorator."""

    def test_ensure_array_converts_list(self):
        """Should convert list to numpy array."""

        @ensure_array
        def dummy_func(e):
            return type(e)

        result = dummy_func([1, 2, 3])
        assert result == np.ndarray

    def test_ensure_array_preserves_ndarray(self):
        """Should keep numpy array as is."""

        @ensure_array
        def dummy_func(e):
            return type(e)

        result = dummy_func(np.array([1, 2, 3]))
        assert result == np.ndarray


class TestNucModelsTable:
    """Tests for kinetic models table."""

    def test_nuc_models_table_structure(self):
        """Each model should have differential and integral forms."""
        for model_name, model_funcs in NUC_MODELS_TABLE.items():
            assert "differential_form" in model_funcs, f"{model_name} missing differential_form"
            assert "integral_form" in model_funcs, f"{model_name} missing integral_form"
            assert callable(model_funcs["differential_form"])
            assert callable(model_funcs["integral_form"])

    def test_nuc_models_list_sorted(self):
        """NUC_MODELS_LIST should be sorted alphabetically."""
        assert NUC_MODELS_LIST == sorted(NUC_MODELS_LIST)

    def test_nuc_models_list_matches_table(self):
        """NUC_MODELS_LIST should contain all models from table."""
        assert set(NUC_MODELS_LIST) == set(NUC_MODELS_TABLE.keys())

    def test_f2_differential(self):
        """F2 differential form should return e^2."""
        from src.core.app_settings import differential_F2

        result = differential_F2(np.array([0.5]))
        assert result[0] == pytest.approx(0.25, rel=1e-8)

    def test_f2_integral(self):
        """F2 integral form should return 1/e - 1."""
        from src.core.app_settings import integral_F2

        result = integral_F2(np.array([0.5]))
        expected = 1 / 0.5 - 1  # = 1
        assert result[0] == pytest.approx(expected, rel=1e-8)

    def test_a2_differential(self):
        """A2 differential form should compute correctly."""
        from src.core.app_settings import differential_A2

        e = 0.5
        result = differential_A2(np.array([e]))
        # A2: 2 * e * (-ln(e))^0.5
        expected = 2 * e * ((-np.log(e)) ** 0.5)
        assert result[0] == pytest.approx(expected, rel=1e-8)

    def test_r3_differential(self):
        """R3 differential form should compute correctly."""
        from src.core.app_settings import differential_R3

        result = differential_R3(np.array([0.5]))
        # R3: 3 * e^(2/3)
        expected = 3 * (0.5 ** (2 / 3))
        assert result[0] == pytest.approx(expected, rel=1e-8)

    def test_model_handles_edge_cases(self):
        """Models should handle edge values (near 0 and 1)."""
        for model_name, model_funcs in NUC_MODELS_TABLE.items():
            # Test near 0
            result = model_funcs["differential_form"](np.array([0.01]))
            assert not np.isnan(result).any(), f"{model_name} produced NaN for e=0.01"
            assert np.isfinite(result).all(), f"{model_name} produced inf for e=0.01"

            # Test near 1
            result = model_funcs["differential_form"](np.array([0.99]))
            assert not np.isnan(result).any(), f"{model_name} produced NaN for e=0.99"
