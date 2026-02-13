"""Tests for calculation module — calculation orchestration."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.app_settings import OperationType
from src.core.calculation import Calculations


class TestCalculationsInit:
    """Tests for Calculations initialization."""

    def test_calculations_creation(self, mock_signals):
        """Calculations should initialize with correct defaults."""
        calc = Calculations(mock_signals)

        assert calc.actor_name == "calculations"
        assert calc.thread is None
        assert calc.best_mse == float("inf")
        assert calc.best_combination is None
        assert calc.calc_params == {}
        assert calc.mse_history == []
        assert calc.calculation_active is False

    def test_calculations_has_strategies(self, mock_signals):
        """Calculations should have strategy instances."""
        calc = Calculations(mock_signals)

        assert hasattr(calc, "deconvolution_strategy")
        assert hasattr(calc, "model_based_calculation_strategy")
        assert calc.result_strategy is None

    def test_calculations_registers_with_signals(self, mock_signals):
        """Calculations should register with signal dispatcher."""
        Calculations(mock_signals)
        mock_signals.register_component.assert_called_once()


class TestCalculationsStrategy:
    """Tests for strategy management."""

    def test_set_result_strategy_deconvolution(self, mock_signals):
        """set_result_strategy should set deconvolution strategy."""
        calc = Calculations(mock_signals)
        calc.set_result_strategy("deconvolution")

        assert calc.result_strategy == calc.deconvolution_strategy

    def test_set_result_strategy_model_based(self, mock_signals):
        """set_result_strategy should set model_based_calculation strategy."""
        calc = Calculations(mock_signals)
        calc.set_result_strategy("model_based_calculation")

        assert calc.result_strategy == calc.model_based_calculation_strategy

    def test_set_result_strategy_unknown_raises(self, mock_signals):
        """set_result_strategy should raise for unknown strategy type."""
        calc = Calculations(mock_signals)

        with pytest.raises(ValueError, match="Unknown strategy type"):
            calc.set_result_strategy("unknown_strategy")


class TestCalculationsStop:
    """Tests for stopping calculations."""

    def test_stop_calculation_no_active_thread(self, mock_signals):
        """stop_calculation should return False if no thread running."""
        calc = Calculations(mock_signals)
        calc.thread = None

        result = calc.stop_calculation()

        assert result is False

    def test_stop_calculation_active_thread(self, mock_signals):
        """stop_calculation should stop active thread."""
        calc = Calculations(mock_signals)
        calc.thread = MagicMock()
        calc.thread.isRunning.return_value = True
        calc.calculation_active = True

        result = calc.stop_calculation()

        assert result is True
        assert calc.calculation_active is False
        assert calc.result_strategy is None
        calc.thread.requestInterruption.assert_called_once()


class TestCalculationsProcessRequest:
    """Tests for process_request method."""

    def test_process_request_stop_calculation(self, mock_signals):
        """process_request should handle STOP_CALCULATION operation."""
        calc = Calculations(mock_signals)
        calc.thread = MagicMock()
        calc.thread.isRunning.return_value = True

        params = {
            "actor": "test",
            "target": "calculations",
            "operation": OperationType.STOP_CALCULATION,
        }
        calc.process_request(params)

        mock_signals.response_signal.emit.assert_called_once()
        response = mock_signals.response_signal.emit.call_args[0][0]
        assert response["data"] is True
        assert response["target"] == "test"


class TestCalculationsRunScenario:
    """Tests for run_calculation_scenario method."""

    def test_run_scenario_missing_scenario_key(self, mock_signals):
        """run_calculation_scenario should handle missing scenario key."""
        calc = Calculations(mock_signals)
        params = {}  # No calculation_scenario key

        calc.run_calculation_scenario(params)

        # Should not start calculation
        assert calc.thread is None

    def test_run_scenario_unknown_scenario(self, mock_signals):
        """run_calculation_scenario should handle unknown scenario."""
        calc = Calculations(mock_signals)
        params = {"calculation_scenario": "unknown_scenario"}

        calc.run_calculation_scenario(params)

        # Should not start calculation
        assert calc.thread is None

    def test_run_scenario_invalid_bounds(self, mock_signals):
        """run_calculation_scenario should handle invalid bounds."""
        calc = Calculations(mock_signals)
        params = {
            "calculation_scenario": "deconvolution",
            "bounds": [(10.0, 5.0)],  # Invalid: upper < lower
        }

        with patch("src.core.calculation.SCENARIO_REGISTRY") as mock_registry:
            mock_scenario_cls = MagicMock()
            mock_scenario = MagicMock()
            mock_scenario.get_bounds.return_value = [(10.0, 5.0)]  # Invalid bounds
            mock_scenario_cls.return_value = mock_scenario
            mock_registry.get.return_value = mock_scenario_cls

            calc.run_calculation_scenario(params)

            # Should raise ValueError internally and log error
            assert calc.thread is None


class TestCalculationsDifferentialEvolution:
    """Tests for start_differential_evolution method."""

    def test_start_de_clears_mse_history(self, mock_signals):
        """start_differential_evolution should clear MSE history."""
        calc = Calculations(mock_signals)
        calc.mse_history = [0.1, 0.05, 0.02]
        calc.best_mse = 0.02

        # Mock the thread to avoid actual execution
        with patch.object(calc, "start_calculation_thread"):
            calc.start_differential_evolution(
                bounds=[(0, 1), (0, 10)],
                target_function=lambda x: 1.0,
            )

        assert calc.mse_history == []
        assert calc.best_mse == float("inf")


class TestCalculationsHandleNewBestResult:
    """Tests for handle_new_best_result method."""

    def test_handle_new_best_with_strategy(self, mock_signals):
        """handle_new_best_result should delegate to strategy."""
        calc = Calculations(mock_signals)
        mock_strategy = MagicMock()
        calc.result_strategy = mock_strategy

        result = {"best_mse": 0.01, "params": [1.0, 2.0]}
        calc.handle_new_best_result(result)

        mock_strategy.handle.assert_called_once_with(result)

    def test_handle_new_best_without_strategy(self, mock_signals):
        """handle_new_best_result should handle missing strategy gracefully."""
        calc = Calculations(mock_signals)
        calc.result_strategy = None

        result = {"best_mse": 0.01, "params": [1.0, 2.0]}
        # Should not raise
        calc.handle_new_best_result(result)


class TestCalculationsCalculationFinished:
    """Tests for _calculation_finished method."""

    def test_calculation_finished_optimize_result(self, mock_signals):
        """_calculation_finished should handle OptimizeResult."""
        calc = Calculations(mock_signals)

        mock_result = MagicMock()
        mock_result.x = [1.0, 2.0]
        mock_result.fun = 0.01
        # Mock to make isinstance work
        with patch("src.core.calculation.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: obj is mock_result and cls.__name__ == "OptimizeResult"

            calc._calculation_finished(mock_result)

        assert calc.calculation_active is False
        assert calc.result_strategy is None

    def test_calculation_finished_exception(self, mock_signals):
        """_calculation_finished should handle exceptions."""
        calc = Calculations(mock_signals)

        error = ValueError("Test error")
        calc._calculation_finished(error)

        assert calc.calculation_active is False
        assert calc.result_strategy is None

    def test_calculation_finished_resets_state(self, mock_signals):
        """_calculation_finished should reset calculation state."""
        calc = Calculations(mock_signals)
        calc.calculation_active = True
        calc.best_mse = 0.01
        calc.best_combination = (1, 2, 3)

        mock_result = MagicMock()
        mock_result.x = [1.0, 2.0]
        mock_result.fun = 0.005

        with patch("src.core.calculation.isinstance") as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: obj is mock_result and cls.__name__ == "OptimizeResult"
            calc._calculation_finished(mock_result)

        assert calc.best_mse == float("inf")
        assert calc.best_combination is None
        assert calc.calculation_active is False


class TestCalculationsThread:
    """Tests for start_calculation_thread method."""

    def test_start_thread_sets_active(self, mock_signals):
        """start_calculation_thread should set calculation_active."""
        calc = Calculations(mock_signals)

        with patch("src.core.calculation.CalculationThread") as MockThread:
            mock_thread = MagicMock()
            MockThread.return_value = mock_thread

            calc.start_calculation_thread(lambda: None)

            assert calc.calculation_active is True
            mock_thread.start.assert_called_once()

    def test_start_thread_clears_stop_event(self, mock_signals):
        """start_calculation_thread should clear stop_event."""
        calc = Calculations(mock_signals)
        calc.stop_event.set()

        with patch("src.core.calculation.CalculationThread") as MockThread:
            mock_thread = MagicMock()
            MockThread.return_value = mock_thread

            calc.start_calculation_thread(lambda: None)

            assert calc.stop_event.is_set() is False
