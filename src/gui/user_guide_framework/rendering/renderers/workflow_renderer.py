"""
Workflow Renderer - Рендерер для последовательностей действий и рабочих процессов
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .base_renderer import BaseRenderer


class WorkflowRenderer(BaseRenderer):
    """
    Рендерер для отображения пошаговых инструкций и рабочих процессов.
    """

    def get_supported_types(self) -> List[str]:
        """Возвращает список поддерживаемых типов workflow."""
        return ["workflow", "step_by_step", "process", "tutorial", "guide_section"]

    def render(self, content: Dict[str, Any]) -> QWidget:
        """
        Рендерит workflow контент.

        Args:
            content: Содержимое с типом и данными

        Returns:
            QWidget: Созданный workflow виджет
        """
        content_type = content.get("type")
        content_data = content.get("content", {})

        if content_type in ["workflow", "step_by_step", "tutorial"]:
            return self._render_step_by_step(content_data)
        elif content_type == "process":
            return self._render_process_flow(content_data)
        elif content_type == "guide_section":
            return self._render_guide_section(content_data)
        else:
            return self._render_step_by_step(content_data)

    def _render_step_by_step(self, workflow_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет пошаговых инструкций.

        Args:
            workflow_data: Данные workflow

        Returns:
            QWidget: Виджет пошаговых инструкций
        """
        container = QWidget()
        main_layout = QVBoxLayout(container)

        title = workflow_data.get("title", "")
        description = workflow_data.get("description", "")
        steps = workflow_data.get("steps", [])
        show_progress = workflow_data.get("show_progress", True)

        # Заголовок
        if title:
            title_label = QLabel(title)
            font = self.get_theme_font("heading")
            if font:
                title_label.setFont(font)

            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    font-weight: bold;
                    padding: 8px 0px;
                    border-bottom: 2px solid {self.get_theme_color("accent")};
                    margin-bottom: 12px;
                }}
            """)
            main_layout.addWidget(title_label)

        # Описание
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setTextFormat(Qt.TextFormat.RichText)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_secondary")};
                    padding: 8px 0px 16px 0px;
                    line-height: 1.4;
                }}
            """)
            main_layout.addWidget(desc_label)

        # Прогресс-бар
        if show_progress and steps:
            progress_layout = QHBoxLayout()
            progress_label = QLabel("Прогресс:")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, len(steps))
            progress_bar.setValue(0)
            progress_bar.setFormat("Шаг %v из %m")

            progress_layout.addWidget(progress_label)
            progress_layout.addWidget(progress_bar)
            main_layout.addLayout(progress_layout)

        # Создаем скроллируемую область для шагов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        steps_container = QWidget()
        steps_layout = QVBoxLayout(steps_container)

        # Отрисовка шагов
        for i, step in enumerate(steps, 1):
            step_widget = self._create_step_widget(step, i, len(steps))
            steps_layout.addWidget(step_widget)

        scroll_area.setWidget(steps_container)
        main_layout.addWidget(scroll_area)

        return container

    def _create_step_widget(self, step_data: Dict[str, Any], step_number: int, total_steps: int) -> QWidget:
        """
        Создает виджет для одного шага.

        Args:
            step_data: Данные шага
            step_number: Номер шага
            total_steps: Общее количество шагов

        Returns:
            QWidget: Виджет шага
        """
        step_container = self._create_step_container()
        layout = QVBoxLayout(step_container)

        # Заголовок шага
        title_layout = self._create_step_title(step_data, step_number)
        layout.addLayout(title_layout)

        # Описание шага
        self._add_step_description(layout, step_data)

        # Дополнительный контент
        self._add_step_content(layout, step_data)

        # Действия шага
        self._add_step_actions(layout, step_data)

        return step_container

    def _create_step_container(self) -> QFrame:
        """Создает контейнер для шага."""
        step_container = QFrame()
        step_container.setFrameStyle(QFrame.Shape.Box)
        step_container.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {self.get_theme_color("border")};
                border-radius: 8px;
                background-color: {self.get_theme_color("surface")};
                margin: 4px 0px;
                padding: 4px;
            }}
        """)
        return step_container

    def _create_step_title(self, step_data: Dict[str, Any], step_number: int) -> QHBoxLayout:
        """Создает заголовок шага."""
        step_title = step_data.get("title", f"Шаг {step_number}")
        title_layout = QHBoxLayout()

        # Номер шага в кружке
        step_number_label = QLabel(str(step_number))
        step_number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step_number_label.setFixedSize(30, 30)
        step_number_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_theme_color("accent")};
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)

        # Заголовок
        title_label = QLabel(step_title)
        font = self.get_theme_font("subheading")
        if font:
            title_label.setFont(font)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.get_theme_color("text_primary")};
                font-weight: bold;
                padding-left: 8px;
            }}
        """)

        title_layout.addWidget(step_number_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        return title_layout

    def _add_step_description(self, layout: QVBoxLayout, step_data: Dict[str, Any]) -> None:
        """Добавляет описание шага."""
        description = step_data.get("description", "")
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setTextFormat(Qt.TextFormat.RichText)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.get_theme_color("text_primary")};
                    padding: 8px 0px 8px 38px;
                    line-height: 1.4;
                }}
            """)
            layout.addWidget(desc_label)

    def _add_step_content(self, layout: QVBoxLayout, step_data: Dict[str, Any]) -> None:
        """Добавляет дополнительный контент шага."""
        content = step_data.get("content", [])
        for content_item in content:
            content_type = content_item.get("type", "")
            if content_type == "code":
                code_widget = self._create_code_snippet(content_item)
                layout.addWidget(code_widget)
            elif content_type == "note":
                note_widget = self._create_note(content_item)
                layout.addWidget(note_widget)

    def _add_step_actions(self, layout: QVBoxLayout, step_data: Dict[str, Any]) -> None:
        """Добавляет действия шага."""
        actions = step_data.get("actions", [])
        if not actions:
            return

        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        for action in actions:
            action_button = QPushButton(action.get("text", "Action"))
            action_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.get_theme_color("accent")};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin: 4px;
                }}
                QPushButton:hover {{
                    background-color: {self.get_theme_color("primary")};
                }}
            """)

            # Обработчики для действий
            action_type = action.get("type", "")
            if action_type == "next_step":
                action_button.clicked.connect(lambda: print("Next step"))
            elif action_type == "show_example":
                action_button.clicked.connect(lambda: print("Show example"))

            actions_layout.addWidget(action_button)

        layout.addLayout(actions_layout)

    def _render_process_flow(self, process_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет диаграммы процесса.

        Args:
            process_data: Данные процесса

        Returns:
            QWidget: Виджет процесса
        """
        container = QWidget()
        layout = QVBoxLayout(container)

        title = process_data.get("title", "Process Flow")
        stages = process_data.get("stages", [])

        # Заголовок
        title_label = QLabel(title)
        font = self.get_theme_font("heading")
        if font:
            title_label.setFont(font)
        layout.addWidget(title_label)

        # Горизонтальный поток процесса
        flow_layout = QHBoxLayout()

        for i, stage in enumerate(stages):
            # Блок этапа
            stage_widget = self._create_process_stage(stage, i + 1)
            flow_layout.addWidget(stage_widget)

            # Стрелка между этапами
            if i < len(stages) - 1:
                arrow_label = QLabel("→")
                arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                arrow_label.setStyleSheet(f"""
                    QLabel {{
                        color: {self.get_theme_color("accent")};
                        font-size: 20px;
                        font-weight: bold;
                        padding: 0px 8px;
                    }}
                """)
                flow_layout.addWidget(arrow_label)

        layout.addLayout(flow_layout)
        return container

    def _create_process_stage(self, stage_data: Dict[str, Any], stage_number: int) -> QWidget:
        """
        Создает виджет этапа процесса.

        Args:
            stage_data: Данные этапа
            stage_number: Номер этапа

        Returns:
            QWidget: Виджет этапа
        """
        stage_container = QFrame()
        stage_container.setFrameStyle(QFrame.Shape.Box)
        stage_container.setFixedWidth(150)
        stage_container.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {self.get_theme_color("accent")};
                border-radius: 8px;
                background-color: {self.get_theme_color("surface")};
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(stage_container)

        # Номер этапа
        number_label = QLabel(str(stage_number))
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_theme_color("accent")};
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
                padding: 4px;
                margin-bottom: 4px;
            }}
        """)

        # Название этапа
        title = stage_data.get("title", f"Stage {stage_number}")
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.get_theme_color("text_primary")};
                font-weight: bold;
                text-align: center;
            }}
        """)

        layout.addWidget(number_label)
        layout.addWidget(title_label)

        return stage_container

    def _render_guide_section(self, section_data: Dict[str, Any]) -> QWidget:
        """
        Создает виджет раздела руководства.

        Args:
            section_data: Данные раздела

        Returns:
            QWidget: Виджет раздела
        """
        container = QGroupBox(section_data.get("title", "Guide Section"))
        layout = QVBoxLayout(container)

        # Контент раздела
        content = section_data.get("content", [])
        for content_item in content:
            content_type = content_item.get("type", "")
            if content_type == "paragraph":
                widget = self._create_paragraph(content_item.get("content", ""))
                layout.addWidget(widget)

        return container

    def _create_code_snippet(self, code_data: Dict[str, Any]) -> QWidget:
        """
        Создает простой код сниппет (упрощенная версия).

        Args:
            code_data: Данные кода

        Returns:
            QWidget: Виджет кода
        """
        code_label = QLabel(f"<pre>{code_data.get('code', '')}</pre>")
        code_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_theme_color("surface")};
                border: 1px solid {self.get_theme_color("border")};
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                margin: 8px 0px;
            }}
        """)
        return code_label

    def _create_note(self, note_data: Dict[str, Any]) -> QWidget:
        """
        Создает простую заметку.

        Args:
            note_data: Данные заметки

        Returns:
            QWidget: Виджет заметки
        """
        note_label = QLabel(f"💡 {note_data.get('content', '')}")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 8px;
                margin: 8px 0px;
                color: #856404;
            }
        """)
        return note_label

    def _create_paragraph(self, text: str) -> QWidget:
        """
        Создает простой параграф.

        Args:
            text: Текст параграфа

        Returns:
            QWidget: Виджет параграфа
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setStyleSheet(f"""
            QLabel {{
                color: {self.get_theme_color("text_primary")};
                padding: 4px 0px;
                line-height: 1.4;
            }}
        """)
        return label
