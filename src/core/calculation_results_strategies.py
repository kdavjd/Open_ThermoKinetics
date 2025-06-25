import datetime
from abc import ABC, abstractmethod
from typing import Dict

from src.core.app_settings import OperationType
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class BestResultStrategy(ABC):
    @abstractmethod
    def handle(self, result: Dict):
        pass


class DeconvolutionStrategy(BestResultStrategy):
    def __init__(self, calculation_instance):
        self.calculation = calculation_instance

    def handle(self, result: Dict):  # noqa: C901
        best_mse = result.get("best_mse")
        best_combination = result.get("best_combination")
        params = result.get("params")
        reaction_variables = result.get("reaction_variables")

        params_per_reaction = [len(reaction_variables[key]) for key in reaction_variables.keys()]

        if best_mse < self.calculation.best_mse:
            self.calculation.best_mse = best_mse
            self.calculation.best_combination = best_combination
            self.calculation.mse_history.append((datetime.datetime.now(), best_mse))
            logger.debug(f"Added MSE to history at {datetime.datetime.now().strftime('%H:%M:%S')}: {best_mse}")
            logger.info("A new best MSE has been found.")

            self.calculation.handle_request_cycle(
                "main_window", OperationType.PLOT_MSE_LINE, mse_data=self.calculation.mse_history
            )

            def reaction_param_count(func_type: str) -> int:
                if func_type == "gauss":
                    return 3
                elif func_type == "fraser":
                    return 4
                elif func_type == "ads":
                    return 5
                else:
                    return 3  # Default

            idx = 0
            parameters_yaml = "parameters:\n"
            for i, func_type in enumerate(best_combination):
                count = reaction_param_count(func_type)
                reaction_params = params[idx : idx + params_per_reaction[i]]
                idx += params_per_reaction[i]

                param_dict = {
                    "h": None,
                    "z": None,
                    "w": None,
                    "fr": None,
                    "ads1": None,
                    "ads2": None,
                }

                try:
                    param_dict["h"] = round(float(reaction_params[0]), 4)
                    param_dict["z"] = round(float(reaction_params[1]), 4)
                    param_dict["w"] = round(float(reaction_params[2]), 4)

                    if func_type == "fraser" and count >= 4:
                        param_dict["fr"] = round(float(reaction_params[3]), 4)
                    elif func_type == "ads" and count >= 5:
                        param_dict["ads1"] = round(float(reaction_params[3]), 4)
                        param_dict["ads2"] = round(float(reaction_params[4]), 4)
                except (IndexError, ValueError) as e:
                    logger.error(f"Error parsing parameters for reaction {i}: {e}")
                    continue

                parameters_yaml += f"  r{i}:\n"
                for key, value in param_dict.items():
                    val_str = "null" if value is None else f"{value:.4f}"
                    parameters_yaml += f"    {key}: {val_str}\n"

            console.log("\nNew best result found:")
            console.log(f"\nBest MSE*10e4: {10_000 * best_mse:.7f}")
            console.log(f"\nReaction combination: {best_combination}")
            console.log(parameters_yaml.rstrip())

            file_name = self.calculation.handle_request_cycle("main_window", OperationType.GET_FILE_NAME)
            self.calculation.handle_request_cycle(
                "calculations_data_operations",
                OperationType.UPDATE_REACTIONS_PARAMS,
                path_keys=[file_name],
                best_combination=best_combination,
                reactions_params=params,
            )


