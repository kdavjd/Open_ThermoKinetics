"""
Numba-compatible kinetic models for model-based ODE optimization.

Provides JIT-compiled kinetic model functions that can be called from Numba-jitted
ODE integrators, enabling ~100x speedup for individual function calls.

All models correspond to entries in NUC_MODELS_TABLE (app_settings.py) and are
defined in terms of concentration e (extent of reactant), where e = 1 - α.

Usage:
    from src.core.kinetic_models_numba import (
        model_f_e,
        ode_function_numba,
        MODEL_NAME_TO_INDEX,
        ALL_MODEL_NAMES,
        get_enabled_model_indices,
        set_enabled_models,
        warmup_numba,
    )

    # Get index for a model name
    idx = MODEL_NAME_TO_INDEX["A2"]

    # Evaluate model at e=0.5
    result = model_f_e(idx, 0.5)

    # Select subset of models for optimization
    set_enabled_models(["F1/A1", "A2", "A3", "R2", "R3"])

    # Get only enabled model indices for bounds
    enabled = get_enabled_model_indices()

    # For MSE computation with deadline timeout, use:
    # from src.core.model_based_calculation import compute_ode_mse, SciPyObjective
"""

import math

import numpy as np
from numba import njit

# ===========================================================================
#  Constants
# ===========================================================================

_EPS = 1e-8
_R_GAS = 8.314  # Universal gas constant J/(mol·K)


# ===========================================================================
#  Individual model functions (all @njit, scalar in / scalar out)
# ===========================================================================


@njit(cache=True, fastmath=True)
def _clip(e: float) -> float:
    """Clip e to valid range [eps, 1-eps]."""
    if e < _EPS:
        return _EPS
    if e > 1.0 - _EPS:
        return 1.0 - _EPS
    return e


# --- F family (n-th order) ------------------------------------------------


@njit(cache=True, fastmath=True)
def _f_F1_3(e: float) -> float:
    e = _clip(e)
    return 1.5 * e ** (1.0 / 3.0)


@njit(cache=True, fastmath=True)
def _f_F3_4(e: float) -> float:
    e = _clip(e)
    return 4.0 * e**0.75


@njit(cache=True, fastmath=True)
def _f_F3_2(e: float) -> float:
    e = _clip(e)
    return 2.0 * e**1.5


@njit(cache=True, fastmath=True)
def _f_F2(e: float) -> float:
    e = _clip(e)
    return e * e


@njit(cache=True, fastmath=True)
def _f_F3(e: float) -> float:
    e = _clip(e)
    return e * e * e


@njit(cache=True, fastmath=True)
def _f_F1_A1(e: float) -> float:
    e = _clip(e)
    return e


# --- A family (Avrami / nucleation) ----------------------------------------


@njit(cache=True, fastmath=True)
def _f_A2(e: float) -> float:
    e = _clip(e)
    return 2.0 * e * (-math.log(e)) ** 0.5


@njit(cache=True, fastmath=True)
def _f_A3(e: float) -> float:
    e = _clip(e)
    return 3.0 * e * (-math.log(e)) ** (2.0 / 3.0)


@njit(cache=True, fastmath=True)
def _f_A4(e: float) -> float:
    e = _clip(e)
    return 4.0 * e * (-math.log(e)) ** 0.75


@njit(cache=True, fastmath=True)
def _f_A2_3(e: float) -> float:
    e = _clip(e)
    return (2.0 / 3.0) * e * (-math.log(e)) ** (-0.5)


@njit(cache=True, fastmath=True)
def _f_A3_2(e: float) -> float:
    e = _clip(e)
    return 1.5 * e * (-math.log(e)) ** (1.0 / 3.0)


@njit(cache=True, fastmath=True)
def _f_A3_4(e: float) -> float:
    e = _clip(e)
    return 0.75 * e * (-math.log(e)) ** (-1.0 / 3.0)


@njit(cache=True, fastmath=True)
def _f_A5_2(e: float) -> float:
    e = _clip(e)
    return 2.5 * e * (-math.log(e)) ** (3.0 / 5.0)


# --- R family (contracting geometry) ---------------------------------------


@njit(cache=True, fastmath=True)
def _f_F0_R1_P1(e: float) -> float:
    return 1.0


