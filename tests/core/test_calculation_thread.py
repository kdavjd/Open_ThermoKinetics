"""Tests for calculation_thread module."""

from unittest.mock import MagicMock, patch

from src.core.calculation_thread import CalculationThread


class TestCalculationThreadInit:
    """Tests for CalculationThread initialization."""

    def test_creation_with_function(self):
        """CalculationThread should store function and args."""
        mock_func = MagicMock()
        thread = CalculationThread(mock_func, 1, 2, key="value")

        assert thread.calculation_func is mock_func
        assert thread.args == (1, 2)
        assert thread.kwargs == {"key": "value"}

    def test_creation_minimal(self):
        """CalculationThread should work with minimal args."""
        mock_func = MagicMock()
        thread = CalculationThread(mock_func)

        assert thread.calculation_func is mock_func
        assert thread.args == ()
        assert thread.kwargs == {}

    def test_has_result_signal(self):
        """CalculationThread should have result_ready signal."""
        mock_func = MagicMock()
        thread = CalculationThread(mock_func)

        assert hasattr(thread, "result_ready")


class TestCalculationThreadRun:
    """Tests for CalculationThread run method."""

    def test_run_calls_function(self):
        """run should call calculation_func with args and kwargs."""
        mock_func = MagicMock(return_value=42)
        thread = CalculationThread(mock_func, 1, 2, key="value")

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()

        mock_func.assert_called_once_with(1, 2, key="value")

    def test_run_emits_result(self):
        """run should emit result via result_ready signal."""
        mock_func = MagicMock(return_value=42)
        thread = CalculationThread(mock_func)

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()
            mock_signal.emit.assert_called_once_with(42)

    def test_run_handles_exception(self):
        """run should emit exception if function raises."""
        test_error = ValueError("Test error")
        mock_func = MagicMock(side_effect=test_error)
        thread = CalculationThread(mock_func)

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()
            mock_signal.emit.assert_called_once_with(test_error)

    def test_run_handles_runtime_error(self):
        """run should handle RuntimeError."""
        test_error = RuntimeError("Runtime issue")
        mock_func = MagicMock(side_effect=test_error)
        thread = CalculationThread(mock_func)

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()
            mock_signal.emit.assert_called_once_with(test_error)

    def test_run_with_no_args(self):
        """run should work with no args."""
        mock_func = MagicMock(return_value="result")
        thread = CalculationThread(mock_func)

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()
            mock_func.assert_called_once_with()
            mock_signal.emit.assert_called_once_with("result")

    def test_run_with_complex_result(self):
        """run should handle complex result types."""
        complex_result = {"data": [1, 2, 3], "nested": {"key": "value"}}
        mock_func = MagicMock(return_value=complex_result)
        thread = CalculationThread(mock_func)

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()
            mock_signal.emit.assert_called_once_with(complex_result)

    def test_run_with_none_result(self):
        """run should handle None result."""
        mock_func = MagicMock(return_value=None)
        thread = CalculationThread(mock_func)

        with patch.object(thread, "result_ready") as mock_signal:
            mock_signal.emit = MagicMock()
            thread.run()
            mock_signal.emit.assert_called_once_with(None)
