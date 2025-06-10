"""
User Guide Framework
A modular, extensible framework for creating interactive user guides in PyQt6.
"""

from .core.content_manager import ContentManager
from .core.localization_manager import LocalizationManager
from .core.navigation_manager import NavigationManager, NavigationNode
from .core.theme_manager import ThemeManager

__all__ = ["ContentManager", "NavigationManager", "NavigationNode", "ThemeManager", "LocalizationManager"]

__version__ = "1.0.0"
