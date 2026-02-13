import threading
from functools import wraps
from multiprocessing import Manager
from typing import Callable, Dict

import numpy as np
from scipy.constants import R
from scipy.integrate import solve_ivp
from scipy.optimize import NonlinearConstraint

from src.core.app_settings import NUC_MODELS_TABLE, PARAMETER_BOUNDS
from src.core.curve_fitting import CurveFitting as cft
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


class BaseCalculationScenario:
    """Base class for defining optimization scenarios."""

    def __init__(self, params: Dict, calculations):
        self.params = params
        self.calculations = calculations

    def get_bounds(self) -> list[tuple]:
        """Return optimization parameter bounds."""
        raise NotImplementedError

    def get_target_function(self, **kwargs) -> Callable:
        """Return objective function for optimization."""
        raise NotImplementedError

    def get_optimization_method(self) -> str:
        """Return optimization algorithm name."""
        return "differential_evolution"

    def get_result_strategy_type(self) -> str:
        """Return result handling strategy type."""
        raise NotImplementedError

    def get_constraints(self) -> list:
        """Return optimization constraints."""
        return []


class DeconvolutionScenario(BaseCalculationScenario):
    """Scenario for peak deconvolution optimization."""

    def get_bounds(self) -> list[tuple]:
        """Return deconvolution parameter bounds."""
        return self.params["bounds"]

    def get_optimization_method(self) -> str:
        """Return deconvolution optimization method."""
        deconv_settings = self.params.get("deconvolution_settings", {})
        return deconv_settings.pop("method", "differential_evolution")

    def get_result_strategy_type(self) -> str:
        return "deconvolution"

    def get_target_function(self, **kwargs) -> Callable:
        reaction_variables = self.params["reaction_variables"]
        reaction_combinations = self.params["reaction_combinations"]
        experimental_data = self.params["experimental_data"]

        def target_function(params_array: np.ndarray) -> float:
            if not self.calculations.calculation_active:
                return float("inf")

            best_mse = float("inf")
            best_combination = None

            for combination in reaction_combinations:
                cumulative_function = np.zeros(len(experimental_data["temperature"]))
                param_idx_local = 0

                for (reaction, coeffs), func in zip(reaction_variables.items(), combination):
                    coeff_count = len(coeffs)
                    func_params = params_array[param_idx_local : param_idx_local + coeff_count]
                    param_idx_local += coeff_count

                    x = experimental_data["temperature"]
                    if len(func_params) < 3:
                        raise ValueError("Not enough parameters for the function.")
                    h, z, w = func_params[0:3]

                    if func == "gauss":
                        reaction_values = cft.gaussian(x, h, z, w)
                    elif func == "fraser":
                        fr = func_params[3]  # fraser_suzuki
                        reaction_values = cft.fraser_suzuki(x, h, z, w, fr)
                    elif func == "ads":
                        ads1 = func_params[3]
                        ads2 = func_params[4]
                        reaction_values = cft.asymmetric_double_sigmoid(x, h, z, w, ads1, ads2)
                    else:
                        logger.warning(f"Unknown function type: {func}")
                        reaction_values = 0

                    cumulative_function += reaction_values

                y_true = experimental_data.iloc[:, 1].to_numpy()
                mse = np.mean((y_true - cumulative_function) ** 2)
                if mse < best_mse:
                    best_mse = mse
                    best_combination = combination
                    self.calculations.new_best_result.emit(
                        {
                            "best_mse": best_mse,
                            "best_combination": best_combination,
                            "params": params_array,
                            "reaction_variables": reaction_variables,
                        }
                    )
            return best_mse

        return target_function


def extract_chains(scheme: dict) -> list:
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
    contributions = X[3 * num_reactions : 4 * num_reactions]
    return np.array([np.sum(contributions[chain]) - 1.0 for chain in chains])


def ode_function(T, y, beta, params, species_list, reactions, num_species, num_reactions, R):
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
    y0 = np.zeros(num_species + num_reactions)
    if num_species > 0:
        y0[0] = 1.0

    def ode_wrapper(T, y):
        return ode_function(T, y, beta, params, species_list, reactions, num_species, num_reactions, R)

    sol = solve_ivp(ode_wrapper, [exp_temperature[0], exp_temperature[-1]], y0, t_eval=exp_temperature, method="RK45")
    if not sol.success:
        return 1e4
    rates_int = sol.y[num_species : num_species + num_reactions, :]
    M0 = exp_mass[0]
    Mfin = exp_mass[-1]
    int_sum = np.sum(contributions[:, np.newaxis] * rates_int, axis=0)

    # Physical constraint: prevent negative mass by clamping int_sum to [0, 1]
    # This ensures model_mass remains between Mfin and M0 as physically required
    int_sum_clamped = np.clip(int_sum, 0.0, 1.0)

    model_mass = M0 - (M0 - Mfin) * int_sum_clamped

    # Sanity check: ensure mass is always non-negative and within physical bounds
    model_mass = np.clip(model_mass, Mfin, M0)

    mse_i = np.mean((model_mass - exp_mass) ** 2)
    return mse_i


def model_based_objective_function(
    params, species_list, reactions, num_species, num_reactions, betas, all_exp_masses, exp_temperature, R, stop_event
):
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


class ModelBasedScenario(BaseCalculationScenario):
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


class ModelBasedTargetFunction:
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


SCENARIO_REGISTRY = {
    "deconvolution": DeconvolutionScenario,
    "model_based_calculation": ModelBasedScenario,
}


def get_core_params_format_info() -> dict:
    """Return information about expected parameter format for core functions."""
    return {
        "params_order": ["logA", "Ea", "model_indices", "contributions"],
        "expected_length_per_reaction": 4,
    }