@njit(cache=True, fastmath=True)
def _f_R2(e: float) -> float:
    e = _clip(e)
    return 2.0 * e**0.5


@njit(cache=True, fastmath=True)
def _f_R3(e: float) -> float:
    e = _clip(e)
    return 3.0 * e ** (2.0 / 3.0)


# --- P family (power law) --------------------------------------------------


@njit(cache=True, fastmath=True)
def _f_P3_2(e: float) -> float:
    e = _clip(e)
    return (2.0 / 3.0) / (1.0 - e) ** 0.5


@njit(cache=True, fastmath=True)
def _f_P2(e: float) -> float:
    e = _clip(e)
    return 2.0 * (1.0 - e) ** 0.5


@njit(cache=True, fastmath=True)
def _f_P3(e: float) -> float:
    e = _clip(e)
    return 3.0 * (1.0 - e) ** (2.0 / 3.0)


@njit(cache=True, fastmath=True)
def _f_P4(e: float) -> float:
    e = _clip(e)
    return 4.0 * (1.0 - e) ** 0.75


# --- E family (exponential) ------------------------------------------------


@njit(cache=True, fastmath=True)
def _f_E1(e: float) -> float:
    e = _clip(e)
    return 1.0 - e


@njit(cache=True, fastmath=True)
def _f_E2(e: float) -> float:
    e = _clip(e)
    return (1.0 - e) / 2.0


# --- D family (diffusion) --------------------------------------------------


@njit(cache=True, fastmath=True)
def _f_D1(e: float) -> float:
    e = _clip(e)
    return 1.0 / (2.0 * (1.0 - e))


@njit(cache=True, fastmath=True)
def _f_D2(e: float) -> float:
    e = _clip(e)
    return 1.0 / (-math.log(e))


@njit(cache=True, fastmath=True)
def _f_D3(e: float) -> float:
    e = _clip(e)
    return (1.5 * e ** (2.0 / 3.0)) / (1.0 - e ** (1.0 / 3.0))


@njit(cache=True, fastmath=True)
def _f_D4(e: float) -> float:
    e = _clip(e)
    return 1.5 / (e ** (-1.0 / 3.0) - 1.0)


@njit(cache=True, fastmath=True)
def _f_D5(e: float) -> float:
    e = _clip(e)
    return (1.5 * e ** (4.0 / 3.0)) / (e ** (-1.0 / 3.0) - 1.0)


@njit(cache=True, fastmath=True)
def _f_D6(e: float) -> float:
    e = _clip(e)
    return (1.5 * (1.0 + e) ** (2.0 / 3.0)) / ((1.0 + e) ** (1.0 / 3.0) - 1.0)


@njit(cache=True, fastmath=True)
def _f_D7(e: float) -> float:
    e = _clip(e)
    return 1.5 / (1.0 - (1.0 + e) ** (-1.0 / 3.0))


@njit(cache=True, fastmath=True)
def _f_D8(e: float) -> float:
    e = _clip(e)
    return (1.5 * (1.0 + e) ** (4.0 / 3.0)) / (1.0 - (1.0 + e) ** (-1.0 / 3.0))


# --- G family (geometrical / nucleation-growth) ----------------------------


@njit(cache=True, fastmath=True)
def _f_G1(e: float) -> float:
    e = _clip(e)
    return 1.0 / (2.0 * e)


@njit(cache=True, fastmath=True)
def _f_G2(e: float) -> float:
    e = _clip(e)
    return 1.0 / (3.0 * e * e)


@njit(cache=True, fastmath=True)
def _f_G3(e: float) -> float:
    e = _clip(e)
    return 1.0 / (4.0 * e * e * e)


@njit(cache=True, fastmath=True)
def _f_G4(e: float) -> float:
    e = _clip(e)
    return 0.5 * e * (-math.log(e))


@njit(cache=True, fastmath=True)
def _f_G5(e: float) -> float:
    e = _clip(e)
    return (1.0 / 3.0) * e * (-math.log(e)) ** 2


@njit(cache=True, fastmath=True)
def _f_G6(e: float) -> float:
    e = _clip(e)
    return 0.25 * e * (-math.log(e)) ** 3


@njit(cache=True, fastmath=True)
def _f_G7(e: float) -> float:
    e = _clip(e)
    return 0.25 * e**0.5 / (1.0 - e**0.5)


