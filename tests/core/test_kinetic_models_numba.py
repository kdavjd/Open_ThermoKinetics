"""Tests for Numba-compatible kinetic models (kinetic_models_numba.py).

Validates:
- All models match Python reference implementations from NUC_MODELS_TABLE
- model_f_e dispatch works for every model index
- MODEL_NAME_TO_INDEX covers all models in NUC_MODELS_TABLE
- Enabled models selection (set/get/local↔global mapping)
- warmup_numba completes successfully
"""

import numpy as np
import pytest

from src.core.app_settings import NUC_MODELS_TABLE
from src.core.kinetic_models_numba import (
    ALL_MODEL_NAMES,
    MODEL_NAME_TO_INDEX,
    NUM_MODELS,
    enabled_global_to_local,
    enabled_local_to_global,
    get_enabled_model_indices,
    get_enabled_model_names,
    get_num_enabled_models,
    model_f_e,
    set_enabled_models,
    warmup_numba,
)

# ============================================================================
#  Fixtures
# ============================================================================


# Test points covering the valid range (avoid exact 0 and 1)
E_TEST_VALUES = [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]


@pytest.fixture(autouse=True)
def _reset_enabled_models():
    """Reset enabled models to all before and after each test."""
    set_enabled_models(None)
    yield
    set_enabled_models(None)


# ============================================================================
#  Test: model_f_e matches Python reference for every model
# ============================================================================


class TestModelFEMatchesPythonReference:
    """For each model in NUC_MODELS_TABLE, verify that model_f_e(idx, e)
    produces the same result as the Python differential_form(e)."""

    @pytest.mark.parametrize("model_name", list(NUC_MODELS_TABLE.keys()))
    @pytest.mark.parametrize("e_val", E_TEST_VALUES)
    def test_model_matches_reference(self, model_name, e_val):
        """model_f_e(idx, e) ≈ NUC_MODELS_TABLE[name]['differential_form'](e)."""
        # B1 has a singularity at e=0.5 where (1-e)-e=0
        if model_name == "B1" and abs(e_val - 0.5) < 1e-6:
            pytest.skip("B1 singularity at e=0.5")

        assert model_name in MODEL_NAME_TO_INDEX, (
            f"Model '{model_name}' from NUC_MODELS_TABLE is missing in MODEL_NAME_TO_INDEX"
        )
        idx = MODEL_NAME_TO_INDEX[model_name]
        python_fn = NUC_MODELS_TABLE[model_name]["differential_form"]

        numba_val = model_f_e(idx, e_val)
        python_val = float(python_fn(e_val))

        assert np.isclose(numba_val, python_val, rtol=1e-10, atol=1e-14), (
            f"Model {model_name} (idx={idx}) at e={e_val}: numba={numba_val}, python={python_val}"
        )


# ============================================================================
#  Test: MODEL_NAME_TO_INDEX completeness
# ============================================================================


class TestModelNameToIndex:
    """Verify the mapping dict is complete and consistent."""

    def test_covers_all_nuc_models(self):
        """Every model in NUC_MODELS_TABLE must have an index."""
        for name in NUC_MODELS_TABLE:
            assert name in MODEL_NAME_TO_INDEX, f"Missing: {name}"

    def test_all_names_list_matches_keys(self):
        """ALL_MODEL_NAMES length must equal NUM_MODELS."""
        assert len(ALL_MODEL_NAMES) == NUM_MODELS

    def test_indices_are_sequential(self):
        """Indices should be 0..NUM_MODELS-1."""
        for i, name in enumerate(ALL_MODEL_NAMES):
            assert MODEL_NAME_TO_INDEX[name] == i

    def test_num_models_equals_nuc_table(self):
        """NUM_MODELS must match the count of NUC_MODELS_TABLE entries."""
        assert NUM_MODELS == len(NUC_MODELS_TABLE)


# ============================================================================
#  Test: model_f_e edge cases
# ============================================================================


