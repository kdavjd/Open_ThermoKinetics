# Feasibility: Параллельная оптимизация Model-Based расчётов — Feature Specification

> **Дата создания:** 2026-02-16
> **Дата завершения:** 2026-02-16
> **Ветка:** `feature/pygmo-feasibility`
> **Статус:** ✅ Завершён
> **Коммит:** `a07135f`
> **Тип:** Feasibility Analysis (исследование совместимости и рекомендации)

---

## Workflow выполнения

Данное ТЗ должно выполняться согласно **генеральному workflow** из [CLAUDE.md](../../CLAUDE.md).

### Определение типа workflow

**Тип задачи:** Новая фича (исследовательская — feasibility analysis)

### Порядок выполнения для новой фичи

| Шаг | Действие            | Навык              | Статус     |
| --- | ------------------- | ------------------ | ---------- |
| а   | Создание ТЗ + Ветка | —                  | ✅ Завершён |
| б   | Реализация          | `spec-implementer` | ✅ Завершён |
| в   | Тестирование        | —                  | ⏭️ Skipped (feasibility) |
| г   | Мерж                | `merge-helper`     | ✅ Завершён |

### Текущий статус и следующий шаг

**Текущий шаг:** б (Реализация) — ✅ Завершён
- Все этапы ТЗ выполнены
- Документ: `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md`

**Следующий шаг:** в (Тестирование) — ❌ Не требуется для feasibility-документов
- Переход к шагу г (Мерж) через навык `merge-helper`

> **Примечание:** Результат реализации данного ТЗ — документ `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md` с анализом и рекомендациями, а не код. Этапы ниже — это исследовательские задачи.

---

## Видение

Исследовать возможность имплементации результатов `docs/ru/4_pygmo_optimization.ipynb` (параллельная оптимизация через PyGMO island model) в продакшен-проект Open ThermoKinetics. Определить оптимальный путь ускорения Model-Based (ODE) расчётов с учётом критических ограничений: **Python 3.13, PyInstaller exe-сборка, pip-зависимости, PyQt6 GUI**.

**Ключевые требования:**
- Определить совместимость PyGMO с текущим стеком (Python 3.13, PyInstaller, pip)
- Исследовать альтернативные пути параллелизации (без PyGMO) с pip-совместимостью
- Оценить ускорение по каждому пути (baseline → expected speedup)
- Определить «быстрые победы» из ноутбука, не требующие новых зависимостей
- Рекомендовать двухфазный подход: pip-совместимый базис + опциональный PyGMO для advanced users
- Специфицировать полный набор параметров для ручного контроля из GUI: CPU cores, алгоритм, pop_size, gen, topology, solver, rtol

**Scope:** Только Model-Based (ODE) расчёты (`src/core/model_based_calculation.py`)

---

## Контекст: Текущее состояние продакшен-кода

### Текущая архитектура расчётов

```
User → GUI → Calculations.run_calculation_scenario()
                  ↓
         ModelBasedScenario.get_target_function()
                  ↓
         ModelBasedTargetFunction.__call__(params)
                  ↓
         model_based_objective_function(params, ...)
                  ↓
         integrate_ode_for_beta(beta, ...) × N_betas
                  ↓
         solve_ivp(ode_wrapper, method="BDF") + threading timeout 50ms
                  ↓
         ode_function() — чистый Python (без Numba JIT)
```

### Текущие узкие места (из ноутбука)

| Проблема                    | Влияние              | Описание                                                               |
| --------------------------- | -------------------- | ---------------------------------------------------------------------- |
| **BDF solver**              | ~12x медленнее LSODA | `model_based_calculation.py:301` использует `method="BDF"`             |
| **Threading timeout**       | ~50мс overhead/вызов | `integration_timeout` через `threading.Thread` — GIL блокирует         |
| **Нет Numba JIT для ODE**   | ~100x медленнее      | `ode_function()` — чистый Python, в ноутбуке `@njit` даёт ~2-5мс/вызов |
| **Однопоточная DE**         | 1x (baseline)        | `differential_evolution` без `workers`, GIL не позволяет threading     |
| **Нет контроля параметров** | —                    | Пользователь не может выбрать solver, rtol, число ядер, алгоритм       |

