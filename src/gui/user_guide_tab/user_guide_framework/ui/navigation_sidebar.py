"""
Navigation Sidebar - Боковая панель навигации для User Guide Framework
"""

from typing import Optional

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTreeView, QVBoxLayout, QWidget

from src.core.logger_config import LoggerManager
from src.core.state_logger import StateLogger
from src.gui.user_guide_tab.user_guide_framework.core.navigation_manager import NavigationManager
from src.gui.user_guide_tab.user_guide_framework.core.theme_manager import ThemeManager

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class NavigationSidebar(QWidget):
    section_selected = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    def __init__(self, navigation_manager: NavigationManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        logger.info("Initializing NavigationSidebar")

        self.navigation_manager = navigation_manager
        self.theme_manager = theme_manager
        self.current_language = "ru"

        # Initialize state logger for comprehensive tracking
        self.state_logger = StateLogger("NavigationSidebar")
        self.state_logger.log_operation_start("initialization")

        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["Разделы"])

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        try:
            self._setup_ui()
            self._connect_signals()
            logger.debug("NavigationSidebar setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup NavigationSidebar: {e}")
            raise
        self._load_navigation_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        title_label = QLabel("Навигация")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English"])
        header_layout.addWidget(self.language_combo)
        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск...")
        search_layout.addWidget(self.search_field)

        self.clear_search_button = QPushButton("")
        self.clear_search_button.setFixedSize(24, 24)
        search_layout.addWidget(self.clear_search_button)
        layout.addLayout(search_layout)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(True)
        layout.addWidget(self.tree_view)

    def _connect_signals(self):
        self.tree_view.clicked.connect(self.on_tree_item_clicked)
        self.search_field.textChanged.connect(self.on_search_text_changed)
        self.clear_search_button.clicked.connect(self.clear_search)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

    def _load_navigation_data(self):
        try:
            self.tree_model.clear()
            self.tree_model.setHorizontalHeaderLabels(["Разделы"])
            nav_structure = self.navigation_manager.get_navigation_structure()
            self._build_tree_recursive(nav_structure, self.tree_model.invisibleRootItem())
            self.tree_view.expandToDepth(0)
        except Exception as e:
            print(f"Ошибка загрузки навигации: {e}")

    def _build_tree_recursive(self, nodes, parent_item):
        for node in nodes:
            title = node.title.get(self.current_language, node.section_id)
            item = QStandardItem(title)
            item.setData(node.section_id, role=1000)
            item.setToolTip(title)
            parent_item.appendRow(item)
            if node.children:
                self._build_tree_recursive(node.children, item)

    def on_tree_item_clicked(self, index):
        if not index.isValid():
            return
        item = self.tree_model.itemFromIndex(index)
        if item:
            section_id = item.data(role=1000)
            if section_id:
                self.section_selected.emit(section_id)

    def on_search_text_changed(self, text):
        self.search_timer.start(300)

    def perform_search(self):
        """Выполнение поиска (заглушка)."""
        # TODO: Реализовать поиск по разделам
        pass

    def clear_search(self):
        self.search_field.clear()

    def on_language_changed(self, language_text):
        language_code = "ru" if language_text == "Русский" else "en"
        if language_code != self.current_language:
            before_state = {"language": self.current_language}
            self.current_language = language_code
            after_state = {"language": self.current_language}

            self.state_logger.log_state_change("language_change", before_state, after_state)
            self._load_navigation_data()
            self.language_changed.emit(language_code)

    def set_language(self, language: str) -> None:
        """
        Установка языка интерфейса.

        Args:
            language: Код языка (ru, en)
        """
        if language != self.current_language:
            self.current_language = language
            self.update_language(language)

    def update_language(self, language: str) -> None:
        """
        Обновление языка интерфейса.

        Args:
            language: Код языка (ru, en)
        """
        if language == self.current_language:
            return  # Язык уже установлен, не нужно обновлять

        self.current_language = language

        # Обновляем комбобокс языков
        if hasattr(self, "language_combo"):
            # Обновляем выбранный элемент без излучения сигнала
            index = 0 if language == "ru" else 1
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(index)
            self.language_combo.blockSignals(False)

        # Перестраиваем дерево навигации с новым языком
        self._load_navigation_data()

        # НЕ излучаем сигнал, так как этот метод вызывается в ответ на сигнал

    def get_current_language(self):
        return self.current_language

    def refresh_navigation(self):
        self._load_navigation_data()

    def update_theme(self) -> None:
        """Update theme for navigation sidebar."""
        logger.debug("NavigationSidebar: Updating theme")

        if not self.theme_manager:
            logger.warning("ThemeManager not available for NavigationSidebar theme update")
            return

        try:
            # Apply theme colors to UI elements
            bg_color = self.theme_manager.get_color("background")
            text_color = self.theme_manager.get_color("text_primary")
            border_color = self.theme_manager.get_color("border")

            logger.debug(f"NavigationSidebar: Theme colors - bg: {bg_color.name()}, text: {text_color.name()}")

            if all([bg_color, text_color, border_color]):
                self.setStyleSheet(f"""
                    NavigationSidebar {{
                        background-color: {bg_color.name()};
                        color: {text_color.name()};
                        border-right: 1px solid {border_color.name()};
                    }}
                    QTreeView {{
                        background-color: {bg_color.name()};
                        color: {text_color.name()};
                        border: none;
                    }}
                    QComboBox {{
                        background-color: {bg_color.name()};
                        color: {text_color.name()};
                        border: 1px solid {border_color.name()};
                    }}
                    QLineEdit {{
                        background-color: {bg_color.name()};
                        color: {text_color.name()};
                        border: 1px solid {border_color.name()};
                    }}
                """)
                logger.debug("NavigationSidebar theme updated successfully")
            else:
                logger.warning("Some theme colors are missing, using default styling")
        except Exception as e:
            logger.error(f"Error updating NavigationSidebar theme: {e}")

    def get_current_section(self) -> Optional[str]:
        """Get currently selected section ID."""
        current_index = self.tree_view.currentIndex()
        if current_index.isValid():
            item = self.tree_model.itemFromIndex(current_index)
            if item:
                section_id = item.data(role=1000)
                logger.debug(f"Current section: {section_id}")
                return section_id
        logger.debug("No section currently selected")
        return None

    def select_section(self, section_id: str) -> None:
        """Programmatically select a section."""
        logger.debug(f"Selecting section programmatically: {section_id}")
        # Find the item with the given section_id
        root_item = self.tree_model.invisibleRootItem()
        item_to_select = self._find_item_by_section_id(root_item, section_id)

        if item_to_select:
            index = self.tree_model.indexFromItem(item_to_select)
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)
            logger.debug(f"Section {section_id} selected successfully")
        else:
            logger.warning(f"Section {section_id} not found in navigation tree")

    def _find_item_by_section_id(self, parent_item, section_id: str):
        """Recursively find item by section_id."""
        for row in range(parent_item.rowCount()):
            item = parent_item.child(row)
            if item and item.data(role=1000) == section_id:
                return item
            # Search in children
            found_item = self._find_item_by_section_id(item, section_id)
            if found_item:
                return found_item
        return None
