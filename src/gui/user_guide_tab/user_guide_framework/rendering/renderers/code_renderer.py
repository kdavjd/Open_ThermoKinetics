"""
Code Renderer - Рендерер для блоков кода и синтаксиса
"""

from typing import Any, Dict, List

from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from src.core.logger_config import LoggerManager
from src.gui.user_guide_tab.user_guide_framework.rendering.renderers.base_renderer import BaseRenderer

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class CodeRenderer(BaseRenderer):
    """
    Рендерер для блоков кода, команд и синтаксиса.
    """

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов кода."""
        return ["code", "python", "shell", "json", "command", "terminal"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит код в соответствующий виджет.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный виджет кода
        """
        content_type = content.get("type")

        if content_type in ["code", "python", "json"]:
            code_text = content.get("code", content.get("content", {}).get("code", ""))
            title = content.get("title", content.get("content", {}).get("title", ""))
            language = content.get("language", content_type)
            return self._render_code_block_simple(code_text, title, language)
        elif content_type in ["shell", "command", "terminal"]:
            code_text = content.get("code", content.get("content", {}).get("code", ""))
            title = content.get("title", content.get("content", {}).get("title", ""))
            return self._render_terminal_block_simple(code_text, title)
        else:
            code_text = content.get("code", content.get("text", ""))
            return self._render_code_block_simple(code_text, "", "text")

    def _render_code_block(self, code_data: Dict[str, Any], language: str = "text") -> QWidget:
        """
        Создает виджет блока кода.

        Args:
            code_data: Данные кода (code, title, highlight)
            language: Язык программирования для подсветки

        Returns:
            QWidget: Виджет с блоком кода
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        code_text = code_data.get("code", "")
        title = code_data.get("title", "")
        readonly = code_data.get("readonly", True)

        # Заголовок блока кода
        if title:
            header_layout = QHBoxLayout()

            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {self.get_theme_color("text_primary")};
                    padding: 4px 8px;
                    background-color: {self.get_theme_color("surface")};
                    border-radius: 4px 4px 0px 0px;
                    border: 1px solid {self.get_theme_color("border")};
                    border-bottom: none;
                }}
            """)

            # Кнопка копирования
            copy_button = QPushButton("📋 Copy")
            copy_button.setMaximumWidth(80)
            copy_button.clicked.connect(lambda: self._copy_to_clipboard(code_text))

            header_layout.addWidget(title_label)
            header_layout.addStretch()
            header_layout.addWidget(copy_button)

            layout.addLayout(header_layout)

        # Текстовый редактор для кода
        code_editor = QTextEdit()
        code_editor.setPlainText(code_text)
        code_editor.setReadOnly(readonly)

        # Настройки шрифта
        font = self.get_theme_font("code")
        if not font:
            font = QFont("Consolas", 10)
            font.setFamily("monospace")

        code_editor.setFont(font)

        # Стилизация редактора кода
        bg_color = self.get_theme_color("surface")
        text_color = self.get_theme_color("text_primary")
        border_color = self.get_theme_color("border")

        code_editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 0px 0px 4px 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                line-height: 1.4;
            }}
            QScrollBar:vertical {{
                background-color: {self.get_theme_color("background")};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.get_theme_color("border")};
                border-radius: 6px;
                min-height: 20px;
            }}
        """)

        # Устанавливаем размер
        font_metrics = QFontMetrics(font)
        line_height = font_metrics.lineSpacing()
        num_lines = min(code_text.count("\n") + 1, 20)  # Максимум 20 строк
        height = line_height * num_lines + 20  # Добавляем отступы
        code_editor.setMaximumHeight(height)
        code_editor.setMinimumHeight(min(height, 100))

        layout.addWidget(code_editor)

        # Добавляем информацию о языке
        if language and language != "text":
            lang_label = QLabel(f"Language: {language.upper()}")
            lang_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_secondary")};
                    font-size: 10px;
                    padding: 2px 8px;
                    text-align: right;
                }}
            """)
            layout.addWidget(lang_label)

        return container

    def _render_terminal_block(self, terminal_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет терминального блока.

        Args:
            terminal_data: Данные терминала

        Returns:
            QWidget: Виджет терминала
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        command = terminal_data.get("command", "")
        output = terminal_data.get("output", "")
        prompt = terminal_data.get("prompt", "$")

        # Заголовок терминала
        header = QLabel("💻 Terminal")
        header.setStyleSheet("""
            QLabel {
                background-color: #2d3748;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px 4px 0px 0px;
            }
        """)
        layout.addWidget(header)

        # Контент терминала
        terminal_widget = QTextEdit()
        terminal_widget.setReadOnly(True)

        # Формируем текст терминала
        terminal_text = ""
        if command:
            terminal_text += f"{prompt} {command}\n"
        if output:
            terminal_text += output

        terminal_widget.setPlainText(terminal_text)

        # Терминальный шрифт и стилизация
        font = QFont("Consolas", 10)
        font.setFamily("monospace")
        terminal_widget.setFont(font)

        terminal_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1a202c;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 0px 0px 4px 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }
            QScrollBar:vertical {
                background-color: #2d3748;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a5568;
                border-radius: 6px;
            }
        """)

        # Размер терминала
        font_metrics = QFontMetrics(font)
        line_height = font_metrics.lineSpacing()
        num_lines = min(terminal_text.count("\n") + 1, 15)
        height = line_height * num_lines + 20
        terminal_widget.setMaximumHeight(height)
        terminal_widget.setMinimumHeight(min(height, 80))

        layout.addWidget(terminal_widget)

        # Кнопка копирования команды
        if command:
            copy_layout = QHBoxLayout()
            copy_layout.addStretch()

            copy_cmd_button = QPushButton("📋 Copy Command")
            copy_cmd_button.clicked.connect(lambda: self._copy_to_clipboard(command))
            copy_cmd_button.setMaximumWidth(120)

            copy_layout.addWidget(copy_cmd_button)
            layout.addLayout(copy_layout)

        return container

    def _copy_to_clipboard(self, text: str) -> None:
        """
        Копирует текст в буфер обмена.

        Args:
            text: Текст для копирования
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # Можно добавить уведомление о копировании

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
                    color: {self.get_theme_color("text_primary")};
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
        if font:
            code_widget.setFont(font)

        code_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.get_theme_color("code_background")};
                color: {self.get_theme_color("code_text")};
                border: 1px solid {self.get_theme_color("border_primary")};
                border-radius: 4px;
                padding: 8px;
                selection-background-color: {self.get_theme_color("selection_background")};
            }}
        """)

        layout.addWidget(code_widget)
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
                    color: {self.get_theme_color("text_primary")};
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
        if font:
            terminal_widget.setFont(font)

        terminal_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.get_theme_color("terminal_background")};
                color: {self.get_theme_color("terminal_text")};
                border: 1px solid {self.get_theme_color("border_primary")};
                border-radius: 4px;
                padding: 8px;
                selection-background-color: {self.get_theme_color("selection_background")};
            }}
        """)

        layout.addWidget(terminal_widget)
        return container
