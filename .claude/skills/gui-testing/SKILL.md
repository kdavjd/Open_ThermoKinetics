---
name: gui-testing
description: >
  Шаг ③ workflow: pytest + pytest-qt тестирование GUI.
  Triggers: "протестируй UI", "test GUI", "run gui tests", "verify UI".
  Запускает pytest тесты после завершения всех этапов реализации.
type: workflow
step: 3
---

# GUI Testing

**Шаг ③ workflow** — автоматизированное тестирование PyQt6 GUI через pytest + pytest-qt.

## Workflow Contract

```yaml
entry:
  branch: NOT main | master
  artifacts:
    - .ai/specs/{branch-name}.md  # все этапы ✅
  condition: все этапы в spec имеют статус ✅

exit:
  condition: все pytest тесты пройдены
  artifacts:
    - htmlcov/ (отчёт покрытия, при --cov)
  cleanup: удалить временные файлы тестов

next_skill: merge-helper  # ОБЯЗАТЕЛЬНО
```

## Architecture Overview

Тестируемое приложение:
- **GUI Framework:** PyQt6
- **Позиционирование:** `src/gui/` (widgets, windows, panels)
- **Business Logic:** `src/core/` (calculations, data)
- **Тестирование:** pytest + pytest-qt + pytest-cov

## Prerequisites

### Required

```bash
# Установка зависимостей тестирования
pip install pytest pytest-qt pytest-cov

# Для Linux CI/CD (headless)
pip install pytest-xvfb
```

### Конфигурация pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
qt_api = "pyqt6"
markers = [
    "gui: GUI тесты, требующие display",
    "slow: Медленные тесты",
]
```

## Testing Guidelines

### 1. Структура тестов

```
tests/
├── conftest.py              # Общие fixtures
├── unit/                    # Unit тесты (без GUI)
│   ├── test_calculation.py
│   └── test_curve_fitting.py
├── gui/                     # GUI тесты (pytest-qt)
│   ├── test_main_window.py
│   ├── test_sidebar.py
│   └── test_plot_canvas.py
└── integration/             # Интеграционные тесты
    └── test_workflow.py
```

### 2. Использование qtbot

```python
def test_button_click(qtbot):
    """Тест клика по кнопке."""
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtCore import Qt

    button = QPushButton("Click me")
    qtbot.addWidget(button)

    clicked = []
    button.clicked.connect(lambda: clicked.append(True))

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert len(clicked) == 1
```

### 3. Ожидание сигналов

```python
def test_signal_emission(qtbot):
    """Тест эмиссии сигнала."""
    from src.core.base_signals import BaseSignals

    signals = BaseSignals()

    with qtbot.wait_signal(signals.response_signal, timeout=1000):
        signals.dispatch_request({"action": "test"})
```

### 4. Тестирование виджетов

```python
@pytest.fixture
def main_window(qtbot):
    """Fixture главного окна."""
    from src.gui.main_window import MainWindow
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_main_window_loads(main_window):
    """Проверка загрузки главного окна."""
    assert main_window.isVisible()
    assert main_window.tab_widget.count() >= 1
```

## Core Testing Patterns

### Pattern 1: Widget Creation

```
1. Создать виджет
2. Добавить в qtbot (qtbot.addWidget)
3. Проверить начальное состояние
4. Выполнить действие
5. Проверить результат
```

### Pattern 2: Signal Testing

```
1. Создать объект с сигналами
2. Подключить обработчик или использовать wait_signal
3. Выполнить действие, эмитирующее сигнал
4. Дождаться сигнала (с timeout)
5. Проверить данные сигнала
```

### Pattern 3: User Input

```
1. Создать виджет с вводом
2. Использовать qtbot.keyClicks для текста
3. Использовать qtbot.mouseClick для кнопок
4. Проверить состояние виджета
```

### Pattern 4: Data Flow

```
1. Загрузить тестовые данные
2. Передать в тестируемый компонент
3. Выполнить расчёт/обработку
4. Проверить результат с ожидаемым
```

## Running Tests

### Локально

```bash
# Все тесты
pytest

# Только GUI тесты
pytest -m gui

# С покрытием
pytest --cov=src --cov-report=html

# Конкретный файл
pytest tests/gui/test_main_window.py -v

# С выводом print
pytest -s tests/gui/test_main_window.py
```

### CI/CD

```bash
# Linux (headless)
export QT_QPA_PLATFORM=offscreen
pytest --cov=src

# Windows (native display)
pytest --cov=src
```

## Error Handling

При падении тестов:

1. Проверить stack trace
2. Проверить fixture dependencies
3. Проверить timeout (увеличить если нужно)
4. Проверить изоляцию теста (нет ли побочных эффектов)
5. Запустить с `-s` для отладки

## Reporting Format

```markdown
## Test Results

**Status:** PASS / FAIL

**Summary:**
- Total: X tests
- Passed: Y
- Failed: Z
- Skipped: W

**Coverage:** XX%

**Failures:**
- test_name: reason

**Run command:**
pytest tests/ -v --cov=src
```

## Best Practices

1. **Изоляция** — каждый тест независим
2. **Fixtures** — переиспользование через conftest.py
3. **Явные ожидания** — wait_signal вместо sleep
4. **Параметризация** — @pytest.mark.parametrize
5. **Маркировка** — @pytest.mark.gui, @pytest.mark.slow

## References

- [pytest-qt-patterns.md](references/pytest-qt-patterns.md) — примеры тестов
- [.ai/TESTING.md](.ai/TESTING.md) — полная документация

---

**Remember:** Этот навык использует pytest + pytest-qt. Доступны все возможности pytest: fixtures, parametrize, markers, hooks.
