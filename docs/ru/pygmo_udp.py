"""
Helper module for PyGMO Model-Based ODE optimization.

Contains Numba-JIT compiled functions and PyGMO UDP (User Defined Problem) class.
Must be a separate .py file for multiprocessing pickling in PyGMO island model
(mp_island sends UDP to worker processes via pickle).
"""

import time
import warnings

import numpy as np
from numba import njit
from scipy.integrate import solve_ivp

warnings.filterwarnings("ignore", category=RuntimeWarning, module="scipy.integrate")
warnings.filterwarnings("ignore", category=UserWarning, module="scipy.integrate")

# === Timeout для зависающих ODE интеграций ===
INTEGRATION_TIMEOUT_MS = 200.0  # мс — лимит на один вызов solve_ivp


class _IntegrationTimeout(Exception):
    """Исключение при превышении deadline внутри ODE wrapper."""

    pass


R_GAS = 8.314
EPS = 1e-10

# === Model indices mapping ===
# 0=A2/3, 1=A3, 2=A3/2, 3=F1/3, 4=F1/A1, 5=F2, 6=F3, 7=G1, 8=G2, 9=R2, 10=R3
MODEL_NAMES = ["A2/3", "A3", "A3/2", "F1/3", "F1/A1", "F2", "F3", "G1", "G2", "R2", "R3"]


@njit(cache=True, fastmath=True)
def model_f_e(model_idx: int, e: float) -> float:
    """
    Дифференциальная форма кинетической модели (Numba JIT).

    Индексы: 0=A2/3, 1=A3, 2=A3/2, 3=F1/3, 4=F1/A1,
             5=F2, 6=F3, 7=G1, 8=G2, 9=R2, 10=R3
    """
    EPS = 1e-10
    EPS_LOG = 1e-6

    e_safe = e
    if e_safe < EPS:
        e_safe = EPS
    if e_safe > 1.0 - EPS:
        e_safe = 1.0 - EPS

    e_log = e
    if e_log < EPS_LOG:
        e_log = EPS_LOG
    if e_log > 1.0 - EPS_LOG:
        e_log = 1.0 - EPS_LOG

    result = 0.0

    if model_idx == 0:  # A2/3: 2e*(-ln(e))^(1/3)
        result = 2.0 * e_log * ((-np.log(e_log)) ** (1.0 / 3.0))
    elif model_idx == 1:  # A3: 3e*(-ln(e))^(2/3)
        result = 3.0 * e_log * ((-np.log(e_log)) ** (2.0 / 3.0))
    elif model_idx == 2:  # A3/2: 1.5e*(-ln(e))^(0.5)
        result = 1.5 * e_log * ((-np.log(e_log)) ** 0.5)
    elif model_idx == 3:  # F1/3: (3/2)*e^(1/3)
        result = 1.5 * (e_safe ** (1.0 / 3.0))
    elif model_idx == 4:  # F1/A1: e
        result = e_safe
    elif model_idx == 5:  # F2: e^2
        result = e_safe * e_safe
    elif model_idx == 6:  # F3: e^3
        result = e_safe * e_safe * e_safe
    elif model_idx == 7:  # G1: e^(1/2)
        result = e_safe**0.5
    elif model_idx == 8:  # G2: e^(1/3)
        result = e_safe ** (1.0 / 3.0)
    elif model_idx == 9:  # R2: 2*e^(1/2)
        result = 2.0 * (e_safe**0.5)
    elif model_idx == 10:  # R3: 3*e^(2/3)
        result = 3.0 * (e_safe ** (2.0 / 3.0))
    else:
        result = e_safe

    if not np.isfinite(result) or result < 0:
        result = 0.0
    return result


@njit(cache=True, fastmath=True)
def ode_function_numba(T, y, beta, params, src_indices, tgt_indices, num_species, num_reactions):
    """
    Numba-JIT compiled ODE right-hand side for kinetic reactions.

    Args:
        T: temperature (K)
        y: state vector [concentrations..., reaction_rates...]
        beta: heating rate (K/min)
        params: [logA..., Ea..., model_idx..., contribution...]
        src_indices: source species indices
        tgt_indices: target species indices
        num_species: number of species
        num_reactions: number of reactions

    Returns:
        dYdt: derivatives w.r.t. temperature
    """
    dYdt = np.zeros_like(y)
    R = 8.314
    T_safe = max(T, 1.0)
    beta_SI = max(beta / 60.0, 0.001)

    for i in range(num_reactions):
        src_idx = src_indices[i]
        tgt_idx = tgt_indices[i]
        e_value = min(max(y[src_idx], 0.0), 1.0)

        logA = params[i]
        Ea = params[num_reactions + i]
        model_idx = int(round(params[2 * num_reactions + i]))
        model_idx = max(0, min(model_idx, 10))

        f_e = model_f_e(model_idx, e_value)

        exponent = -Ea * 1000.0 / (R * T_safe)
        exponent = max(-700.0, min(700.0, exponent))
        k_i = (10.0**logA) * np.exp(exponent) / beta_SI
        k_i = min(k_i, 1e10)

        rate = k_i * f_e
        if not np.isfinite(rate):
            rate = 0.0

        dYdt[src_idx] -= rate
        dYdt[tgt_idx] += rate
        dYdt[num_species + i] = rate

    return dYdt


