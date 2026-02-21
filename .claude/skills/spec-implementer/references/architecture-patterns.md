# Architecture Patterns Reference

Паттерны реализации для **Open ThermoKinetics** (PyQt6 desktop GUI).

## TOC
1. [Слои приложения](#слои-приложения)
2. [Правила создания файлов](#правила-создания-файлов)
3. [Signal-Slot паттерны](#signal-slot-паттерны)
4. [Data Flow](#data-flow)
5. [Лимиты](#лимиты)

## Слои приложения

```
GUI Layer     → src/gui/          (PyQt6 виджеты, signal emission, UI update)
Core Layer    → src/core/         (бизнес-логика, вычисления, данные)
Signal Bus    → src/core/base_signals.py  (BaseSignals — центральный диспетчер)
```

## Правила создания файлов

| Тип файла           | Расположение                               | Паттерн                          |
| ------------------- | ------------------------------------------ | -------------------------------- |
| Sub-sidebar panel   | `src/gui/main_tab/sub_sidebar/{name}/`     | QWidget + регистрация в Hub      |
| Plot component      | `src/gui/main_tab/plot_canvas/`            | Matplotlib + QWidget             |
| Sidebar / Nav       | `src/gui/main_tab/sidebar.py`              | QTreeWidget + signal emit        |
| Core module         | `src/core/{name}.py`                       | dataclass/class + operations     |
| Core operations     | `src/core/{name}_operations.py`            | Высокоуровневые операции над data|
| Signal handler      | регистрация в `base_signals.py`            | `request_signal` / `response_signal` |
| Tests               | `tests/`                                   | pytest + pytest-qt               |

## Signal-Slot паттерны

### Эмиссия запроса (GUI → Core)

```python
self.base_signals.request_signal.emit({
    "action": "action_name",
    "data": {...}
})
```

### Обработчик запроса (Core)

```python
def process_request(self, payload: dict):
    if payload.get("action") == "action_name":
        result = self._do_work(payload["data"])
        self.base_signals.response_signal.emit({
            "action": "action_name",
            "data": result
        })
```

### Обработчик ответа (GUI)

```python
@pyqtSlot(dict)
def on_response(self, payload: dict):
    if payload.get("action") == "action_name":
        self._update_ui(payload["data"])
```

### Регистрация в диспетчере

```python
# В __init__ компонента
self.base_signals.request_signal.connect(self.process_request)
self.base_signals.response_signal.connect(self.on_response)
```

## Data Flow

```
User Action (GUI widget)
    ↓ emit request_signal(dict)
BaseSignals.dispatch_request()
    ↓
Core Module.process_request(dict)
    ↓ Business Logic
emit response_signal(dict)
    ↓
GUI widget.on_response(dict)
    ↓ UI Update
```

## Лимиты

**Максимум строк на этап:** 250

**Исключения (не считаются):**
- `*.lock` — lock-файлы
- `.ai/*.md` — документация фреймворка
- `tests/` — тесты учитываются отдельно
