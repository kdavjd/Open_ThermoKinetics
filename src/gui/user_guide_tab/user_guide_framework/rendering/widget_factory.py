"""
Widget Factory - Фабрика для создания специализированных виджетов
"""

from typing import Any, Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.core.logger_config import LoggerManager

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class WidgetFactory:
    """
    Фабрика для создания часто используемых виджетов с применением тем.
    """

    def __init__(self, theme_manager=None):
        """
        Инициализация фабрики виджетов.

        Args:
            theme_manager: Менеджер тем для стилизации
        """
        self.theme_manager = theme_manager

    def create_styled_label(
        self,
        text: str,
        style_type: str = "body",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        word_wrap: bool = True,
    ) -> QLabel:
        """
        Создает стилизованный label.

        Args:
            text: Текст label
            style_type: Тип стиля (body, heading, subheading)
            alignment: Выравнивание текста
            word_wrap: Перенос слов

        Returns:
            QLabel: Стилизованный label
        """
        label = QLabel(text)
        label.setAlignment(alignment)
        label.setWordWrap(word_wrap)

        # Применяем шрифт из темы
        font = self._get_font_for_style(style_type)
        if font:
            label.setFont(font)

        # Применяем цвет
        color = self._get_color("text_primary")
        if style_type == "heading":
            label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    padding: 8px 0px;
                    border-bottom: 2px solid {self._get_color("accent")};
                }}
            """)
        elif style_type == "subheading":
            label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    padding: 6px 0px;
                }}
            """)
        else:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    padding: 4px 0px;
                    line-height: 1.4;
                }}
            """)

        return label

    def create_styled_button(
        self, text: str, button_type: str = "primary", click_handler: Optional[Callable] = None
    ) -> QPushButton:
        """
        Создает стилизованную кнопку.

        Args:
            text: Текст кнопки
            button_type: Тип кнопки (primary, secondary, danger, success)
            click_handler: Обработчик клика

        Returns:
            QPushButton: Стилизованная кнопка
        """
        button = QPushButton(text)

        if click_handler:
            button.clicked.connect(click_handler)

        # Определяем цвета для разных типов кнопок
        color_map = {
            "primary": self._get_color("accent"),
            "secondary": self._get_color("secondary"),
            "danger": self._get_color("error"),
            "success": self._get_color("success"),
            "info": self._get_color("info"),
        }

        bg_color = color_map.get(button_type, self._get_color("accent"))

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(bg_color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color)};
            }}
            QPushButton:disabled {{
                background-color: {self._get_color("border")};
                color: {self._get_color("text_secondary")};
            }}
        """)

        return button

    def create_input_field(self, placeholder: str = "", input_type: str = "text", default_value: Any = None) -> QWidget:
        """
        Создает поле ввода.

        Args:
            placeholder: Текст placeholder
            input_type: Тип поля (text, number, decimal, combo)
            default_value: Значение по умолчанию

        Returns:
            QWidget: Поле ввода
        """
        if input_type == "text":
            widget = QLineEdit()
            widget.setPlaceholderText(placeholder)
            if default_value:
                widget.setText(str(default_value))

        elif input_type == "number":
            widget = QSpinBox()
            widget.setRange(-999999, 999999)
            if default_value is not None:
                widget.setValue(int(default_value))

        elif input_type == "decimal":
            from PyQt6.QtWidgets import QDoubleSpinBox

            widget = QDoubleSpinBox()
            widget.setRange(-999999.0, 999999.0)
            widget.setDecimals(3)
            if default_value is not None:
                widget.setValue(float(default_value))

        elif input_type == "combo":
            widget = QComboBox()
            if isinstance(default_value, list):
                widget.addItems([str(item) for item in default_value])

        else:
            widget = QLineEdit()
            widget.setPlaceholderText(placeholder)

        # Общая стилизация
        base_style = f"""
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                border: 1px solid {self._get_color("border")};
                border-radius: 4px;
                padding: 6px;
                background-color: {self._get_color("surface")};
                color: {self._get_color("text_primary")};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border: 2px solid {self._get_color("accent")};
            }}
        """
        widget.setStyleSheet(base_style)

        return widget

    def create_group_box(self, title: str, content_widget: QWidget = None) -> QGroupBox:
        """
        Создает стилизованный группировочный виджет.

        Args:
            title: Заголовок группы
            content_widget: Виджет содержимого

        Returns:
            QGroupBox: Группировочный виджет
        """
        group_box = QGroupBox(title)

        if content_widget:
            layout = QVBoxLayout(group_box)
            layout.addWidget(content_widget)

        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {self._get_color("border")};
                border-radius: 8px;
                margin: 8px 0px;
                padding-top: 16px;
                background-color: {self._get_color("surface")};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {self._get_color("text_primary")};
                background-color: {self._get_color("surface")};
            }}
        """)

        return group_box

    def create_progress_bar(self, min_value: int = 0, max_value: int = 100, current: int = 0) -> QProgressBar:
        """
        Создает стилизованный прогресс-бар.

        Args:
            min_value: Минимальное значение
            max_value: Максимальное значение
            current: Текущее значение

        Returns:
            QProgressBar: Прогресс-бар
        """
        progress = QProgressBar()
        progress.setRange(min_value, max_value)
        progress.setValue(current)

        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self._get_color("border")};
                border-radius: 4px;
                text-align: center;
                background-color: {self._get_color("surface")};
                color: {self._get_color("text_primary")};
            }}
            QProgressBar::chunk {{
                background-color: {self._get_color("accent")};
                border-radius: 3px;
            }}
        """)

        return progress

    def create_separator(self, orientation: str = "horizontal") -> QFrame:
        """
        Создает разделительную линию.

        Args:
            orientation: Ориентация (horizontal, vertical)

        Returns:
            QFrame: Разделительная линия
        """
        separator = QFrame()

        if orientation == "horizontal":
            separator.setFrameShape(QFrame.Shape.HLine)
        else:
            separator.setFrameShape(QFrame.Shape.VLine)

        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {self._get_color("border")};
                background-color: {self._get_color("border")};
            }}
        """)

        return separator

    def create_card_widget(self, content_widget: QWidget, title: str = "") -> QFrame:
        """
        Создает карточку (виджет в рамке).

        Args:
            content_widget: Содержимое карточки
            title: Заголовок карточки

        Returns:
            QFrame: Карточка
        """
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(card)

        if title:
            title_label = self.create_styled_label(title, "subheading")
            layout.addWidget(title_label)

        layout.addWidget(content_widget)

        card.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {self._get_color("border")};
                border-radius: 8px;
                background-color: {self._get_color("surface")};
                padding: 12px;
                margin: 4px;
            }}
        """)

        return card

    def _get_font_for_style(self, style_type: str) -> Optional[QFont]:
        """Получает шрифт для указанного стиля."""
        if not self.theme_manager:
            return None

        if style_type == "heading":
            return self.theme_manager.get_font("heading")
        elif style_type == "subheading":
            return self.theme_manager.get_font("subheading")
        elif style_type == "code":
            return self.theme_manager.get_font("code")
        else:
            return self.theme_manager.get_font("body")

    def _get_color(self, color_key: str) -> str:
        """Получает цвет из темы или возвращает цвет по умолчанию."""
        if self.theme_manager:
            color = self.theme_manager.get_color(color_key)
            return color.name() if color else "#000000"
        return "#000000"

    def _lighten_color(self, color: str) -> str:
        """Осветляет цвет (упрощенная реализация)."""
        # Пока возвращаем тот же цвет
        # В реальной реализации можно использовать QColor.lighter()
        return color

    def _darken_color(self, color: str) -> str:
        """Затемняет цвет (упрощенная реализация)."""
        # Пока возвращаем тот же цвет
        # В реальной реализации можно использовать QColor.darker()
        return color
