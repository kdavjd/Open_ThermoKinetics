"""
State Logger - Comprehensive state logger with assert functionality for User Guide Framework
"""

import time
from typing import Any, Dict

from src.core.logger_config import LoggerManager


class LogDebouncer:
    """Intelligent log debouncing to prevent cascading identical logs."""

    def __init__(self, window_seconds: int = 5):
        """
        Initialize log debouncer.

        Args:
            window_seconds: Time window for debouncing identical logs
        """
        self.window_seconds = window_seconds
        self.recent_logs = {}

    def should_log(self, message: str, level: str) -> bool:
        """
        Determine if message should be logged based on recent history.

        Args:
            message: Log message
            level: Log level (debug, info, warning, error)

        Returns:
            True if message should be logged, False if debounced
        """
        key = f"{level}:{hash(message)}"
        now = time.time()

        if key in self.recent_logs:
            if now - self.recent_logs[key] < self.window_seconds:
                return False

        self.recent_logs[key] = now
        return True

    def clear_cache(self) -> None:
        """Clear the debouncing cache."""
        self.recent_logs.clear()


class StateLogger:
    """Comprehensive state logger with assert functionality."""

    def __init__(self, component_name: str):
        """
        Initialize state logger.

        Args:
            component_name: Name of the component using this logger
        """
        self.component_name = component_name
        self.logger = LoggerManager.get_logger(f"state.{component_name}")
        self.state_cache = {}
        self.debouncer = LogDebouncer()

    def log_state_change(self, operation: str, before_state: Dict[str, Any], after_state: Dict[str, Any]) -> None:
        """
        Log state changes with comprehensive details.

        Args:
            operation: Name of the operation that caused the state change
            before_state: State before the operation
            after_state: State after the operation
        """
        changes = self._calculate_changes(before_state, after_state)
        message = f"{operation} - State changes: {changes}"

        if self.debouncer.should_log(message, "info"):
            self.logger.info(message)

    def assert_state(self, condition: bool, message: str, **context) -> None:
        """
        Assert with comprehensive state logging.

        Args:
            condition: Condition to assert
            message: Error message if assertion fails
            **context: Additional context for logging

        Raises:
            AssertionError: If condition is False
        """
        if not condition:
            error_msg = f"ASSERTION FAILED: {message} | Context: {context}"
            if self.debouncer.should_log(error_msg, "error"):
                self.logger.error(error_msg)
            raise AssertionError(f"{self.component_name}: {message}")
        else:
            debug_msg = f"ASSERTION PASSED: {message}"
            if self.debouncer.should_log(debug_msg, "debug"):
                self.logger.debug(debug_msg)

    def log_operation_start(self, operation: str, **params) -> None:
        """
        Log the start of an operation.

        Args:
            operation: Operation name
            **params: Operation parameters
        """
        message = f"OPERATION START: {operation} | Params: {params}"
        if self.debouncer.should_log(message, "debug"):
            self.logger.debug(message)

    def log_operation_end(self, operation: str, success: bool = True, **result) -> None:
        """
        Log the end of an operation.

        Args:
            operation: Operation name
            success: Whether operation was successful
            **result: Operation result
        """
        status = "SUCCESS" if success else "FAILURE"
        message = f"OPERATION END: {operation} | Status: {status} | Result: {result}"
        level = "debug" if success else "error"

        if self.debouncer.should_log(message, level):
            getattr(self.logger, level)(message)

    def log_error(self, message: str, **context) -> None:
        """
        Log an error with context.

        Args:
            message: Error message
            **context: Additional context
        """
        full_message = f"ERROR: {message} | Context: {context}"
        if self.debouncer.should_log(full_message, "error"):
            self.logger.error(full_message)

    def log_warning(self, message: str, **context) -> None:
        """
        Log a warning with context.

        Args:
            message: Warning message
            **context: Additional context
        """
        full_message = f"WARNING: {message} | Context: {context}"
        if self.debouncer.should_log(full_message, "warning"):
            self.logger.warning(full_message)

    def _calculate_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate changes between two states.

        Args:
            before: State before change
            after: State after change

        Returns:
            Dictionary of changes
        """
        changes = {}

        # Find changed values
        for key in set(before.keys()) | set(after.keys()):
            before_val = before.get(key)
            after_val = after.get(key)

            if before_val != after_val:
                changes[key] = {"before": before_val, "after": after_val}

        return changes

    def update_cache(self, key: str, value: Any) -> None:
        """
        Update state cache.

        Args:
            key: Cache key
            value: Cache value
        """
        self.state_cache[key] = value

    def get_cached_state(self, key: str, default: Any = None) -> Any:
        """
        Get value from state cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        return self.state_cache.get(key, default)

    def clear_debouncer(self) -> None:
        """Clear the debouncer cache."""
        self.debouncer.clear_cache()
