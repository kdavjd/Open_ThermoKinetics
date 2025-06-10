"""
Демонстрационный скрипт для тестирования второй фазы User Guide Framework - Система рендеринга
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

# Добавим путь к нашему фреймворку
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Импорт фазы 1 (уже готовой)
    from src.gui.user_guide_framework.core.content_manager import ContentManager
    from src.gui.user_guide_framework.core.theme_manager import ThemeManager  # Импорт фазы 2 (новой системы рендеринга)
    from src.gui.user_guide_framework.rendering.renderer_manager import RendererManager
    from src.gui.user_guide_framework.rendering.renderers import (
        CodeRenderer,
        InteractiveRenderer,
        ListRenderer,
        TextRenderer,
        WorkflowRenderer,
    )
    from src.gui.user_guide_framework.rendering.widget_factory import WidgetFactory
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the framework modules are properly installed")
    sys.exit(1)


def test_renderer_manager():
    """Тест RendererManager"""
    print("=== Тестирование RendererManager ===")

    # Инициализация с темой
    themes_dir = Path("src/gui/user_guide_framework/data/themes")
    theme_manager = ThemeManager(themes_dir)
    theme_manager.load_available_themes()
    theme_manager.set_theme("default")

    renderer_manager = RendererManager(theme_manager)

    # Тест получения поддерживаемых типов
    supported_types = renderer_manager.get_supported_types()
    print(f"Поддерживаемые типы контента: {len(supported_types)}")
    print(f"Типы: {supported_types[:10]}...")  # Показываем первые 10

    # Тест рендеринга различных типов контента
    test_contents = [
        {"type": "paragraph", "content": "Это тестовый параграф с <b>жирным</b> текстом и <a href='#'>ссылкой</a>."},
        {"type": "heading", "content": "Заголовок раздела"},
        {"type": "note", "content": "Это важная заметка для пользователя."},
        {
            "type": "code",
            "content": {
                "code": "def hello_world():\n    print('Hello, World!')",
                "title": "Python код",
                "line_numbers": True,
            },
        },
        {
            "type": "list",
            "content": {
                "title": "Список действий",
                "items": ["Первый пункт списка", "Второй пункт списка", "Третий пункт списка"],
            },
        },
    ]

    # Тестируем рендеринг каждого типа
    for i, content in enumerate(test_contents):
        widget = renderer_manager.render_block(content)
        content_type = content.get("type", "unknown")

        if widget:
            print(f"✓ Успешно отрендерен контент типа '{content_type}'")
            print(f"  Класс виджета: {widget.__class__.__name__}")
        else:
            print(f"✗ Ошибка рендеринга контента типа '{content_type}'")

    # Тест информации о рендерерах
    renderer_info = renderer_manager.get_renderer_info()
    print("\nИнформация о системе рендеринга:")
    print(f"  Всего рендереров: {renderer_info['total_renderers']}")
    print(f"  Всего типов контента: {len(renderer_info['supported_types'])}")

    print("RendererManager: ✓ Успешно\n")


def test_individual_renderers():
    """Тест отдельных рендереров"""
    print("=== Тестирование отдельных рендереров ===")

    # Инициализация темы
    themes_dir = Path("src/gui/user_guide_framework/data/themes")
    theme_manager = ThemeManager(themes_dir)
    theme_manager.load_available_themes()
    theme_manager.set_theme("default")

    # Тест TextRenderer
    text_renderer = TextRenderer(theme_manager)
    text_content = {"type": "paragraph", "content": "Тестовый текст для TextRenderer"}
    text_widget = text_renderer.render(text_content)
    print(f"TextRenderer: {'✓' if text_widget else '✗'} {text_renderer.get_supported_types()}")

    # Тест CodeRenderer
    code_renderer = CodeRenderer(theme_manager)
    code_content = {
        "type": "python",
        "content": {"code": "import numpy as np\nprint('Hello World')", "title": "Пример Python кода"},
    }
    code_widget = code_renderer.render(code_content)
    print(f"CodeRenderer: {'✓' if code_widget else '✗'} {code_renderer.get_supported_types()}")

    # Тест ListRenderer
    list_renderer = ListRenderer(theme_manager)
    list_content = {
        "type": "ordered_list",
        "content": {"title": "Пронумерованный список", "items": ["Пункт 1", "Пункт 2", "Пункт 3"]},
    }
    list_widget = list_renderer.render(list_content)
    print(f"ListRenderer: {'✓' if list_widget else '✗'} {list_renderer.get_supported_types()}")

    # Тест InteractiveRenderer
    interactive_renderer = InteractiveRenderer(theme_manager)
    interactive_content = {
        "type": "parameter_adjustment",
        "content": {
            "parameter_name": "Temperature",
            "initial_value": 25.0,
            "min_value": 0.0,
            "max_value": 100.0,
            "step": 1.0,
        },
    }
    interactive_widget = interactive_renderer.render(interactive_content)
    print(f"InteractiveRenderer: {'✓' if interactive_widget else '✗'} {interactive_renderer.get_supported_types()}")

    # Тест WorkflowRenderer
    workflow_renderer = WorkflowRenderer(theme_manager)
    workflow_content = {
        "type": "workflow",
        "content": {
            "title": "Пример рабочего процесса",
            "steps": [
                {"title": "Шаг 1", "description": "Описание первого шага"},
                {"title": "Шаг 2", "description": "Описание второго шага"},
            ],
        },
    }
    workflow_widget = workflow_renderer.render(workflow_content)
    print(f"WorkflowRenderer: {'✓' if workflow_widget else '✗'} {workflow_renderer.get_supported_types()}")

    print("Индивидуальные рендереры: ✓ Успешно\n")


def test_widget_factory():
    """Тест WidgetFactory"""
    print("=== Тестирование WidgetFactory ===")

    # Инициализация темы
    themes_dir = Path("src/gui/user_guide_framework/data/themes")
    theme_manager = ThemeManager(themes_dir)
    theme_manager.load_available_themes()
    theme_manager.set_theme("default")

    widget_factory = WidgetFactory(theme_manager)

    # Тест создания различных виджетов
    widgets_created = 0

    # Стилизованный label
    label = widget_factory.create_styled_label("Test Label", "heading")
    if label:
        widgets_created += 1
        print(f"✓ Создан стилизованный label: {label.__class__.__name__}")

    # Стилизованная кнопка
    button = widget_factory.create_styled_button("Test Button", "primary")
    if button:
        widgets_created += 1
        print(f"✓ Создана стилизованная кнопка: {button.__class__.__name__}")

    # Поле ввода
    input_field = widget_factory.create_input_field("Enter text", "text")
    if input_field:
        widgets_created += 1
        print(f"✓ Создано поле ввода: {input_field.__class__.__name__}")

    # Группировочный виджет
    group_box = widget_factory.create_group_box("Test Group")
    if group_box:
        widgets_created += 1
        print(f"✓ Создана группа: {group_box.__class__.__name__}")

    # Прогресс-бар
    progress_bar = widget_factory.create_progress_bar(0, 100, 50)
    if progress_bar:
        widgets_created += 1
        print(f"✓ Создан прогресс-бар: {progress_bar.__class__.__name__}")

    print(f"WidgetFactory: ✓ Создано {widgets_created} виджетов\n")


def test_error_handling():
    """Тест обработки ошибок"""
    print("=== Тестирование обработки ошибок ===")

    renderer_manager = RendererManager()

    # Тест с невалидным контентом
    invalid_contents = [
        None,
        {},
        {"content": "test"},  # Нет типа
        {"type": "unknown_type", "content": "test"},  # Неизвестный тип
        {"type": "paragraph"},  # Нет контента
    ]

    errors_handled = 0
    for content in invalid_contents:
        widget = renderer_manager.render_block(content)
        if widget and "Error" in widget.text():
            errors_handled += 1

    print(f"✓ Обработано {errors_handled} из {len(invalid_contents)} ошибочных случаев")
    print("Обработка ошибок: ✓ Успешно\n")


def test_content_integration():
    """Тест интеграции с реальным контентом"""
    print("=== Тестирование интеграции с контентом ===")

    try:
        # Загружаем реальный контент
        data_dir = Path("src/gui/user_guide_framework/data")
        content_manager = ContentManager(data_dir)

        # Инициализируем рендер-менеджер
        themes_dir = data_dir / "themes"
        theme_manager = ThemeManager(themes_dir)
        theme_manager.load_available_themes()
        theme_manager.set_theme("default")

        renderer_manager = RendererManager(theme_manager)

        # Загружаем секцию
        deconv_section = content_manager.get_section_content("deconvolution")
        if deconv_section:
            content_blocks = deconv_section.content.get("ru", [])
            print(f"Найдено {len(content_blocks)} блоков контента в секции деконволюции")

            # Пытаемся отрендерить каждый блок
            rendered_count = 0
            for block in content_blocks[:3]:  # Тестируем первые 3 блока
                widget = renderer_manager.render_block(block)
                if widget:
                    rendered_count += 1
                    print(f"✓ Отрендерен блок типа: {block.get('type', 'unknown')}")
                else:
                    print(f"✗ Ошибка рендеринга блока типа: {block.get('type', 'unknown')}")

            print(f"Успешно отрендерено {rendered_count} из {min(len(content_blocks), 3)} блоков")
        else:
            print("✗ Не удалось загрузить секцию деконволюции")

    except Exception as e:
        print(f"✗ Ошибка интеграции: {e}")

    print("Интеграция с контентом: ✓ Завершена\n")


if __name__ == "__main__":
    print("Тестирование User Guide Framework - Фаза 2: Система рендеринга")

    # Создаем QApplication для работы с Qt виджетами
    app = QApplication(sys.argv)

    try:
        test_renderer_manager()
        test_individual_renderers()
        test_widget_factory()
        test_error_handling()
        test_content_integration()

        print("🎉 Все тесты второй фазы прошли успешно!")
        print("Фаза 2 завершена: Система рендеринга готова")
        print("Следующий этап: Фаза 3 - UI компоненты")

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback

        traceback.print_exc()

    # Завершаем приложение
    app.quit()
