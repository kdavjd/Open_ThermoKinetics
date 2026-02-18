"""
Model-based calculation module for kinetic analysis.

Contains ODE-based optimization components for multi-step reaction schemes.
Extracted from calculation_scenarios.py for better maintainability.

================================================================================
                            MATHEMATICAL FOUNDATION
================================================================================

The model-based method is founded on solving a system of ordinary differential
equations (ODE) describing the kinetics of multi-step solid-state reactions.

CONCENTRATION VS. CONVERSION
-------------------------------

This module uses concentration e (extent of reactant) rather than conversion α:

    e = 1 - α    (concentration decreases from 1 to 0 during reaction)
    α = 1 - e    (conversion increases from 0 to 1 during reaction)

All kinetic models in NUC_MODELS_TABLE are defined in terms of e.

FUNDAMENTAL KINETIC EQUATION
-------------------------------

The reaction rate is described by the Arrhenius-type equation:

    -de/dt = A · exp(-Ea / (R · T)) · f(e)

or equivalently:

    dα/dt = A · exp(-Ea / (R · T)) · f(e)

where:
    e  — concentration (fraction of unreacted material), [1 → 0]
    α  — degree of conversion (fraction reacted), α = 1 - e, [0 → 1]
    t  — time, s
    T  — absolute temperature, K
    A  — pre-exponential factor, s⁻¹
    Ea — activation energy, kJ/mol
    R  — universal gas constant = 8.314 J/(mol·K)
    f(e) — reaction model (differential form, function of concentration)

HEATING RATE CONSIDERATION
-----------------------------

For non-isothermal conditions (linear heating T = T₀ + β·t):

    dT/dt = β  (β — heating rate, K/min)

Transforming to temperature derivative:

    -de/dT = (A / β) · exp(-Ea / (R · T)) · f(e)

In the code, logA = log₁₀(A) is used, and Ea is in kJ/mol:

    k(T) = 10^logA · exp(-Ea·1000 / (R·T)) / β

IMPORTANT: β in °C/min equals β in K/min numerically!
Since ΔT(K) = ΔT(°C) (Kelvin and Celsius scales have the same increment size),
the numerical value of heating rate is identical regardless of temperature unit.
User inputs β in °C/min, which is used directly without conversion.

See `ode_function()` lines 94-115.

ODE SYSTEM FOR MULTI-STEP REACTIONS
--------------------------------------

For a reaction scheme with N species and M reactions:

    Species:    C₁, C₂, ..., C_N
    Reactions:  C_i → C_j  (with parameters A_m, Ea_m, model_m)

ODE system for species concentrations Y_k and reaction rates r_m:

    dY_k/dT = -Σ r_m (for reactants) + Σ r_m (for products)
    dr_m/dT = rate_m

where rate_m is computed as:

    rate_m = k_m(T) · f_m(e_source) · contribution_m

and e_source = Y[source_index] is the concentration of the reactant species.

See `ode_function()` — the core ODE integration kernel.

KINETIC MODELS f(e)
----------------------

Supported models from NUC_MODELS_TABLE (app_settings.py), defined for e ∈ [0,1]:

    | Category    | Models        | f(e)                           |
    |-------------|---------------|--------------------------------|
    | F (n-order) | F1/3, F2, F3  | eⁿ  (e.g., F2: f(e) = e²)      |
    | A (Avrami)  | A2, A3, A4    | n·e·[-ln(e)]^(1-1/n)           |
    | R (Contr.)  | R2, R3        | n·e^(1-1/n)                    |
    | D (Diffus.) | D1-D8         | Various diffusion laws         |
    | P (Power)   | P2, P3, P4    | e^(1-1/n)                      |

Note: In conventional notation these models are often expressed as f(α),
but in this implementation they take concentration e = 1 - α as argument.

The model for each reaction is selected from the allowed_models list.

OPTIMIZATION PARAMETER VECTOR
--------------------------------

For a scheme with M reactions, the params vector has the structure:

    params = [logA₁, ..., logA_M,           # 0 : M-1
              Ea₁, ..., Ea_M,               # M : 2M-1
              model_idx₁, ..., model_idx_M, # 2M : 3M-1
              contrib₁, ..., contrib_M]     # 3M : 4M-1

    • logA_i     — log₁₀ of pre-exponential factor for reaction i
    • Ea_i       — activation energy for reaction i (kJ/mol)
    • model_idx_i — model index from allowed_models for reaction i
    • contrib_i  — contribution of reaction i to the cumulative curve

See `get_core_params_format_info()` lines 255-260.

CONSTRAINTS
--------------

For schemes with parallel reaction chains, the following constraint applies:

    Σ contrib_i = 1  (for each independent chain)

This ensures physical correctness: the total degree of conversion does not
exceed 1. Chains are extracted via `extract_chains()`.

See `constraint_fun()` lines 88-91.

OBJECTIVE FUNCTION
---------------------

Mean squared error (MSE) is minimized between experimental and model data
for all heating rates β:

    MSE_total = Σ MSE_β

where for each β:

    MSE_β = mean((M_exp - M_model)²)

Model mass is computed from integrated reaction rates (cumulative conversion):

    α_cum(T) = Σ contrib_m · ∫rate_m(T')dT'   (integrated from T_start to T)
    M_model(T) = M₀ - (M₀ - M_fin) · α_cum(T)

The ODE solver tracks reaction rates in y[num_species:num_species+num_reactions],
which are integrated to obtain cumulative conversion.

See `model_based_objective_function()` lines 150-176.


ODE INTEGRATION
-------------------

For each β, an initial value problem is solved using BDF (Backward
Differentiation Formula) method:

    solve_ivp(ode_wrapper, [T_start, T_end], y₀, method="BDF")

BDF is preferred over explicit methods (RK45) for stiff ODE systems, which
commonly arise in chemical kinetics when reactions have vastly different
rate constants (large activation energies).

with a 50 ms timeout via the `@integration_timeout` decorator.

Initial conditions: y₀ = [1, 0, ..., 0] (first species has e=1, others e=0)

See `integrate_ode_for_beta()` lines 118-147.

================================================================================
"""

