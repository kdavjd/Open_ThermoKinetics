from abc import ABC, abstractmethod
from typing import Any, Dict, List

from PyQt6.QtWidgets import QWidget

from src.core.logger_config import LoggerManager

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class BaseRenderer(ABC):
    def __init__(self, theme_manager=None):
        self.theme_manager = theme_manager

    @abstractmethod
    def render(self, content: Dict[str, Any]) -> QWidget:
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        pass

    def can_render(self, content_type: str) -> bool:
        return content_type in self.get_supported_types()

    def apply_theme(self, widget: QWidget, style_key: str = None) -> None:
        if self.theme_manager and style_key:
            stylesheet = self.theme_manager.generate_stylesheet(widget.__class__.__name__, style_key)
            if stylesheet:
                widget.setStyleSheet(stylesheet)

    def get_theme_color(self, color_key: str) -> str:
        if self.theme_manager:
            color = self.theme_manager.get_color(color_key)
            return color.name() if color else "#000000"
        return "#000000"

    def get_theme_font(self, font_key: str):
        if self.theme_manager:
            return self.theme_manager.get_font(font_key)
        return None