@njit(cache=True, fastmath=True)
def _f_G8(e: float) -> float:
    e = _clip(e)
    return (1.0 / 3.0) * e ** (2.0 / 3.0) / (1.0 - e ** (1.0 / 3.0))


# --- B family (Prout-Tompkins) ---------------------------------------------


@njit(cache=True, fastmath=True)
def _f_B1(e: float) -> float:
    e = _clip(e)
    denom = (1.0 - e) - e
    if abs(denom) < _EPS:
        return 1.0 / _EPS  # avoid division by zero at e≈0.5
    return 1.0 / denom


# ===========================================================================
#  Master dispatch function
# ===========================================================================

# Ordered list of ALL model names — index in this list == model_idx
ALL_MODEL_NAMES: list[str] = [
    "F1/3",  # 0
    "F3/4",  # 1
    "F3/2",  # 2
    "F2",  # 3
    "F3",  # 4
    "F1/A1",  # 5
    "A2",  # 6
    "A3",  # 7
    "A4",  # 8
    "A2/3",  # 9
    "A3/2",  # 10
    "A3/4",  # 11
    "A5/2",  # 12
    "F0/R1/P1",  # 13
    "R2",  # 14
    "R3",  # 15
    "P3/2",  # 16
    "P2",  # 17
    "P3",  # 18
    "P4",  # 19
    "E1",  # 20
    "E2",  # 21
    "D1",  # 22
    "D2",  # 23
    "D3",  # 24
    "D4",  # 25
    "D5",  # 26
    "D6",  # 27
    "D7",  # 28
    "D8",  # 29
    "G1",  # 30
    "G2",  # 31
    "G3",  # 32
    "G4",  # 33
    "G5",  # 34
    "G6",  # 35
    "G7",  # 36
    "G8",  # 37
    "B1",  # 38
]

# Name -> global index mapping (constant, all 39 models)
MODEL_NAME_TO_INDEX: dict[str, int] = {name: i for i, name in enumerate(ALL_MODEL_NAMES)}

NUM_MODELS: int = len(ALL_MODEL_NAMES)

# ===========================================================================
#  Enabled models management
# ===========================================================================

# _enabled_indices is a sorted numpy array of global model indices that the
# user has chosen to include in the optimization.  By default ALL models are
# enabled.  GUI code (or tests) call set_enabled_models() to narrow the set.

_enabled_indices: np.ndarray = np.arange(NUM_MODELS, dtype=np.int64)

# _enabled_names mirrors _enabled_indices as a list of model name strings.
_enabled_names: list[str] = list(ALL_MODEL_NAMES)


def set_enabled_models(names: list[str] | None = None) -> None:
    """Select which models are available for optimization.

    Parameters
    ----------
    names : list[str] | None
        Model names to enable.  ``None`` or empty list resets to ALL models.
        Names not found in ``ALL_MODEL_NAMES`` are silently ignored.

    After calling this function, ``get_enabled_model_indices()`` returns only
    the selected indices, and ``get_enabled_model_names()`` returns the
    corresponding names.  The mapping from *local* index (0-based position in
    the enabled list) to *global* model_idx used by ``model_f_e`` is provided
    by ``enabled_local_to_global()``.
    """
    global _enabled_indices, _enabled_names

    if not names:
        _enabled_indices = np.arange(NUM_MODELS, dtype=np.int64)
        _enabled_names = list(ALL_MODEL_NAMES)
        return

    indices = sorted(MODEL_NAME_TO_INDEX[n] for n in names if n in MODEL_NAME_TO_INDEX)
    if not indices:
        # Fallback: enable all if no valid names
        _enabled_indices = np.arange(NUM_MODELS, dtype=np.int64)
        _enabled_names = list(ALL_MODEL_NAMES)
        return

    _enabled_indices = np.array(indices, dtype=np.int64)
    _enabled_names = [ALL_MODEL_NAMES[i] for i in indices]


def get_enabled_model_indices() -> np.ndarray:
    """Return sorted array of *global* model indices currently enabled."""
    return _enabled_indices


def get_enabled_model_names() -> list[str]:
    """Return list of model names currently enabled (same order as indices)."""
    return list(_enabled_names)


