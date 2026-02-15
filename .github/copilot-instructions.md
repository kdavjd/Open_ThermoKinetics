## Workflow

**ВАЖНО:** За сессию выполняется только один шаг workflow. Перед началом работы определить текущий шаг.

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐     ┌──────────────┐
│  spec-creation  │────►│ spec-implementer │────►│  gui-testing   │────►│ merge-helper │
│  ① ТЗ + Ветка   │     │  ② Реализация    │     │ ③ Тестирование │     │   ④ Мерж     │
└─────────────────┘     └──────────────────┘     └────────────────┘     └──────────────┘
```

### 1. Новая фича workflow

| Шаг | Навык                                                                   | Действие                            | ENTRY                         | EXIT                              |
| --- | ----------------------------------------------------------------------- | ----------------------------------- | ----------------------------- | --------------------------------- |
| ①   | [spec-creation](.claude/skills/spec-creation/SKILL.md)                  | ТЗ + Ветка + Коммит                 | branch: `main`                | `.ai/specs/{branch}.md` создан    |
| ②   | [spec-implementer](.claude/skills/spec-implementer/SKILL.md)            | Реализация этапов ТЗ                | spec существует, есть ⬜ этапы | все этапы ✅                       |
| ③   | [gui-testing](.claude/skills/gui-testing/SKILL.md)                      | pytest + pytest-qt тесты            | все этапы ✅                   | тесты пройдены                    |
| ④   | [merge-helper](.claude/skills/merge-helper/SKILL.md)                    | CHANGELOG + архив spec + merge main | тесты пройдены                | branch: `main`, spec в `archive/` |

### 2. Исправление бага workflow

| Шаг | Навык                                                  | Действие                  | ENTRY          | EXIT                           |
| --- | ------------------------------------------------------ | ------------------------- | -------------- | ------------------------------ |
| ①   | [spec-creation](.claude/skills/spec-creation/SKILL.md) | Тест бага + ветка bugfix  | branch: `main` | тест красный, ветка `bugfix/*` |
| ②   | —                                                      | Исправление, тест зелёный | тест красный   | тест зелёный                   |
| ③   | [merge-helper](.claude/skills/merge-helper/SKILL.md)   | CHANGELOG + merge main    | тест зелёный   | branch: `main`                 |

### Правила переходов

1. **Нельзя пропускать шаги** — каждый навык проверяет ENTRY условия
2. **Один шаг за сессию** — после завершения шага очистить контекст (`/clear`)
3. **Явный next_skill** — каждый навык указывает следующий обязательный шаг

---

## Структура приложения

**Open ThermoKinetics** — desktop GUI приложение для расчёта кинетических моделей твердофазных химических реакций.

Подробная архитектура описана в [`.ai/ARCHITECTURE.md`](.ai/ARCHITECTURE.md)

### Точка входа

```
src/gui/__main__.py    # Запуск приложения (python -m src.gui)
```

### Компоненты верхнего уровня

```
src/
├── gui/                          # PyQt6 GUI слой
│   ├── main_window.py            # Главное окно (контейнер вкладок)
│   ├── console_widget.py         # Виджет консольного вывода
│   ├── main_tab/                 # Главная вкладка анализа
│   │   ├── main_tab.py           # 4-панельный layout менеджер
│   │   ├── sidebar.py            # Дерево навигации (файлы, серии)
│   │   ├── load_file_button.py   # Загрузка экспериментальных файлов
│   │   ├── plot_canvas/          # Matplotlib визуализация
│   │   │   ├── plot_canvas.py    # Основной canvas
│   │   │   ├── anchor_group.py   # Интерактивные якоря (drag & drop)
│   │   │   └── plot_styling.py   # Стилизация графиков
│   │   └── sub_sidebar/          # Панели анализа
│   │       ├── sub_side_hub.py   # Переключатель панелей
│   │       ├── experiment/       # Операции с данными
│   │       ├── deconvolution/    # Деконволюция пиков
│   │       ├── model_fit/        # Подгонка моделей
│   │       ├── model_free/       # Model-free анализ
│   │       ├── model_based/      # Model-based анализ
│   │       └── series/           # Управление сериями
│   └── user_guide_tab/           # Вкладка документации
│       └── user_guide_framework/  # Кастомный фреймворк документации
│
└── core/                         # Бизнес-логика и вычисления
    ├── base_signals.py           # Центральный диспетчер сигналов
    ├── app_settings.py           # Конфигурация, модели, константы
    ├── calculation.py            # Оркестрация оптимизации
    ├── calculation_scenarios.py  # Сценарии расчётов
    ├── calculation_data.py       # Хранение параметров реакций
    ├── calculation_data_operations.py  # Высокоуровневые операции
    ├── curve_fitting.py          # Математические функции
    ├── file_data.py              # Данные экспериментальных файлов
    ├── file_operations.py        # Операции с файлами
    ├── series_data.py            # Управление сериями экспериментов
    ├── model_fit_calculation.py  # Model-fitting алгоритмы
    └── model_free_calculation.py # Model-free алгоритмы
```

### Ключевые технологии

| Технология | Версия | Назначение |
|------------|--------|------------|
| **PyQt6** | ^6.6.1 | GUI фреймворк |
| **Matplotlib** | 3.8.3 | Визуализация графиков |
| **NumPy** | ^1.26.4 | Численные вычисления |
| **SciPy** | ^1.13.1 | Оптимизация (`differential_evolution`, `solve_ivp`) |
| **Numba** | ^0.61.0 | JIT-компиляция для производительности |
| **Pandas** | ^2.2.1 | Работа с табличными данными |
| **Optuna** | ^4.1.0 | Альтернативная оптимизация |
| **Joblib** | ^1.4.2 | Параллельные вычисления |

---

## Архитектурные паттерны

### Signal-Slot коммуникация

**Центральный диспетчер:** `BaseSignals` ([base_signals.py](src/core/base_signals.py))

```python
class BaseSignals(QObject):
    request_signal = pyqtSignal(dict)
    response_signal = pyqtSignal(dict)
```

Все компоненты регистрируются в диспетчере и обмениваются данными через слабосвязанные сигналы.

### Request-Response паттерн

**Базовый класс:** `BaseSlots` — синхронный request-response поверх асинхронных Qt сигналов через `QEventLoop`.

### Data Flow

```
User Action (GUI)
       ↓
   Signal Emission (pyqtSignal)
       ↓
BaseSignals.dispatch_request()
       ↓
Target Component.process_request()
       ↓
Business Logic Execution
       ↓
Response Signal Emission
       ↓
UI Update (pyqtSlot)
```

---

## Расчётные модули

| Модуль | Описание |
|--------|----------|
| **Deconvolution** | Разделение пиков (Gaussian, Fraser-Suzuki, ADS) |
| **Model-Fit** | Подгонка к стандартным кинетическим моделям (F1/3, R3, A2, ...) |
| **Model-Free** | Изоконверсионные методы (Friedman, Kissinger, Vyazovkin) |
| **Model-Based** | ODE интеграция со схемами реакций (A→B→C), оптимизация через DE |

---

## UI Layout

### 4-панельный layout (MainTab)

```
┌──────────┬──────────────┬────────────────┬──────────┐
│ Sidebar  │ Sub-Sidebar  │  Plot Canvas   │ Console  │
│ (Nav)    │ (Analysis)   │  (Matplotlib)  │ (Logs)   │
└──────────┴──────────────┴────────────────┴──────────┘
```

### Особенности

- **Draggable anchors** — интерактивная настройка параметров на графике
- **Real-time updates** — обновление кривых во время оптимизации
- **Multi-heating-rate** — поддержка данных при разных скоростях нагрева

---

## Навыки (Skills)

### Workflow навыки (вызываются пользователем)

| Навык              | Файл                                                                                     | Шаг | Описание                                        |
| ------------------ | ---------------------------------------------------------------------------------------- | --- | ----------------------------------------------- |
| spec-creation      | [.claude/skills/spec-creation/SKILL.md](.claude/skills/spec-creation/SKILL.md)           | ①   | ТЗ по IEEE 29148 + ветка + коммит               |
| spec-implementer   | [.claude/skills/spec-implementer/SKILL.md](.claude/skills/spec-implementer/SKILL.md)     | ②   | Реализация этапов ТЗ с учётом архитектуры       |
| gui-testing        | [.claude/skills/gui-testing/SKILL.md](.claude/skills/gui-testing/SKILL.md)               | ③   | pytest + pytest-qt тесты для PyQt6              |
| merge-helper       | [.claude/skills/merge-helper/SKILL.md](.claude/skills/merge-helper/SKILL.md)             | ④   | CHANGELOG + архив spec + merge в main           |

### Служебные навыки (внутренние)

| Навык         | Файл                                                                           | Вызывается из                  | Описание             |
| ------------- | ------------------------------------------------------------------------------ | ------------------------------ | -------------------- |
| commit-helper | [.claude/skills/commit-helper/SKILL.md](.claude/skills/commit-helper/SKILL.md) | spec-implementer, merge-helper | Conventional commits |

---

## Документация

| Документ       | Путь                                               | Описание                                 |
| -------------- | -------------------------------------------------- | ---------------------------------------- |
| Архитектура    | [`.ai/ARCHITECTURE.md`](.ai/ARCHITECTURE.md)       | Архитектура проекта, модули, паттерны    |
| UI Архитектура | [`.ai/UI_ARCHITECTURE.md`](.ai/UI_ARCHITECTURE.md) | Структура GUI, виджеты, сигналы          |
| Модели данных  | [`.ai/DATA_MODELS.md`](.ai/DATA_MODELS.md)         | Структуры данных и их взаимосвязи        |
| ТЗ             | [`.ai/specs/`](.ai/specs/)                         | Технические задания на фичи              |
| CHANGELOG      | [`.ai/CHANGELOG.md`](.ai/CHANGELOG.md)             | История изменений                        |
