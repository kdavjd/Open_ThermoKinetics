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

import threading
from functools import wraps
from multiprocessing import Manager

import numpy as np
from scipy.constants import R
from scipy.integrate import solve_ivp

from src.core.app_settings import NUC_MODELS_TABLE, PARAMETER_BOUNDS
from src.core.logger_config import logger


class TimeoutError(Exception):  # noqa: A001
    """Custom timeout exception for integration functions."""

    pass


def integration_timeout(timeout_ms):
    """
    Decorator to limit execution time of integration functions.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]  # Use list to allow modification in nested function

            def target():
                result[0] = func(*args, **kwargs)

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout_ms / 1000.0)  # Convert ms to seconds

            if thread.is_alive():
                raise TimeoutError(f"Integration timeout after {timeout_ms}ms")

            return result[0]

        return wrapper

    return decorator


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


def constraint_fun(X, chains, num_reactions):
    """Compute constraint values for chain contributions."""
    contributions = X[3 * num_reactions : 4 * num_reactions]
    return np.array([np.sum(contributions[chain]) - 1.0 for chain in chains])


def ode_function(T, y, beta, params, species_list, reactions, num_species, num_reactions, R):
    """ODE system for reaction kinetics."""
    dYdt = np.zeros_like(y)
    for i in range(num_reactions):
        src = reactions[i]["from"]
        tgt = reactions[i]["to"]
        src_index = species_list.index(src)
        tgt_index = species_list.index(tgt)
        e_value = y[src_index]
        model_param_index = 2 * num_reactions + i
        model_index = int(np.clip(round(params[model_param_index]), 0, len(reactions[i]["allowed_models"]) - 1))
        reaction_type = reactions[i]["allowed_models"][model_index]
        model = NUC_MODELS_TABLE.get(reaction_type)
        f_e = model["differential_form"](e_value) if model else e_value
        logA = params[i]
        Ea = params[num_reactions + i]
        k_i = (10**logA * np.exp(-Ea * 1000 / (R * T))) / beta
        rate = k_i * f_e
        dYdt[src_index] -= rate
        dYdt[tgt_index] += rate
        dYdt[num_species + i] = rate
    return dYdt


@integration_timeout(50.0)
def integrate_ode_for_beta(
    beta, contributions, params, species_list, reactions, num_species, num_reactions, exp_temperature, exp_mass, R
):
    """Integrate ODE for a single heating rate beta."""
    y0 = np.zeros(num_species + num_reactions)
    if num_species > 0:
        y0[0] = 1.0

    def ode_wrapper(T, y):
        return ode_function(T, y, beta, params, species_list, reactions, num_species, num_reactions, R)

    sol = solve_ivp(ode_wrapper, [exp_temperature[0], exp_temperature[-1]], y0, t_eval=exp_temperature, method="BDF")
    if not sol.success:
        return 1e4
    rates_int = sol.y[num_species : num_species + num_reactions, :]
    M0 = exp_mass[0]
    Mfin = exp_mass[-1]
    int_sum = np.sum(contributions[:, np.newaxis] * rates_int, axis=0)

    # Physical constraint: prevent negative mass by clamping int_sum to [0, 1]
    int_sum_clamped = np.clip(int_sum, 0.0, 1.0)

    model_mass = M0 - (M0 - Mfin) * int_sum_clamped

    # Sanity check: ensure mass is always non-negative and within physical bounds
    model_mass = np.clip(model_mass, Mfin, M0)

    mse_i = np.mean((model_mass - exp_mass) ** 2)
    return mse_i


def model_based_objective_function(
    params, species_list, reactions, num_species, num_reactions, betas, all_exp_masses, exp_temperature, R, stop_event
):
    """Objective function for model-based optimization."""
    total_mse = 0.0
    contributions = params[3 * num_reactions : 4 * num_reactions]
    for beta, exp_mass in zip(betas, all_exp_masses):
        if stop_event.is_set():
            return float("inf")

        try:
            mse_i = integrate_ode_for_beta(
                beta,
                contributions,
                params,
                species_list,
                reactions,
                num_species,
                num_reactions,
                exp_temperature,
                exp_mass,
                R,
            )
            total_mse += mse_i
        except TimeoutError:
            return 1e4
    return total_mse


class ModelBasedTargetFunction:
    """Callable target function for model-based optimization with shared state."""

    def __init__(
        self,
        species_list,
        reactions,
        num_species,
        num_reactions,
        betas,
        all_exp_masses,
        exp_temperature,
        best_mse,
        best_params,
        lock,
        stop_event,
    ):
        self.species_list = species_list
        self.reactions = reactions
        self.num_species = num_species
        self.num_reactions = num_reactions
        self.betas = betas
        self.all_exp_masses = all_exp_masses
        self.exp_temperature = exp_temperature
        self.best_mse = best_mse
        self.best_params = best_params
        self.lock = lock
        self.R = R
        self.stop_event = stop_event

    def __call__(self, params: np.ndarray) -> float:
        if self.stop_event.is_set():
            return float("inf")
        try:
            total_mse = model_based_objective_function(
                params,
                self.species_list,
                self.reactions,
                self.num_species,
                self.num_reactions,
                self.betas,
                self.all_exp_masses,
                self.exp_temperature,
                self.R,
                self.stop_event,
            )
            with self.lock:
                if total_mse < self.best_mse.value:
                    self.best_mse.value = total_mse
                    del self.best_params[:]
                    self.best_params.extend(params.tolist())
            return total_mse
        except Exception as e:
            logger.error(f"Error in ModelBasedTargetFunction: {e}")
            raise


def make_de_callback(target_obj, calculations_instance):
    """Create callback for differential evolution optimization."""

    def callback(x, convergence):
        if calculations_instance.stop_event.is_set():
            return True
        best_mse = target_obj.best_mse.value
        best_params = list(target_obj.best_params)
        calculations_instance.new_best_result.emit(
            {
                "best_mse": best_mse,
                "params": best_params,
            }
        )
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

        manager = Manager()
        best_mse = manager.Value("d", np.inf)
        best_params = manager.list()
        lock = manager.Lock()

        return ModelBasedTargetFunction(
            species_list,
            reactions,
            num_species,
            num_reactions,
            betas,
            all_exp_masses,
            exp_temperature,
            best_mse,
            best_params,
            lock,
            stop_event=self.calculations.stop_event,
        )
