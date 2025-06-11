"""
Guide Framework - Главный фреймворк пользовательского руководства
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QSplitter, QVBoxLayout, QWidget

from src.core.logger_config import LoggerManager
from src.gui.user_guide_tab.user_guide_framework.core.content_manager import ContentManager
from src.gui.user_guide_tab.user_guide_framework.core.localization_manager import LocalizationManager
from src.gui.user_guide_tab.user_guide_framework.core.navigation_manager import NavigationManager
from src.gui.user_guide_tab.user_guide_framework.core.theme_manager import ThemeManager
from src.gui.user_guide_tab.user_guide_framework.rendering.renderer_manager import RendererManager
from src.gui.user_guide_tab.user_guide_framework.ui.content_widget import ContentWidget
from src.gui.user_guide_tab.user_guide_framework.ui.guide_toolbar import GuideToolBar
from src.gui.user_guide_tab.user_guide_framework.ui.navigation_sidebar import NavigationSidebar
from src.gui.user_guide_tab.user_guide_framework.ui.status_widget import StatusWidget

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


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
        logger.info(f"Initializing GuideFramework with data directory: {data_directory}")

        # Инициализация менеджеров
        try:
            self.content_manager = ContentManager(data_directory)
            self.navigation_manager = NavigationManager(self.content_manager)
            self.theme_manager = ThemeManager(data_directory / "themes")
            self.localization_manager = LocalizationManager(data_directory / "lang")
            self.renderer_manager = RendererManager(self.theme_manager)
            logger.debug("All managers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize managers: {e}")
            raise

        # Загрузка тем и локализации
        try:
            self._initialize_managers()
            logger.debug("Managers initialization completed")
        except Exception as e:
            logger.error(f"Failed to initialize managers: {e}")
            raise

        # Настройка UI
        try:
            self.setup_ui()
            self.setup_connections()
            logger.debug("UI setup completed")
        except Exception as e:
            logger.error(f"Failed to setup UI: {e}")
            raise

        # Установка минимальных размеров
        self.setMinimumSize(1200, 700)
        logger.info("GuideFramework initialization completed successfully")

    def _initialize_managers(self) -> None:
        """Инициализация менеджеров с загрузкой данных."""
        logger.debug("Initializing theme and localization managers")
        try:
            # Загружаение доступных тем
            self.theme_manager.load_available_themes()
            self.theme_manager.set_theme("default")

            # Загрузка языков
            self.localization_manager.load_available_languages()
            self.localization_manager.set_language("ru")
            logger.debug("Managers initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing managers: {e}")
            raise

    def setup_ui(self) -> None:
        """Инициализация главного UI layout."""
        logger.debug("Setting up GuideFramework UI layout")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создание главного splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)

        # Навигационная боковая панель
        logger.debug("Creating navigation sidebar")
        self.navigation_sidebar = NavigationSidebar(self.navigation_manager, self.theme_manager)
        self.navigation_sidebar.setMinimumWidth(250)
        self.navigation_sidebar.setMaximumWidth(375)
        self.splitter.addWidget(self.navigation_sidebar)

        # Область контента
        logger.debug("Creating content area")
        content_area = self._create_content_area()
        self.splitter.addWidget(content_area)

        # Установка пропорций splitter
        self.splitter.setSizes([300, 900])
        logger.debug("GuideFramework UI setup completed")

    def _create_content_area(self) -> QWidget:
        """Создание области отображения контента с панелью инструментов и статусом."""
        logger.debug("Creating content area with toolbar and status")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Панель инструментов
        self.toolbar = GuideToolBar(self.localization_manager, self.theme_manager)
        layout.addWidget(self.toolbar)

        # Область контента
        self.content_widget = ContentWidget(self.renderer_manager, self.content_manager, self.theme_manager)
        layout.addWidget(self.content_widget)  # Статусная панель
        self.status_widget = StatusWidget(self.theme_manager, self)
        layout.addWidget(self.status_widget)

        logger.debug("Content area created successfully")
        return widget

    def setup_connections(self) -> None:
        """Настройка сигналов и слотов между компонентами."""
        logger.debug("Setting up signal connections")  # Навигация
        self.navigation_sidebar.section_selected.connect(self.on_section_selected)
        self.navigation_sidebar.section_selected.connect(self.section_changed)
        self.navigation_sidebar.language_changed.connect(self.on_language_changed)
        self.navigation_sidebar.language_changed.connect(self.language_changed)

        # Панель инструментов
        self.toolbar.theme_changed.connect(self.on_theme_changed)

        # TODO: Add content-related signal connections when needed

        logger.debug("Signal connections established")

    def on_section_selected(self, section_id: str) -> None:
        """Обработка выбора раздела."""
        logger.info(f"Section selected: {section_id}")
        try:
            # Display the section directly using section_id
            self.content_widget.display_section(section_id)
            self.status_widget.update_section_info(section_id)
            logger.debug(f"Content displayed for section: {section_id}")
        except Exception as e:
            logger.error(f"Error displaying section {section_id}: {e}")

    def on_language_changed(self, language_code: str) -> None:
        """Обработка смены языка."""
        logger.info(f"Language changed to: {language_code}")
        try:
            self.localization_manager.set_language(language_code)
            self.navigation_sidebar.update_language()
            self.toolbar.update_language()
            self.status_widget.update_language()

            # Обновление контента для текущего раздела
            current_section = self.navigation_sidebar.get_current_section()
            if current_section:
                self.on_section_selected(current_section)

            logger.debug(f"Language successfully changed to: {language_code}")
        except Exception as e:
            logger.error(f"Error changing language to {language_code}: {e}")

    def on_theme_changed(self, theme_name: str) -> None:
        """Обработка смены темы."""
        logger.info(f"Theme changed to: {theme_name}")
        try:
            self.theme_manager.set_theme(theme_name)
            self.navigation_sidebar.update_theme()
            self.toolbar.update_theme()
            self.content_widget.update_theme()
            self.status_widget.update_theme()
            logger.debug(f"Theme successfully changed to: {theme_name}")
        except Exception as e:
            logger.error(f"Error changing theme to {theme_name}: {e}")

    def set_language(self, language_code: str) -> None:
        """Установка языка программно."""
        logger.info(f"Setting language programmatically to: {language_code}")
        self.toolbar.set_language(language_code)

    def set_section(self, section_id: str) -> None:
        """Установка раздела программно."""
        logger.info(f"Setting section programmatically to: {section_id}")
        self.navigation_sidebar.select_section(section_id)

    def get_current_section(self) -> Optional[str]:
        """Получение текущего раздела."""
        current_section = self.navigation_sidebar.get_current_section()
        logger.debug(f"Current section: {current_section}")
        return current_section

    def get_current_language(self) -> str:
        """Получение текущего языка."""
        current_language = self.localization_manager.get_current_language()
        logger.debug(f"Current language: {current_language}")
        return current_language
