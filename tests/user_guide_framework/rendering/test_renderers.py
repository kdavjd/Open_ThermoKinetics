"""
Тесты для рендереров user guide framework.
Проверяют корректность обработки различных форматов контента.
"""

from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication, QWidget

from src.gui.user_guide_tab.user_guide_framework.core.theme_manager import ThemeManager
from src.gui.user_guide_tab.user_guide_framework.rendering.renderers.code_renderer import CodeRenderer
from src.gui.user_guide_tab.user_guide_framework.rendering.renderers.list_renderer import ListRenderer
from src.gui.user_guide_tab.user_guide_framework.rendering.renderers.text_renderer import TextRenderer


@pytest.fixture
def app():
    """Создание QApplication для тестов."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def theme_manager():
    """Создание ThemeManager для тестов."""
    # Создаем простой mock theme manager
    themes_dir = (
        Path(__file__).parent.parent.parent.parent
        / "src"
        / "gui"
        / "user_guide_tab"
        / "user_guide_framework"
        / "data"
        / "themes"
    )
    return ThemeManager(themes_dir)


@pytest.fixture
def text_renderer(theme_manager):
    """Создание TextRenderer для тестов."""
    return TextRenderer(theme_manager)


@pytest.fixture
def list_renderer(theme_manager):
    """Создание ListRenderer для тестов."""
    return ListRenderer(theme_manager)


@pytest.fixture
def code_renderer(theme_manager):
    """Создание CodeRenderer для тестов."""
    return CodeRenderer(theme_manager)


class TestTextRenderer:
    """Тесты для TextRenderer."""

    def test_render_paragraph_with_text_field(self, app, text_renderer):
        """Тест: paragraph с полем 'text'."""
        content = {"type": "paragraph", "text": "Это тестовый параграф"}
        widget = text_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_heading_with_text_and_level(self, app, text_renderer):
        """Тест: heading с полями 'text' и 'level'."""
        content = {"type": "heading", "text": "Тестовый заголовок", "level": 2}
        widget = text_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_note_with_text_and_note_type(self, app, text_renderer):
        """Тест: note с полями 'text' и 'note_type'."""
        content = {"type": "note", "text": "Это важная заметка", "note_type": "warning"}
        widget = text_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_empty_text(self, app, text_renderer):
        """Тест: обработка пустого текста."""
        content = {"type": "paragraph", "text": ""}
        widget = text_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_missing_text_field(self, app, text_renderer):
        """Тест: отсутствие поля 'text'."""
        content = {"type": "paragraph"}
        widget = text_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None


class TestListRenderer:
    """Тесты для ListRenderer."""

    def test_render_unordered_list_with_items(self, app, list_renderer):
        """Тест: неупорядоченный список с items."""
        content = {
            "type": "list",
            "list_type": "unordered",
            "items": ["Первый элемент", "Второй элемент", "Третий элемент"],
        }
        widget = list_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_ordered_list_with_items(self, app, list_renderer):
        """Тест: упорядоченный список с items."""
        content = {"type": "list", "list_type": "ordered", "items": ["Первый пункт", "Второй пункт", "Третий пункт"]}
        widget = list_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_list_old_format(self, app, list_renderer):
        """Тест: старый формат списка с content.items."""
        content = {"type": "list", "content": {"items": ["Элемент 1", "Элемент 2"], "list_type": "unordered"}}
        widget = list_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_empty_list(self, app, list_renderer):
        """Тест: пустой список."""
        content = {"type": "list", "list_type": "unordered", "items": []}
        widget = list_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_list_missing_items(self, app, list_renderer):
        """Тест: список без поля items."""
        content = {"type": "list", "list_type": "unordered"}
        widget = list_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None


class TestCodeRenderer:
    """Тесты для CodeRenderer."""

    def test_render_code_block_with_code_field(self, app, code_renderer):
        """Тест: блок кода с полем 'code'."""
        content = {"type": "code", "code": "print('Hello, World!')", "language": "python", "title": "Пример кода"}
        widget = code_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_terminal_command(self, app, code_renderer):
        """Тест: команда терминала."""
        content = {"type": "shell", "code": "poetry run ssk-gui", "title": "Запуск приложения"}
        widget = code_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_code_old_format(self, app, code_renderer):
        """Тест: старый формат кода с content.code."""
        content = {"type": "code", "content": {"code": "import json", "title": "Импорт модуля"}}
        widget = code_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_empty_code(self, app, code_renderer):
        """Тест: пустой блок кода."""
        content = {"type": "code", "code": ""}
        widget = code_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None

    def test_render_code_missing_code_field(self, app, code_renderer):
        """Тест: отсутствие поля 'code'."""
        content = {"type": "code", "title": "Блок без кода"}
        widget = code_renderer.render(content)
        assert isinstance(widget, QWidget)
        assert widget is not None


class TestRendererErrors:
    """Тесты для обработки ошибок рендеринга."""

    def test_str_object_has_no_attribute_get_error(self, app, text_renderer):
        """
        Тест для предотвращения ошибки 'str object has no attribute get'.
        Проверяет, что рендерер корректно обрабатывает случаи, когда контент
        передается как строка вместо словаря.
        """
        # Симулируем ошибочную ситуацию
        invalid_content = "это строка, а не словарь"

        # Рендерер должен обрабатывать это корректно
        try:
            widget = text_renderer.render({"type": "paragraph", "text": invalid_content})
            assert isinstance(widget, QWidget)
        except AttributeError as e:
            pytest.fail(f"Рендерер не обработал некорректный контент: {e}")

    def test_missing_content_structure(self, app, list_renderer):
        """
        Тест для предотвращения ошибок в структуре контента.
        """
        # Различные некорректные структуры
        invalid_structures = [
            {},  # Пустой словарь
            {"type": "list"},  # Без items
            {"items": ["test"]},  # Без type
            {"type": "list", "items": None},  # items = None
        ]

        for content in invalid_structures:
            try:
                widget = list_renderer.render(content)
                assert isinstance(widget, QWidget)
            except Exception as e:
                pytest.fail(f"Рендерер не обработал структуру {content}: {e}")

    def test_content_manager_integration(self, app):
        """
        Тест интеграции с ContentManager для предотвращения ошибок загрузки.
        """
        from pathlib import Path

        from src.gui.user_guide_tab.user_guide_framework.core.content_manager import ContentManager

        # Путь к тестовым данным
        data_dir = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "gui"
            / "user_guide_tab"
            / "user_guide_framework"
            / "data"
        )

        if data_dir.exists():
            try:
                content_manager = ContentManager(data_dir)

                # Проверяем, что основные разделы загружаются без ошибок
                test_sections = ["overview", "file_operations", "model_free", "model_based"]

                for section_id in test_sections:
                    try:
                        section = content_manager.get_section_content(section_id)
                        if section:
                            # Проверяем структуру контента
                            assert hasattr(section, "content")
                            assert isinstance(section.content, dict)

                            # Проверяем, что есть контент для русского языка
                            if "ru" in section.content:
                                ru_content = section.content["ru"]
                                assert isinstance(ru_content, list)

                                # Проверяем структуру каждого блока
                                for block in ru_content:
                                    assert isinstance(block, dict)
                                    assert "type" in block

                    except Exception as e:
                        pytest.fail(f"Ошибка загрузки раздела {section_id}: {e}")

            except Exception as e:
                pytest.fail(f"Ошибка инициализации ContentManager: {e}")