import time

import numpy as np
from scipy.integrate import solve_ivp

from src.core.app_settings import PARAMETER_BOUNDS
from src.core.kinetic_models_numba import ode_function_numba
from src.core.logger_config import logger


class _IntegrationTimeout(Exception):
    """Raised when ODE integration exceeds the deadline timeout.

    This exception is used internally by compute_ode_mse() to implement
    inline deadline-based timeout without threading overhead (~0ms vs ~50ms).
    """

    pass


def extract_chains(scheme: dict) -> list:
    """Extract reaction chains from reaction scheme."""
    components = [comp["id"] for comp in scheme["components"]]
    outgoing = {node: [] for node in components}
    incoming = {node: [] for node in components}

    for idx, reaction in enumerate(scheme["reactions"]):
        src = reaction["from"]
        dst = reaction["to"]
        outgoing[src].append((idx, dst))
        incoming[dst].append((idx, src))

    start_nodes = [node for node in components if len(incoming[node]) == 0]
    end_nodes = [node for node in components if len(outgoing[node]) == 0]

    chains = []

    def dfs(current_node, current_chain, visited):
        if current_node in visited:
            return
        visited.add(current_node)
        if current_node in end_nodes:
            chains.append(current_chain.copy())
        for edge_idx, next_node in outgoing[current_node]:
            current_chain.append(edge_idx)
            dfs(next_node, current_chain, visited)
            current_chain.pop()
        visited.remove(current_node)

    for start in start_nodes:
        dfs(start, [], set())

    return chains


def make_de_callback(objective, calculations_instance, manager):
    """Create callback for differential_evolution with SciPyObjective.

    This callback receives the current best solution vector after each iteration
    and emits results to GUI when improvement is found.

    Parameters
    ----------
    objective : SciPyObjective
        The objective function for evaluating candidates.
    calculations_instance : Calculations
        Calculations instance for stop_event and signal emission.
    manager : multiprocessing.Manager
        Manager for shared state (best_mse, best_params).

    Returns
    -------
    callable
        Callback function for differential_evolution.
    """
    best_mse = manager.Value("d", float("inf"))
    best_params = manager.list()

    def callback(xk, convergence):
        """Callback called after each DE iteration.

        Parameters
        ----------
        xk : np.ndarray
            Current best solution vector (shape: n_params,).
        convergence : float
            Current convergence metric.
        """
        if calculations_instance.stop_event.is_set():
            return True

        try:
            # Evaluate the current best solution
            current_best_mse = float(objective(xk))
            current_best_params = list(xk)

            # Update shared state if improved
            if current_best_mse < best_mse.value:
                best_mse.value = current_best_mse
                best_params[:] = current_best_params

                # Emit signal to GUI
                calculations_instance.new_best_result.emit(
                    {
                        "best_mse": current_best_mse,
                        "params": current_best_params,
                    }
                )
        except Exception as e:
            logger.error(f"Error in DE callback: {e}")

        return False

    return callback


