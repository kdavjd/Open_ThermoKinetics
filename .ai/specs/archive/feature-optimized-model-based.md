# Optimized Model-Based Calculation - Feature Specification

> **Дата создания:** 2026-02-16
> **Дата завершения:** 2026-02-18
> **Ветка:** `feature/optimized-model-based`
> **Статус:** ✅ Завершён
> **Коммит:** 501ecd3

---

## Workflow выполнения

Данное ТЗ должно выполняться согласно **генеральному workflow** из [CLAUDE.md](../../CLAUDE.md).

### Тип workflow

**Новая фича** — оптимизация существующего модуля с полным рефакторингом API.

### Порядок выполнения

| Шаг | Действие            | Навык              | Статус     |
| --- | ------------------- | ------------------ | ---------- |
| а   | Создание ТЗ + Ветка | —                  | ✅ Завершён |
| б   | Реализация          | `spec-implementer` | ✅ Завершён |
| в   | Тестирование        | `gui-testing`      | ✅ Завершён |
| г   | Мерж                | `merge-helper`     | ✅ Завершён |

### Текущий статус и следующий шаг

**Текущий шаг:** б (Реализация) — ✅ Завершён
- Все 6 этапов реализованы
- 405 тестов пройдено

**Следующий шаг:** в (Тестирование)
- Выполнить через навык `gui-testing`: `/gui-testing`

---

## Видение

Ускорение Model-Based оптимизации в **50-200x** без изменения зависимостей (Фаза 1 из `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md`).

**Ключевые требования:**
- Numba JIT компиляция ODE функции (~100x speedup для вызовов)
- LSODA solver вместо BDF (~12x speedup, <2% MSE deviation)
- Deadline-based inline timeout (~0ms overhead vs ~50ms threading)
- Picklable objective для `workers=-1` параллельной оптимизации
- Configurable solver parameters через GUI
- Полный рефакторинг API с обновлением всех зависимостей

### Бенчмарк (из `docs/ru/3_model_based.ipynb`)

| Метрика              | Значение                      |
| -------------------- | ----------------------------- |
| Время оптимизации    | 982.6 сек (16.4 мин)          |
| MSE                  | 0.00005498                    |
| Итерации             | 1000                          |
| Function evaluations | 600,600                       |
| CPU cores            | 16 (workers=-1)               |
| ODE solver           | LSODA, rtol=0.01, atol=0.0001 |

---

## План реализации

### Этап 1: Numba-совместимые кинетические модели (~200 строк)
**Статус:** ✅ Завершён

**Цель:** Реализовать все модели из `NUC_MODELS_TABLE` в Numba-совместимом формате.

**Задачи:**
- [x] Создать `src/core/kinetic_models_numba.py` с `@njit` функциями
- [x] Реализовать `model_f_e(model_idx, e)` с switch по model index
- [x] Добавить mapping dict `MODEL_NAME_TO_INDEX` для 39 моделей
- [x] Реализовать `warmup_numba()` функцию для import-time JIT компиляции
- [x] Добавить enabled models management (set_enabled_models / get_enabled_model_indices)

**Файлы:**
- `src/core/kinetic_models_numba.py` (create)

**Критерий приёмки:**
- Все модели из `NUC_MODELS_TABLE` доступны через `model_f_e(model_idx, e)`
- Функция работает с `@njit(cache=True, fastmath=True)`
- Warmup завершается < 1 сек
- `pytest tests/test_kinetic_models_numba.py` — все тесты зелёные

---

### Этап 2: Numba-JIT ODE функция (~150 строк)
**Статус:** ✅ Завершён

**Цель:** Numba-совместимая `ode_function_numba()` для интеграции с `solve_ivp`.

**Задачи:**
- [x] Реализовать `ode_function_numba(T, y, beta, params, src_indices, tgt_indices, num_species, num_reactions)`
- [x] Использовать `@njit(cache=True, fastmath=True)`
- [x] Интеграция с `model_f_e()` из этапа 1
- [x] Безопасная обработка граничных условий (T_safe, e_safe, exponent clamping)

**Файлы:**
- `src/core/kinetic_models_numba.py` (modify)

**Критерий приёмки:**
- `ode_function_numba()` корректно вызывается из `solve_ivp`
- Результаты совпадают с Python версией (MSE deviation < 1e-10)
- Numba JIT warmup включён в `warmup_numba()`

---

### Этап 3: Deadline timeout и compute_ode_mse (~100 строк)
**Статус:** ✅ Завершён

**Цель:** Inline timeout без threading overhead.

**Задачи:**
- [x] Реализовать `_IntegrationTimeout` exception class
- [x] Добавить `deadline` проверку через `time.perf_counter()` в ODE wrapper
- [x] Реализовать `compute_ode_mse()` с параметрами:
  - `solver_method` (default: "LSODA")
  - `solver_rtol` (default: 1e-2)
  - `solver_atol` (default: 1e-4)
  - `timeout_ms` (default: 200.0)
- [x] Возвращать 1e4 при timeout или solver failure

**Файлы:**
- `src/core/kinetic_models_numba.py` (modify)

**Критерий приёмки:**
- Timeout работает корректно (возвращает 1e4 при превышении)
- Benchmark показывает ~0ms overhead vs ~50ms threading approach
- Configurable solver parameters влияют на точность/скорость

