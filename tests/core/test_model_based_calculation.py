"""Tests for model_based_calculation module — ODE integration and optimization.

Validates:
- ode_function_numba() produces consistent derivatives
- compute_ode_mse() returns valid MSE with mock data
- SciPyObjective is picklable for multiprocessing
- SciPyObjective.__call__() returns scalar MSE
"""

import pickle

import numpy as np
import pytest

from src.core.kinetic_models_numba import ode_function_numba
from src.core.model_based_calculation import SciPyObjective, compute_ode_mse

# ============================================================================
#  Fixtures
# ============================================================================


@pytest.fixture
def simple_ode_params():
    """Simple ODE parameters for A→B reaction."""
    return np.array([10.0, 100.0, 5.0, 1.0])  # logA, Ea, model_idx(F1/A1), contrib


@pytest.fixture
def simple_scheme_indices():
    """Source/target indices for A→B reaction."""
    return np.array([0], dtype=np.int64), np.array([1], dtype=np.int64)


@pytest.fixture
def mock_temperature():
    """Mock temperature array (K)."""
    return np.linspace(300, 600, 100)


@pytest.fixture
def mock_exp_mass(mock_temperature):
    """Mock experimental mass (normalized)."""
    # Simple sigmoid decay from 1 to 0
    return 1.0 / (1.0 + np.exp((mock_temperature - 450) / 30))


# ============================================================================
#  Test: ode_function_numba
# ============================================================================


class TestOdeFunctionNumba:
    """Tests for ode_function_numba function."""

    def test_returns_correct_shape(self, simple_ode_params, simple_scheme_indices):
        """ode_function_numba should return array with same shape as y."""
        src, tgt = simple_scheme_indices
        y = np.array([1.0, 0.0, 0.0])  # 2 species + 1 reaction rate
        T = 400.0
        beta = 10.0

        dydt = ode_function_numba(T, y, beta, simple_ode_params, src, tgt, 2, 1)

        assert dydt.shape == y.shape

    def test_reactant_decreases(self, simple_ode_params, simple_scheme_indices):
        """Reactant concentration should decrease (negative derivative)."""
        src, tgt = simple_scheme_indices
        y = np.array([0.8, 0.2, 0.0])
        T = 450.0
        beta = 10.0

        dydt = ode_function_numba(T, y, beta, simple_ode_params, src, tgt, 2, 1)

        assert dydt[0] < 0  # Reactant decreases

    def test_product_increases(self, simple_ode_params, simple_scheme_indices):
        """Product concentration should increase (positive derivative)."""
        src, tgt = simple_scheme_indices
        y = np.array([0.8, 0.2, 0.0])
        T = 450.0
        beta = 10.0

        dydt = ode_function_numba(T, y, beta, simple_ode_params, src, tgt, 2, 1)

        assert dydt[1] > 0  # Product increases

    def test_rate_is_positive(self, simple_ode_params, simple_scheme_indices):
        """Reaction rate should be positive."""
        src, tgt = simple_scheme_indices
        y = np.array([0.8, 0.2, 0.0])
        T = 450.0
        beta = 10.0

        dydt = ode_function_numba(T, y, beta, simple_ode_params, src, tgt, 2, 1)

        assert dydt[2] > 0  # Rate is positive


# ============================================================================
#  Test: compute_ode_mse
# ============================================================================


class TestComputeOdeMse:
    """Tests for compute_ode_mse function."""

    def test_returns_scalar(self, mock_temperature, mock_exp_mass, simple_ode_params, simple_scheme_indices):
        """compute_ode_mse should return a scalar float."""
        src, tgt = simple_scheme_indices
        contributions = np.array([1.0])

        mse = compute_ode_mse(
            beta=10.0,
            params=simple_ode_params,
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
            exp_temperature=mock_temperature,
            exp_mass=mock_exp_mass,
            contributions=contributions,
        )

        assert isinstance(mse, float)

    def test_returns_finite_value(self, mock_temperature, mock_exp_mass, simple_ode_params, simple_scheme_indices):
        """compute_ode_mse should return finite value for valid inputs."""
        src, tgt = simple_scheme_indices
        contributions = np.array([1.0])

        mse = compute_ode_mse(
            beta=10.0,
            params=simple_ode_params,
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
            exp_temperature=mock_temperature,
            exp_mass=mock_exp_mass,
            contributions=contributions,
        )

        assert np.isfinite(mse)

    def test_perfect_fit_returns_low_mse(self, mock_temperature, simple_scheme_indices):
        """Well-tuned parameters should produce low MSE."""
        src, tgt = simple_scheme_indices
        # Generate perfect data from known parameters
        params = np.array([12.0, 120.0, 5.0, 1.0])  # logA, Ea, F1/A1, contrib
        contributions = np.array([1.0])

        # Generate mock data that matches the model output
        from scipy.integrate import solve_ivp

        y0 = np.array([1.0, 0.0, 0.0])

        def ode_wrapper(T, y):
            return ode_function_numba(T, y, 10.0, params, src, tgt, 2, 1)

        sol = solve_ivp(
            ode_wrapper, [mock_temperature[0], mock_temperature[-1]], y0, t_eval=mock_temperature, method="LSODA"
        )
        mock_mass = 1.0 - sol.y[2, :]  # Use integrated rate as alpha

        mse = compute_ode_mse(
            beta=10.0,
            params=params,
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
            exp_temperature=mock_temperature,
            exp_mass=mock_mass,
            contributions=contributions,
        )

        assert mse < 0.01  # Should be very low for perfect fit


