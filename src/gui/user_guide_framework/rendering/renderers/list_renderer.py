"""
List Renderer - Рендерер для списков и структурированного контента
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .base_renderer import BaseRenderer


class ListRenderer(BaseRenderer):
    """
    Рендерер для различных типов списков.
    """

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов списков."""
        return ["list", "ordered_list", "checklist", "tree_list", "definition_list"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит список в соответствующий виджет.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный виджет списка
        """
        content_type = content.get("type")

        if content_type == "list":
            # Проверяем формат данных
            if "items" in content:
                # Новый формат: items напрямую в content
                items = content.get("items", [])
                list_type = content.get("list_type", "unordered")
            else:
                # Старый формат: items в content.content
                content_data = content.get("content", {})
                items = content_data.get("items", [])
                list_type = content_data.get("list_type", "unordered")

            if list_type == "ordered":
                return self._render_ordered_list_simple(items)
            else:
                return self._render_bullet_list_simple(items)
        elif content_type == "ordered_list":
            items = content.get("items", content.get("content", {}).get("items", []))
            return self._render_ordered_list_simple(items)
        elif content_type == "checklist":
            content_data = content.get("content", {})
            return self._render_checklist(content_data)
        elif content_type == "tree_list":
            content_data = content.get("content", {})
            return self._render_tree_list(content_data)
        elif content_type == "definition_list":
            content_data = content.get("content", {})
            return self._render_definition_list(content_data)
        else:
            items = content.get("items", [])
            return self._render_bullet_list_simple(items)

    def _render_bullet_list(self, list_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет маркированного списка.

        Args:
            list_data: Данные списка

        Returns:
            QWidget: Виджет списка
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = list_data.get("title", "")
        items = list_data.get("items", [])
        bullet_style = list_data.get("bullet_style", "•")

        # Заголовок списка
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
                    margin-bottom: 8px;
                }}
            """)
            layout.addWidget(title_label)

        # Элементы списка
        for item in items:
            item_layout = QHBoxLayout()

            # Маркер
            bullet_label = QLabel(bullet_style)
            bullet_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            bullet_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("accent")};
                    font-weight: bold;
                    padding: 2px 8px 2px 0px;
                    min-width: 20px;
                }}
            """)

            # Текст элемента
            if isinstance(item, str):
                text = item
            else:
                text = item.get("text", "")

            item_label = QLabel(text)
            item_label.setWordWrap(True)
            item_label.setTextFormat(Qt.TextFormat.RichText)

            font = self.get_theme_font("body")
            if font:
                item_label.setFont(font)

            item_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    padding: 2px 0px;
                    line-height: 1.4;
                }}
            """)

            item_layout.addWidget(bullet_label)
            item_layout.addWidget(item_label)
            item_layout.setStretchFactor(item_label, 1)

            layout.addLayout(item_layout)
            layout.addStretch()
        return container

    def _render_bullet_list_simple(self, items: List[str]) -> QWidget:
        """
        Создает виджет простого маркированного списка из массива строк.

        Args:
            items: Список строк для отображения

        Returns:
            QWidget: Виджет списка
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        # Проверяем валидность items
        if not items:
            items = []

        # Элементы списка
        for item in items:
            item_layout = QHBoxLayout()

            # Маркер
            bullet_label = QLabel("•")
            bullet_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            bullet_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("accent_primary")};
                    font-weight: bold;
                    padding: 0px 8px 0px 0px;
                    min-width: 16px;
                }}
            """)

            # Текст элемента
            text_label = QLabel(str(item))
            text_label.setWordWrap(True)
            text_label.setTextFormat(Qt.TextFormat.RichText)
            text_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    padding: 0px;
                    line-height: 1.4;
                }}
            """)

            item_layout.addWidget(bullet_label)
            item_layout.addWidget(text_label, 1)
            layout.addLayout(item_layout)

        layout.addStretch()
        return container

    def _render_ordered_list(self, list_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет нумерованного списка.

        Args:
            list_data: Данные списка

        Returns:
            QWidget: Виджет нумерованного списка
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = list_data.get("title", "")
        items = list_data.get("items", [])
        start_number = list_data.get("start", 1)

        # Заголовок
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            layout.addWidget(title_label)

        # Нумерованные элементы
        for i, item in enumerate(items, start=start_number):
            item_layout = QHBoxLayout()

            # Номер
            number_label = QLabel(f"{i}.")
            number_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            number_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("accent")};
                    font-weight: bold;
                    padding: 2px 8px 2px 0px;
                    min-width: 30px;
                }}
            """)

            # Текст
            if isinstance(item, str):
                text = item
            else:
                text = item.get("text", "")

            item_label = QLabel(text)
            item_label.setWordWrap(True)
            item_label.setTextFormat(Qt.TextFormat.RichText)

            item_layout.addWidget(number_label)
            item_layout.addWidget(item_label)
            item_layout.setStretchFactor(item_label, 1)

            layout.addLayout(item_layout)

        layout.addStretch()
        return container

    def _render_ordered_list_simple(self, items: List[str]) -> QWidget:
        """
        Создает виджет простого нумерованного списка из массива строк.

        Args:
            items: Список строк для отображения

        Returns:
            QWidget: Виджет списка
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        # Проверяем валидность items
        if not items:
            items = []

        # Элементы списка
        for i, item in enumerate(items, 1):
            item_layout = QHBoxLayout()

            # Номер
            number_label = QLabel(f"{i}.")
            number_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            number_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("accent_primary")};
                    font-weight: bold;
                    padding: 0px 8px 0px 0px;
                    min-width: 24px;
                }}
            """)

            # Текст элемента
            text_label = QLabel(str(item))
            text_label.setWordWrap(True)
            text_label.setTextFormat(Qt.TextFormat.RichText)
            text_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    padding: 0px;
                    line-height: 1.4;
                }}
            """)

            item_layout.addWidget(number_label)
            item_layout.addWidget(text_label, 1)
            layout.addLayout(item_layout)

        layout.addStretch()
        return container

    def _render_checklist(self, list_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет чек-листа.

        Args:
            list_data: Данные чек-листа

        Returns:
            QWidget: Виджет чек-листа
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = list_data.get("title", "")
        items = list_data.get("items", [])

        # Заголовок
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            layout.addWidget(title_label)

        # Элементы с чекбоксами
        for item in items:
            item_layout = QHBoxLayout()

            if isinstance(item, str):
                text = item
                checked = False
            else:
                text = item.get("text", "")
                checked = item.get("checked", False)

            # Чекбокс
            checkbox = QCheckBox()
            checkbox.setChecked(checked)

            # Текст
            item_label = QLabel(text)
            item_label.setWordWrap(True)

            # Стиль для выполненных пунктов
            if checked:
                item_label.setStyleSheet(f"""
                    QLabel {{
                        color: {self.get_theme_color("text_secondary")};
                        text-decoration: line-through;
                    }}
                """)

            item_layout.addWidget(checkbox)
            item_layout.addWidget(item_label)
            item_layout.setStretchFactor(item_label, 1)

            layout.addLayout(item_layout)

        layout.addStretch()
        return container

    def _render_tree_list(self, list_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет древовидного списка.

        Args:
            list_data: Данные дерева

        Returns:
            QWidget: Виджет дерева
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = list_data.get("title", "")
        items = list_data.get("items", [])

        # Заголовок
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            layout.addWidget(title_label)

        # Дерево
        tree_widget = QTreeWidget()
        tree_widget.setHeaderHidden(True)

        # Стилизация дерева
        tree_widget.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {self.get_theme_color("surface")};
                border: 1px solid {self.get_theme_color("border")};
                border-radius: 4px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 4px;
                color: {self.get_theme_color("text_primary")};
            }}
            QTreeWidget::item:selected {{
                background-color: {self.get_theme_color("accent")};
                color: white;
            }}
        """)

        # Добавляем элементы в дерево
        self._add_tree_items(tree_widget, items)

        tree_widget.expandAll()
        layout.addWidget(tree_widget)

        return container

    def _add_tree_items(self, parent_widget, items):
        """
        Рекурсивно добавляет элементы в дерево.

        Args:
            parent_widget: Родительский виджет или элемент
            items: Список элементов для добавления
        """
        for item_data in items:
            if isinstance(item_data, str):
                item = QTreeWidgetItem([item_data])
                parent_widget.addTopLevelItem(item)
            else:
                text = item_data.get("text", "")
                children = item_data.get("children", [])

                item = QTreeWidgetItem([text])
                parent_widget.addTopLevelItem(item)

                if children:
                    self._add_tree_items(item, children)

    def _render_definition_list(self, list_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет списка определений.

        Args:
            list_data: Данные списка определений

        Returns:
            QWidget: Виджет списка определений
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = list_data.get("title", "")
        definitions = list_data.get("definitions", [])

        # Заголовок
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            layout.addWidget(title_label)

        # Определения
        for definition in definitions:
            term = definition.get("term", "")
            description = definition.get("description", "")

            # Термин
            term_label = QLabel(f"<b>{term}</b>")
            term_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    font-weight: bold;
                    padding: 8px 0px 4px 0px;
                }}
            """)

            # Описание
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setTextFormat(Qt.TextFormat.RichText)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    padding: 0px 0px 8px 16px;
                    line-height: 1.4;
                }}
            """)

            layout.addWidget(term_label)
            layout.addWidget(desc_label)

        layout.addStretch()
        return container
