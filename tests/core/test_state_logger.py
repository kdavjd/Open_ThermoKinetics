"""Tests for state_logger module."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.state_logger import LogAggregator, LogDebouncer, LogEvent, StateLogger


class TestLogEvent:
    """Tests for LogEvent dataclass."""

    def test_creation_minimal(self):
        """LogEvent should create with minimal required fields."""
        event = LogEvent(timestamp=1.0, level="INFO", module="test", operation="op")

        assert event.timestamp == 1.0
        assert event.level == "INFO"
        assert event.module == "test"
        assert event.operation == "op"
        assert event.status is None
        assert event.content_type is None
        assert event.error_details is None
        assert event.context is None

    def test_creation_full(self):
        """LogEvent should create with all fields."""
        event = LogEvent(
            timestamp=1.0,
            level="ERROR",
            module="test",
            operation="op",
            status="error",
            content_type="image",
            error_details="Failed to load",
            context={"key": "value"},
        )

        assert event.status == "error"
        assert event.content_type == "image"
        assert event.error_details == "Failed to load"
        assert event.context == {"key": "value"}


class TestLogDebouncer:
    """Tests for LogDebouncer."""

    def test_creation(self):
        """LogDebouncer should initialize correctly."""
        debouncer = LogDebouncer()
        assert debouncer.window_seconds == 5
        assert debouncer.recent_logs == {}

    def test_custom_window(self):
        """LogDebouncer should accept custom window."""
        debouncer = LogDebouncer(window_seconds=10)
        assert debouncer.window_seconds == 10

    def test_should_log_first_time(self):
        """should_log should return True for first occurrence."""
        debouncer = LogDebouncer()
        result = debouncer.should_log("test message", "info")
        assert result is True

    def test_should_log_duplicate_within_window(self):
        """should_log should return False for duplicate within window."""
        debouncer = LogDebouncer(window_seconds=10)
        debouncer.should_log("test message", "info")
        result = debouncer.should_log("test message", "info")
        assert result is False

    def test_different_messages_should_log(self):
        """should_log should allow different messages."""
        debouncer = LogDebouncer()
        debouncer.should_log("message 1", "info")
        result = debouncer.should_log("message 2", "info")
        assert result is True

    def test_different_levels_should_log(self):
        """should_log should treat different levels separately."""
        debouncer = LogDebouncer()
        debouncer.should_log("message", "info")
        result = debouncer.should_log("message", "error")
        assert result is True

    def test_clear_cache(self):
        """clear_cache should reset recent_logs."""
        debouncer = LogDebouncer()
        debouncer.should_log("test", "info")
        debouncer.clear_cache()
        assert debouncer.recent_logs == {}


class TestLogAggregator:
    """Tests for LogAggregator."""

    def test_creation(self):
        """LogAggregator should initialize correctly."""
        aggregator = LogAggregator()
        assert aggregator.aggregation_window == 1.0
        assert aggregator.pending_events.maxlen is None

    def test_custom_window(self):
        """LogAggregator should accept custom window."""
        aggregator = LogAggregator(aggregation_window=2.0)
        assert aggregator.aggregation_window == 2.0

    def test_add_event(self):
        """add_event should add event to pending queue."""
        aggregator = LogAggregator()

        with patch.object(aggregator, "_check_flush"):
            aggregator.add_event(module="test", operation="op")

        assert len(aggregator.pending_events) == 1

    def test_add_event_with_all_params(self):
        """add_event should store all parameters."""
        aggregator = LogAggregator()

        with patch.object(aggregator, "_check_flush"):
            aggregator.add_event(
                module="test",
                operation="op",
                level="ERROR",
                status="error",
                content_type="image",
                error_details="Failed",
                context={"key": "value"},
            )

        event = aggregator.pending_events[0]
        assert event.level == "ERROR"
        assert event.status == "error"
        assert event.content_type == "image"
        assert event.error_details == "Failed"

    def test_force_flush(self):
        """force_flush should process pending events."""
        aggregator = LogAggregator()
        aggregator.add_event(module="test", operation="op")

        with patch.object(aggregator, "_flush_aggregated_logs") as mock_flush:
            aggregator.force_flush()
            mock_flush.assert_called_once()


class TestStateLogger:
    """Tests for StateLogger."""

    def test_creation(self):
        """StateLogger should initialize correctly."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test_component")

            assert logger.component_name == "test_component"
            assert logger.state_cache == {}
            assert logger.debouncer is not None
            assert logger.aggregator is not None

    def test_log_state_change(self):
        """log_state_change should log changes."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.log_state_change("update", {"a": 1}, {"a": 2})

            mock_logger.info.assert_called_once()

    def test_assert_state_passes(self):
        """assert_state should pass for True condition."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.assert_state(True, "Should pass")

            # Should not raise

    def test_assert_state_fails(self):
        """assert_state should raise for False condition."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")

            with pytest.raises(AssertionError, match="Should fail"):
                logger.assert_state(False, "Should fail")

    def test_log_operation_start(self):
        """log_operation_start should log start of operation."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.log_operation_start("test_op", param1="value1")

            mock_logger.debug.assert_called()

    def test_log_operation_end_success(self):
        """log_operation_end should log successful end."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.log_operation_end("test_op", success=True, result="done")

            mock_logger.debug.assert_called()

    def test_log_operation_end_failure(self):
        """log_operation_end should log failure."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.log_operation_end("test_op", success=False, error="failed")

            mock_logger.error.assert_called()

    def test_log_error(self):
        """log_error should log error with context."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.log_error("Test error", key="value")

            mock_logger.error.assert_called()

    def test_log_warning(self):
        """log_warning should log warning with context."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.log_warning("Test warning", key="value")

            mock_logger.warning.assert_called()

    def test_update_cache(self):
        """update_cache should store value."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.update_cache("key", "value")

            assert logger.state_cache["key"] == "value"

    def test_get_cached_state(self):
        """get_cached_state should return cached value."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.state_cache["key"] = "value"

            assert logger.get_cached_state("key") == "value"

    def test_get_cached_state_default(self):
        """get_cached_state should return default for missing key."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            assert logger.get_cached_state("missing", "default") == "default"

    def test_clear_debouncer(self):
        """clear_debouncer should clear debouncer cache."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")
            logger.debouncer.should_log("test", "info")
            logger.clear_debouncer()

            assert logger.debouncer.recent_logs == {}

    def test_flush_aggregated_logs(self):
        """flush_aggregated_logs should call aggregator force_flush."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")

            with patch.object(logger.aggregator, "force_flush") as mock_flush:
                logger.flush_aggregated_logs()
                mock_flush.assert_called_once()

    def test_log_rendering_operation(self):
        """log_rendering_operation should add event to aggregator."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")

            with patch.object(logger.aggregator, "add_event") as mock_add:
                logger.log_rendering_operation("image", success=True)
                mock_add.assert_called_once()

    def test_log_rendering_operation_error(self):
        """log_rendering_operation should include error details on failure."""
        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            logger = StateLogger("test")

            with patch.object(logger.aggregator, "add_event") as mock_add:
                logger.log_rendering_operation(
                    "image",
                    success=False,
                    error_details="Failed to load",
                    context={"path": "/test.png"},
                )
                mock_add.assert_called_once()
                call_kwargs = mock_add.call_args[1]
                assert call_kwargs["error_details"] == "Failed to load"
                assert call_kwargs["context"] == {"path": "/test.png"}


