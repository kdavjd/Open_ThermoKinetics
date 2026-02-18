import pandas as pd

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger


class ActiveFileOperations(BaseSlots):
    """Provides data transformation functions for experimental preprocessing."""

    def __init__(self, signals):
        super().__init__(actor_name="active_file_operations", signals=signals)

    def process_request(self, params: dict):
        """Process transformation function requests for experimental data."""
        operation = params.get("operation")
        actor = params.get("actor")
        logger.debug(f"{self.actor_name} processing request '{operation}' from '{actor}'")
        response = params.copy()

        if operation == OperationType.TO_DTG:
            response["data"] = self.diff_function

        if operation == OperationType.TO_A_T:
            response["data"] = self.to_a_t_function

        else:
            logger.warning(f"{self.actor_name} received unknown operation '{operation}'")

        response["target"], response["actor"] = response["actor"], response["target"]
        self.signals.response_signal.emit(response)

    def diff_function(self, series: pd.Series):
        """Calculate derivative for DTG analysis."""
        return series.diff()

    def to_a_t_function(self, series: pd.Series) -> pd.Series:
        """Convert mass loss data to conversion α(t) with validation."""
        if series.empty:
            logger.warning("Series is empty.")
            return series

        m0 = series.iloc[0]
        mf = series.iloc[-1]
        if m0 == mf:
            logger.warning("m₀ and m_f are equal, returning a zero series to avoid division by zero.")
            return pd.Series(0, index=series.index)
        else:
            return (m0 - series) / (m0 - mf)
