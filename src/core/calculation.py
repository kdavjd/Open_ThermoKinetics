from multiprocessing import Manager
from typing import Callable, Optional

import numpy as np
import optuna
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from scipy.optimize import OptimizeResult, differential_evolution

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSlots
from src.core.calculation_results_strategies import (
    BestResultStrategy,
    DeconvolutionStrategy,
    ModelBasedCalculationStrategy,
)
from src.core.calculation_scenarios import SCENARIO_REGISTRY, make_de_callback
from src.core.calculation_thread import CalculationThread
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console


class Calculations(BaseSlots):
    """
    Manages calculation execution with threading and result handling strategies.

    Provides threaded optimization calculations for deconvolution and model-based
    analysis using scipy's differential evolution algorithm. Implements strategy
    pattern for result processing and maintains MSE history for optimization tracking.
    """

    new_best_result = pyqtSignal(dict)

    def __init__(self, signals):
        """Initialize calculation manager with strategy instances and threading."""
        super().__init__(actor_name="calculations", signals=signals)
        self.thread: Optional[CalculationThread] = None
        self.best_combination: Optional[tuple] = None
        self.best_mse: float = float("inf")
        self.new_best_result.connect(self.handle_new_best_result)
        self.calc_params = {}
        self.mse_history = []
        self.calculation_active = False

        self.manager = Manager()
        self.stop_event = self.manager.Event()

        self.deconvolution_strategy = DeconvolutionStrategy(self)
        self.model_based_calculation_strategy = ModelBasedCalculationStrategy(self)
        self.result_strategy: Optional[BestResultStrategy] = None

    def set_result_strategy(self, strategy_type: str):
        """Configure result handling strategy for current calculation type."""
        if strategy_type == "deconvolution":
            self.result_strategy = self.deconvolution_strategy
        elif strategy_type == "model_based_calculation":
            self.result_strategy = self.model_based_calculation_strategy
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

    def start_calculation_thread(self, func: Callable, *args, **kwargs) -> None:
        """Start calculation in background thread with result handling."""
        self.stop_event.clear()
        self.calculation_active = True
        self.thread = CalculationThread(func, *args, **kwargs)
        self.thread.result_ready.connect(self._calculation_finished)
        self.thread.start()

    def stop_calculation(self):
        """Stop active calculation thread and reset state."""
        if self.thread and self.thread.isRunning():
            logger.info("Stopping current calculation...")
            self.stop_event.set()
            self.calculation_active = False
            self.result_strategy = None
            self.thread.requestInterruption()
            console.log("\nCalculation thread has been requested to stop. Wait for it to finish.")
            return True
        else:
            logger.info("No active calculation to stop.")
        return False

    @pyqtSlot(dict)
    def process_request(self, params: dict):
        """Handle stop calculation requests from other components."""
        operation = params.get("operation")
        response = params.copy()
        if operation == OperationType.STOP_CALCULATION:
            response["data"] = self.stop_calculation()

        response["target"], response["actor"] = response["actor"], response["target"]
        self.signals.response_signal.emit(response)

    @pyqtSlot(dict)
    def run_calculation_scenario(self, params: dict):
        """
        Execute calculation scenario with parameter validation and error handling.

        Sets up optimization scenario, validates bounds, configures strategy, and
        starts differential evolution with appropriate constraints and callbacks.
        Supports both deconvolution and model-based calculation scenarios.
        """
        self.calc_params = params.copy()
        scenario_key = params.get("calculation_scenario")
        if not scenario_key:
            logger.error("No 'calculation_scenario' provided in params.")
            return

        scenario_cls = SCENARIO_REGISTRY.get(scenario_key)
        if not scenario_cls:
            logger.error(f"Unknown calculation scenario: {scenario_key}")
            return

        scenario_instance = scenario_cls(params, self)
        try:
            bounds = scenario_instance.get_bounds()
            for lb, ub in bounds:
                if ub < lb:
                    console.log("Invalid bounds: upper bound is less than lower bound.")
                    raise ValueError("Invalid bounds: upper bound is less than lower bound.")
            # Pass calculations instance to scenario
            target_function = scenario_instance.get_target_function(calculations_instance=self)
            optimization_method = scenario_instance.get_optimization_method()
            strategy_type = scenario_instance.get_result_strategy_type()

            self.set_result_strategy(strategy_type)

            if optimization_method == "differential_evolution":
                calc_params = params.get("calculation_settings", {}).get("method_parameters", {}).copy()

                if scenario_key == "model_based_calculation":
                    calc_params["constraints"] = scenario_instance.get_constraints()
                    calc_params["callback"] = make_de_callback(target_function, self)

                logger.debug("Differential evolution parameters before execution:")
                for key, value in calc_params.items():
                    logger.debug(f"  {key}: {value} (type: {type(value).__name__})")

                self.start_differential_evolution(bounds=bounds, target_function=target_function, **calc_params)
            else:
                logger.error(f"Unsupported optimization method: {optimization_method}")

        except Exception as e:
            logger.error(f"Error setting up scenario '{scenario_key}': {e}")
            console.log(f"Error setting up scenario '{scenario_key}': {e}")

    def start_differential_evolution(self, bounds, target_function, **kwargs):
        """Initialize and start differential evolution optimization."""
        # Clear MSE history at the start of new calculation
        self.mse_history = []
        self.best_mse = float("inf")
        logger.debug("Starting new differential evolution calculation - cleared MSE history")

        self.start_calculation_thread(
            differential_evolution,
            target_function,
            bounds=bounds,
            **kwargs,
        )

    def start_optuna_optimization(self, bounds, target_function, **kwargs):
        """Initialize and start Optuna optimization with live MSE updates."""
        if optuna is None:
            logger.error("Optuna is not installed. Please install optuna to use this optimization method.")
            console.log("Optuna is not installed. Please install optuna to use this optimization method.")
            return
        self.mse_history = []
        self.best_mse = float("inf")
        logger.debug("Starting new Optuna optimization - cleared MSE history")

        n_trials = kwargs.get("n_trials", 100)
        direction = kwargs.get("direction", "minimize")

        # Получаем актуальные переменные и комбинации для деконволюции
        best_combination = self.calc_params.get("best_combination")
        reaction_variables = self.calc_params.get("reaction_variables")

        def optuna_objective(trial):
            params = []
            for i, (lb, ub) in enumerate(bounds):
                params.append(trial.suggest_float(f"x{i}", lb, ub))
            value = target_function(np.array(params))
            return value

        def optuna_callback(study, trial):
            if study.best_trial == trial:
                best_params = [trial.params[f"x{i}"] for i in range(len(bounds))]
                result = {"best_mse": trial.value, "params": best_params}
                if self.result_strategy == self.deconvolution_strategy:
                    result["best_combination"] = best_combination
                    result["reaction_variables"] = reaction_variables
                self.handle_new_best_result(result)

        def run_study():
            # print("[DIAG] run_study started")
            try:
                study = optuna.create_study(direction=direction)
                study.optimize(optuna_objective, n_trials=n_trials, callbacks=[optuna_callback])
                best_params = [study.best_params[f"x{i}"] for i in range(len(bounds))]
                result = {"best_mse": study.best_value, "params": best_params}
                if self.result_strategy == self.deconvolution_strategy:
                    result["best_combination"] = best_combination
                    result["reaction_variables"] = reaction_variables
                self.handle_new_best_result(result)
                return {"x": best_params, "fun": study.best_value}
            except Exception:
                # print(f"[DIAG] Exception in run_study: {e}")
                raise

        self.start_calculation_thread(run_study)

    @pyqtSlot(object)
    def _calculation_finished(self, result):
        """Handle calculation completion and reset state."""
        try:
            if isinstance(result, Exception):
                if str(result) == "array must not contain infs or NaNs":
                    console.log("\nСalculation was successfully terminated.")
                else:
                    logger.error(f"Calculation error: {result}")
            elif isinstance(result, OptimizeResult):
                x = result.x
                fun = result.fun
                logger.info(f"Calculation completed. Optimal parameters: {x}, fun={fun}")
                console.log(f"Calculation completed. Optimal parameters: {x}, fun={fun}")
                self.best_mse = float("inf")
                self.best_combination = None
            else:
                logger.info("Calculation finished with a non-OptimizeResult object.")
                console.log(f"Calculation result: {result}")
        except Exception as e:
            logger.error(f"Error processing the result: {e}")
            console.log("An error occurred while processing the result. Check logs for details.")

        self.calculation_active = False
        self.result_strategy = None
        self.best_mse = float("inf")
        self.best_combination = None
        # Keep mse_history for display - it will be cleared on next calculation start
        self.handle_request_cycle("main_window", OperationType.CALCULATION_FINISHED)

    @pyqtSlot(dict)
    def handle_new_best_result(self, result: dict):
        """Process new best optimization results using configured strategy."""
        try:
            logger.debug(f"Handling new best result: {result}")
            if self.result_strategy:
                self.result_strategy.handle(result)
            else:
                logger.warning("No strategy set. Best result will not be handled.")
        except Exception as e:
            logger.error(f"Error handling new best result: {e}")
            console.log(f"Error handling new best result: {e}")