def get_core_params_format_info() -> dict:
    """Return information about expected parameter format for core functions."""
    return {
        "params_order": ["logA", "Ea", "model_indices", "contributions"],
        "expected_length_per_reaction": 4,
    }


class ModelBasedScenario:
    """Scenario for model-based ODE optimization."""

    def __init__(self, params, calculations):
        self.params = params
        self.calculations = calculations

    def get_result_strategy_type(self) -> str:
        return "model_based_calculation"

    def get_optimization_method(self) -> str:
        return self.params.get("calculation_settings", {}).get("method", "differential_evolution")

    def get_bounds(self) -> list[tuple]:
        scheme = self.params.get("reaction_scheme")
        if not scheme:
            raise ValueError("No 'reaction_scheme' provided for ModelBasedScenario.")
        reactions = scheme.get("reactions")
        if not reactions:
            raise ValueError("No 'reactions' in reaction_scheme.")

        bounds = []
        bounds_config = PARAMETER_BOUNDS.model_based
        for reaction in reactions:
            logA_min = reaction.get("log_A_min", bounds_config.scenario_log_a_min)
            logA_max = reaction.get("log_A_max", bounds_config.scenario_log_a_max)
            bounds.append((logA_min, logA_max))

        for reaction in reactions:
            Ea_min = reaction.get("Ea_min", bounds_config.ea_min)
            Ea_max = reaction.get("Ea_max", bounds_config.ea_max)
            bounds.append((Ea_min, Ea_max))

        for reaction in reactions:
            num_models = len(reaction["allowed_models"])
            bounds.append((0, num_models - 1))

        for reaction in reactions:
            contrib_min = reaction.get("contribution_min", bounds_config.scenario_contribution_min)
            contrib_max = reaction.get("contribution_max", bounds_config.scenario_contribution_max)
            bounds.append((contrib_min, contrib_max))
        return bounds

    def get_constraints(self) -> list:
        from scipy.optimize import NonlinearConstraint

        try:
            scheme = self.params.get("reaction_scheme")
            chains = extract_chains(scheme)
            num_reactions = len(scheme["reactions"])

            if len(chains) == 0:
                raise ValueError("No valid reaction chains found.")

            def constraint_function(X):
                contributions = X[3 * num_reactions : 4 * num_reactions]
                return np.array([np.sum(contributions[chain]) - 1.0 for chain in chains])

            return [NonlinearConstraint(constraint_function, [0.0] * len(chains), [0.0] * len(chains))]

        except Exception as e:
            logger.error(f"Error in get_constraints: {e}")
            return []

    def get_target_function(self, **kwargs) -> callable:
        """Create optimized objective function using SciPyObjective.

        Returns SciPyObjective for parallel optimization with workers=-1,
        using Numba-JIT compiled ODE integration for ~50-200x speedup.

        Solver parameters are extracted from calculation_settings:
            - solver_method: ODE solver (default: "LSODA")
            - solver_rtol: Relative tolerance (default: 1e-2)
            - solver_atol: Absolute tolerance (default: 1e-4)
            - timeout_ms: ODE timeout per call in ms (default: 200.0)
        """
        scheme = self.params.get("reaction_scheme")
        reactions = scheme.get("reactions")
        components = scheme.get("components")
        species_list = [comp["id"] for comp in components]
        num_species = len(species_list)
        num_reactions = len(reactions)

        experimental_data = self.params.get("experimental_data")
        if experimental_data is None:
            raise ValueError("No 'experimental_data' provided for ModelBasedScenario.")

        exp_temperature = experimental_data["temperature"].to_numpy() + 273.15

        betas = [float(col) for col in experimental_data.columns if col.lower() != "temperature"]

        all_exp_masses = []
        for beta in betas:
            col_name = str(beta)
            if col_name not in experimental_data.columns:
                col_name = str(int(beta))
            if col_name not in experimental_data.columns:
                raise ValueError(f"Experimental data does not contain column for beta value {beta}")
            exp_mass = experimental_data[col_name].to_numpy()
            all_exp_masses.append(exp_mass)

        # Extract solver parameters from calculation_settings
        calc_settings = self.params.get("calculation_settings", {})
        solver_method = calc_settings.get("solver_method", "LSODA")
        solver_rtol = float(calc_settings.get("solver_rtol", 1e-2))
        solver_atol = float(calc_settings.get("solver_atol", 1e-4))
        timeout_ms = float(calc_settings.get("timeout_ms", 200.0))

        # Convert reaction scheme to src_indices and tgt_indices arrays
        src_indices = np.array([species_list.index(reactions[i]["from"]) for i in range(num_reactions)], dtype=np.int64)
        tgt_indices = np.array([species_list.index(reactions[i]["to"]) for i in range(num_reactions)], dtype=np.int64)

        return SciPyObjective(
            betas=betas,
            exp_temperature=exp_temperature,
            all_exp_masses=all_exp_masses,
            src_indices=src_indices,
            tgt_indices=tgt_indices,
            num_species=num_species,
            num_reactions=num_reactions,
            solver_method=solver_method,
            solver_rtol=solver_rtol,
            solver_atol=solver_atol,
            timeout_ms=timeout_ms,
        )


