"""
Демонстрационный скрипт для тестирования первой фазы User Guide Framework
"""

import sys
from pathlib import Path

# Добавим путь к нашему фреймворку
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.gui.user_guide_framework.core.content_manager import ContentManager
    from src.gui.user_guide_framework.core.localization_manager import LocalizationManager
    from src.gui.user_guide_framework.core.navigation_manager import NavigationManager
    from src.gui.user_guide_framework.core.theme_manager import ThemeManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the framework modules are properly installed")
    sys.exit(1)


def test_content_manager():
    """Тест ContentManager"""
    print("=== Тестирование ContentManager ===")

    data_dir = Path("src/gui/user_guide_framework/data")
    content_manager = ContentManager(data_dir)

    # Тест загрузки TOC
    print(f"TOC загружен: {content_manager.toc_data is not None}")

    # Тест получения метаданных
    metadata = content_manager.get_metadata()
    print(f"Заголовок: {metadata.get('title')}")
    print(f"Доступные языки: {metadata.get('languages')}")

    # Тест загрузки контента
    intro_section = content_manager.get_section_content("introduction")
    if intro_section:
        print(f"Загружен раздел: {intro_section.section_id}")
        print(f"Заголовок (RU): {intro_section.title.get('ru')}")
        print(f"Заголовок (EN): {intro_section.title.get('en')}")
        print(f"Количество блоков контента (RU): {len(intro_section.content.get('ru', []))}")

    # Тест поиска
    search_results = content_manager.search_content("деконволюция", "ru")
    print(f"Результатов поиска для 'деконволюция': {len(search_results)}")

    print("ContentManager: ✓ Успешно\n")


def test_navigation_manager():
    """Тест NavigationManager"""
    print("=== Тестирование NavigationManager ===")

    data_dir = Path("src/gui/user_guide_framework/data")
    content_manager = ContentManager(data_dir)
    nav_manager = NavigationManager(content_manager)

    # Тест структуры навигации
    print(f"Корневых узлов: {len(nav_manager.root_nodes)}")
    print(f"Всего узлов: {len(nav_manager.node_map)}")

    # Тест получения узла
    intro_node = nav_manager.get_node("introduction")
    if intro_node:
        print(f"Узел 'introduction': {intro_node.title.get('ru')}")
        print(f"Дочерних узлов: {len(intro_node.children)}")

    # Тест breadcrumb
    breadcrumb = nav_manager.get_breadcrumb("deconvolution")
    print(f"Breadcrumb для 'deconvolution': {[node.section_id for node in breadcrumb]}")

    # Тест плоской структуры
    flat_structure = nav_manager.get_flat_structure("ru")
    print(f"Элементов в плоской структуре: {len(flat_structure)}")

    # Тест информации о дереве
    tree_info = nav_manager.get_tree_info()
    print(f"Информация о дереве: {tree_info}")

    print("NavigationManager: ✓ Успешно\n")


def test_theme_manager():
    """Тест ThemeManager"""
    print("=== Тестирование ThemeManager ===")

    themes_dir = Path("src/gui/user_guide_framework/data/themes")
    theme_manager = ThemeManager(themes_dir)

    # Загрузка доступных тем
    theme_manager.load_available_themes()
    available_themes = theme_manager.get_available_themes()
    print(f"Доступные темы: {available_themes}")

    # Тест установки темы
    theme_manager.set_theme("dark")
    print(f"Текущая тема: {theme_manager.get_current_theme_name()}")

    # Тест получения цветов
    primary_color = theme_manager.get_color("primary")
    print(f"Основной цвет (тёмная тема): {primary_color.name()}")

    # Тест получения шрифтов
    heading_font = theme_manager.get_font("heading")
    print(f"Шрифт заголовка: {heading_font.family()}, {heading_font.pointSize()}pt")

    # Тест генерации стилей
    button_style = theme_manager.generate_stylesheet("QPushButton")
    print(f"Сгенерирован стиль для кнопки: {len(button_style)} символов")

    print("ThemeManager: ✓ Успешно\n")


def test_localization_manager():
    """Тест LocalizationManager"""
    print("=== Тестирование LocalizationManager ===")

    lang_dir = Path("src/gui/user_guide_framework/data/lang")
    loc_manager = LocalizationManager(lang_dir, "ru")

    # Загрузка языков
    loc_manager.load_available_languages()
    available_langs = loc_manager.get_available_languages()
    print(f"Доступные языки: {available_langs}")

    # Тест получения текста
    search_text = loc_manager.get_text("ui_search")
    print(f"Текст 'ui_search' (RU): {search_text}")

    # Переключение на английский
    loc_manager.set_language("en")
    search_text_en = loc_manager.get_text("ui_search")
    print(f"Текст 'ui_search' (EN): {search_text_en}")

    # Тест форматирования
    formatted_text = loc_manager.get_text("search_found", count=5)
    print(f"Форматированный текст: {formatted_text}")

    # Тест проверки существования перевода
    has_translation = loc_manager.has_translation("ui_search")
    print(f"Существует перевод для 'ui_search': {has_translation}")

    # Информация о языке
    lang_info = loc_manager.get_language_info("ru")
    print(f"Информация о русском языке: {lang_info}")

    print("LocalizationManager: ✓ Успешно\n")


def test_integration():
    """Тест интеграции всех компонентов"""
    print("=== Тестирование интеграции ===")

    data_dir = Path("src/gui/user_guide_framework/data")

    # Инициализация всех менеджеров
    content_manager = ContentManager(data_dir)
    nav_manager = NavigationManager(content_manager)
    theme_manager = ThemeManager(data_dir / "themes")
    loc_manager = LocalizationManager(data_dir / "lang", "ru")

    # Загрузка всех ресурсов
    theme_manager.load_available_themes()
    loc_manager.load_available_languages()

    print("Все компоненты инициализированы успешно")  # Тест работы с реальным контентом
    deconv_section = content_manager.get_section_content("deconvolution")
    if deconv_section:
        # Получение локализованного заголовка
        title_key = f"nav_{deconv_section.section_id}"
        localized_title = loc_manager.get_text(title_key)
        print(f"Локализованный заголовок: {localized_title}")

        # Тест навигации
        deconv_node = nav_manager.get_node("deconvolution")
        if deconv_node:
            print(f"Узел навигации найден: {deconv_node.node_id}")

        # Применение темы
        theme_manager.set_theme("default")
        text_color = theme_manager.get_color("text_primary")
        print(f"Цвет текста из темы: {text_color.name()}")

    print("Интеграция: ✓ Успешно\n")


if __name__ == "__main__":
    print("Тестирование User Guide Framework - Фаза 1\n")

    try:
        test_content_manager()
        test_navigation_manager()
        test_theme_manager()
        test_localization_manager()
        test_integration()

        print("🎉 Все тесты первой фазы прошли успешно!")
        print("\nГотово к переходу ко второй фазе: Система рендеринга")

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback

        traceback.print_exc()