### Результаты исследования из ноутбука

| Оптимизация                        | Ожидаемый эффект              | Новые зависимости |
| ---------------------------------- | ----------------------------- | ----------------- |
| LSODA вместо BDF                   | ~12x ускорение ODE solve      | Нет (SciPy)       |
| Deadline timeout вместо threading  | ~0 overhead vs ~50мс          | Нет               |
| Numba JIT для ODE                  | ~100x на единичный вызов      | Numba (уже есть)  |
| rtol=1e-2 для exploration          | ~3-5x ускорение ODE           | Нет               |
| PyGMO archipelago (mp_island)      | ~Nx scaling (N = cpu_count)   | PyGMO (conda)     |
| Self-adaptive DE (de1220, sade)    | Лучший MSE при равном бюджете | PyGMO (conda)     |
| Двухфазная стратегия (coarse→fine) | Быстрее сходимость            | Нет               |

---

## Ограничения стека

| Constraint          | Значение                     | Влияние на решение                             |
| ------------------- | ---------------------------- | ---------------------------------------------- |
| **Python**          | 3.13 (requires-python ≥3.13) | PyGMO может не иметь wheels для 3.13           |
| **Package manager** | pip + uv (pyproject.toml)    | PyGMO: только conda-forge, НЕТ pip             |
| **Build system**    | PyInstaller ≥6.12            | Сложность сборки C++ shared libs (pagmo)       |
| **GUI**             | PyQt6                        | multiprocessing: freeze_support(), fork safety |
| **Numba**           | ≥0.61                        | Уже есть, `@njit` работает                     |
| **OS target**       | Windows (exe)                | `mp_island` через pickle, `spawn` method       |
| **JIT caching**     | Numba cache                  | Нужно учитывать при multiprocessing (pre-warm) |

---

## План реализации (исследовательские этапы)

### Этап 1: Совместимость PyGMO со стеком (~50 строк документа)
**Статус:** ✅ Завершён

**Цель:** Определить техническую возможность использования PyGMO в продакшене.

**Задачи:**
- [ ] Проверить наличие PyGMO wheels для Python 3.13 на conda-forge и PyPI
- [ ] Исследовать совместимость PyGMO (pagmo2 C++ backend) с PyInstaller 
- [ ] Оценить размер бинарника (pygmo shared libs: libpagmo, libboost, libtbb)
- [ ] Проверить `mp_island` поведение в frozen exe (pickle + multiprocessing spawn на Windows)
- [ ] Исследовать возможность гибридного deploy: основное приложение pip + отдельный conda-процесс для вычислений
- [ ] Документировать: conda/pixi vs pip lock-file коллизии

**Файлы:**
- `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md` (create) — Раздел 1: PyGMO Compatibility

**Критерий приёмки:**
- Для каждого аспекта (Python 3.13, PyInstaller, pip, Windows spawn) дан ответ: ✅ совместимо / ⚠️ с оговорками / ❌ несовместимо
- Указан размер дополнительных зависимостей (МБ)
- Вынесен вердикт: PyGMO пригоден/непригоден для прямой интеграции

---

### Этап 2: Параметры GUI-контроля расчётов (~40 строк документа)
**Статус:** ✅ Завершён

**Цель:** Специфицировать полный набор параметров, доступных пользователю для ручного управления Model-Based расчётом.

**Задачи:**
- [x] Составить полный список параметров для GUI: CPU cores, algorithm, pop_size, gen/maxiter, topology (если island model), solver_method, rtol, atol, timeout, mutation, recombination, seed, workers
- [x] Для каждого параметра: тип (int/float/enum), диапазон допустимых значений, default, UI widget (spinbox/combobox/slider), tooltip
- [x] Определить зависимость параметров от выбранного Path (A/B/C/D/E) — какие параметры доступны при каком подходе
- [x] Определить группировку параметров в блоки: "Optimization Engine", "ODE Solver", "Parallelization", "Advanced"

