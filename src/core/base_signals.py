import uuid
from typing import Any, Callable, Dict, Optional

from PyQt6.QtCore import QEventLoop, QObject, QTimer, pyqtSignal, pyqtSlot

from src.core.logger_config import logger


class BaseSignals(QObject):
    """Central dispatcher for component communication via Qt signals.

    Routes requests and responses between registered components using a
    publisher-subscriber pattern. Each component registers request/response
    handlers for loose coupling and centralized message routing.
    """

    request_signal = pyqtSignal(dict)
    response_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.components: Dict[str, (Callable[[dict], None], Callable[[dict], None])] = {}
        self.request_signal.connect(self.dispatch_request)
        self.response_signal.connect(self.dispatch_response)

    def register_component(
        self,
        component_name: str,
        process_request_method: Callable[[dict], None],
        process_response_method: Callable[[dict], None],
    ) -> None:
        """Register component with request and response handlers.

        Args:
            component_name: Unique component identifier
            process_request_method: Handler for incoming requests
            process_response_method: Handler for incoming responses
        """
        self.components[component_name] = (process_request_method, process_response_method)
        logger.debug(f"Component '{component_name}' registered with dispatcher.")

    @pyqtSlot(dict)
    def dispatch_request(self, params: dict) -> None:
        """Route request to target component."""
        target = params.get("target")
        if target in self.components:
            process_request_method, _ = self.components[target]
            process_request_method(params)
        else:
            logger.error(f"No component found for target '{target}'")

    @pyqtSlot(dict)
    def dispatch_response(self, params: dict) -> None:
        """Route response to target component."""
        target = params.get("target")
        if target in self.components:
            _, process_response_method = self.components[target]
            process_response_method(params)
        else:
            logger.error(f"No component found for target '{target}'")


class BaseSlots(QObject):
    """Base class for request/response communication via Qt signals.

    Provides synchronous request/response operations over Qt's asynchronous
    signal system using QEventLoop blocking. Components inherit this class
    to participate in centralized message routing.
    """

    def __init__(self, actor_name: str, signals: BaseSignals):
        super().__init__()
        if not actor_name:
            raise ValueError("actor_name must be provided for BaseSignals.")
        self.actor_name = actor_name
        self.signals = signals
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        self.event_loops: Dict[str, QEventLoop] = {}
        self.signals.register_component(self.actor_name, self.process_request, self.process_response)

    def connect_to_dispatcher(self) -> None:
        """Connect component to signal dispatcher."""
        self.signals.request_signal.connect(self.process_request)
        self.signals.response_signal.connect(self.process_response)
        logger.debug(f"{self.actor_name} connected to signals.")

    def handle_request_cycle(self, target: str, operation: str, **kwargs) -> Any:
        """Send request and wait for response synchronously.

        Creates request, emits signal, blocks on QEventLoop until response
        received or timeout occurs. Used throughout codebase for component
        communication.

        Args:
            target: Target component name
            operation: Operation type from OperationType enum
            **kwargs: Additional request parameters

        Returns:
            Response data or None if timeout/error
        """
        request_id = self.create_and_emit_request(target, operation, **kwargs)
        response_data = self.handle_response_data(request_id, operation)
        if response_data is not None:
            return response_data
        else:
            logger.error(f"{self.actor_name}_handle_request_cycle: {operation} completed with None")
            return None

    def create_and_emit_request(self, target: str, operation: str, **kwargs) -> str:
        """Create request with unique ID and emit signal."""
        request_id = str(uuid.uuid4())
        self.pending_requests[request_id] = {"received": False, "data": None}
        request = {
            "actor": self.actor_name,
            "target": target,
            "operation": operation,
            "request_id": request_id,
            **kwargs,
        }
        logger.debug(f"{self.actor_name} is emitting request: {request}")
        self.signals.request_signal.emit(request)
        return request_id

    def process_request(self, params: dict) -> None:
        """Process incoming request. Override in subclasses."""
        pass

    def process_response(self, params: dict) -> None:
        """Process incoming response and unblock waiting event loop."""
        """Process an incoming response.

        Args:
            params (dict): The response parameters, must contain 'request_id' and 'operation'.
        """
        if params.get("target") != self.actor_name:
            return
        logger.debug(f"{self.actor_name} will process response:\n{params=}")
        request_id = params.get("request_id")
        operation = params.get("operation")
        if request_id in self.pending_requests:
            self.pending_requests[request_id]["data"] = params
            self.pending_requests[request_id]["received"] = True
            if request_id in self.event_loops:
                self.event_loops[request_id].quit()
        else:
            logger.error(f"{self.actor_name}_response_slot: unknown operation='{operation}' UUID: {request_id}")

    def wait_for_response(self, request_id: str, timeout: int = 1000) -> Optional[dict]:
        """Block on QEventLoop until response received or timeout.

        Critical synchronization method that converts async Qt signals to
        synchronous operations throughout the application.

        Args:
            request_id: Unique request identifier
            timeout: Maximum wait time in milliseconds

        Returns:
            Response data dict or None if timeout
        """
        if request_id not in self.pending_requests:
            self.pending_requests[request_id] = {"received": False, "data": None}

        loop = QEventLoop()
        self.event_loops[request_id] = loop

        timed_out = False

        def on_timeout():
            nonlocal timed_out
            timed_out = True
            loop.quit()

        QTimer.singleShot(timeout, on_timeout)

        while not self.pending_requests[request_id]["received"] and not timed_out:
            loop.exec()

        del self.event_loops[request_id]

        if timed_out:
            logger.error(
                f"{self.actor_name}_wait_for_response: {request_id} waiting time has expired\n"
                f"waiting is stopped: {self.event_loops.get(request_id, None) is None}"
            )
            return None
        return self.pending_requests.pop(request_id)["data"]

    def handle_response_data(self, request_id: str, operation: str) -> Any:
        """Extract response data from completed request."""
        response_data = self.wait_for_response(request_id)
        if response_data is not None:
            return response_data.pop("data", None)
        else:
            logger.error(f"{self.actor_name}_handle_response: {operation} waiting time has expired")
            return None