class ModelBasedCalculationStrategy(BestResultStrategy):
    def __init__(self, calculation_instance):
        self.calculation = calculation_instance

    def handle(self, result: Dict):  # noqa: C901
        try:
            best_mse = result.get("best_mse") or result.get("mse")
            params = result.get("params") or result.get("parameters")

            # Validate input parameters
            if best_mse is None or params is None:
                logger.error(f"Missing best_mse or params in result. Keys: {list(result.keys())}")
                return

            # Validate calculation parameters structure
            if not hasattr(self.calculation, "calc_params") or self.calculation.calc_params is None:
                logger.error("Missing calc_params in calculation instance")
                return

            calc_params = self.calculation.calc_params
            if "reaction_scheme" not in calc_params or calc_params["reaction_scheme"] is None:
                logger.error("Missing reaction_scheme in calc_params")
                return

            if "reactions" not in calc_params["reaction_scheme"]:
                logger.error("Missing reactions in reaction_scheme")
                return

            reactions = calc_params["reaction_scheme"]["reactions"]
            if not reactions or len(reactions) == 0:
                logger.error("Empty reactions list")
                return

            # Convert dict parameters to list format if needed
            if isinstance(params, dict):
                params = self._convert_dict_params_to_list(params, reactions)
                if params is None:
                    return
            elif not isinstance(params, list):
                logger.error(f"Invalid params type: {type(params)}")
                return

            num_reactions = len(reactions)
            expected_length = 4 * num_reactions  # logA, Ea, model_index, contributions
            if len(params) < expected_length:
                logger.error(f"Insufficient params length: got {len(params)}, expected {expected_length}")
                return

            # Extract parameter arrays
            logA = params[0 * num_reactions : 1 * num_reactions]
            Ea = params[1 * num_reactions : 2 * num_reactions]
            model_index = params[2 * num_reactions : 3 * num_reactions]
            contributions = params[3 * num_reactions : 4 * num_reactions]

            logger.debug(f"Received new result for best_mse: {best_mse} with params: {params}")

            if best_mse < self.calculation.best_mse:
                self._process_new_best_result(best_mse, reactions, logA, Ea, model_index, contributions)

        except Exception as e:
            logger.error(f"Error in ModelBasedCalculationStrategy: {e}")
            console.log(f"Error in ModelBasedCalculationStrategy: {e}")

    def _convert_dict_params_to_list(self, params_dict, reactions):
        """Convert parameters dictionary to list format"""
        try:
            logger.debug(f"Processing parameters dict: {params_dict}")

            num_reactions = len(reactions)
            logA = []
            Ea = []
            contributions = []

            for i, reaction in enumerate(reactions):
                reaction_from = reaction.get("from", "A")
                reaction_to = reaction.get("to", "B")
                reaction_id = f"{reaction_from} -> {reaction_to}"

                if reaction_id in params_dict:
                    reaction_params = params_dict[reaction_id]
                    logA.append(reaction_params.get("log_A", 0))
                    Ea.append(reaction_params.get("Ea", 0))
                    contributions.append(reaction_params.get("contribution", 0))
                else:
                    logger.warning(f"Missing parameters for reaction {reaction_id}")
                    logA.append(0)
                    Ea.append(0)
                    contributions.append(0)

            # For model_index, set to 0 for now (will be determined by optimization)
            model_index = [0] * num_reactions

            # Reconstruct params array in expected format [logA, Ea, model_index, contributions]
            params_list = logA + Ea + model_index + contributions
            logger.debug(f"Converted dict params to list: {len(params_list)} elements")
            return params_list

        except Exception as e:
            logger.error(f"Error converting dict params: {e}")
            return None

    def _process_new_best_result(self, best_mse, reactions, logA, Ea, model_index, contributions):
        """Process new best optimization result"""
        try:
            logger.debug(f"New best MSE found: {best_mse} (previous: {self.calculation.best_mse})")
            self.calculation.best_mse = best_mse
            self.calculation.mse_history.append((datetime.datetime.now(), best_mse))
            logger.debug(f"Added MSE to history at {datetime.datetime.now().strftime('%H:%M:%S')}: {best_mse}")
            logger.info("A new best MSE has been found in model calculation.")

            self.calculation.handle_request_cycle(
                "main_window", OperationType.PLOT_MSE_LINE, mse_data=self.calculation.mse_history
            )

            parameters_yaml = "parameters:\n"

            for i, reaction in enumerate(reactions):
                reaction_desc = f"{reaction.get('from')} -> {reaction.get('to')}"
                try:
                    logA_val = float(logA[i])
                    ea_val = int(Ea[i])
                    mod_idx = int(model_index[i])
                    contribution_val = float(contributions[i])
                except Exception as e:
                    logger.error(f"Error processing reaction {i}: {e}")
                    continue

                allowed_models = reaction.get("allowed_models", [])
                try:
                    model_str = allowed_models[mod_idx]
                except Exception as e:
                    logger.error(f"Error processing model index for reaction {i}: {e}")
                    model_str = "Unknown"

                parameters_yaml += f"{reaction_desc}:\n"
                parameters_yaml += f"    logA: {logA_val:.2f}\n"
                parameters_yaml += f"    Ea: {ea_val}\n"
                parameters_yaml += f"    model: {model_str}\n"
                parameters_yaml += f"    contribution: {contribution_val:.3f}\n"

            console.log("\nNew best result found in model calculation:")
            console.log(f"Best MSE: {best_mse:.4f}")
            console.log(parameters_yaml.rstrip())

            # Send individual best values updates for each reaction
            for i, reaction in enumerate(reactions):
                try:
                    logA_val = float(logA[i])
                    ea_val = float(Ea[i])
                    contribution_val = float(contributions[i])

                    # Send update for this specific reaction
                    self.calculation.handle_request_cycle(
                        "main_window",
                        OperationType.UPDATE_MODEL_BASED_BEST_VALUES,
                        reaction_index=i,
                        Ea=ea_val,
                        logA=logA_val,
                        contribution=contribution_val,
                        mse=best_mse,
                    )

                    logger.debug(
                        f"Sent best values update for reaction {i}: "
                        f"Ea={ea_val}, logA={logA_val:.2f}, contribution={contribution_val:.3f}"
                    )

                except Exception as e:
                    logger.error(f"Error sending best values update for reaction {i}: {e}")

        except Exception as e:
            logger.error(f"Error processing new best result: {e}")
