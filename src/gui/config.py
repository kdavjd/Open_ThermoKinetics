"""
Main GUI configuration module.
Central configuration management for the entire GUI system.
"""

from dataclasses import dataclass

from .analysis import AnalysisConfig
from .application import ApplicationConfig
from .controls import ControlsConfig
from .dialogs import DialogsConfig
from .localization import LocalizationManager, StringResources
from .modeling import ModelingConfig
from .visualization import VisualizationConfig


@dataclass
class GUIConfig:
    """
    Main configuration class that aggregates all GUI configurations.
    Provides centralized access to all application settings.
    """

    application: ApplicationConfig = None
    analysis: AnalysisConfig = None
    modeling: ModelingConfig = None
    visualization: VisualizationConfig = None
    controls: ControlsConfig = None
    dialogs: DialogsConfig = None
    strings: StringResources = None
    localization: LocalizationManager = None

    def __post_init__(self):
        """Initialize all configuration sections with defaults if not provided."""
        if self.application is None:
            self.application = ApplicationConfig()
        if self.analysis is None:
            self.analysis = AnalysisConfig()
        if self.modeling is None:
            self.modeling = ModelingConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()
        if self.controls is None:
            self.controls = ControlsConfig()
        if self.dialogs is None:
            self.dialogs = DialogsConfig()
        if self.strings is None:
            self.strings = StringResources()
        if self.localization is None:
            self.localization = LocalizationManager()


# Global configuration instance
_gui_config: GUIConfig = None


def get_config() -> GUIConfig:
    """
    Get the global GUI configuration instance.
    Creates and initializes if it doesn't exist.

    Returns:
        GUIConfig: The global configuration instance
    """
    global _gui_config
    if _gui_config is None:
        _gui_config = GUIConfig()
    return _gui_config


def init_config(config: GUIConfig = None) -> GUIConfig:
    """
    Initialize the global configuration.

    Args:
        config: Optional custom configuration. If None, uses defaults.

    Returns:
        GUIConfig: The initialized configuration instance
    """
    global _gui_config
    if config is None:
        _gui_config = GUIConfig()
    else:
        _gui_config = config
    return _gui_config


# Convenience functions for accessing specific configurations
def get_app_config() -> ApplicationConfig:
    """Get application configuration."""
    return get_config().application


def get_analysis_config() -> AnalysisConfig:
    """Get analysis configuration."""
    return get_config().analysis


def get_modeling_config() -> ModelingConfig:
    """Get modeling configuration."""
    return get_config().modeling


def get_visualization_config() -> VisualizationConfig:
    """Get visualization configuration."""
    return get_config().visualization


def get_controls_config() -> ControlsConfig:
    """Get controls configuration."""
    return get_config().controls


def get_dialogs_config() -> DialogsConfig:
    """Get dialogs configuration."""
    return get_config().dialogs


def get_strings() -> StringResources:
    """Get string resources."""
    return get_config().strings


def get_localization() -> LocalizationManager:
    """Get localization manager."""
    return get_config().localization


# Shorthand access functions for commonly used values
def get_window_config():
    """Get main window configuration."""
    return get_app_config().window


def get_tab_config():
    """Get tab configuration."""
    return get_app_config().tabs


def get_button_config():
    """Get button configuration."""
    return get_controls_config().buttons


def get_table_config():
    """Get table configuration."""
    return get_controls_config().tables


def get_plot_config():
    """Get plot configuration."""
    return get_visualization_config().plots