class TestLogAggregatorInternal:
    """Tests for LogAggregator internal methods."""

    def test_flush_aggregated_logs_empty(self):
        """_flush_aggregated_logs should handle empty queue."""
        aggregator = LogAggregator()
        aggregator._flush_aggregated_logs()  # Should not raise

    def test_flush_aggregated_logs_single_event(self):
        """_flush_aggregated_logs should log individual events when < 3."""
        aggregator = LogAggregator(aggregation_window=100)  # Long window to prevent auto-flush

        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            aggregator.add_event(module="test", operation="custom_op", level="INFO")
            aggregator._flush_aggregated_logs()

            # Single event should be logged individually
            mock_logger.info.assert_called()

    def test_flush_aggregated_logs_rendering_summary(self):
        """_flush_aggregated_logs should create summary for 3+ rendering events."""
        aggregator = LogAggregator(aggregation_window=100)

        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            # Add 3 rendering events to trigger aggregation
            for i in range(3):
                aggregator.add_event(
                    module="test",
                    operation="rendering",
                    level="DEBUG",
                    status="success",
                    content_type="heading",
                )
            aggregator._flush_aggregated_logs()

            # Should log summary table
            mock_logger.info.assert_called()

    def test_flush_aggregated_logs_with_errors(self):
        """_flush_aggregated_logs should log error details."""
        aggregator = LogAggregator(aggregation_window=100)

        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            # Add events with errors
            for i in range(3):
                aggregator.add_event(
                    module="test",
                    operation="rendering",
                    level="ERROR",
                    status="error",
                    content_type="image",
                    error_details=f"Error {i}",
                    context={"path": f"/img{i}.png"},
                )
            aggregator._flush_aggregated_logs()

            # Should log error analysis
            mock_logger.error.assert_called()

    def test_log_generic_operation_summary(self):
        """_log_generic_operation_summary should log non-rendering operations."""
        aggregator = LogAggregator(aggregation_window=100)

        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            for i in range(3):
                aggregator.add_event(
                    module="test",
                    operation="data_sync",
                    level="INFO",
                    status="success" if i < 2 else "error",
                )
            aggregator._flush_aggregated_logs()

            # Should log generic summary
            mock_logger.info.assert_called()

    def test_collect_rendering_stats(self):
        """_collect_rendering_stats should group events by content type."""
        aggregator = LogAggregator()

        events = [
            LogEvent(1.0, "DEBUG", "test", "rendering", "success", "heading"),
            LogEvent(2.0, "DEBUG", "test", "rendering", "success", "heading"),
            LogEvent(3.0, "ERROR", "test", "rendering", "error", "image"),
        ]

        stats = aggregator._collect_rendering_stats(events)

        assert stats["heading"]["count"] == 2
        assert stats["heading"]["success"] == 2
        assert stats["image"]["count"] == 1
        assert stats["image"]["error"] == 1

    def test_log_troubleshooting_suggestions(self):
        """_log_troubleshooting_suggestions should log appropriate suggestions."""
        aggregator = LogAggregator()

        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            aggregator._log_troubleshooting_suggestions("image")

            # Should log suggestions for image type
            mock_logger.error.assert_called()

    def test_log_individual_event(self):
        """_log_individual_event should log event details."""
        aggregator = LogAggregator()

        with patch("src.core.state_logger.LoggerManager") as mock_manager:
            mock_logger = MagicMock()
            mock_manager.get_logger.return_value = mock_logger

            event = LogEvent(1.0, "INFO", "test_module", "test_op", "success", "heading")
            aggregator._log_individual_event(event)

            mock_logger.info.assert_called()
