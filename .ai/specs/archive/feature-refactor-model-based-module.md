# Выделение model_based_calculation.py модуля - Feature Specification

> **Дата создания:** 2026-02-14
> **Дата завершения:** 2026-02-14
> **Ветка:** `feature/refactor-model-based-module`
> **Статус:** ✅ Завершён
> **Коммит:** 1c45378

---

## Workflow выполнения

Данное ТЗ должно выполняться согласно **генеральному workflow** из [CLAUDE.md](../../CLAUDE.md).

### Тип workflow: Рефакторинг

Это задача рефакторинга без изменения функциональности — следуем "Новая фича workflow" с адаптацией под рефакторинг.

### Порядок выполнения

| Шаг | Действие            | Навык                                  | Статус     |
| --- | ------------------- | -------------------------------------- | ---------- |
| а   | Создание ТЗ + Ветка | —                                      | ✅ Завершён |
| б   | Реализация          | `spec-implementer`                     | ✅ Завершён |
| в   | Тестирование        | `gui-testing`                          | ✅ Пропущен |
| г   | Мерж                | `merge-helper`                         | ✅ Завершён |

### Текущий статус и следующий шаг

**Текущий шаг:** б (Реализация) — ✅ Завершён
- Все этапы реализованы
- Тесты проходят (27/27)

**Следующий шаг:** в (Тестирование)
- Выполнить через навык `gui-testing`: `/gui-testing`

---

## Видение

Выделить model-based функционал из монолитного `calculation_scenarios.py` (~460 строк) в отдельный модуль `src/core/model_based_calculation.py` для улучшения maintainability, тестируемости и соответствия Single Responsibility Principle.

**Ключевые требования:**
- Создать новый модуль `src/core/model_based_calculation.py` (~300 строк)
- Перенести 11 model-based специфичных компонентов
- Обновить импорты в 3 зависимых файлах
- Обновить тесты
- Не добавлять новый функционал — только рефакторинг

---

## Архитектурные решения

| Вопрос | Решение | Обоснование |
|--------|---------|-------------|
| SCENARIO_REGISTRY | Остаётся в `calculation_scenarios.py` | Реестр общий, регистрирует оба сценария |
| make_de_callback() | Переносится в `model_based_calculation.py` | Специфичен для model-based |
| ModelBasedCalculationStrategy | Остаётся в `calculation_results_strategies.py` | Следует паттерну с другими стратегиями |
| Обратная совместимость | ❌ Нет | Чистый разрыв, обновить все импорты |
| Организация тестов | Обновить `test_calculation_scenarios.py` | Минимальные изменения |

---

## План реализации

### Этап 1: Создание модуля model_based_calculation.py (~180 строк)
**Статус:** ✅ Завершён

**Цель:** Создать новый модуль с перенесёнными компонентами

**Задачи:**
- [x] Создать файл `src/core/model_based_calculation.py`
- [x] Перенести `TimeoutError` (exception class)
- [x] Перенести `integration_timeout()` (decorator)
- [x] Перенести `extract_chains()` (chain extraction)
- [x] Перенести `constraint_fun()` (optimization constraints)
- [x] Перенести `ode_function()` (ODE system)
- [x] Перенести `integrate_ode_for_beta()` (ODE integration)
- [x] Перенести `model_based_objective_function()` (objective function)
- [x] Перенести `ModelBasedScenario` (scenario class)
- [x] Перенести `ModelBasedTargetFunction` (callable target)
- [x] Перенести `make_de_callback()` (DE callback)
- [x] Перенести `get_core_params_format_info()` (format info)
- [x] Добавить необходимые импорты (numpy, scipy, threading)

**Файлы:**
- `src/core/model_based_calculation.py` (create)

**Критерий приёмки:**
- ✅ Файл создан, все компоненты перенесены без изменений логики
- ✅ Модуль импортируется без ошибок: `python -c "from src.core.model_based_calculation import ModelBasedScenario"`

**Тестирование:**
- ✅ Unit test: `import ModelBasedScenario` succeeds
- ✅ Unit test: `import extract_chains` succeeds
- ✅ Unit test: `import make_de_callback` succeeds

---

### Этап 2: Обновление calculation_scenarios.py (~40 строк изменений)
**Статус:** ✅ Завершён

**Цель:** Удалить перенесённые компоненты, оставить только deconvolution и общий код

