# config.py for models_scheme module
"""Configuration settings for the models scheme diagram component."""

from dataclasses import dataclass

from PyQt6.QtGui import QColor


@dataclass(frozen=True)
class DiagramConfig:
    """Configuration for diagram visual elements."""

    # Node dimensions
    node_width: int = 30
    node_height: int = 20

    # Spacing and positioning
    arrow_inset: int = 3
    horizontal_gap: int = 45
    vertical_step: int = 22
    arrow_size: int = 3

    # Colors
    pen_color: QColor = QColor("black")
    node_brush_color: QColor = QColor("white")
    arrow_color: QColor = QColor("black")


@dataclass(frozen=True)
class ModelsSchemeConfig:
    """Main configuration for models scheme module."""

    diagram: DiagramConfig = DiagramConfig()
