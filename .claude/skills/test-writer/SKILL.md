---
name: test-writer
description: >
  Шаг ③ workflow: Написание pytest-тестов для нового функционала.
  Triggers: "напиши тесты", "write tests", "создай тесты", "покрой тестами".
  Трассирует реализованный код из spec, пишет unit/GUI/integration тесты,
  запускает pytest и коммитит. Вызывается после spec-implementer (все этапы ✅),
  до gui-testing.
type: workflow
step: 3
---

# Test Writer Skill

**Шаг ③ workflow** — написание тестов для нового функционала на основе реализованного кода.

## Workflow Contract

```yaml
entry:
  branch: NOT main | master
  artifacts:
    - .ai/specs/{branch-name}.md  # все этапы ✅
  condition: все этапы в spec имеют статус ✅

exit:
  condition: тесты написаны и все GREEN
  artifacts:
    - tests/**/*.py  # новые тест-файлы

next_skill: gui-testing  # ОБЯЗАТЕЛЬНО
```

## Предварительные требования (ENTRY проверка)

- Текущая ветка — НЕ `main`/`master`
- Существует `.ai/specs/{branch-name}.md`
- Все этапы spec имеют статус ✅ (реализация завершена)

## Алгоритм работы

### Фаза 1: Инициализация

1. **Проверить ветку:** `git branch --show-current`
   - Если main/master → STOP

2. **Загрузить spec:** `.ai/specs/{branch-name}.md`
   - Если не все этапы ✅ → STOP, предложить `spec-implementer`

3. **Аудит покрытия:** `uv run pytest --collect-only`
   - Определить, какие новые модули ещё не покрыты тестами

### Фаза 2: Трассировка реализации

Запустить **субагент** (`Explore`) для каждого нового модуля из spec:

**Цель:** понять что тестировать — публичные методы, сигналы, data flow.

Для каждого изменённого файла определить:
- Публичные методы и их сигнатуры
- `pyqtSignal` / `@pyqtSlot` — что эмитируется и принимается
- Структуры dict для request/response (все ключи и типы)
- Граничные условия (edge cases) из spec

### Фаза 3: Планирование тестов

Составить план тестов перед написанием:

| Тип | Расположение | Что тестировать |
|-----|-------------|-----------------|
| Unit | `tests/unit/` | Функции `src/core/` без GUI-зависимостей |
| GUI | `tests/gui/` | Виджеты PyQt6, взаимодействие пользователя |
| Integration | `tests/integration/` | Signal-Slot flow между компонентами |

**Приоритет покрытия:**
1. Публичные методы нового кода (обязательно)
2. Граничные условия из spec (обязательно)
3. Сигнальные взаимодействия (если задействованы pyqtSignal)
4. Интеграционные тесты только для ключевых workflow

### Фаза 4: Написание тестов

#### Структура unit-теста

```python
# tests/unit/test_{module}.py
import pytest
from src.core.{module} import {Class}


class Test{Class}:
    """Тесты для {Class}."""

    def test_{method}_returns_expected(self):
        """Happy path."""
        # Arrange
        obj = {Class}(...)
        # Act
        result = obj.{method}(...)
        # Assert
        assert result == expected

    def test_{method}_raises_on_invalid_input(self):
        """Граничный случай."""
        obj = {Class}()
        with pytest.raises(ValueError):
            obj.{method}(invalid_arg)
```

#### Структура GUI-теста (pytest-qt)

```python
# tests/gui/test_{widget}.py
import pytest
from PyQt6.QtCore import Qt
from src.gui.{module} import {Widget}


@pytest.fixture
def widget(qtbot):
    w = {Widget}()
    qtbot.addWidget(w)
    return w


def test_{widget}_initial_state(widget):
    assert widget.{property} == {expected}


def test_{widget}_emits_{signal}_on_action(qtbot, widget):
    with qtbot.wait_signal(widget.{signal}, timeout=1000):
        widget.{trigger_action}()
```

#### Тест Signal-Slot flow через BaseSignals

```python
def test_request_response_flow(qtbot):
    from src.core.base_signals import BaseSignals

    signals = BaseSignals()
    received = []
    signals.response_signal.connect(lambda d: received.append(d))

    signals.dispatch_request({"action": "test_action", "key": "value"})
    qtbot.wait(100)

    assert len(received) == 1
    assert received[0]["status"] == "success"
```

### Фаза 5: Верификация

```bash
# Только новые тесты
uv run pytest tests/ -v -k "{feature_keyword}"

# Все тесты (проверка отсутствия регрессий)
uv run pytest

# Покрытие нового кода
uv run pytest --cov=src --cov-report=term-missing
```

**Критерии прохождения:**
- Все новые тесты GREEN ✅
- Нет регрессий в существующих тестах
- Покрытие нового кода ≥ 60%

### Фаза 6: Коммит

```bash
git add tests/
git commit -m "test({scope}): add tests for {feature}

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

## Именование тестов

| Паттерн | Пример |
|---------|--------|
| `test_{thing}_does_{action}` | `test_series_calculates_activation_energy` |
| `test_{thing}_{action}_when_{condition}` | `test_button_disabled_when_no_data` |
| `test_{thing}_{action}_raises_{error}` | `test_calc_raises_on_empty_input` |

## Рекомендации следующего шага

| Ситуация | Рекомендация |
|----------|--------------|
| Тесты написаны и GREEN | `/clear` → "протестируй UI" (`gui-testing`) |
| Тесты RED | Исправить реализацию → перезапустить |
| Тривиальный код (геттеры/конфиг) | Пропустить, перейти к `gui-testing` напрямую |

## Ссылки

**Связанные skills:**
- [spec-implementer](../spec-implementer/SKILL.md) — предыдущий шаг
- [gui-testing](../gui-testing/SKILL.md) — следующий шаг

**Архитектура:**
- [.ai/ARCHITECTURE.md](../../../.ai/ARCHITECTURE.md)
- [.ai/UI_ARCHITECTURE.md](../../../.ai/UI_ARCHITECTURE.md)
