"""
Custom exceptions for the User Guide Framework
"""

from src.core.logger_config import LoggerManager

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class GuideFrameworkError(Exception):
    """Base exception for all user guide framework errors"""

    pass


class ContentNotFoundError(GuideFrameworkError):
    """Raised when requested content section is not found"""

    pass


class NavigationError(GuideFrameworkError):
    """Raised when navigation structure is invalid"""

    pass


class ThemeNotFoundError(GuideFrameworkError):
    """Raised when requested theme is not found"""

    pass


class LocalizationError(GuideFrameworkError):
    """Raised when localization data is invalid or missing"""

    pass


class RendererError(GuideFrameworkError):
    """Raised when content rendering fails"""

    pass