def get_num_enabled_models() -> int:
    """Return count of currently enabled models."""
    return len(_enabled_indices)


def enabled_local_to_global(local_idx: int) -> int:
    """Convert a local index (0..num_enabled-1) to the global model_idx.

    This is used in the optimization bounds: the model_idx parameter in the
    params vector ranges over [0, num_enabled-1], and this function maps it
    back to the global index consumed by ``model_f_e``.
    """
    return int(_enabled_indices[local_idx])


def enabled_global_to_local(global_idx: int) -> int:
    """Convert a global model_idx to local index (0..num_enabled-1).

    Raises ValueError if the model is not enabled.
    """
    pos = np.searchsorted(_enabled_indices, global_idx)
    if pos < len(_enabled_indices) and _enabled_indices[pos] == global_idx:
        return int(pos)
    raise ValueError(f"Model index {global_idx} is not enabled")


# ===========================================================================
#  model_f_e — Numba-jitted dispatcher
# ===========================================================================


@njit(cache=True, fastmath=True)
def model_f_e(model_idx: int, e: float) -> float:  # noqa: C901
    """Evaluate the differential form f(e) for the model identified by *model_idx*.

    Parameters
    ----------
    model_idx : int
        Global index of the model (see ``MODEL_NAME_TO_INDEX``).
    e : float
        Concentration (extent of unreacted material), ∈ (0, 1).

    Returns
    -------
    float
        f(e) value for the specified model.
    """
    if model_idx == 0:
        return _f_F1_3(e)
    elif model_idx == 1:
        return _f_F3_4(e)
    elif model_idx == 2:
        return _f_F3_2(e)
    elif model_idx == 3:
        return _f_F2(e)
    elif model_idx == 4:
        return _f_F3(e)
    elif model_idx == 5:
        return _f_F1_A1(e)
    elif model_idx == 6:
        return _f_A2(e)
    elif model_idx == 7:
        return _f_A3(e)
    elif model_idx == 8:
        return _f_A4(e)
    elif model_idx == 9:
        return _f_A2_3(e)
    elif model_idx == 10:
        return _f_A3_2(e)
    elif model_idx == 11:
        return _f_A3_4(e)
    elif model_idx == 12:
        return _f_A5_2(e)
    elif model_idx == 13:
        return _f_F0_R1_P1(e)
    elif model_idx == 14:
        return _f_R2(e)
    elif model_idx == 15:
        return _f_R3(e)
    elif model_idx == 16:
        return _f_P3_2(e)
    elif model_idx == 17:
        return _f_P2(e)
    elif model_idx == 18:
        return _f_P3(e)
    elif model_idx == 19:
        return _f_P4(e)
    elif model_idx == 20:
        return _f_E1(e)
    elif model_idx == 21:
        return _f_E2(e)
    elif model_idx == 22:
        return _f_D1(e)
    elif model_idx == 23:
        return _f_D2(e)
    elif model_idx == 24:
        return _f_D3(e)
    elif model_idx == 25:
        return _f_D4(e)
    elif model_idx == 26:
        return _f_D5(e)
    elif model_idx == 27:
        return _f_D6(e)
    elif model_idx == 28:
        return _f_D7(e)
    elif model_idx == 29:
        return _f_D8(e)
    elif model_idx == 30:
        return _f_G1(e)
    elif model_idx == 31:
        return _f_G2(e)
    elif model_idx == 32:
        return _f_G3(e)
    elif model_idx == 33:
        return _f_G4(e)
    elif model_idx == 34:
        return _f_G5(e)
    elif model_idx == 35:
        return _f_G6(e)
    elif model_idx == 36:
        return _f_G7(e)
    elif model_idx == 37:
        return _f_G8(e)
    elif model_idx == 38:
        return _f_B1(e)
    else:
        # Unknown model — return e as safe fallback
        return e


# ===========================================================================
#  Warmup
# ===========================================================================


