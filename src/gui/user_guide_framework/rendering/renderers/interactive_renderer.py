"""
Interactive Renderer - Рендерер для интерактивных элементов
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .base_renderer import BaseRenderer


class InteractiveRenderer(BaseRenderer):
    """
    Рендерер для интерактивных элементов: слайдеры, кнопки, формы.
    """

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых интерактивных элементов."""
        return ["interactive_widget", "parameter_adjustment", "form", "button_group", "slider_group"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит интерактивный элемент.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный интерактивный виджет
        """
        content_type = content.get("type")
        content_data = content.get("content", {})

        if content_type == "interactive_widget":
            widget_type = content_data.get("widget_type", "")
            if widget_type == "parameter_adjustment":
                return self._create_parameter_widget(content_data)
            elif widget_type == "slider":
                return self._create_slider_widget(content_data)
            elif widget_type == "button":
                return self._create_button_widget(content_data)
        elif content_type == "parameter_adjustment":
            return self._create_parameter_widget(content_data)
        elif content_type == "form":
            return self._create_form_widget(content_data)
        elif content_type == "button_group":
            return self._create_button_group(content_data)
        elif content_type == "slider_group":
            return self._create_slider_group(content_data)

        return self._create_placeholder("Unknown interactive widget type")

    def _create_parameter_widget(self, config: Dict[str, Any]) -> QWidget:
        """
        Создает виджет настройки параметров (аналог AdjustmentRowWidget).

        Args:
            config: Конфигурация параметра

        Returns:
            QWidget: Виджет настройки параметра
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        parameter_name = config.get("parameter_name", "Parameter")
        initial_value = config.get("initial_value", 0.0)
        min_value = config.get("min_value", -100.0)
        max_value = config.get("max_value", 100.0)
        step = config.get("step", 1.0)
        decimals = config.get("decimals", 2)

        # Заголовок параметра
        title_label = QLabel(f"{parameter_name}: {initial_value:.{decimals}f}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                color: {self.get_theme_color("text_primary")};
                padding: 4px;
                background-color: {self.get_theme_color("surface")};
                border-radius: 4px;
                margin-bottom: 8px;
            }}
        """)
        layout.addWidget(title_label)

        # Горизонтальный контейнер для контролов
        controls_layout = QHBoxLayout()

        # Кнопка уменьшения
        decrease_button = QPushButton("◀")
        decrease_button.setMaximumWidth(30)
        decrease_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.get_theme_color("accent")};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.get_theme_color("primary")};
            }}
        """)

        # Слайдер
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(25)

        # Кнопка увеличения
        increase_button = QPushButton("▶")
        increase_button.setMaximumWidth(30)
        increase_button.setStyleSheet(decrease_button.styleSheet())

        controls_layout.addWidget(decrease_button)
        controls_layout.addWidget(slider)
        controls_layout.addWidget(increase_button)

        layout.addLayout(controls_layout)

        # Поле ввода значения
        value_input = QDoubleSpinBox()
        value_input.setRange(min_value, max_value)
        value_input.setValue(initial_value)
        value_input.setDecimals(decimals)
        value_input.setSingleStep(step)
        value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_input)

        # Связываем контролы
        current_value = initial_value

        def update_value(new_value):
            nonlocal current_value
            current_value = new_value
            title_label.setText(f"{parameter_name}: {current_value:.{decimals}f}")
            value_input.setValue(current_value)

        def on_slider_change(slider_value):
            offset = slider_value * step / 10
            update_value(initial_value + offset)

        def on_decrease():
            update_value(max(min_value, current_value - step))

        def on_increase():
            update_value(min(max_value, current_value + step))

        def on_input_change(value):
            update_value(value)

        slider.valueChanged.connect(on_slider_change)
        decrease_button.clicked.connect(on_decrease)
        increase_button.clicked.connect(on_increase)
        value_input.valueChanged.connect(on_input_change)

        return container

    def _create_slider_widget(self, config: Dict[str, Any]) -> QWidget:
        """
        Создает простой слайдер.

        Args:
            config: Конфигурация слайдера

        Returns:
            QWidget: Виджет слайдера
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = config.get("title", "Slider")
        min_value = config.get("min", 0)
        max_value = config.get("max", 100)
        initial_value = config.get("value", 50)

        # Заголовок
        title_label = QLabel(f"{title}: {initial_value}")
        layout.addWidget(title_label)

        # Слайдер
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(initial_value)

        def on_value_change(value):
            title_label.setText(f"{title}: {value}")

        slider.valueChanged.connect(on_value_change)
        layout.addWidget(slider)

        return container

    def _create_button_widget(self, config: Dict[str, Any]) -> QWidget:
        """
        Создает кнопку.

        Args:
            config: Конфигурация кнопки

        Returns:
            QWidget: Виджет кнопки
        """
        text = config.get("text", "Button")
        action = config.get("action", "")

        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.get_theme_color("accent")};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.get_theme_color("primary")};
            }}
            QPushButton:pressed {{
                background-color: {self.get_theme_color("secondary")};
            }}
        """)

        if action:
            button.clicked.connect(lambda: print(f"Action: {action}"))

        return button

    def _create_form_widget(self, config: Dict[str, Any]) -> QWidget:
        """
        Создает форму с полями ввода.

        Args:
            config: Конфигурация формы

        Returns:
            QWidget: Виджет формы
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = config.get("title", "Form")
        fields = config.get("fields", [])

        # Заголовок формы
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            layout.addWidget(title_label)

        # Форма
        form_layout = QFormLayout()

        for field in fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "text")
            field_label = field.get("label", field_name)
            default_value = field.get("default", "")

            if field_type == "text":
                widget = QLineEdit(str(default_value))
            elif field_type == "number":
                widget = QSpinBox()
                widget.setValue(int(default_value) if default_value else 0)
            elif field_type == "decimal":
                widget = QDoubleSpinBox()
                widget.setValue(float(default_value) if default_value else 0.0)
            elif field_type == "combo":
                widget = QComboBox()
                options = field.get("options", [])
                widget.addItems(options)
            elif field_type == "checkbox":
                widget = QCheckBox()
                widget.setChecked(bool(default_value))
            else:
                widget = QLineEdit(str(default_value))

            form_layout.addRow(field_label, widget)

        layout.addLayout(form_layout)

        # Кнопки формы
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        submit_button = QPushButton("Submit")
        reset_button = QPushButton("Reset")

        submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.get_theme_color("success")};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
        """)

        reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.get_theme_color("secondary")};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
        """)

        buttons_layout.addWidget(submit_button)
        buttons_layout.addWidget(reset_button)

        layout.addLayout(buttons_layout)

        return container

    def _create_button_group(self, config: Dict[str, Any]) -> QWidget:
        """
        Создает группу кнопок.

        Args:
            config: Конфигурация группы кнопок

        Returns:
            QWidget: Виджет группы кнопок
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = config.get("title", "")
        buttons = config.get("buttons", [])
        orientation = config.get("orientation", "horizontal")

        if title:
            title_label = QLabel(title)
            layout.addWidget(title_label)

        if orientation == "horizontal":
            buttons_layout = QHBoxLayout()
        else:
            buttons_layout = QVBoxLayout()

        for button_config in buttons:
            button = self._create_button_widget(button_config)
            buttons_layout.addWidget(button)

        layout.addLayout(buttons_layout)
        return container

    def _create_slider_group(self, config: Dict[str, Any]) -> QWidget:
        """
        Создает группу слайдеров.

        Args:
            config: Конфигурация группы слайдеров

        Returns:
            QWidget: Виджет группы слайдеров
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = config.get("title", "")
        sliders = config.get("sliders", [])

        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("subheading")
            if font:
                title_label.setFont(font)
            layout.addWidget(title_label)

        for slider_config in sliders:
            slider_widget = self._create_slider_widget(slider_config)
            layout.addWidget(slider_widget)

        return container

    def _create_placeholder(self, message: str) -> QWidget:
        """
        Создает placeholder для неизвестных типов.

        Args:
            message: Сообщение placeholder

        Returns:
            QWidget: Placeholder виджет
        """
        placeholder = QLabel(message)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"""
            QLabel {{
                border: 1px dashed {self.get_theme_color("border")};
                border-radius: 4px;
                padding: 20px;
                background-color: {self.get_theme_color("surface")};
                color: {self.get_theme_color("text_secondary")};
            }}
        """)
        return placeholder
