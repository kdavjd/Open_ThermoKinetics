"""
Content Widget - Виджет динамического отображения контента
"""

from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from src.core.logger_config import LoggerManager
from src.core.state_logger import StateLogger
from src.gui.user_guide_tab.user_guide_framework.core.content_manager import ContentManager, ContentSection
from src.gui.user_guide_tab.user_guide_framework.core.localization_manager import LocalizationManager
from src.gui.user_guide_tab.user_guide_framework.rendering.renderer_manager import RendererManager

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


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
        logger.info("Initializing ContentWidget")

        self.content_manager = content_manager
        self.renderer_manager = renderer_manager
        self.localization_manager = localization_manager

        # Initialize state logger for comprehensive tracking
        self.state_logger = StateLogger("ContentWidget")

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
        # Type validation with StateLogger
        self.state_logger.assert_state(
            isinstance(section_id, str), "section_id must be string", section_id=section_id, type=type(section_id)
        )

        if section_id == self.current_section:
            return

        self.state_logger.log_state_change(
            "section_change", {"current_section": self.current_section}, {"current_section": section_id}
        )

        self.current_section = section_id

        # Используем таймер для избежания множественных обновлений
        self.update_timer.stop()
        self.update_timer.start(50)  # 50ms задержка    def _update_content_delayed(self) -> None:
        """Отложенное обновление контента с безопасной проверкой типов."""
        if not self.current_section:
            return

        self.state_logger.log_operation_start("content_update", section_id=self.current_section)
        self._clear_content()

        try:
            section_content = self._get_and_validate_content()
            if section_content is None:
                return

            self._render_section_content(section_content)
            self._finalize_content_update()

        except Exception as e:
            self.state_logger.log_error("Error loading content", error=str(e), section_id=self.current_section)
            self._show_error_message(f"Ошибка загрузки контента: {e}")

    def _get_and_validate_content(self):
        """Get and validate section content."""
        section_content = self.content_manager.get_section_content(self.current_section)

        if section_content is None:
            self.state_logger.log_error("No content found for section", section_id=self.current_section)
            self._show_error_message("Раздел не найден")
            return None

        # Validate content structure
        self.state_logger.assert_state(
            hasattr(section_content, "content"),
            "Section content must have content attribute",
            section_id=self.current_section,
        )

        return section_content

    def _render_section_content(self, section_content) -> None:
        """Render section content and metadata."""
        # Отображение метаданных раздела
        self._display_section_metadata(section_content)

        # Get content blocks for current language
        content_blocks = self._get_content_blocks(section_content)
        if not content_blocks:
            self._show_error_message("Контент для данного языка недоступен")
            return

        # Render content blocks
        self._render_content_blocks(content_blocks)

        # Display related sections if available
        if hasattr(section_content, "related_sections"):
            self._display_related_sections(section_content.related_sections)

    def _get_content_blocks(self, section_content) -> list:
        """Get content blocks for current language with fallback."""
        content_blocks = section_content.content.get(self.current_language, [])
        if not content_blocks:
            # Try English as fallback
            content_blocks = section_content.content.get("en", [])
        return content_blocks

    def _render_content_blocks(self, content_blocks: list) -> None:
        """Render individual content blocks."""
        for block in content_blocks:
            try:
                validated_block = self._validate_content_block(block)
                if validated_block is None:
                    continue

                widget = self.renderer_manager.render_block(validated_block)
                if widget:
                    self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
            except Exception as e:
                self.state_logger.log_error("Error rendering block", error=str(e), block=block)
                error_widget = self._create_error_block(f"Ошибка рендеринга блока: {e}")
                self.content_layout.insertWidget(self.content_layout.count() - 1, error_widget)

    def _validate_content_block(self, block):
        """Validate and normalize content block."""
        if isinstance(block, str):
            return {"type": "text", "content": block}
        elif isinstance(block, dict):
            return block
        else:
            self.state_logger.log_error(
                "Invalid content block type", block_type=type(block), section_id=self.current_section
            )
            return None

    def _finalize_content_update(self) -> None:
        """Finalize content update."""
        # Scroll to top
        self.scroll_area.verticalScrollBar().setValue(0)
        self.state_logger.log_operation_end("content_update", success=True)

    def _display_section_metadata(self, section: ContentSection) -> None:
        """Отображение метаданных раздела."""
        if not hasattr(section, "metadata") or not section.metadata:
            return

        metadata = section.metadata

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
            try:
                section_content = self.content_manager.get_section_content(section_id)
                if section_content and hasattr(section_content, "metadata"):
                    title = section_content.metadata.get("title", {}).get(self.current_language, section_id)
                else:
                    title = section_id

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
                related_layout.addWidget(link_label)
            except Exception as e:
                self.state_logger.log_warning("Error loading related section", section_id=section_id, error=str(e))

        self.content_layout.insertWidget(self.content_layout.count() - 1, related_widget)

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

    def update_theme(self) -> None:
        """Update theme for content widget."""
        # Theme update implementation can be added here
        pass
