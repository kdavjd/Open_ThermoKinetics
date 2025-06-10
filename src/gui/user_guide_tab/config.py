"""
User Guide Tab Configuration
Contains configuration constants and settings for the user guide interface.
"""

from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    """Supported languages for the user guide"""

    ENGLISH = "en"
    RUSSIAN = "ru"


@dataclass
class GuideConfig:
    """Configuration constants for the user guide interface"""

    # Layout constants
    MIN_WIDTH_SIDEBAR = 250
    MIN_WIDTH_CONTENT = 600
    MIN_HEIGHT_GUIDE = 600

    # Font settings
    HEADING_FONT_SIZE = 16
    SUBHEADING_FONT_SIZE = 14
    BODY_FONT_SIZE = 11
    CODE_FONT_SIZE = 10

    # Colors
    HEADING_COLOR = "#2c3e50"
    SUBHEADING_COLOR = "#34495e"
    CODE_BACKGROUND = "#f8f9fa"
    CODE_BORDER = "#e9ecef"
    LINK_COLOR = "#3498db"

    # Spacing
    SECTION_SPACING = 20
    PARAGRAPH_SPACING = 10
    LIST_INDENT = 20


# Section navigation structure
GUIDE_SECTIONS = {
    "en": {
        "Introduction": "introduction",
        "Getting Started": {"File Loading": "file_loading", "Data Preprocessing": "data_preprocessing"},
        "Analysis Methods": {
            "Peak Deconvolution": "deconvolution",
            "Model-Fit Analysis": "model_fit",
            "Model-Free Analysis": "model_free",
            "Model-Based Analysis": "model_based",
        },
        "Working with Series": "series",
        "Additional Features": {
            "Table View": "table_view",
            "Console Output": "console",
            "Import/Export": "import_export",
        },
        "Tips & Troubleshooting": "tips",
    },
    "ru": {
        "Введение": "introduction",
        "Начало работы": {"Загрузка файлов": "file_loading", "Предобработка данных": "data_preprocessing"},
        "Методы анализа": {
            "Деконволюция пиков": "deconvolution",
            "Model-Fit анализ": "model_fit",
            "Model-Free анализ": "model_free",
            "Model-Based анализ": "model_based",
        },
        "Работа с сериями": "series",
        "Дополнительные возможности": {
            "Табличный просмотр": "table_view",
            "Вывод консоли": "console",
            "Импорт/экспорт": "import_export",
        },
        "Советы и устранение проблем": "tips",
    },
}