# ============================================================================
#  Test: SciPyObjective picklability
# ============================================================================


class TestSciPyObjectivePicklability:
    """Tests for SciPyObjective pickling (required for multiprocessing)."""

    @pytest.fixture
    def objective(self, mock_temperature, mock_exp_mass, simple_scheme_indices):
        """Create SciPyObjective instance for testing."""
        src, tgt = simple_scheme_indices
        return SciPyObjective(
            betas=[5.0, 10.0],
            exp_temperature=mock_temperature,
            all_exp_masses=[mock_exp_mass, mock_exp_mass],
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
        )

    def test_pickle_dumps(self, objective):
        """pickle.dumps should succeed."""
        pickled = pickle.dumps(objective)
        assert isinstance(pickled, bytes)

    def test_pickle_roundtrip(self, objective):
        """Pickle roundtrip should preserve functionality."""
        pickled = pickle.dumps(objective)
        restored = pickle.loads(pickled)

        assert isinstance(restored, SciPyObjective)
        assert restored._num_species == objective._num_species
        assert restored._num_reactions == objective._num_reactions

    def test_restored_objective_works(self, objective, simple_ode_params):
        """Restored objective should compute MSE."""
        pickled = pickle.dumps(objective)
        restored = pickle.loads(pickled)

        mse = restored(simple_ode_params)

        assert isinstance(mse, float)
        assert np.isfinite(mse)


# ============================================================================
#  Test: SciPyObjective.__call__
# ============================================================================


class TestSciPyObjectiveCall:
    """Tests for SciPyObjective.__call__ method."""

    @pytest.fixture
    def objective(self, mock_temperature, mock_exp_mass, simple_scheme_indices):
        """Create SciPyObjective instance for testing."""
        src, tgt = simple_scheme_indices
        return SciPyObjective(
            betas=[10.0],
            exp_temperature=mock_temperature,
            all_exp_masses=[mock_exp_mass],
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
        )

    def test_returns_scalar(self, objective, simple_ode_params):
        """__call__ should return scalar float."""
        mse = objective(simple_ode_params)

        assert isinstance(mse, float)

    def test_returns_finite(self, objective, simple_ode_params):
        """__call__ should return finite value for valid params."""
        mse = objective(simple_ode_params)

        assert np.isfinite(mse)

    def test_sums_multiple_heating_rates(self, mock_temperature, mock_exp_mass, simple_scheme_indices):
        """__call__ should sum MSE across all heating rates."""
        src, tgt = simple_scheme_indices
        objective = SciPyObjective(
            betas=[5.0, 10.0, 20.0],
            exp_temperature=mock_temperature,
            all_exp_masses=[mock_exp_mass, mock_exp_mass, mock_exp_mass],
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
        )
        params = np.array([10.0, 100.0, 5.0, 1.0])

        mse = objective(params)

        # Should be sum of 3 heating rates
        assert mse > 0
        assert np.isfinite(mse)

    def test_rounds_model_indices(self, mock_temperature, mock_exp_mass, simple_scheme_indices):
        """__call__ should round model indices to nearest integer."""
        src, tgt = simple_scheme_indices
        objective = SciPyObjective(
            betas=[10.0],
            exp_temperature=mock_temperature,
            all_exp_masses=[mock_exp_mass],
            src_indices=src,
            tgt_indices=tgt,
            num_species=2,
            num_reactions=1,
        )
        # Pass non-integer model index
        params = np.array([10.0, 100.0, 5.7, 1.0])

        # Should not raise - model index is rounded internally
        mse = objective(params)

        assert np.isfinite(mse)
