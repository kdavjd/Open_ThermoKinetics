"""
Content Widget - Виджет динамического отображения контента
"""

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..core.content_manager import ContentManager, ContentSection
from ..core.localization_manager import LocalizationManager
from ..rendering.renderer_manager import RendererManager


class ContentWidget(QWidget):
    """
    Виджет для динамического отображения контента разделов руководства.
    """

    def __init__(
        self,
        content_manager: ContentManager,
        renderer_manager: RendererManager,
        localization_manager: LocalizationManager,
        parent=None,
    ):
        """
        Инициализация виджета контента.

        Args:
            content_manager: Менеджер контента
            renderer_manager: Менеджер рендеринга
            localization_manager: Менеджер локализации
            parent: Родительский виджет
        """
        super().__init__(parent)

        self.content_manager = content_manager
        self.renderer_manager = renderer_manager
        self.localization_manager = localization_manager

        self.current_section: Optional[str] = None
        self.current_language = "ru"

        self.setup_ui()

        # Таймер для обновления контента
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_content_delayed)

    def setup_ui(self) -> None:
        """Инициализация UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создание области прокрутки
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Контейнер для контента
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)

        # Добавление растяжки в конец
        self.content_layout.addStretch()

        self.scroll_area.setWidget(self.content_container)
        layout.addWidget(self.scroll_area)

        # Показываем приветственное сообщение
        self._show_welcome_message()

    def _show_welcome_message(self) -> None:
        """Показ приветственного сообщения."""
        welcome_label = QLabel("Добро пожаловать в руководство пользователя!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 40px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)

        self.content_layout.insertWidget(0, welcome_label)

    def display_section(self, section_id: str) -> None:
        """
        Отображение контента для указанного раздела.

        Args:
            section_id: Идентификатор раздела
        """
        if section_id == self.current_section:
            return

        self.current_section = section_id

        # Используем таймер для избежания множественных обновлений
        self.update_timer.stop()
        self.update_timer.start(50)  # 50ms задержка

    def _update_content_delayed(self) -> None:
        """Отложенное обновление контента."""
        if not self.current_section:
            return

        self._clear_content()

        # Получение контента раздела
        section_content = self.content_manager.get_section_content(self.current_section)
        if not section_content:
            self._show_error_message("Раздел не найден")
            return

        try:
            # Отображение метаданных раздела
            self._display_section_metadata(section_content)

            # Рендеринг блоков контента
            content_blocks = section_content.content.get(self.current_language, [])
            if not content_blocks:
                # Пробуем английский как fallback
                content_blocks = section_content.content.get("en", [])

            if not content_blocks:
                self._show_error_message("Контент для данного языка недоступен")
                return

            # Рендеринг каждого блока
            for block in content_blocks:
                try:
                    widget = self.renderer_manager.render_block(block)
                    if widget:
                        self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
                except Exception as e:
                    error_widget = self._create_error_block(f"Ошибка рендеринга блока: {e}")
                    self.content_layout.insertWidget(self.content_layout.count() - 1, error_widget)

            # Отображение связанных разделов
            self._display_related_sections(section_content.related_sections)

            # Прокрутка в начало
            self.scroll_area.verticalScrollBar().setValue(0)

        except Exception as e:
            self._show_error_message(f"Ошибка загрузки контента: {e}")

    def _display_section_metadata(self, section: ContentSection) -> None:
        """Отображение метаданных раздела."""
        metadata = section.metadata

        if not metadata:
            return

        # Создание контейнера метаданных
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)

        # Заголовок раздела
        title = metadata.get("title", {}).get(self.current_language, section.section_id)
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 8px 0px;
                    border-bottom: 2px solid #3498db;
                    margin-bottom: 16px;
                }
            """)
            metadata_layout.addWidget(title_label)

        # Описание
        description = metadata.get("description", {}).get(self.current_language, "")
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #6c757d;
                    padding: 8px 0px 16px 0px;
                    line-height: 1.5;
                }
            """)
            metadata_layout.addWidget(desc_label)

        # Дополнительная информация
        info_layout = QHBoxLayout()

        # Сложность
        difficulty = metadata.get("difficulty", "")
        if difficulty:
            difficulty_label = QLabel(f"Сложность: {difficulty}")
            difficulty_label.setStyleSheet("QLabel { color: #17a2b8; font-weight: bold; }")
            info_layout.addWidget(difficulty_label)

        # Время
        estimated_time = metadata.get("estimated_time", "")
        if estimated_time:
            time_label = QLabel(f"Время: {estimated_time}")
            time_label.setStyleSheet("QLabel { color: #28a745; font-weight: bold; }")
            info_layout.addWidget(time_label)

        info_layout.addStretch()

        if info_layout.count() > 1:  # Есть хотя бы одна метка
            metadata_layout.addLayout(info_layout)

        self.content_layout.insertWidget(0, metadata_widget)

    def _display_related_sections(self, related_sections: List[str]) -> None:
        """Отображение связанных разделов."""
        if not related_sections:
            return

        related_widget = QWidget()
        related_layout = QVBoxLayout(related_widget)

        # Заголовок
        header_label = QLabel("Связанные разделы:")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 0px;
                margin-top: 20px;
            }
        """)
        related_layout.addWidget(header_label)

        # Список связанных разделов
        for section_id in related_sections:
            # Получаем информацию о разделе
            section_content = self.content_manager.get_section_content(section_id)
            if section_content:
                title = section_content.metadata.get("title", {}).get(self.current_language, section_id)

                link_label = QLabel(f"• {title}")
                link_label.setStyleSheet("""
                    QLabel {
                        color: #3498db;
                        padding: 2px 16px;
                        text-decoration: underline;
                    }
                    QLabel:hover {
                        color: #2980b9;
                    }
                """)
                link_label.setCursor(Qt.CursorShape.PointingHandCursor)

                # Здесь можно добавить обработчик клика для навигации

                related_layout.addWidget(link_label)

        self.content_layout.insertWidget(self.content_layout.count() - 1, related_widget)

    def display_search_results(self, results: List[Dict]) -> None:
        """
        Отображение результатов поиска.

        Args:
            results: Список результатов поиска
        """
        self._clear_content()

        # Заголовок результатов
        header_label = QLabel(f"Результаты поиска ({len(results)} найдено)")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 0px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 16px;
            }
        """)
        self.content_layout.insertWidget(0, header_label)

        # Отображение результатов
        for result in results:
            result_widget = self._create_search_result_widget(result)
            self.content_layout.insertWidget(self.content_layout.count() - 1, result_widget)

        # Прокрутка в начало
        self.scroll_area.verticalScrollBar().setValue(0)

    def _create_search_result_widget(self, result: Dict) -> QWidget:
        """Создание виджета результата поиска."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок результата
        title = result.get("title", "Без названия")
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #3498db;
                text-decoration: underline;
            }
        """)
        title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(title_label)

        # Фрагмент текста
        snippet = result.get("snippet", "")
        if snippet:
            snippet_label = QLabel(snippet)
            snippet_label.setWordWrap(True)
            snippet_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    padding: 4px 0px;
                    line-height: 1.4;
                }
            """)
            layout.addWidget(snippet_label)

        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: #f8f9fa;
                margin: 4px 0px;
                padding: 8px;
            }
        """)

        return widget

    def _clear_content(self) -> None:
        """Очистка текущего контента."""
        # Удаляем все виджеты кроме растяжки
        while self.content_layout.count() > 1:
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_error_message(self, message: str) -> None:
        """Отображение сообщения об ошибке."""
        self._clear_content()

        error_label = QLabel(f"Ошибка: {message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 16px;
                font-weight: bold;
                padding: 20px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                margin: 20px;
            }
        """)

        self.content_layout.insertWidget(0, error_label)

    def _create_error_block(self, message: str) -> QWidget:
        """Создание виджета ошибки для блока."""
        error_label = QLabel(f"⚠️ {message}")
        error_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 8px;
                margin: 4px 0px;
            }
        """)
        return error_label

    def update_language(self, language: str) -> None:
        """Обновление языка интерфейса."""
        if language != self.current_language:
            self.current_language = language

            # Перерендеринг текущего раздела
            if self.current_section:
                self.display_section(self.current_section)
