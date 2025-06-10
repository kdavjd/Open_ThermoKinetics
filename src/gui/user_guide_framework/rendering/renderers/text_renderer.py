"""
Text Renderer - Рендерер для текстовых элементов
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from .base_renderer import BaseRenderer


class TextRenderer(BaseRenderer):
    """
    Рендерер для текстовых элементов: параграфы, заголовки, заметки.
    """

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов текстового контента."""
        return ["paragraph", "heading", "subheading", "note", "warning", "info"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит текстовый контент в соответствующий виджет.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный текстовый виджет
        """
        content_type = content.get("type")
        content_data = content.get("content", "")

        if content_type == "paragraph":
            return self._render_paragraph(content_data)
        elif content_type == "heading":
            return self._render_heading(content_data, level=1)
        elif content_type == "subheading":
            return self._render_heading(content_data, level=2)
        elif content_type == "note":
            return self._render_note(content_data, note_type="note")
        elif content_type == "warning":
            return self._render_note(content_data, note_type="warning")
        elif content_type == "info":
            return self._render_note(content_data, note_type="info")
        else:
            return self._render_paragraph(f"Unknown content type: {content_type}")

    def _render_paragraph(self, text: str) -> QWidget:
        """
        Создает виджет параграфа.

        Args:
            text: Текст параграфа

        Returns:
            QLabel: Виджет с текстом параграфа
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(True)

        # Применяем тему для параграфа
        font = self.get_theme_font("body")
        if font:
            label.setFont(font)

        label.setStyleSheet(f"""
            QLabel {{
                color: {self.get_theme_color("text_primary")};
                padding: 8px 0px;
                line-height: 1.4;
            }}
        """)

        return label

    def _render_heading(self, text: str, level: int = 1) -> QWidget:
        """
        Создает виджет заголовка.

        Args:
            text: Текст заголовка
            level: Уровень заголовка (1-3)

        Returns:
            QLabel: Виджет заголовка
        """
        label = QLabel(text)
        label.setWordWrap(True)

        # Выбираем шрифт в зависимости от уровня
        if level == 1:
            font = self.get_theme_font("heading")
        else:
            font = self.get_theme_font("subheading")

        if font:
            label.setFont(font)

        # Стилизация заголовка
        label.setStyleSheet(f"""
            QLabel {{
                color: {self.get_theme_color("text_primary")};
                font-weight: bold;
                padding: 12px 0px 8px 0px;
                border-bottom: 2px solid {self.get_theme_color("accent")};
                margin-bottom: 8px;
            }}
        """)

        return label

    def _render_note(self, text: str, note_type: str = "note") -> QWidget:
        """
        Создает виджет заметки с соответствующей стилизацией.

        Args:
            text: Текст заметки
            note_type: Тип заметки (note, warning, info)

        Returns:
            QGroupBox: Виджет заметки в рамке
        """
        # Определяем цвета и иконки для разных типов заметок
        note_styles = {
            "note": {
                "border_color": self.get_theme_color("info"),
                "bg_color": self.get_theme_color("surface"),
                "title": "📝 Заметка",
            },
            "warning": {
                "border_color": self.get_theme_color("warning"),
                "bg_color": "#fff3cd",
                "title": "⚠️ Предупреждение",
            },
            "info": {"border_color": self.get_theme_color("info"), "bg_color": "#d1ecf1", "title": "ℹ️ Информация"},
        }

        style = note_styles.get(note_type, note_styles["note"])

        # Создаем групповой виджет
        group_box = QGroupBox(style["title"])
        layout = QVBoxLayout(group_box)

        # Создаем текстовый виджет
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextFormat(Qt.TextFormat.RichText)

        font = self.get_theme_font("body")
        if font:
            text_label.setFont(font)

        layout.addWidget(text_label)

        # Применяем стилизацию
        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {style["border_color"]};
                border-radius: 6px;
                margin: 8px 0px;
                padding-top: 16px;
                background-color: {style["bg_color"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {style["border_color"]};
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: {self.get_theme_color("text_primary")};
                padding: 8px;
            }}
        """)

        return group_box
