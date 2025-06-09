"""
Dialogs module initialization for configuration management.
"""

from .dialogs_config import (
    AnnotationDialogConfig,
    CalculationSettingsDialogConfig,
    DialogDimensions,
    DialogsConfig,
    FileSelectionDialogConfig,
    ModelsSelectionDialogConfig,
)

__all__ = [
    "DialogsConfig",
    "DialogDimensions",
    "AnnotationDialogConfig",
    "CalculationSettingsDialogConfig",
    "ModelsSelectionDialogConfig",
    "FileSelectionDialogConfig",
]
