"""
Guide Toolbar - Панель инструментов для управления руководством
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from ..core.localization_manager import LocalizationManager
from ..core.theme_manager import ThemeManager


class GuideToolBar(QWidget):
    """
    Панель инструментов для управления функциями руководства.
    """

    search_requested = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    print_requested = pyqtSignal()
    export_requested = pyqtSignal()

    def __init__(self, localization_manager: LocalizationManager, theme_manager: ThemeManager, parent=None):
        """
        Инициализация панели инструментов.

        Args:
            localization_manager: Менеджер локализации
            theme_manager: Менеджер тем
            parent: Родительский виджет
        """
        super().__init__(parent)

        self.localization_manager = localization_manager
        self.theme_manager = theme_manager
        self.current_language = "ru"

        self.setup_ui()
        self.setup_connections()
        self.apply_theme()

    def setup_ui(self) -> None:
        """Инициализация UI компонентов."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Группа поиска
        self._create_search_group(layout)

        # Разделитель
        separator1 = self._create_separator()
        layout.addWidget(separator1)

        # Группа настроек отображения
        self._create_display_group(layout)

        # Разделитель
        separator2 = self._create_separator()
        layout.addWidget(separator2)

        # Группа экспорта
        self._create_export_group(layout)

        # Растяжка
        layout.addStretch()

        # Информация о разделе
        self._create_info_group(layout)

    def _create_search_group(self, layout: QHBoxLayout) -> None:
        """Создание группы поиска."""
        # Метка поиска
        search_label = QLabel("Поиск:")
        layout.addWidget(search_label)

        # Поле поиска
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Введите запрос...")
        self.search_field.setMaximumWidth(200)
        layout.addWidget(self.search_field)

        # Кнопка поиска
        self.search_button = QPushButton("🔍")
        self.search_button.setFixedSize(32, 24)
        self.search_button.setToolTip("Поиск по содержимому")
        layout.addWidget(self.search_button)

        # Кнопка очистки
        self.clear_button = QPushButton("✖")
        self.clear_button.setFixedSize(32, 24)
        self.clear_button.setToolTip("Очистить поиск")
        layout.addWidget(self.clear_button)

    def _create_display_group(self, layout: QHBoxLayout) -> None:
        """Создание группы настроек отображения."""
        # Выбор темы
        theme_label = QLabel("Тема:")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная", "Высокий контраст"])
        self.theme_combo.setCurrentText("Светлая")
        self.theme_combo.setMaximumWidth(120)
        layout.addWidget(self.theme_combo)

        # Размер шрифта
        font_label = QLabel("Шрифт:")
        layout.addWidget(font_label)

        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Мелкий", "Обычный", "Крупный"])
        self.font_size_combo.setCurrentText("Обычный")
        self.font_size_combo.setMaximumWidth(80)
        layout.addWidget(self.font_size_combo)

    def _create_export_group(self, layout: QHBoxLayout) -> None:
        """Создание группы экспорта."""
        # Кнопка печати
        self.print_button = QPushButton("🖨")
        self.print_button.setFixedSize(32, 24)
        self.print_button.setToolTip("Печать текущего раздела")
        layout.addWidget(self.print_button)

        # Кнопка экспорта
        self.export_button = QPushButton("💾")
        self.export_button.setFixedSize(32, 24)
        self.export_button.setToolTip("Экспорт в PDF")
        layout.addWidget(self.export_button)

    def _create_info_group(self, layout: QHBoxLayout) -> None:
        """Создание группы информации."""
        # Информация о текущем разделе
        self.section_info = QLabel("Готов к работе")
        self.section_info.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-style: italic;
                padding: 4px;
            }
        """)
        layout.addWidget(self.section_info)

    def _create_separator(self) -> QWidget:
        """Создание вертикального разделителя."""
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("""
            QWidget {
                background-color: #dee2e6;
                margin: 2px 4px;
            }
        """)
        return separator

    def setup_connections(self) -> None:
        """Настройка соединений сигналов."""
        # Поиск
        self.search_button.clicked.connect(self.on_search_clicked)
        self.search_field.returnPressed.connect(self.on_search_clicked)
        self.clear_button.clicked.connect(self.on_clear_search)

        # Настройки отображения
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.font_size_combo.currentTextChanged.connect(self.on_font_size_changed)

        # Экспорт
        self.print_button.clicked.connect(self.print_requested)
        self.export_button.clicked.connect(self.export_requested)

    def on_search_clicked(self) -> None:
        """Обработка поискового запроса."""
        query = self.search_field.text().strip()
        if query:
            self.search_requested.emit(query)

    def on_clear_search(self) -> None:
        """Очистка поискового поля."""
        self.search_field.clear()

    def on_theme_changed(self, theme_text: str) -> None:
        """Обработка смены темы."""
        theme_map = {"Светлая": "default", "Темная": "dark", "Высокий контраст": "high_contrast"}

        theme_name = theme_map.get(theme_text, "default")
        self.theme_changed.emit(theme_name)

    def on_font_size_changed(self, size_text: str) -> None:
        """Обработка смены размера шрифта."""
        # Здесь можно добавить логику изменения размера шрифта
        pass

    def set_section_info(self, section_name: str) -> None:
        """Установка информации о текущем разделе."""
        if section_name:
            self.section_info.setText(f"Раздел: {section_name}")
        else:
            self.section_info.setText("Готов к работе")

    def update_language(self, language: str) -> None:
        """Обновление языка интерфейса."""
        self.current_language = language

        if language == "en":
            # Обновляем тексты на английский
            self._update_english_labels()
        else:
            # Обновляем тексты на русский
            self._update_russian_labels()

    def _update_russian_labels(self) -> None:
        """Обновление меток на русский язык."""
        # Обновляем placeholder и тексты
        self.search_field.setPlaceholderText("Введите запрос...")

        # Обновляем tooltips
        self.search_button.setToolTip("Поиск по содержимому")
        self.clear_button.setToolTip("Очистить поиск")
        self.print_button.setToolTip("Печать текущего раздела")
        self.export_button.setToolTip("Экспорт в PDF")

    def _update_english_labels(self) -> None:
        """Обновление меток на английский язык."""
        # Обновляем placeholder и тексты
        self.search_field.setPlaceholderText("Enter search query...")

        # Обновляем tooltips
        self.search_button.setToolTip("Search content")
        self.clear_button.setToolTip("Clear search")
        self.print_button.setToolTip("Print current section")
        self.export_button.setToolTip("Export to PDF")

    def apply_theme(self) -> None:
        """Применение текущей темы."""
        if not self.theme_manager:
            return

        # Получаем цвета темы
        bg_color = self.theme_manager.get_color("background")
        text_color = self.theme_manager.get_color("text_primary")
        border_color = self.theme_manager.get_color("border")
        accent_color = self.theme_manager.get_color("accent")

        if not all([bg_color, text_color, border_color, accent_color]):
            return

        # Применяем стили
        self.setStyleSheet(f"""
            GuideToolBar {{
                background-color: {bg_color.name()};
                border-bottom: 1px solid {border_color.name()};
                padding: 4px;
            }}

            QLabel {{
                color: {text_color.name()};
                font-weight: bold;
            }}

            QLineEdit {{
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                color: {text_color.name()};
            }}

            QLineEdit:focus {{
                border: 2px solid {accent_color.name()};
            }}

            QComboBox {{
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                color: {text_color.name()};
            }}

            QPushButton {{
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                background-color: {accent_color.name()};
                color: white;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {accent_color.lighter(110).name()};
            }}

            QPushButton:pressed {{
                background-color: {accent_color.darker(110).name()};
            }}
        """)

    def get_current_search_query(self) -> str:
        """Возвращает текущий поисковый запрос."""
        return self.search_field.text().strip()

    def set_search_query(self, query: str) -> None:
        """Устанавливает поисковый запрос."""
        self.search_field.setText(query)
