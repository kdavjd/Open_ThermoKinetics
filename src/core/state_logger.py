"""
State Logger - Enhanced comprehensive state logger with detailed error analysis
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.core.logger_config import LoggerManager


@dataclass
class LogEvent:
    """Individual log event for aggregation."""

    timestamp: float
    level: str
    module: str
    operation: str
    status: Optional[str] = None
    content_type: Optional[str] = None
    error_details: Optional[str] = None  # Added for detailed error information
    context: Optional[Dict[str, Any]] = None  # Added for additional context


class LogAggregator:
    """Cascading log aggregation system to reduce verbose rendering logs."""

    def __init__(self, aggregation_window: float = 1.0):
        """
        Initialize log aggregator.

        Args:
            aggregation_window: Time window in seconds to group related operations
        """
        self.aggregation_window = aggregation_window
        self.pending_events: deque = deque()
        self.operation_groups: Dict[str, List[LogEvent]] = defaultdict(list)
        self.last_flush = time.time()

    def add_event(
        self,
        module: str,
        operation: str,
        level: str = "DEBUG",
        status: Optional[str] = None,
        content_type: Optional[str] = None,
        error_details: Optional[str] = None,  # Added for detailed error information
        context: Optional[Dict[str, Any]] = None,  # Added for additional context
    ) -> None:
        """
        Add log event for potential aggregation.

        Args:
            module: Source module name
            operation: Operation type (e.g., 'rendering', 'content_update')
            level: Log level
            status: Operation status (success, error, etc.)
            content_type: Content type being processed
            error_details: Detailed error information if applicable
            context: Additional context information for debugging
        """
        event = LogEvent(
            timestamp=time.time(),
            level=level,
            module=module,
            operation=operation,
            status=status,
            content_type=content_type,
            error_details=error_details,
            context=context,
        )

        self.pending_events.append(event)
        self._check_flush()

    def _check_flush(self) -> None:
        """Check if aggregation window has passed and flush if needed."""
        now = time.time()
        if now - self.last_flush >= self.aggregation_window:
            self._flush_aggregated_logs()

    def _flush_aggregated_logs(self) -> None:
        """Flush aggregated logs as summary tables."""
        if not self.pending_events:
            return

        # Group events by operation type
        operation_groups = defaultdict(list)
        while self.pending_events:
            event = self.pending_events.popleft()
            operation_groups[event.operation].append(event)

        # Generate summary for each operation group
        for operation, events in operation_groups.items():
            if len(events) >= 3:  # Only aggregate if 3+ similar events
                self._log_operation_summary(operation, events)
            else:
                # Log individual events if not enough for aggregation                for event in events:
                self._log_individual_event(event)

        self.last_flush = time.time()

    def _log_operation_summary(self, operation: str, events: List[LogEvent]) -> None:
        """Log aggregated summary table for operation with enhanced error details."""
        if operation == "rendering":
            self._log_rendering_summary(events)
        else:
            self._log_generic_operation_summary(operation, events)

    def _log_rendering_summary(self, events: List[LogEvent]) -> None:
        """Log rendering operation summary with detailed error analysis."""
        logger = LoggerManager.get_logger("state_logger")
        content_stats = self._collect_rendering_stats(events)

        # Create compact table for overview
        self._log_rendering_table(logger, events, content_stats)

        # Enhanced error analysis section
        self._log_rendering_errors(logger, content_stats)

    def _collect_rendering_stats(self, events: List[LogEvent]) -> Dict[str, Dict[str, Any]]:
        """Collect statistics for rendering events by content type."""
        content_stats = defaultdict(lambda: {"count": 0, "success": 0, "error": 0, "error_events": []})

        for event in events:
            content_type = event.content_type or "unknown"
            content_stats[content_type]["count"] += 1
            if event.status == "success":
                content_stats[content_type]["success"] += 1
            elif event.status == "error":
                content_stats[content_type]["error"] += 1
                content_stats[content_type]["error_events"].append(event)

        return content_stats

    def _log_rendering_table(self, logger, events: List[LogEvent], content_stats: Dict[str, Dict[str, Any]]) -> None:
        """Log the compact rendering summary table."""
        logger.info(f"📋 Content Rendering Summary ({len(events)} operations):")
        logger.info("┌─────────────┬───────┬─────────┬───────┐")
        logger.info("│ Type        │ Count │ Success │ Error │")
        logger.info("├─────────────┼───────┼─────────┼───────┤")

        for content_type, stats in content_stats.items():
            type_name = content_type[:11].ljust(11)
            count = str(stats["count"]).center(5)
            success = str(stats["success"]).center(7)
            error = str(stats["error"]).center(5)
            logger.info(f"│ {type_name} │ {count} │ {success} │ {error} │")

        logger.info("└─────────────┴───────┴─────────┴───────┘")

    def _log_rendering_errors(self, logger, content_stats: Dict[str, Dict[str, Any]]) -> None:
        """Log detailed error analysis for rendering operations."""
        total_errors = sum(stats["error"] for stats in content_stats.values())
        if total_errors == 0:
            return

        logger.error("")
        logger.error("🔍 DETAILED ERROR ANALYSIS:")
        logger.error("=" * 60)

        for content_type, stats in content_stats.items():
            if stats["error"] > 0:
                self._log_content_type_errors(logger, content_type, stats)

        logger.info("=" * 60)

    def _log_content_type_errors(self, logger, content_type: str, stats: Dict[str, Any]) -> None:
        """Log errors for a specific content type."""
        error_count = stats["error"]
        header = f"❌ {content_type.upper()} RENDERING ERRORS ({error_count} total):"
        logger.error(header)
        logger.error("─" * 50)

        for idx, error_event in enumerate(stats["error_events"], 1):
            self._log_single_error_details(logger, idx, error_event)

        # Provide troubleshooting suggestions
        logger.error(f"   💡 TROUBLESHOOTING SUGGESTIONS for {content_type}:")
        self._log_troubleshooting_suggestions(content_type)
        logger.error("")

    def _log_single_error_details(self, logger, idx: int, error_event: LogEvent) -> None:
        """Log details for a single error event."""
        logger.error(f"   Error #{idx}:")
        timestamp = time.strftime("%H:%M:%S", time.localtime(error_event.timestamp))
        logger.error(f"     • Timestamp: {timestamp}")
        logger.error(f"     • Module: {error_event.module}")
        logger.error(f"     • Content Type: {error_event.content_type}")
        logger.error(f"     • Level: {error_event.level}")
        if error_event.error_details:
            logger.error(f"     • Details: {error_event.error_details}")
        if error_event.context:
            logger.error(f"     • Context: {error_event.context}")
        logger.error("")

    def _log_generic_operation_summary(self, operation: str, events: List[LogEvent]) -> None:
        """Log summary for non-rendering operations."""
        logger = LoggerManager.get_logger("state_logger")
        success_count = sum(1 for e in events if e.status == "success")
        error_count = sum(1 for e in events if e.status == "error")
        error_events = [e for e in events if e.status == "error"]

        logger.info(
            f"{operation.title()} Summary: {len(events)} ops, " f"{success_count} success, {error_count} errors"
        )

        # Show detailed error information for non-rendering operations
        if error_events:
            logger.error(f"❌ DETAILED {operation.upper()} ERRORS:")
            for idx, error_event in enumerate(error_events, 1):
                timestamp = time.strftime("%H:%M:%S", time.localtime(error_event.timestamp))
                logger.error(f"   Error #{idx}: {error_event.module} - {timestamp}")
                if error_event.error_details:
                    logger.error(f"     Details: {error_event.error_details}")

    def _log_troubleshooting_suggestions(self, content_type: str) -> None:
        """Provide specific troubleshooting suggestions based on content type."""
        logger = LoggerManager.get_logger("state_logger")

        suggestions = {
            "heading": [
                "Check if 'level' parameter is specified (1-6)",
                "Verify 'text' field is not empty",
                "Ensure theme styling is properly loaded",
            ],
            "paragraph": [
                "Check if 'text' field exists and is not empty",
                "Verify text encoding (UTF-8 expected)",
                "Check for malformed HTML in text content",
            ],
            "code": [
                "Verify 'code' field is present and valid",
                "Check 'language' parameter for syntax highlighting",
                "Ensure monospace font is available",
            ],
            "image": [
                "Check if image file exists at specified path",
                "Verify image format is supported (PNG, JPG, SVG)",
                "Check file permissions and accessibility",
                "Validate 'src' field is properly formatted",
            ],
            "list": [
                "Verify 'items' array is present and not empty",
                "Check item structure (each item should have 'text')",
                "Validate list type (ordered/unordered)",
            ],
            "interactive": [
                "Check if event handlers are properly connected",
                "Verify PyQt6 widgets are correctly initialized",
                "Ensure required parameters are provided",
            ],
            "workflow": [
                "Validate workflow data structure",
                "Check if all workflow steps are defined",
                "Verify step connections and transitions",
            ],
            "unknown": [
                "Content type not recognized by any renderer",
                "Check if renderer is registered in RendererManager",
                "Verify content structure matches expected format",
            ],
        }

        content_suggestions = suggestions.get(content_type, suggestions["unknown"])
        for suggestion in content_suggestions:
            logger.error(f"     - {suggestion}")

        # Additional generic suggestions
        logger.error("     - Check theme manager initialization")
        logger.error("     - Verify content JSON structure validity")
        logger.error(f"     - Review recent changes to {content_type} renderer")

    def _log_individual_event(self, event: LogEvent) -> None:
        """Log individual event normally."""
        logger = LoggerManager.get_logger(event.module)
        message = f"{event.operation}"
        if event.content_type:
            message += f" of type: {event.content_type}"
            if event.status:
                message += f" - {event.status}"

        getattr(logger, event.level.lower())(message)

    def force_flush(self) -> None:
        """Force flush all pending events immediately."""
        self._flush_aggregated_logs()


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
        # Initialize log aggregator for batch operations
        self.aggregator = LogAggregator(aggregation_window=1.0)

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
        # Use aggregator for rendering operations to reduce verbosity
        if operation in ["rendering", "content_update"]:
            self.aggregator.add_event(
                module=self.component_name,
                operation=operation,
                level="DEBUG",
                status="start",
                content_type=params.get("content_type"),
            )
        else:
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

    def log_rendering_operation(
        self,
        content_type: str,
        success: bool = True,
        error_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log rendering operation for aggregation with enhanced error information.

        Args:
            content_type: Type of content being rendered
            success: Whether rendering was successful
            error_details: Detailed error information if rendering failed
            context: Additional context information for debugging
        """
        status = "success" if success else "error"
        self.aggregator.add_event(
            module=self.component_name,
            operation="rendering",
            level="DEBUG",
            status=status,
            content_type=content_type,
            error_details=error_details if not success else None,
            context=context if not success else None,
        )

    def flush_aggregated_logs(self) -> None:
        """Force flush all aggregated logs."""
        self.aggregator.force_flush()

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
        Get cached state value.

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
