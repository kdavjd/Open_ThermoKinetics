from PyQt6.QtCore import QThread, pyqtSignal

from src.core.logger_config import logger


class CalculationThread(QThread):
    """Thread wrapper for non-blocking calculation execution."""

    result_ready = pyqtSignal(object)

    def __init__(self, calculation_func, *args, **kwargs):
        """Initialize thread with calculation function and parameters."""
        super().__init__()
        self.calculation_func = calculation_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Execute calculation in background thread with error handling."""
        try:
            result = self.calculation_func(*self.args, **self.kwargs)
        except Exception as e:
            logger.error(f"Error during calculation: {e}")
            result = e
        self.result_ready.emit(result)
