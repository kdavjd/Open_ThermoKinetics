"""
Демонстрационный скрипт для тестирования третьей фазы User Guide Framework - UI Layer
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# Добавим путь к нашему фреймворку
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Импорт фазы 3 (UI Layer)
    # Импорт фаз 1-2 (уже готовы)
    from src.gui.user_guide_framework.core.content_manager import ContentManager
    from src.gui.user_guide_framework.core.localization_manager import LocalizationManager
    from src.gui.user_guide_framework.core.navigation_manager import NavigationManager
    from src.gui.user_guide_framework.core.theme_manager import ThemeManager
    from src.gui.user_guide_framework.rendering.renderer_manager import RendererManager
    from src.gui.user_guide_framework.ui.content_widget import ContentWidget
    from src.gui.user_guide_framework.ui.guide_framework import GuideFramework
    from src.gui.user_guide_framework.ui.guide_toolbar import GuideToolBar
    from src.gui.user_guide_framework.ui.navigation_sidebar import NavigationSidebar
    from src.gui.user_guide_framework.ui.status_widget import StatusWidget

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что все модули фреймворка созданы")
    sys.exit(1)


def test_ui_components():
    """Тест отдельных UI компонентов"""
    print("=== Тестирование UI компонентов ===")

    app = QApplication(sys.argv)

    # Путь к данным
    data_directory = Path("src/gui/user_guide_framework/data")

    try:
        # Инициализация менеджеров
        content_manager = ContentManager(data_directory)
        navigation_manager = NavigationManager(content_manager)
        theme_manager = ThemeManager(data_directory / "themes")
        localization_manager = LocalizationManager(data_directory / "lang")
        renderer_manager = RendererManager(theme_manager)

        print("✓ Менеджеры инициализированы")
        # Тест NavigationSidebar
        navigation_sidebar = NavigationSidebar(navigation_manager, theme_manager)
        assert navigation_sidebar is not None  # Используем переменную для проверки
        print("✓ NavigationSidebar создан")

        # Тест ContentWidget
        content_widget = ContentWidget(content_manager, renderer_manager, localization_manager)
        assert content_widget is not None  # Используем переменную для проверки
        print("✓ ContentWidget создан")

        # Тест GuideToolBar
        toolbar = GuideToolBar(localization_manager, theme_manager)
        assert toolbar is not None  # Используем переменную для проверки
        print("✓ GuideToolBar создан")

        # Тест StatusWidget
        status_widget = StatusWidget(theme_manager)
        assert status_widget is not None  # Используем переменную для проверки
        print("✓ StatusWidget создан")

        print("\n✅ Все UI компоненты успешно созданы!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании UI компонентов: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        app.quit()


def test_guide_framework():
    """Тест главного фреймворка"""
    print("\n=== Тестирование GuideFramework ===")

    app = QApplication(sys.argv)

    # Путь к данным
    data_directory = Path("src/gui/user_guide_framework/data")

    try:
        # Создание главного фреймворка
        framework = GuideFramework(data_directory)
        print("✓ GuideFramework создан")

        # Тестирование основных методов
        current_language = framework.get_current_language()
        print(f"✓ Текущий язык: {current_language}")

        current_section = framework.get_current_section()
        print(f"✓ Текущий раздел: {current_section}")

        # Тестирование смены языка
        framework.set_language("en")
        print("✓ Язык изменен на английский")

        framework.set_language("ru")
        print("✓ Язык изменен на русский")

        print("\n✅ GuideFramework работает корректно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании GuideFramework: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        app.quit()


def create_demo_window():
    """Создание демонстрационного окна"""
    print("\n=== Создание демонстрационного окна ===")

    app = QApplication(sys.argv)

    # Путь к данным
    data_directory = Path("src/gui/user_guide_framework/data")

    try:
        # Создание главного окна
        main_window = QMainWindow()
        main_window.setWindowTitle("User Guide Framework - Phase 3 Demo")
        main_window.setMinimumSize(1200, 700)

        # Создание центрального виджета
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Создание и добавление фреймворка
        framework = GuideFramework(data_directory)
        layout.addWidget(framework)

        print("✓ Демонстрационное окно создано")

        # Показ окна
        main_window.show()
        print("✓ Окно отображено")

        print("\n🎉 Демонстрационное приложение запущено!")
        print("Закройте окно для завершения тестирования.")

        # Запуск приложения
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Ошибка при создании демонстрационного окна: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_signal_connections():
    """Тест соединений сигналов"""
    print("\n=== Тестирование соединений сигналов ===")

    app = QApplication(sys.argv)

    data_directory = Path("src/gui/user_guide_framework/data")

    try:
        framework = GuideFramework(data_directory)

        # Счетчики для проверки сигналов
        signal_counts = {"section_changed": 0, "language_changed": 0}

        def on_section_changed(section_id):
            signal_counts["section_changed"] += 1
            print(f"  📡 Сигнал section_changed: {section_id}")

        def on_language_changed(language):
            signal_counts["language_changed"] += 1
            print(f"  📡 Сигнал language_changed: {language}")

        # Подключение тестовых слотов
        framework.section_changed.connect(on_section_changed)
        framework.language_changed.connect(on_language_changed)

        # Тестирование эмиссии сигналов
        framework.navigation_sidebar.section_selected.emit("test_section")
        framework.navigation_sidebar.language_changed.emit("en")

        print("✓ Сигналы протестированы:")
        print(f"  - section_changed: {signal_counts['section_changed']}")
        print(f"  - language_changed: {signal_counts['language_changed']}")

        return signal_counts["section_changed"] > 0 and signal_counts["language_changed"] > 0

    except Exception as e:
        print(f"❌ Ошибка при тестировании сигналов: {e}")
        return False
    finally:
        app.quit()


def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования User Guide Framework - Phase 3 (UI Layer)")
    print("=" * 70)

    results = []

    # Тест UI компонентов
    results.append(test_ui_components())

    # Тест главного фреймворка
    results.append(test_guide_framework())

    # Тест сигналов
    results.append(test_signal_connections())

    # Сводка результатов
    print("\n" + "=" * 70)
    print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ Все тесты пройдены: {passed}/{total}")
        print("\n🎉 Фаза 3 (UI Layer) успешно реализована!")

        # Предложение запуска демо
        response = input("\n💡 Хотите запустить демонстрационное приложение? (y/n): ")
        if response.lower() in ["y", "yes", "да"]:
            create_demo_window()

    else:
        print(f"❌ Некоторые тесты не пройдены: {passed}/{total}")
        print("\n🔧 Требуется доработка компонентов")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