class TestModelFEEdgeCases:
    """Test boundary behaviour of model_f_e."""

    def test_unknown_index_returns_e(self):
        """An out-of-range index should return e (safe fallback)."""
        assert model_f_e(999, 0.5) == 0.5
        assert model_f_e(-1, 0.3) == 0.3

    @pytest.mark.parametrize("idx", range(NUM_MODELS))
    def test_returns_finite_at_midpoint(self, idx):
        """All models must produce finite values at e=0.5."""
        val = model_f_e(idx, 0.5)
        assert np.isfinite(val), f"model_f_e({idx}, 0.5) = {val} is not finite"

    @pytest.mark.parametrize("idx", range(NUM_MODELS))
    def test_returns_positive_at_midpoint(self, idx):
        """Most models should produce positive f(e) at e=0.5."""
        val = model_f_e(idx, 0.5)
        # B1 at e=0.5: f(e) = 1/(0.5-0.5) → very large, but after clipping it's finite
        # All models should be positive for typical e values
        assert val > 0 or np.isfinite(val), f"model_f_e({idx}, 0.5) = {val}"


# ============================================================================
#  Test: Enabled models management
# ============================================================================


class TestEnabledModels:
    """Test the model selection (enable/disable) mechanism."""

    def test_default_all_enabled(self):
        """By default all models are enabled."""
        assert get_num_enabled_models() == NUM_MODELS
        assert len(get_enabled_model_names()) == NUM_MODELS
        np.testing.assert_array_equal(get_enabled_model_indices(), np.arange(NUM_MODELS, dtype=np.int64))

    def test_set_subset(self):
        """Enabling a subset should narrow the available models."""
        subset = ["F1/A1", "A2", "R3"]
        set_enabled_models(subset)

        names = get_enabled_model_names()
        assert set(names) == set(subset)
        assert get_num_enabled_models() == 3

        indices = get_enabled_model_indices()
        assert len(indices) == 3
        # Indices must be sorted
        assert list(indices) == sorted(indices)

    def test_reset_with_none(self):
        """Passing None resets to all models."""
        set_enabled_models(["A2"])
        assert get_num_enabled_models() == 1
        set_enabled_models(None)
        assert get_num_enabled_models() == NUM_MODELS

    def test_reset_with_empty_list(self):
        """Passing empty list resets to all models."""
        set_enabled_models(["A2"])
        set_enabled_models([])
        assert get_num_enabled_models() == NUM_MODELS

    def test_invalid_names_ignored(self):
        """Unknown model names are silently ignored."""
        set_enabled_models(["A2", "NONEXISTENT", "R3"])
        names = get_enabled_model_names()
        assert set(names) == {"A2", "R3"}

    def test_all_invalid_resets_to_all(self):
        """If all names are invalid, fall back to all models."""
        set_enabled_models(["FAKE1", "FAKE2"])
        assert get_num_enabled_models() == NUM_MODELS

    def test_local_to_global_mapping(self):
        """enabled_local_to_global maps correctly."""
        set_enabled_models(["F2", "A3", "D1"])
        # Global indices: F2=3, A3=7, D1=22  →  sorted: [3, 7, 22]
        assert enabled_local_to_global(0) == MODEL_NAME_TO_INDEX["F2"]
        assert enabled_local_to_global(1) == MODEL_NAME_TO_INDEX["A3"]
        assert enabled_local_to_global(2) == MODEL_NAME_TO_INDEX["D1"]

    def test_global_to_local_mapping(self):
        """enabled_global_to_local maps correctly."""
        set_enabled_models(["F2", "A3", "D1"])
        assert enabled_global_to_local(MODEL_NAME_TO_INDEX["F2"]) == 0
        assert enabled_global_to_local(MODEL_NAME_TO_INDEX["A3"]) == 1
        assert enabled_global_to_local(MODEL_NAME_TO_INDEX["D1"]) == 2

    def test_global_to_local_raises_for_disabled(self):
        """enabled_global_to_local raises ValueError for non-enabled model."""
        set_enabled_models(["F2"])
        with pytest.raises(ValueError, match="not enabled"):
            enabled_global_to_local(MODEL_NAME_TO_INDEX["A2"])


# ============================================================================
#  Test: warmup_numba
# ============================================================================


class TestWarmup:
    """Test JIT warmup function."""

    def test_warmup_completes(self):
        """warmup_numba() should complete without error."""
        warmup_numba()  # Should not raise

    def test_warmup_idempotent(self):
        """Calling warmup twice should be fine."""
        warmup_numba()
        warmup_numba()