# ===========================================================================
#  Optimized ODE Integration with Deadline Timeout
# ===========================================================================


def compute_ode_mse(
    beta: float,
    params: np.ndarray,
    src_indices: np.ndarray,
    tgt_indices: np.ndarray,
    num_species: int,
    num_reactions: int,
    exp_temperature: np.ndarray,
    exp_mass: np.ndarray,
    contributions: np.ndarray,
    solver_method: str = "LSODA",
    solver_rtol: float = 1e-2,
    solver_atol: float = 1e-4,
    timeout_ms: float = 200.0,
) -> float:
    """Compute MSE between experimental and model mass with deadline-based timeout.

    This function integrates the ODE system using the Numba-jitted ode_function_numba
    and computes the mean squared error between model predictions and experimental data.
    It implements an inline deadline-based timeout (~0ms overhead) instead of threading
    (~50ms overhead per call).

    Parameters
    ----------
    beta : float
        Heating rate (K/min). Must be > 0.
    params : np.ndarray
        Parameter vector of length 4*M (logA, Ea, model_idx, contribution for each reaction).
    src_indices : np.ndarray (int64)
        Source species index for each reaction (length M).
    tgt_indices : np.ndarray (int64)
        Target species index for each reaction (length M).
    num_species : int
        Number of species in the reaction scheme.
    num_reactions : int
        Number of reactions in the reaction scheme.
    exp_temperature : np.ndarray
        Experimental temperature values (K).
    exp_mass : np.ndarray
        Experimental mass values (normalized 0-1 or original scale).
    contributions : np.ndarray
        Contribution weights for each reaction (length M).
    solver_method : str, default "LSODA"
        ODE solver method for solve_ivp ("LSODA", "BDF", "RK45", etc.).
    solver_rtol : float, default 1e-2
        Relative tolerance for ODE solver.
    solver_atol : float, default 1e-4
        Absolute tolerance for ODE solver.
    timeout_ms : float, default 200.0
        Timeout in milliseconds for ODE integration.

    Returns
    -------
    float
        MSE value if integration succeeds, or 1e4 if timeout or solver failure.
    """
    deadline = time.perf_counter() + timeout_ms / 1000.0

    # Initial condition: first species has e=1, others e=0
    y0 = np.zeros(num_species + num_reactions)
    if num_species > 0:
        y0[0] = 1.0

    def ode_wrapper(T: float, y: np.ndarray) -> np.ndarray:
        """ODE wrapper with deadline check for inline timeout."""
        if time.perf_counter() > deadline:
            raise _IntegrationTimeout(f"ODE integration exceeded {timeout_ms}ms deadline")
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

        if not sol.success:
            return 1e4

        # Extract integrated rates and compute model mass
        rates_int = sol.y[num_species : num_species + num_reactions, :]

        M0 = exp_mass[0]
        Mfin = exp_mass[-1]

        # Weighted sum of integrated rates by contributions
        int_sum = np.sum(contributions[:, np.newaxis] * rates_int, axis=0)

        # Physical constraint: clamp cumulative conversion to [0, 1]
        int_sum_clamped = np.clip(int_sum, 0.0, 1.0)

        # Model mass: M(T) = M0 - (M0 - M_fin) * alpha_cum(T)
        model_mass = M0 - (M0 - Mfin) * int_sum_clamped

        # Sanity check: ensure mass is within physical bounds
        model_mass = np.clip(model_mass, min(Mfin, M0), max(Mfin, M0))

        # Compute MSE
        mse = float(np.mean((model_mass - exp_mass) ** 2))
        return mse

    except _IntegrationTimeout:
        return 1e4


# ===========================================================================
#  SciPyObjective — Picklable callable for parallel optimization
# ===========================================================================