---

### Этап 4: Picklable SciPyObjective класс (~150 строк)
**Статус:** ✅ Завершён

**Цель:** Picklable callable для `scipy.optimize.differential_evolution(workers=-1)`.

**Задачи:**
- [x] Реализовать `SciPyObjective.__init__()` с picklable attributes:
  - `_betas`, `_exp_temperature`, `_all_exp_masses` (numpy arrays/lists)
  - `_src_indices`, `_tgt_indices` (numpy int64 arrays)
  - `_num_species`, `_num_reactions` (int primitives)
  - `_solver_method`, `_solver_rtol`, `_solver_atol`, `_timeout_ms`
- [x] Реализовать `SciPyObjective.__call__(x)` для scipy DE compatibility
- [x] Round model indices to nearest integer в `__call__`
- [x] Суммировать MSE по всем heating rates

**Файлы:**
- `src/core/kinetic_models_numba.py` (modify)

**Критерий приёмки:**
- `pickle.dumps(objective)` проходит без ошибок
- `pickle.loads(pickle.dumps(objective))` возвращает работающий объект
- `differential_evolution(objective, ..., workers=-1)` корректно работает на Windows

---

### Этап 5: Интеграция с ModelBasedScenario (~200 строк)
**Статус:** ✅ Завершён

**Цель:** Обновить `ModelBasedScenario` для использования нового API.

**Задачи:**
- [x] Обновить `ModelBasedScenario.get_target_function()`:
  - Возвращать `SciPyObjective` вместо `ModelBasedTargetFunction`
  - Извлекать параметры из `calculation_settings`:
    - `solver_method`, `solver_rtol`, `solver_atol`, `timeout_ms`
  - Преобразовывать scheme в `src_indices`, `tgt_indices` arrays
- [x] Обновить `make_de_callback()`:
  - Использовать `updating='deferred'` для workers != 1
  - Callback оценивает популяцию и находит лучший candidate
- [x] Обновить `calculation.py`:
  - Передавать `manager` в callback
  - Устанавливать `updating='deferred'` для параллельной оптимизации
- [x] Обновить GUI panel (`model_based_panel.py`):
  - Использовать `compute_ode_mse()` вместо `model_based_objective_function`
  - Использовать `ode_function_numba()` вместо `ode_function`
- [x] Удалить deprecated код:
  - `ModelBasedTargetFunction` class
  - `integration_timeout` decorator
  - `ode_function` Python version
  - `integrate_ode_for_beta`
  - `model_based_objective_function`
  - `TimeoutError` class
  - `constraint_fun` function

**Файлы:**
- `src/core/model_based_calculation.py` (modify)
- `src/core/calculation.py` (modify)
- `src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py` (modify)

**Критерий приёмки:**
- GUI расчёты работают с новыми параметрами
- `new_best_result` callback корректно работает с `updating='deferred'`
- Stop event корректно прерывает оптимизацию
- Все GUI функции (запуск, остановка, отображение результатов) работают

---

### Этап 6: Тестирование и документация (~150 строк)
**Статус:** ✅ Завершён

**Цель:** Unit tests и обновление документации.

**Задачи:**
- [x] Создать `tests/test_model_based_calculation.py`:
  - Test `model_f_e()` для всех моделей vs Python reference
  - Test `ode_function_numba()` vs Python version
  - Test `compute_ode_mse()` с mock data
  - Test `SciPyObjective` picklability
  - Test `SciPyObjective.__call__()` возвращает scalar MSE
- [x] Обновить `.ai/ARCHITECTURE.md`:
  - Добавить секцию `kinetic_models_numba.py`
  - Обновить секцию `model_based_calculation.py`
  - Добавить новые параметры в конфигурацию


**Файлы:**
- `.ai/ARCHITECTURE.md` (modify)
- `tests/test_model_based_calculation.py` (modify)

**Критерий приёмки:**
- `pytest tests/test_kinetic_models_numba.py` — все тесты зелёные
- `pytest tests/` — все существующие тесты проходят
- Benchmark показывает ≥50x speedup vs старая реализация
- ARCHITECTURE.md актуализирован

---

## История изменений

| Дата       | Этап | Коммит  | Описание                                         |
| ---------- | ---- | ------- | ------------------------------------------------ |
| 2026-02-16 | -    | 45e1dbf | ТЗ создано (IEEE 29148: 92%)                     |
| 2026-02-16 | 1    | 4299de2 | Numba kinetic models + enabled models management |
| 2026-02-16 | 2    | 1fda37c | Numba-JIT ODE function with safe boundary handling |
| 2026-02-16 | 3    | 3b8736f | Deadline timeout + compute_ode_mse()             |
| 2026-02-17 | 4    | f707334 | Picklable SciPyObjective class for parallel DE   |
| 2026-02-17 | 5    | 2a05522 | GUI integration with new API + deprecated cleanup |
| 2026-02-17 | 6    | d69abb8 | Unit tests + ARCHITECTURE.md update              |
| 2026-02-18 | -    | 501ecd3 | Simplified DE callback, .gitignore update        |
| 2026-02-18 | MERGE | -      | Feature merged to main                           |
