"""
User Guide Framework - Rendering Layer
Система рендеринга контента для User Guide фреймворка
"""

from .renderer_manager import RendererManager
from .renderers.base_renderer import BaseRenderer
from .widget_factory import WidgetFactory

__all__ = ["RendererManager", "BaseRenderer", "WidgetFactory"]