class SciPyObjective:
    """Picklable objective function for scipy.optimize.differential_evolution.

    This class is designed to work with `workers=-1` in differential_evolution,
    which requires the objective to be picklable for multiprocessing.

    All attributes are picklable types:
    - numpy arrays (contiguous, C-order)
    - Python lists and primitives

    The class uses compute_ode_mse() internally for ~50-200x speedup compared
    to the old threading-based approach.

    Parameters
    ----------
    betas : list[float] | np.ndarray
        Heating rates for each experimental curve.
    exp_temperature : np.ndarray
        Temperature values (K), shared across all heating rates.
    all_exp_masses : list[np.ndarray]
        Experimental mass values for each heating rate.
    src_indices : np.ndarray (int64)
        Source species index for each reaction.
    tgt_indices : np.ndarray (int64)
        Target species index for each reaction.
    num_species : int
        Number of species in the reaction scheme.
    num_reactions : int
        Number of reactions in the reaction scheme.
    solver_method : str, default "LSODA"
        ODE solver method.
    solver_rtol : float, default 1e-2
        Relative tolerance for ODE solver.
    solver_atol : float, default 1e-4
        Absolute tolerance for ODE solver.
    timeout_ms : float, default 200.0
        Timeout per ODE integration in milliseconds.

    Example
    -------
    >>> objective = SciPyObjective(
    ...     betas=[5.0, 10.0, 20.0],
    ...     exp_temperature=T_exp,
    ...     all_exp_masses=[M_5, M_10, M_20],
    ...     src_indices=np.array([0], dtype=np.int64),
    ...     tgt_indices=np.array([1], dtype=np.int64),
    ...     num_species=2,
    ...     num_reactions=1,
    ... )
    >>> mse = objective(params_vector)
    >>> # For parallel optimization:
    >>> from scipy.optimize import differential_evolution
    >>> result = differential_evolution(objective, bounds, workers=-1, updating='deferred')
    """

    def __init__(
        self,
        betas: list[float] | np.ndarray,
        exp_temperature: np.ndarray,
        all_exp_masses: list[np.ndarray],
        src_indices: np.ndarray,
        tgt_indices: np.ndarray,
        num_species: int,
        num_reactions: int,
        solver_method: str = "LSODA",
        solver_rtol: float = 1e-2,
        solver_atol: float = 1e-4,
        timeout_ms: float = 200.0,
    ):
        # Store as picklable types (numpy arrays, lists, primitives)
        self._betas: list[float] = list(betas) if not isinstance(betas, list) else betas
        self._exp_temperature: np.ndarray = np.ascontiguousarray(exp_temperature, dtype=np.float64)
        self._all_exp_masses: list[np.ndarray] = [np.ascontiguousarray(m, dtype=np.float64) for m in all_exp_masses]
        self._src_indices: np.ndarray = np.ascontiguousarray(src_indices, dtype=np.int64)
        self._tgt_indices: np.ndarray = np.ascontiguousarray(tgt_indices, dtype=np.int64)
        self._num_species: int = int(num_species)
        self._num_reactions: int = int(num_reactions)
        self._solver_method: str = str(solver_method)
        self._solver_rtol: float = float(solver_rtol)
        self._solver_atol: float = float(solver_atol)
        self._timeout_ms: float = float(timeout_ms)

    def __call__(self, x: np.ndarray) -> float:
        """Compute total MSE across all heating rates.

        Parameters
        ----------
        x : np.ndarray
            Parameter vector of length 4*M:
            - x[0:M] = logA (log10 pre-exponential factor)
            - x[M:2M] = Ea (activation energy, kJ/mol)
            - x[2M:3M] = model_idx (kinetic model index, will be rounded to int)
            - x[3M:4M] = contribution (reaction contribution, 0-1)

        Returns
        -------
        float
            Sum of MSE values across all heating rates. Returns 1e4 per failed
            heating rate (timeout or solver failure).
        """
        # Ensure params is contiguous float64 array
        params = np.ascontiguousarray(x, dtype=np.float64)

        # Round model indices to nearest integer (indices are in x[2M:3M])
        M = self._num_reactions
        for i in range(M):
            idx = 2 * M + i
            params[idx] = round(params[idx])

        # Extract contributions
        contributions = np.ascontiguousarray(params[3 * M : 4 * M], dtype=np.float64)

        # Sum MSE across all heating rates
        total_mse = 0.0
        for beta, exp_mass in zip(self._betas, self._all_exp_masses):
            mse = compute_ode_mse(
                beta=beta,
                params=params,
                src_indices=self._src_indices,
                tgt_indices=self._tgt_indices,
                num_species=self._num_species,
                num_reactions=self._num_reactions,
                exp_temperature=self._exp_temperature,
                exp_mass=exp_mass,
                contributions=contributions,
                solver_method=self._solver_method,
                solver_rtol=self._solver_rtol,
                solver_atol=self._solver_atol,
                timeout_ms=self._timeout_ms,
            )
            total_mse += mse

        return total_mse