**Задачи:**
- [x] Удалить `TimeoutError` class
- [x] Удалить `integration_timeout()` decorator
- [x] Удалить `extract_chains()` function
- [x] Удалить `constraint_fun()` function
- [x] Удалить `ode_function()` function
- [x] Удалить `integrate_ode_for_beta()` function
- [x] Удалить `model_based_objective_function()` function
- [x] Удалить `ModelBasedScenario` class
- [x] Удалить `ModelBasedTargetFunction` class
- [x] Удалить `make_de_callback()` function
- [x] Удалить `get_core_params_format_info()` function
- [x] Добавить импорт `from src.core.model_based_calculation import ModelBasedScenario`
- [x] Обновить `SCENARIO_REGISTRY` — регистрация через импортированный класс

**Файлы:**
- `src/core/calculation_scenarios.py` (modify)

**Критерий приёмки:**
- ✅ Файл содержит только `BaseCalculationScenario`, `DeconvolutionScenario`, `SCENARIO_REGISTRY`
- ✅ `SCENARIO_REGISTRY["model_based_calculation"]` ссылается на импортированный `ModelBasedScenario`
- ✅ Модуль импортируется без ошибок

**Тестирование:**
- ✅ Unit test: `SCENARIO_REGISTRY["model_based_calculation"]` exists
- ✅ Unit test: `SCENARIO_REGISTRY["deconvolution"]` exists
- ✅ Unit test: Both scenarios are different classes

---

### Этап 3: Обновление импортов в зависимостях (~10 строк)
**Статус:** ✅ Завершён

**Цель:** Обновить импорты в файлах, зависящих от model-based функционала

**Задачи:**
- [x] Обновить `src/core/calculation.py`:
  - Изменить `from src.core.calculation_scenarios import SCENARIO_REGISTRY, make_de_callback`
  - На `from src.core.calculation_scenarios import SCENARIO_REGISTRY` + `from src.core.model_based_calculation import make_de_callback`
- [x] Обновить `src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py`:
  - Изменить `from src.core.calculation_scenarios import model_based_objective_function, ode_function`
  - На `from src.core.model_based_calculation import model_based_objective_function, ode_function`

**Файлы:**
- `src/core/calculation.py` (modify)
- `src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py` (modify)

**Критерий приёмки:**
- ✅ Оба файла импортируются без ошибок

**Тестирование:**
- ✅ Integration test: Imports work correctly

---

### Этап 4: Обновление тестов (~30 строк)
**Статус:** ✅ Завершён

**Цель:** Обновить импорты в тестах

**Задачи:**
- [x] Обновить `tests/core/test_calculation_scenarios.py`:
  - Разделить импорты: `from src.core.calculation_scenarios import ...` (deconvolution)
  - Добавить: `from src.core.model_based_calculation import ...` (model-based)
- [x] Проверить, что все тесты проходят

**Файлы:**
- `tests/core/test_calculation_scenarios.py` (modify)

**Критерий приёмки:**
- ✅ `pytest tests/core/test_calculation_scenarios.py` — все тесты PASS (27/27)

**Тестирование:**
- ✅ Run: `pytest tests/core/test_calculation_scenarios.py -v`
- ✅ All tests pass

---

### Этап 5: Обновление документации (~15 строк)
**Статус:** ✅ Завершён

**Цель:** Отразить новую структуру модулей в документации

**Задачи:**
- [x] Обновить `.ai/ARCHITECTURE.md`:
  - Добавить `model_based_calculation.py` в структуру `src/core/`
  - Добавить описание модуля в раздел "Модули расчётов"

**Файлы:**
- `.ai/ARCHITECTURE.md` (modify)

**Критерий приёмки:**
- ✅ Документация отражает актуальную структуру

**Тестирование:**
- ✅ Manual review: Architecture doc matches code structure

---

## Сводка изменений

| Файл | Действие | Строк |
|------|----------|-------|
| `src/core/model_based_calculation.py` | create | ~350 |
| `src/core/calculation_scenarios.py` | modify | -340 |
| `src/core/calculation.py` | modify | ~2 |
| `src/gui/.../model_based_panel.py` | modify | ~1 |
| `tests/core/test_calculation_scenarios.py` | modify | ~3 |
| `.ai/ARCHITECTURE.md` | modify | ~10 |

**Итого:** ~350 строк нового кода, ~340 строк удалено, ~16 строк изменено

---

## История изменений

| Дата   | Этап | Коммит | Описание   |
| ------ | ---- | ------ | ---------- |
| 2026-02-14 | -    | 300b157 | ТЗ создано |
| 2026-02-14 | 1-5  | 9bb0e40 | Реализация завершена |
| 2026-02-14 | MERGE | 1c45378 | Feature merged to main |