def compute_ode_mse(
    beta,
    params,
    exp_temperature,
    exp_mass,
    src_indices,
    tgt_indices,
    num_species,
    num_reactions,
    solver_method="LSODA",
    solver_rtol=1e-2,
    solver_atol=1e-4,
    timeout_ms=INTEGRATION_TIMEOUT_MS,
):
    """
    Compute MSE between model and experiment for one heating rate beta.

    Deadline-based timeout: проверка time.perf_counter() внутри ODE wrapper
    (практически нулевой overhead вс threading).
    Default solver: LSODA rtol=1e-2 (12x быстрее BDF, <2% MSE deviation).

    Returns float MSE value (1e4 on failure/timeout).
    """
    y0 = np.zeros(num_species + num_reactions)
    y0[0] = 1.0

    deadline = time.perf_counter() + timeout_ms / 1000.0

    def ode_wrapper(T, y):
        if time.perf_counter() > deadline:
            raise _IntegrationTimeout()
        return ode_function_numba(T, y, beta, params, src_indices, tgt_indices, num_species, num_reactions)

    try:
        sol = solve_ivp(
            ode_wrapper,
            [exp_temperature[0], exp_temperature[-1]],
            y0,
            t_eval=exp_temperature,
            method=solver_method,
            rtol=solver_rtol,
            atol=solver_atol,
        )
    except (_IntegrationTimeout, Exception):
        return 1e4

    if not sol.success:
        return 1e4

    rates_int = sol.y[num_species : num_species + num_reactions, :]
    contributions = params[3 * num_reactions : 4 * num_reactions]
    int_sum = np.sum(contributions[:, np.newaxis] * rates_int, axis=0)
    int_sum_clamped = np.clip(int_sum, 0.0, 1.0)

    M0, Mfin = exp_mass[0], exp_mass[-1]
    model_mass = M0 - (M0 - Mfin) * int_sum_clamped
    model_mass = np.clip(model_mass, Mfin, M0)

    return float(np.mean((model_mass - exp_mass) ** 2))


class SciPyObjective:
    """
    Picklable callable for scipy.optimize.differential_evolution(workers=-1).

    On Windows, multiprocessing uses 'spawn' — worker processes re-import the module.
    Functions defined in Jupyter notebook cells (__main__) can't be imported by workers,
    causing a deadlock. This class lives in a proper .py module, so workers can pickle/unpickle it.

    Usage:
        obj = SciPyObjective(betas, exp_temperature, all_exp_masses, ...)
        result = differential_evolution(obj, bounds=..., workers=-1)
    """

    def __init__(
        self,
        betas,
        exp_temperature,
        all_exp_masses,
        src_indices,
        tgt_indices,
        num_species,
        num_reactions,
        solver_method="LSODA",
        solver_rtol=1e-2,
        solver_atol=1e-4,
        timeout_ms=INTEGRATION_TIMEOUT_MS,
    ):
        self._betas = list(betas)
        self._exp_temperature = np.array(exp_temperature, dtype=np.float64)
        self._all_exp_masses = [np.array(m, dtype=np.float64) for m in all_exp_masses]
        self._src_indices = np.array(src_indices, dtype=np.int64)
        self._tgt_indices = np.array(tgt_indices, dtype=np.int64)
        self._num_species = int(num_species)
        self._num_reactions = int(num_reactions)
        self._solver_method = solver_method
        self._solver_rtol = solver_rtol
        self._solver_atol = solver_atol
        self._timeout_ms = timeout_ms

    def __call__(self, x):
        """Evaluate total MSE. Returns scalar (compatible with scipy DE)."""
        params = np.array(x, dtype=np.float64)
        nr = self._num_reactions
        # Round model indices to nearest integer
        for i in range(nr):
            params[2 * nr + i] = round(params[2 * nr + i])

        total_mse = 0.0
        for i, beta in enumerate(self._betas):
            total_mse += compute_ode_mse(
                beta,
                params,
                self._exp_temperature,
                self._all_exp_masses[i],
                self._src_indices,
                self._tgt_indices,
                self._num_species,
                self._num_reactions,
                self._solver_method,
                self._solver_rtol,
                self._solver_atol,
                self._timeout_ms,
            )
        return total_mse


class ModelBasedUDP:
    """
    PyGMO User Defined Problem (UDP) for model-based kinetic optimization.

    Picklable for mp_island (multiprocessing). All data stored as attributes.
    Uses Numba-JIT ode_function_numba from this module (importable in workers).
    """

    def __init__(
        self,
        betas,
        exp_temperature,
        all_exp_masses,
        src_indices,
        tgt_indices,
        num_species,
        num_reactions,
        bounds_list,
        solver_method="LSODA",
        solver_rtol=1e-2,
        solver_atol=1e-4,
    ):
        self._betas = list(betas)
        self._exp_temperature = np.array(exp_temperature, dtype=np.float64)
        self._all_exp_masses = [np.array(m, dtype=np.float64) for m in all_exp_masses]
        self._src_indices = np.array(src_indices, dtype=np.int64)
        self._tgt_indices = np.array(tgt_indices, dtype=np.int64)
        self._num_species = int(num_species)
        self._num_reactions = int(num_reactions)
        self._lb = [float(b[0]) for b in bounds_list]
        self._ub = [float(b[1]) for b in bounds_list]
        self._solver_method = solver_method
        self._solver_rtol = solver_rtol
        self._solver_atol = solver_atol

    def fitness(self, x):
        """Fitness = total MSE across all heating rates."""
        params = np.array(x, dtype=np.float64)
        total_mse = 0.0
        for i, beta in enumerate(self._betas):
            total_mse += compute_ode_mse(
                beta,
                params,
                self._exp_temperature,
                self._all_exp_masses[i],
                self._src_indices,
                self._tgt_indices,
                self._num_species,
                self._num_reactions,
                self._solver_method,
                self._solver_rtol,
                self._solver_atol,
            )
        return [total_mse]

    def get_bounds(self):
        return (self._lb, self._ub)

    def get_name(self):
        return "Model-Based ODE Kinetics (A->B->C->D)"

    def get_extra_info(self):
        return f"Reactions: {self._num_reactions}, Betas: {self._betas}, Solver: {self._solver_method}"