**Файлы:**
- `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md` (modify) — Раздел 4: GUI Control Parameters

**Критерий приёмки:**
- Таблица всех параметров с типом, диапазоном, default, widget
- Пояснение какие параметры доступны для какого пути параллелизации
- Mockup группировки параметров (текстовый wireframe)

---

### Этап 3: Итоговая рекомендация и Cost/Benefit (~40 строк документа)
**Статус:** ✅ Завершён

**Цель:** Вынести финальную рекомендацию: каким путём и какой ценой ускорить расчёты.

**Задачи:**
- [x] **Фаза 1 (pip-совместимая):** Рекомендовать комбинацию Quick Wins + лучший pip-совместимый путь параллелизации. Оценить: суммарный expected speedup, effort (дни разработки), risk
- [x] **Фаза 2 (опциональная):** Рекомендовать стратегию для PyGMO (если feasible) или максимальное ускорение. Оценить: дополнительный speedup vs complexity
- [x] **Cost/Benefit матрица:** Таблица (путь × effort × speedup × risk × compatibility)
- [x] **Рекомендация:** Конкретный порядок действий с обоснованием
- [x] **Next steps:** Какие ТЗ нужно создать для реализации рекомендованного пути

**Файлы:**
- `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md` (modify) — Раздел 5: Recommendation & Cost/Benefit

**Критерий приёмки:**
- Cost/Benefit матрица с числовыми оценками
- Чёткая рекомендация Фазы 1 и Фазы 2
- Список конкретных follow-up ТЗ для реализации

---

## Выходной артефакт

Результат реализации данного ТЗ — документ:

```
.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md
```

### Структура документа

```markdown
# Feasibility: Параллельная оптимизация Model-Based расчётов

## 1. PyGMO Compatibility Analysis
## 2. GUI Control Parameters Specification
## 3. Recommendation & Cost/Benefit
## Appendix A: Benchmark Data from Notebook
## Appendix B: Current Production Code Analysis
```

---

## Входные данные для анализа

### Из ноутбука `docs/ru/4_pygmo_optimization.ipynb`

| Этап   | Данные                                                            |
| ------ | ----------------------------------------------------------------- |
| Этап 2 | Archipelago: 2/4/8/N островов, ring/fully_connected/unconnected   |
| Этап 3 | Solver tuning: BDF/LSODA/Radau × rtol {1e-2, 1e-3, 1e-4}          |

### Из продакшен-кода

| Файл                                  | Что анализировать                                                        |
| ------------------------------------- | ------------------------------------------------------------------------ |
| `src/core/model_based_calculation.py` | `ode_function()`, `integrate_ode_for_beta()`, `ModelBasedTargetFunction` |
| `src/core/calculation.py`             | `Calculations`, threading, `differential_evolution` вызов                |
| `src/core/calculation_thread.py`      | `CalculationThread` (QThread)                                            |
| `src/core/app_settings.py`            | `ModelBasedDifferentialEvolutionConfig`, bounds                          |
| `pyproject.toml`                      | Зависимости, python version, PyInstaller                                 |

---

## История изменений

| Дата       | Этап | Коммит  | Описание                                   |
| ---------- | ---- | ------- | ------------------------------------------ |
| 2026-02-16 | —    | 6053012 | ТЗ создано                               |
| 2026-02-16 | 1    | 2d65332 | PyGMO Compatibility Analysis             |
| 2026-02-16 | 2    | 2d65332 | GUI Control Parameters Specification     |
| 2026-02-16 | 3    | 2d65332 | Recommendation & Cost/Benefit            |
| 2026-02-16 | MERGE| a07135f | Feature merged to main                   |
