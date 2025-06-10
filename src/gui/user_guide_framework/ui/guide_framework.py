"""
Guide Framework - Главный фреймворк пользовательского руководства
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QSplitter, QVBoxLayout, QWidget

from ..core.content_manager import ContentManager
from ..core.localization_manager import LocalizationManager
from ..core.navigation_manager import NavigationManager
from ..core.theme_manager import ThemeManager
from ..rendering.renderer_manager import RendererManager
from .content_widget import ContentWidget
from .guide_toolbar import GuideToolBar
from .navigation_sidebar import NavigationSidebar
from .status_widget import StatusWidget


class GuideFramework(QWidget):
    """
    Главный фреймворк для user guide приложения.
    Объединяет все компоненты: навигацию, контент, инструменты.
    """

    section_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    def __init__(self, data_directory: Path, parent=None):
        """
        Инициализация фреймворка.

        Args:
            data_directory: Путь к директории с данными
            parent: Родительский виджет
        """
        super().__init__(parent)

        # Инициализация менеджеров
        self.content_manager = ContentManager(data_directory)
        self.navigation_manager = NavigationManager(self.content_manager)
        self.theme_manager = ThemeManager(data_directory / "themes")
        self.localization_manager = LocalizationManager(data_directory / "lang")
        self.renderer_manager = RendererManager(self.theme_manager)

        # Загрузка тем и локализации
        self._initialize_managers()

        # Настройка UI
        self.setup_ui()
        self.setup_connections()

        # Установка минимальных размеров
        self.setMinimumSize(1200, 700)

    def _initialize_managers(self) -> None:
        """Инициализация менеджеров с загрузкой данных."""
        try:
            # Загружаение доступных тем
            self.theme_manager.load_available_themes()
            self.theme_manager.set_theme("default")

            # Загрузка языков
            self.localization_manager.load_available_languages()
            self.localization_manager.set_language("ru")

        except Exception as e:
            print(f"Error initializing managers: {e}")

    def setup_ui(self) -> None:
        """Инициализация главного UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создание главного splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)  # Навигационная боковая панель
        self.navigation_sidebar = NavigationSidebar(self.navigation_manager, self.theme_manager)
        self.navigation_sidebar.setMinimumWidth(250)
        self.navigation_sidebar.setMaximumWidth(375)
        self.splitter.addWidget(self.navigation_sidebar)

        # Область контента
        content_area = self._create_content_area()
        self.splitter.addWidget(content_area)

        # Установка пропорций splitter
        self.splitter.setSizes([300, 900])

    def _create_content_area(self) -> QWidget:
        """Создание области отображения контента с панелью инструментов и статусом."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Панель инструментов
        self.toolbar = GuideToolBar(self.localization_manager, self.theme_manager)
        layout.addWidget(self.toolbar)

        # Виджет контента
        self.content_widget = ContentWidget(self.content_manager, self.renderer_manager, self.localization_manager)
        layout.addWidget(self.content_widget)  # Статусный виджет
        self.status_widget = StatusWidget(self.theme_manager)
        layout.addWidget(self.status_widget)

        return widget

    def setup_connections(self) -> None:
        """Настройка соединений сигналов и слотов."""
        # Навигация
        self.navigation_sidebar.section_selected.connect(self.on_section_selected)
        self.navigation_sidebar.language_changed.connect(self.on_language_changed)

        # Панель инструментов
        self.toolbar.search_requested.connect(self.on_search_requested)
        self.toolbar.theme_changed.connect(self.on_theme_changed)

        # Пробрасываем сигналы наружу
        self.navigation_sidebar.section_selected.connect(self.section_changed)
        self.navigation_sidebar.language_changed.connect(self.language_changed)

    def on_section_selected(self, section_id: str) -> None:
        """Обработка выбора раздела."""
        self.content_widget.display_section(section_id)
        self.status_widget.set_current_section(section_id)

    def on_language_changed(self, language: str) -> None:
        """Обработка смены языка."""
        self.localization_manager.set_language(language)

        # Обновляем все компоненты
        self.navigation_sidebar.update_language(language)
        self.content_widget.update_language(language)
        self.toolbar.update_language(language)
        self.status_widget.update_language(language)

    def on_search_requested(self, query: str) -> None:
        """Обработка поискового запроса."""
        results = self.content_manager.search_content(query, self.localization_manager.current_language)
        self.content_widget.display_search_results(results)

    def on_theme_changed(self, theme_name: str) -> None:
        """Обработка смены темы."""
        self.theme_manager.set_theme(theme_name)

        # Обновляем рендерер
        self.renderer_manager.theme_manager = self.theme_manager

        # Обновляем текущий контент
        current_section = self.content_widget.current_section
        if current_section:
            self.content_widget.display_section(current_section)

    def get_current_section(self) -> Optional[str]:
        """Возвращает текущий выбранный раздел."""
        return self.content_widget.current_section

    def set_section(self, section_id: str) -> None:
        """Программная установка текущего раздела."""
        self.navigation_sidebar.select_section(section_id)

    def get_current_language(self) -> str:
        """Возвращает текущий язык."""
        return self.localization_manager.current_language

    def set_language(self, language: str) -> None:
        """Программная установка языка."""
        self.navigation_sidebar.set_language(language)
