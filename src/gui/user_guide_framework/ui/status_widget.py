"""
Status Widget - Виджет статуса для User Guide Framework
"""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget

from ..core.theme_manager import ThemeManager


class StatusWidget(QWidget):
    """
    Виджет для отображения статуса и прогресса операций.
    """

    def __init__(self, theme_manager: ThemeManager, parent=None):
        """
        Инициализация виджета статуса.

        Args:
            theme_manager: Менеджер тем
            parent: Родительский виджет
        """
        super().__init__(parent)

        self.theme_manager = theme_manager
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_temporary_status)

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self) -> None:
        """Инициализация UI компонентов."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)

        # Основной статус
        self.status_label = QLabel("Готов")
        self.status_label.setMinimumWidth(120)
        layout.addWidget(self.status_label)

        # Текущий раздел
        self.section_label = QLabel("")
        layout.addWidget(self.section_label)

        # Растяжка
        layout.addStretch()

        # Прогресс-бар (скрыт по умолчанию)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)

        # Дополнительная информация
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.info_label)

    def set_status(self, message: str, status_type: str = "info") -> None:
        """
        Установка основного статуса.

        Args:
            message: Текст статуса
            status_type: Тип статуса (info, success, warning, error)
        """
        self.status_label.setText(message)

        # Применяем стили в зависимости от типа
        color_map = {"info": "#17a2b8", "success": "#28a745", "warning": "#ffc107", "error": "#dc3545"}

        color = color_map.get(status_type, "#17a2b8")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                padding: 2px 8px;
                border-radius: 4px;
                background-color: {color}22;
            }}
        """)

    def set_temporary_status(self, message: str, status_type: str = "info", timeout: int = 3000) -> None:
        """
        Установка временного статуса с автоочисткой.

        Args:
            message: Текст статуса
            status_type: Тип статуса
            timeout: Время показа в миллисекундах
        """
        self.set_status(message, status_type)
        self.status_timer.start(timeout)

    def clear_temporary_status(self) -> None:
        """Очистка временного статуса."""
        self.set_status("Готов")

    def set_current_section(self, section_name: str) -> None:
        """
        Установка информации о текущем разделе.

        Args:
            section_name: Название раздела
        """
        if section_name:
            self.section_label.setText(f"Раздел: {section_name}")
        else:
            self.section_label.setText("")

    def show_progress(self, maximum: int = 100) -> None:
        """
        Показать прогресс-бар.

        Args:
            maximum: Максимальное значение прогресса
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

    def update_progress(self, value: int) -> None:
        """
        Обновление значения прогресса.

        Args:
            value: Текущее значение прогресса
        """
        self.progress_bar.setValue(value)

    def hide_progress(self) -> None:
        """Скрыть прогресс-бар."""
        self.progress_bar.setVisible(False)

    def set_info(self, info_text: str) -> None:
        """
        Установка дополнительной информации.

        Args:
            info_text: Дополнительная информация
        """
        self.info_label.setText(info_text)

    def clear_info(self) -> None:
        """Очистка дополнительной информации."""
        self.info_label.setText("")

    def show_loading(self, message: str = "Загрузка...") -> None:
        """
        Показать индикатор загрузки.

        Args:
            message: Сообщение загрузки
        """
        self.set_status(message, "info")
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setVisible(True)

    def hide_loading(self) -> None:
        """Скрыть индикатор загрузки."""
        self.hide_progress()
        self.set_status("Готов")

    def show_error(self, error_message: str) -> None:
        """
        Показать сообщение об ошибке.

        Args:
            error_message: Текст ошибки
        """
        self.set_temporary_status(f"Ошибка: {error_message}", "error", 5000)

    def show_success(self, success_message: str) -> None:
        """
        Показать сообщение об успехе.

        Args:
            success_message: Текст успеха
        """
        self.set_temporary_status(success_message, "success", 2000)

    def show_warning(self, warning_message: str) -> None:
        """
        Показать предупреждение.

        Args:
            warning_message: Текст предупреждения
        """
        self.set_temporary_status(warning_message, "warning", 4000)

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
            StatusWidget {{
                background-color: {bg_color.name()};
                border-top: 1px solid {border_color.name()};
                padding: 4px;
            }}

            QLabel {{
                color: {text_color.name()};
            }}

            QProgressBar {{
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }}

            QProgressBar::chunk {{
                background-color: {accent_color.name()};
                border-radius: 3px;
            }}
        """)

    def update_language(self, language: str) -> None:
        """
        Обновление языка интерфейса.

        Args:
            language: Код языка
        """
        if language == "en":
            # Обновляем тексты на английский
            if self.status_label.text() == "Готов":
                self.status_label.setText("Ready")

            current_section = self.section_label.text()
            if current_section.startswith("Раздел:"):
                section_name = current_section.replace("Раздел:", "").strip()
                self.section_label.setText(f"Section: {section_name}")
        else:
            # Обновляем тексты на русский
            if self.status_label.text() == "Ready":
                self.status_label.setText("Готов")

            current_section = self.section_label.text()
            if current_section.startswith("Section:"):
                section_name = current_section.replace("Section:", "").strip()
                self.section_label.setText(f"Раздел: {section_name}")

    def get_current_status(self) -> str:
        """Возвращает текущий статус."""
        return self.status_label.text()

    def is_loading(self) -> bool:
        """Проверяет, активен ли индикатор загрузки."""
        return self.progress_bar.isVisible() and self.progress_bar.maximum() == 0
