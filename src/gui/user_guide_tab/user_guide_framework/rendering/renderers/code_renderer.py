"""
Code Renderer - Рендерер для блоков кода и синтаксиса
"""

from typing import Any, Dict, List

from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from src.core.logger_config import LoggerManager
from src.core.state_logger import StateLogger
from src.gui.user_guide_tab.user_guide_framework.rendering.renderers.base_renderer import BaseRenderer

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class CodeRenderer(BaseRenderer):
    """
    Рендерер для блоков кода, команд и синтаксиса.
    """

    def __init__(self, theme_manager):
        super().__init__(theme_manager)
        self.state_logger = StateLogger("CodeRenderer")

    def _get_safe_theme_color(self, color_key: str, fallback: str) -> str:
        """Get theme color with safe fallback."""
        try:
            color = self.get_theme_color(color_key)
            if color and hasattr(color, "name"):
                return color.name()
            else:
                self.state_logger.log_warning(f"Invalid color for key: {color_key}", fallback=fallback)
                return fallback
        except Exception as e:
            self.state_logger.log_error(f"Error getting theme color: {color_key}", error=str(e), fallback=fallback)
            return fallback

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов кода."""
        return ["code", "code_block", "python", "shell", "json", "command", "terminal"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит код в соответствующий виджет.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный виджет кода
        """
        content_type = content.get("type")

        if content_type in ["code", "code_block", "python", "json"]:
            code_text = content.get("code", content.get("content", {}).get("code", ""))
            if not code_text:
                code_text = content.get("text", "")
            title = content.get("title", content.get("content", {}).get("title", ""))
            language = content.get("language", content_type)
            return self._render_code_block_simple(code_text, title, language)
        elif content_type in ["shell", "command", "terminal"]:
            code_text = content.get("code", content.get("content", {}).get("code", ""))
            if not code_text:
                code_text = content.get("text", "")
            title = content.get("title", content.get("content", {}).get("title", ""))
            return self._render_terminal_block_simple(code_text, title)
        else:
            code_text = content.get("code", content.get("text", ""))
            return self._render_code_block_simple(code_text, "", "text")

    def _render_code_block_simple(self, code_text: str, title: str = "", language: str = "text") -> QWidget:
        """
        Создает простой виджет блока кода.

        Args:
            code_text: Текст кода
            title: Заголовок блока
            language: Язык программирования

        Returns:
            QWidget: Виджет с блоком кода
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        # Проверяем валидность кода
        if code_text is None:
            code_text = ""

        # Заголовок блока
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {self._get_safe_theme_color("text_primary", "#000000")};
                    font-weight: bold;
                    padding: 4px 0px;
                }}
            """)
            layout.addWidget(title_label)

        # Блок кода
        code_widget = QTextEdit()
        code_widget.setPlainText(code_text)
        code_widget.setReadOnly(True)

        # Применяем моноширинный шрифт
        font = self.get_theme_font("code")
        if not font:
            font = QFont("Consolas", 10)
            font.setFamily("monospace")
        code_widget.setFont(font)

        # Вычисляем высоту на основе количества строк
        font_metrics = QFontMetrics(font)
        line_height = font_metrics.lineSpacing()
        num_lines = min(code_text.count("\n") + 1, 20)  # Максимум 20 строк
        height = line_height * num_lines + 20  # Добавляем отступы
        code_widget.setMaximumHeight(height)
        code_widget.setMinimumHeight(min(height, 80))

        code_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self._get_safe_theme_color("code_background", "#F5F5F5")};
                color: {self._get_safe_theme_color("code_text", "#333333")};
                border: 1px solid {self._get_safe_theme_color("border_primary", "#CCCCCC")};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                selection-background-color: {self._get_safe_theme_color("selection_background", "#D0D0D0")};
            }}
        """)

        layout.addWidget(code_widget)

        # Добавляем информацию о языке если нужно
        if language and language != "text":
            lang_label = QLabel(f"Language: {language.upper()}")
            lang_label.setStyleSheet(f"""
                QLabel {{
                    color: {self._get_safe_theme_color("text_secondary", "#666666")};
                    font-size: 10px;
                    padding: 2px 8px;
                    text-align: right;
                }}
            """)
            layout.addWidget(lang_label)

        return container

    def _render_terminal_block_simple(self, code_text: str, title: str = "") -> QWidget:
        """
        Создает простой виджет блока терминала.

        Args:
            code_text: Текст команды
            title: Заголовок блока

        Returns:
            QWidget: Виджет с блоком терминала
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        # Заголовок блока
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {self._get_safe_theme_color("text_primary", "#000000")};
                    font-weight: bold;
                    padding: 4px 0px;
                }}
            """)
            layout.addWidget(title_label)

        # Блок терминала
        terminal_widget = QTextEdit()
        terminal_widget.setPlainText(code_text)
        terminal_widget.setReadOnly(True)

        # Применяем моноширинный шрифт
        font = self.get_theme_font("code")
        if not font:
            font = QFont("Consolas", 10)
            font.setFamily("monospace")
        terminal_widget.setFont(font)

        # Вычисляем высоту на основе количества строк
        font_metrics = QFontMetrics(font)
        line_height = font_metrics.lineSpacing()
        num_lines = min(code_text.count("\n") + 1, 15)
        height = line_height * num_lines + 20
        terminal_widget.setMaximumHeight(height)
        terminal_widget.setMinimumHeight(min(height, 60))

        terminal_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self._get_safe_theme_color("terminal_background", "#1a202c")};
                color: {self._get_safe_theme_color("terminal_text", "#e2e8f0")};
                border: 1px solid {self._get_safe_theme_color("border_primary", "#4a5568")};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                selection-background-color: {self._get_safe_theme_color("selection_background", "#D0D0D0")};
            }}
        """)

        layout.addWidget(terminal_widget)
        return container
