"""
User Guide Framework
A modular, extensible framework for creating interactive user guides in PyQt6.
"""

# Core modules
from .core.content_manager import ContentManager
from .core.localization_manager import LocalizationManager
from .core.navigation_manager import NavigationManager, NavigationNode
from .core.theme_manager import ThemeManager

# Rendering modules
from .rendering.renderer_manager import RendererManager
from .rendering.widget_factory import WidgetFactory
from .ui.content_widget import ContentWidget

# UI modules
from .ui.guide_framework import GuideFramework
from .ui.guide_toolbar import GuideToolBar
from .ui.navigation_sidebar import NavigationSidebar
from .ui.status_widget import StatusWidget

__all__ = [
    # Core
    "ContentManager",
    "NavigationManager",
    "NavigationNode",
    "ThemeManager",
    "LocalizationManager",
    # Rendering
    "RendererManager",
    "WidgetFactory",
    # UI
    "GuideFramework",
    "NavigationSidebar",
    "ContentWidget",
    "GuideToolBar",
    "StatusWidget",
]

__version__ = "1.0.0"