def warmup_numba() -> None:
    """Trigger JIT compilation for all model functions and ODE function.

    Should be called once at application startup (e.g. during import or
    in a background thread) so that subsequent calls execute at native speed.

    This function warms up:
    - All kinetic model functions via model_f_e()
    - ode_function_numba() for ODE integration

    Note: compute_ode_mse() warmup is handled in model_based_calculation.py
    to avoid circular imports.
    """
    e_test = 0.5
    for idx in range(NUM_MODELS):
        model_f_e(idx, e_test)

    # Warmup ode_function_numba with minimal test case
    y_test = np.array([1.0, 0.0, 0.0, 0.0, 0.0])  # 2 species + 1 reaction
    params_test = np.array([10.0, 100.0, 0.0, 1.0])  # logA, Ea, model_idx, contrib
    src_test = np.array([0], dtype=np.int64)
    tgt_test = np.array([1], dtype=np.int64)
    ode_function_numba(300.0, y_test, 10.0, params_test, src_test, tgt_test, 2, 1)


# ===========================================================================
#  ODE Function for Model-Based Optimization
# ===========================================================================


@njit(cache=True, fastmath=True)
def ode_function_numba(
    T: float,
    y: np.ndarray,
    beta: float,
    params: np.ndarray,
    src_indices: np.ndarray,
    tgt_indices: np.ndarray,
    num_species: int,
    num_reactions: int,
) -> np.ndarray:
    """Numba-jitted ODE system for reaction kinetics.

    This is a Numba-compatible version of ode_function() from model_based_calculation.py,
    optimized for ~100x speedup in the inner loop of ODE integration.

    Parameters
    ----------
    T : float
        Current temperature (K). Must be > 0.
    y : np.ndarray
        State vector [e_1, ..., e_N, rate_1, ..., rate_M] where:
        - e_i is concentration of species i (dimensionless, 0-1)
        - rate_j is cumulative rate of reaction j
    beta : float
        Heating rate (K/min). Must be > 0.
    params : np.ndarray
        Parameter vector of length 4*M:
        - params[0:M]         = logA (log₁₀ of pre-exponential factor)
        - params[M:2M]        = Ea (activation energy, kJ/mol)
        - params[2M:3M]       = model_idx (kinetic model index)
        - params[3M:4M]       = contribution (reaction contribution, 0-1)
    src_indices : np.ndarray (int64)
        Source species index for each reaction (length M).
    tgt_indices : np.ndarray (int64)
        Target species index for each reaction (length M).
    num_species : int
        Number of species in the reaction scheme.
    num_reactions : int
        Number of reactions in the reaction scheme.

    Returns
    -------
    np.ndarray
        Derivative dy/dT with same shape as y.

    Notes
    -----
    The ODE system implements the Arrhenius equation:

        rate = (10^logA / β) * exp(-Ea·1000 / (R·T)) * f(e)

    where f(e) is the kinetic model function evaluated via model_f_e().

    Safety measures:
        - T is clamped to minimum 1.0 K to avoid division by zero
        - Exponent argument is clamped to [-700, 700] to avoid overflow
    """
    dYdt = np.zeros_like(y)

    # Safety: ensure T > 0 to avoid division by zero
    T_safe = T if T > 1.0 else 1.0

    for i in range(num_reactions):
        src_idx = src_indices[i]
        tgt_idx = tgt_indices[i]

        # Concentration of reactant species
        e_value = y[src_idx]

        # Get model index (round to nearest integer, clamp to valid range)
        model_param_idx = 2 * num_reactions + i
        model_idx = int(round(params[model_param_idx]))
        if model_idx < 0:
            model_idx = 0
        elif model_idx >= NUM_MODELS:
            model_idx = NUM_MODELS - 1

        # Evaluate kinetic model f(e)
        f_e = model_f_e(model_idx, e_value)

        # Arrhenius parameters
        logA = params[i]
        Ea = params[num_reactions + i]

        # Rate constant: k = (10^logA / β) * exp(-Ea·1000 / (R·T))
        # Clamp exponent to avoid overflow in exp()
        exponent = -Ea * 1000.0 / (_R_GAS * T_safe)
        if exponent < -700.0:
            exponent = -700.0
        elif exponent > 700.0:
            exponent = 700.0

        k_i = (10.0**logA * math.exp(exponent)) / beta

        # Reaction rate
        rate = k_i * f_e

        # Update derivatives: reactant loses mass, product gains mass
        dYdt[src_idx] -= rate
        dYdt[tgt_idx] += rate

        # Store rate in state vector (for cumulative conversion tracking)
        dYdt[num_species + i] = rate

    return dYdt
