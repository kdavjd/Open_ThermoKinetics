"""Tests for base_signals module — signal-slot communication."""

from unittest.mock import MagicMock

import pytest

from src.core.base_signals import BaseSignals, BaseSlots


class TestBaseSignals:
    """Tests for BaseSignals dispatcher."""

    def test_base_signals_creation(self, qtbot):
        """BaseSignals should create with empty components dict."""
        signals = BaseSignals()
        assert signals.components == {}

    def test_register_component(self, qtbot):
        """register_component should add component handlers."""
        signals = BaseSignals()
        mock_request = MagicMock()
        mock_response = MagicMock()

        signals.register_component("test_component", mock_request, mock_response)

        assert "test_component" in signals.components
        assert signals.components["test_component"] == (mock_request, mock_response)

    def test_dispatch_request_routes_to_target(self, qtbot):
        """dispatch_request should call correct component's request handler."""
        signals = BaseSignals()
        mock_request = MagicMock()
        mock_response = MagicMock()
        signals.register_component("target_component", mock_request, mock_response)

        params = {"target": "target_component", "operation": "test_op"}
        signals.dispatch_request(params)

        mock_request.assert_called_once_with(params)

    def test_dispatch_request_unknown_target(self, qtbot):
        """dispatch_request should handle unknown target gracefully."""
        signals = BaseSignals()

        params = {"target": "unknown_component", "operation": "test_op"}
        # Should not raise
        signals.dispatch_request(params)

    def test_dispatch_response_routes_to_target(self, qtbot):
        """dispatch_response should call correct component's response handler."""
        signals = BaseSignals()
        mock_request = MagicMock()
        mock_response = MagicMock()
        signals.register_component("target_component", mock_request, mock_response)

        params = {"target": "target_component", "operation": "test_op"}
        signals.dispatch_response(params)

        mock_response.assert_called_once_with(params)

    def test_dispatch_response_unknown_target(self, qtbot):
        """dispatch_response should handle unknown target gracefully."""
        signals = BaseSignals()

        params = {"target": "unknown_component", "operation": "test_op"}
        # Should not raise
        signals.dispatch_response(params)

    def test_request_signal_connected(self, qtbot):
        """request_signal should be connected to dispatch_request."""
        signals = BaseSignals()
        mock_request = MagicMock()
        mock_response = MagicMock()
        signals.register_component("test", mock_request, mock_response)

        params = {"target": "test", "operation": "test_op"}
        signals.request_signal.emit(params)

        qtbot.wait(10)  # Allow signal processing
        mock_request.assert_called_once()


class TestBaseSlots:
    """Tests for BaseSlots base class."""

    def test_base_slots_creation(self, qtbot):
        """BaseSlots should initialize with actor_name and signals."""
        signals = BaseSignals()
        slots = BaseSlots("test_actor", signals)

        assert slots.actor_name == "test_actor"
        assert slots.signals == signals
        assert slots.pending_requests == {}
        assert "test_actor" in signals.components

    def test_base_slots_requires_actor_name(self, qtbot):
        """BaseSlots should raise ValueError if actor_name is empty."""
        signals = BaseSignals()

        with pytest.raises(ValueError, match="actor_name must be provided"):
            BaseSlots("", signals)

    def test_create_and_emit_request(self, qtbot):
        """create_and_emit_request should create request with UUID."""
        signals = BaseSignals()
        slots = BaseSlots("test_actor", signals)

        request_id = slots.create_and_emit_request("target", "TEST_OP", extra_param=123)

        assert request_id is not None
        assert request_id in slots.pending_requests
        assert slots.pending_requests[request_id]["received"] is False

    def test_connect_to_dispatcher(self, qtbot):
        """connect_to_dispatcher should connect signals."""
        signals = BaseSignals()
        slots = BaseSlots("test_actor", signals)

        # This is called in __init__, but we can call it again
        slots.connect_to_dispatcher()

        # Should not raise - connections are internal Qt operations

    def test_process_response_ignores_wrong_target(self, qtbot):
        """process_response should ignore responses for other actors."""
        signals = BaseSignals()
        slots = BaseSlots("test_actor", signals)

        # Create a pending request
        request_id = "test-request-id"
        slots.pending_requests[request_id] = {"received": False, "data": None}

        # Response for different target
        params = {"target": "other_actor", "request_id": request_id, "data": {"result": 42}}
        slots.process_response(params)

        # Should not update pending request
        assert slots.pending_requests[request_id]["received"] is False

    def test_process_response_updates_pending_request(self, qtbot):
        """process_response should update correct pending request."""
        signals = BaseSignals()
        slots = BaseSlots("test_actor", signals)

        request_id = "test-request-id"
        slots.pending_requests[request_id] = {"received": False, "data": None}

        params = {
            "target": "test_actor",
            "request_id": request_id,
            "operation": "TEST_OP",
            "data": {"result": 42},
        }
        slots.process_response(params)

        assert slots.pending_requests[request_id]["received"] is True
        assert slots.pending_requests[request_id]["data"] == params

    def test_wait_for_response_timeout(self, qtbot):
        """wait_for_response should return None on timeout."""
        signals = BaseSignals()
        slots = BaseSlots("test_actor", signals)

        request_id = "test-request-id"
        result = slots.wait_for_response(request_id, timeout=50)  # 50ms timeout

        assert result is None

    def test_handle_request_cycle_creates_request(self, qtbot):
        """handle_request_cycle should create request with correct structure."""
        signals = BaseSignals()
        requester = BaseSlots("requester", signals)

        # Verify request structure without waiting for response
        request_id = requester.create_and_emit_request("responder", "TEST_OP")

        assert request_id is not None
        assert request_id in requester.pending_requests
        assert requester.pending_requests[request_id]["received"] is False


class TestBaseSlotsMockVersion:
    """Tests for BaseSlots using mock_signals fixture (no Qt event loop)."""

    def test_base_slots_with_mock_signals(self, mock_signals):
        """BaseSlots should work with mock signals for unit testing."""
        slots = BaseSlots("test_actor", mock_signals)

        assert slots.actor_name == "test_actor"
        mock_signals.register_component.assert_called_once()

    def test_create_request_with_mock(self, mock_signals):
        """create_and_emit_request should work with mock signals."""
        slots = BaseSlots("test_actor", mock_signals)

        request_id = slots.create_and_emit_request("target", "TEST_OP", param=123)

        assert request_id is not None
        mock_signals.request_signal.emit.assert_called_once()

        # Verify request structure
        call_args = mock_signals.request_signal.emit.call_args[0][0]
        assert call_args["actor"] == "test_actor"
        assert call_args["target"] == "target"
        assert call_args["operation"] == "TEST_OP"
        assert call_args["param"] == 123

    def test_process_response_with_mock(self, mock_signals):
        """process_response should update pending requests with mock signals."""
        slots = BaseSlots("test_actor", mock_signals)

        request_id = "test-id"
        slots.pending_requests[request_id] = {"received": False, "data": None}

        params = {
            "target": "test_actor",
            "request_id": request_id,
            "operation": "TEST_OP",
            "data": {"result": 42},
        }
        slots.process_response(params)

        assert slots.pending_requests[request_id]["received"] is True
