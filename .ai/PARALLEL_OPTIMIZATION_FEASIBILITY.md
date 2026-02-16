# Feasibility: Параллельная оптимизация Model-Based расчётов

> **Дата создания:** 2026-02-16
> **Источник ТЗ:** `.ai/specs/feature-pygmo-feasibility.md`
> **Scope:** `src/core/model_based_calculation.py` — ODE-based optimization

---

## 1. PyGMO Compatibility Analysis

### 1.1 Совместимость с Python 3.13

| Канал установки  | Версия | Python 3.13    | Windows (win-64) | Статус                                       |
| ---------------- | ------ | -------------- | ---------------- | -------------------------------------------- |
| **PyPI (pip)**   | 2.19.5 | ❌ Нет wheels   | ❌ Нет wheels     | Только Linux wheels для cp38–cp311           |
| **conda-forge**  | 2.19.7 | ✅ py313 builds | ✅ win-64 builds  | Полная поддержка (есть даже py314)           |
| **Source build** | 2.19.x | ⚠️ Возможно     | ⚠️ Возможно       | Требует C++17, CMake, pagmo, Boost, pybind11 |

**Детали PyPI:**
- Последняя версия: 2.19.5, всего 8 файлов — только `manylinux_2_28` wheels
- Поддерживаемые Python: 3.8, 3.9, 3.10, 3.11 (x86_64 + aarch64)
- Windows/macOS: **отсутствуют** (официально: "lack of manpower")
- Версия 2.19.0 на PyPI — tarball без `setup.py`/`pyproject.toml` (не устанавливается)

**Детали conda-forge:**
- Последняя версия: 2.19.7, 1012+ builds для всех платформ
- win-64 + py313: 6 builds, последний `pygmo-2.19.7-py313h42beeac_7.conda` (0.61 MB)
- Зависимости: pagmo ≥2.19.1, libboost ≥1.88, cloudpickle, numpy, scipy, pybind11-abi 11

**Вердикт Python 3.13:** ❌ pip / ✅ conda-forge

### 1.2 Совместимость с PyInstaller

| Аспект                          | Оценка         | Риск    | Описание                                                                                                            |
| ------------------------------- | -------------- | ------- | ------------------------------------------------------------------------------------------------------------------- |
| **C++ shared libs**             | ⚠️ С оговорками | Средний | pygmo — pybind11-обёртка над C++ pagmo; PyInstaller требует ручного добавления `.dll` через `--add-binary` или hook |
| **mp_island (multiprocessing)** | ⚠️ С оговорками | Средний | Использует `multiprocessing.spawn` + pickle UDP; frozen exe потребует `freeze_support()` (уже стандарт)             |
| **Pickle UDP**                  | ⚠️ С оговорками | Низкий  | UDP-класс должен быть importable в worker-процессе; в frozen exe все модули включены                                |
| **Нет документации**            | ⚠️ Неизвестно   | Высокий | 0 issues/PRs о PyInstaller на GitHub pygmo2; нет подтверждённого опыта                                              |

**Требуемые shared libraries (Windows):**

| Библиотека      | Размер (conda) | Назначение                      |
| --------------- | -------------- | ------------------------------- |
| pygmo           | 0.61 MB        | Python bindings (pybind11)      |
| pagmo           | 3.89 MB        | C++ optimization core           |
| libboost        | 2.29 MB        | Сериализация, multithreading    |
| tbb (Intel TBB) | 0.15 MB        | Thread Building Blocks          |
| nlopt           | 0.34 MB        | Нелинейная оптимизация          |
| ipopt           | 0.90 MB        | Interior Point оптимизация      |
| **Итого**       | **~8.2 MB**    | Дополнительный размер бинарника |

**Риски PyInstaller:**
- pybind11-модули требуют явного включения `.pyd` + зависимых `.dll` (pagmo, boost, tbb)
- `mp_island` создаёт новые процессы через `multiprocessing.spawn` — в frozen exe worker должен корректно импортировать все модули
- Отсутствие PyInstaller-hooks для pygmo означает ручную конфигурацию `.spec` файла
- При обновлении PyGMO/pagmo ABI-совместимость может сломаться (pybind11-abi pinning)

**Вердикт PyInstaller:** ⚠️ Теоретически возможно, но без подтверждённого опыта. Высокий риск неожиданных проблем при сборке.

### 1.3 Совместимость с pip (package manager)

| Критерий                           | Статус | Описание                                        |
| ---------------------------------- | ------ | ----------------------------------------------- |
| `pip install pygmo` на Windows     | ❌      | Нет wheels для Windows (только Linux)           |
| `pip install pygmo` на Python 3.13 | ❌      | Нет wheels для Python 3.12+                     |
| Включение в `pyproject.toml`       | ❌      | Невозможно — пакет не устанавливается через pip |
| `uv add pygmo`                     | ❌      | uv использует PyPI — те же ограничения          |

**Вердикт pip:** ❌ Несовместимо. PyGMO не может быть добавлен в `pyproject.toml` как зависимость.

### 1.4 mp_island в frozen exe (Windows spawn)

| Аспект                  | Оценка | Описание                                                                                    |
| ----------------------- | ------ | ------------------------------------------------------------------------------------------- |
| `multiprocessing.spawn` | ✅      | Стандартный метод на Windows; совместим с frozen exe при `freeze_support()`                 |
| Pickle UDP              | ⚠️      | UDP-класс и все его зависимости (numpy arrays, функции) должны быть pickle-совместимы       |
| Worker import           | ⚠️      | Worker-процесс импортирует модуль с UDP — в frozen exe может быть нестандартный import path |
| GIL bypass              | ✅      | `mp_island` использует настоящие процессы — полный обход GIL                                |

### 1.5 Гибридный deploy (pip + conda subprocess)

**Концепция:** основное приложение через pip/PyInstaller, вычислительное ядро в отдельном conda-окружении, коммуникация через IPC.

| Аспект          | Оценка    | Описание                                                             |
| --------------- | --------- | -------------------------------------------------------------------- |
| Isolation       | ✅         | Полная изоляция зависимостей                                         |
| Complexity      | ❌ Высокая | IPC (pipes/sockets), управление conda env, error handling            |
| User experience | ❌         | Требует установить conda отдельно, или bundling conda env (~500+ MB) |
| Maintenance     | ❌         | Два менеджера зависимостей, два lock-файла, сложная CI/CD            |
| Latency         | ⚠️         | Overhead на запуск subprocess + IPC serialization                    |

**Вердикт hybrid deploy:** ⚠️ Возможно, но неоправданно сложно для текущего проекта.

### 1.6 conda/pixi vs pip lock-file коллизии

| Проблема                  | Описание                                                                  |
| ------------------------- | ------------------------------------------------------------------------- |
| **Конфликт менеджеров**   | pip и conda управляют одним site-packages — взаимные перезаписи           |
| **Lock-файлы**            | `uv.lock` (pip-based) несовместим с `conda.lock` / `pixi.lock`            |
| **Переход на conda/pixi** | Потребует переписать CI/CD, отказаться от uv, перевести все зависимости   |
| **Размер окружения**      | conda-окружение ~500–1000 MB vs pip venv ~200 MB                          |
| **PyInstaller**           | PyInstaller официально поддерживает pip-установленные пакеты; conda — нет |

### 1.7 Итоговый вердикт по PyGMO

```
┌─────────────────────────────┬──────────┬──────────────────────────────────────────┐
│ Критерий                    │ Статус   │ Комментарий                              │
├─────────────────────────────┼──────────┼──────────────────────────────────────────┤
│ Python 3.13                 │ ❌ pip    │ Нет wheels на PyPI                       │
│                             │ ✅ conda  │ conda-forge 2.19.7 py313 win-64         │
│ PyInstaller                 │ ⚠️       │ Нет документации, высокий риск           │
│ pip install                 │ ❌        │ Невозможно на Windows/Python 3.13        │
│ Windows spawn (mp_island)   │ ⚠️       │ Возможно, но не протестировано в frozen   │
│ Hybrid deploy               │ ⚠️       │ Возможно, но чрезмерная сложность        │
│ Размер зависимостей         │ ~8.2 MB  │ pygmo + pagmo + boost + tbb + nlopt + ipopt │
└─────────────────────────────┴──────────┴──────────────────────────────────────────┘
```

**Финальный вердикт:** ❌ **PyGMO НЕ пригоден для прямой интеграции** в текущий стек (pip + PyInstaller + Windows + Python 3.13). Возможен только через conda-based deployment, что требует полного пересмотра системы сборки и дистрибуции.

---

## 2. GUI Control Parameters Specification

### 2.1 Полный список параметров для Model-Based расчётов

| Параметр            | Тип      | Диапазон             | Default   | Widget       | Tooltip                                                                 |
|---------------------|----------|----------------------|-----------|--------------|-------------------------------------------------------------------------|
| **ODE Solver**      |          |                      |           |              |                                                                         |
| `solver_method`     | enum     | LSODA, BDF, Radau    | LSODA     | ComboBox     | LSODA — автовыбор stiff/non-stiff, BDF — для жёстких ODE                |
| `solver_rtol`       | float    | 1e-4 … 1e-1          | 1e-2      | ComboBox     | Relative tolerance: 1e-2 (fast), 1e-3 (balanced), 1e-4 (accurate)       |
| `solver_atol`       | float    | 1e-6 … 1e-2          | 1e-4      | ComboBox     | Absolute tolerance для ODE solver                                       |
| `ode_timeout_ms`    | int      | 50 … 2000            | 200       | SpinBox      | Timeout на одно ODE интегрирование (мс). 0 = без лимита                 |
| **DE Optimization** |          |                      |           |              |                                                                         |
| `maxiter`           | int      | 1 … 10000            | 1000      | SpinBox      | Макс. число поколений DE                                                |
| `popsize`           | int      | 5 … 200              | 50        | SpinBox      | Размер популяции (pop_size = popsize × n_params)                        |
| `mutation`          | float    | 0.1 … 2.0            | 0.5       | DoubleSpinBox | F-параметр DE: коэффициент мутации                                      |
| `recombination`     | float    | 0.0 … 1.0            | 0.7       | DoubleSpinBox | CR-параметр DE: вероятность кроссовера                                  |
| `tol`               | float    | 1e-6 … 1.0           | 0.01      | DoubleSpinBox | Tol для критерия остановки: std(pop) < tol                              |
| `seed`              | int      | 0 … 2³¹-1            | 42        | SpinBox      | Seed для воспроизводимости. 0 = random                                  |
| `polish`            | bool     | —                    | False     | CheckBox     | L-BFGS-B полировка результата (долго, но точнее)                        |
| **Parallelization** |          |                      |           |              |                                                                         |
| `workers`           | int      | 1 … cpu_count        | 1         | SpinBox      | Число worker-процессов (1 = однопоточно)                                |
| **Advanced**        |          |                      |           |              |                                                                         |
| `strategy`          | enum     | best1bin, rand1bin…  | best1bin  | ComboBox     | Стратегия DE (best1bin — рекомендуемая)                                 |
| `init`              | enum     | latinhypercube, random | latinhypercube | ComboBox | Метод инициализации популяции                                           |

### 2.2 Группировка параметров в GUI

```
┌─────────────────────────────────────────────────────────────────────┐
│ Model-Based Settings                                                │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─ ODE Solver ─────────────────────────────────────────────────────┐│
│ │ Method: [LSODA ▼]   rtol: [1e-2 ▼]   atol: [1e-4 ▼]             ││
│ │ Timeout (ms): [200]                                               ││
│ └──────────────────────────────────────────────────────────────────┘│
│ ┌─ Differential Evolution ─────────────────────────────────────────┐│
│ │ Max Iterations: [1000]    Population Size: [50]                  ││
│ │ Mutation: [0.5]           Recombination: [0.7]                   ││
│ │ Tolerance: [0.01]         Seed: [42]                             ││
│ │ [ ] Polish result (L-BFGS-B)                                      ││
│ └──────────────────────────────────────────────────────────────────┘│
│ ┌─ Parallelization ────────────────────────────────────────────────┐│
│ │ Workers (CPU cores): [1]                                          ││
│ └──────────────────────────────────────────────────────────────────┘│
│ ┌─ Advanced ───────────────────────────────────────────────────────┐│
│ │ Strategy: [best1bin ▼]   Init: [latinhypercube ▼]               ││
│ └──────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 Рекомендуемые пресеты

| Пресет       | maxiter | popsize | solver_rtol | workers | Описание                              |
|--------------|---------|---------|-------------|---------|---------------------------------------|
| **Fast**     | 500     | 20      | 1e-2        | 1       | Быстрый exploration (~30 сек)         |
| **Balanced** | 1000    | 50      | 1e-3        | 1       | Баланс скорость/качество (~2 мин)     |
| **Accurate** | 2000    | 100     | 1e-4        | 1       | Точный результат (~10 мин)            |
| **Parallel** | 1000    | 50      | 1e-2        | N       | Параллельный расчёт (N = cpu_count)   |

---

## 3. Recommendation & Cost/Benefit

### 3.1 Фаза 1: pip-совместимые оптимизации (рекомендуется)

**Цель:** Максимальное ускорение без изменения зависимостей.

| Оптимизация                         | Expected Speedup | Effort (дни) | Risk | Breaking Changes |
|-------------------------------------|------------------|--------------|------|------------------|
| **LSODA вместо BDF**                | ~12x ODE         | 0.5          | Low  | Нет              |
| **Deadline timeout (inline)**       | ~50мс → ~0мс     | 0.5          | Low  | Нет              |
| **Numba JIT для ode_function**      | ~100x ODE call   | 2–3          | Med  | Требует тестов    |
| **Configurable rtol/atol**          | ~3–5x at rtol=1e-2 | 1          | Low  | Нет              |
| **Двухфазная стратегия**            | ~2x convergence  | 1            | Low  | Нет              |

**Суммарный ожидаемый speedup:** **~50–200x** (LSODA × Numba × rtol tuning)

**Рекомендация Фазы 1:**
1. Заменить `method="BDF"` → `method="LSODA"` в `integrate_ode_for_beta()`
2. Заменить `@integration_timeout(50.0)` на inline deadline check
3. Добавить `@njit` к `ode_function()` (с fallback для pickle-совместимости)
4. Параметризовать `rtol`, `atol`, `timeout` через GUI
5. Реализовать двухфазную стратегию: exploration (rtol=1e-2) → polish (rtol=1e-4)

**Total effort:** 4–6 дней | **Risk:** Low | **Dependencies:** Нет новых

### 3.2 Фаза 2: PyGMO (опциональная, НЕ рекомендуется)

**Почему НЕ рекомендуется:**
- ❌ PyGMO недоступен через pip для Windows + Python 3.13
- ❌ Требует перехода на conda/pixi (перепись CI/CD, lock-файлов)
- ❌ PyInstaller совместимость не документирована (высокий риск)
- ❌ Гибридный deploy (pip + conda subprocess) — чрезмерная сложность

**Если всё же требуется:**
- Переход на pixi/conda для всего проекта
- Перепись PyInstaller spec под conda environment
- Значительное увеличение размера дистрибутива (+8 MB libs + conda overhead)

**Expected speedup:** ~Nx (N = cpu_count) при archipelago | **Risk:** High | **Effort:** 10–15 дней

### 3.3 Cost/Benefit матрица

| Путь                    | Speedup | Effort (дни) | Risk  | pip-совместимость | PyInstaller | Рекомендация |
|-------------------------|---------|--------------|-------|-------------------|-------------|--------------|
| **Фаза 1 (LSODA+Numba)**| 50–200x | 4–6          | Low   | ✅                 | ✅           | **Да**       |
| Фаза 1 + workers=-1     | +Nx     | +1           | Med   | ✅                 | ⚠️          | Опционально  |
| PyGMO archipelago       | +Nx     | 10–15        | High  | ❌                 | ⚠️          | **Нет**      |
| Hybrid deploy           | +Nx     | 15–20        | High  | ⚠️                 | ⚠️          | **Нет**      |

### 3.4 Next Steps (ТЗ для реализации)

1. **ТЗ: LSODA + Deadline Timeout** (~1 день)
   - Заменить BDF → LSODA
   - Убрать threading timeout decorator
   - Добавить inline deadline check

2. **ТЗ: Numba JIT для ODE** (~2–3 дня)
   - Создать `@njit` версию `ode_function`
   - Обеспечить pickle-совместимость (для multiprocessing)
   - Добавить warmup при старте расчёта

3. **ТЗ: GUI Control Parameters** (~1–2 дня)
   - Добавить виджеты для rtol, atol, timeout, maxiter, popsize
   - Реализовать пресеты (Fast/Balanced/Accurate)
   - Сохранять настройки в app_settings

4. **ТЗ: Двухфазная оптимизация** (~1 день)
   - Coarse phase: rtol=1e-2, maxiter=500
   - Fine phase: rtol=1e-4, maxiter=200 от лучшего результата coarse

---

## Appendix A: Benchmark Data from Notebook

### Данные из `docs/ru/4_pygmo_optimization.ipynb`

**Этап 2: SciPy DE vs PyGMO single-island** (maxiter=15, popsize=5, seed=42, LSODA rtol=1e-2):
- Baseline: SciPy `differential_evolution` с LSODA + deadline timeout 200мс
- Сравнение: PyGMO `de`, `de1220`, `sade` — одинаковый бюджет evaluations

**Этап 3: 7 алгоритмов PyGMO** (pop_size=60, gen=20, ~1200 evals):
- `de`, `de1220`, `sade`, `cmaes`, `pso`, `bee_colony`, `sea`
- DE-семейство (de1220, sade) — лучшие для mixed-integer параметров

**Этап 4: Archipelago** (mp_island, ring/fully_connected/unconnected):
- 2/4/8/cpu_count островов
- Линейный speedup до cpu_count, `ring` — лучший баланс MSE/speed
- `mp_island` обходит GIL через multiprocessing

**Этап 5: Solver tuning** (BDF/LSODA/Radau × rtol 1e-2/1e-3/1e-4):
- LSODA rtol=1e-2 — максимальная скорость при адекватном качестве
- BDF ~12x медленнее LSODA
- Двухфазная стратегия: coarse → fine

### Ключевые оптимизации найденные в ноутбуке

| Оптимизация                       | Ожидаемый эффект              | Зависимости        |
| --------------------------------- | ----------------------------- | ------------------ |
| LSODA вместо BDF                  | ~12x ускорение ODE            | Нет (SciPy)        |
| Deadline timeout вместо threading | ~0 overhead vs ~50мс          | Нет                |
| Numba JIT для ODE                 | ~100x на единичный вызов      | Numba (уже есть)   |
| rtol=1e-2 для exploration         | ~3–5x ускорение ODE           | Нет                |
| PyGMO archipelago (mp_island)     | ~Nx scaling (N = cpu_count)   | PyGMO (conda-only) |
| Self-adaptive DE (de1220, sade)   | Лучший MSE при равном бюджете | PyGMO (conda-only) |
| Двухфазная стратегия              | Быстрее сходимость            | Нет                |

---

## Appendix B: Current Production Code Analysis

### Файл: `src/core/model_based_calculation.py` (542 строки)

**Архитектура:**
```
ModelBasedTargetFunction.__call__(params)
    → model_based_objective_function(params, ...)
        → integrate_ode_for_beta(beta, ...) × N_betas  [for-loop, последовательно]
            → solve_ivp(ode_wrapper, method="BDF")  [stiff solver]
                → ode_function(T, y, ...)  [чистый Python, без Numba]
            + @integration_timeout(50.0)  [threading.Thread]
```

**Выявленные узкие места:**

| Строка                              | Проблема                                     | Влияние                    |
| ----------------------------------- | -------------------------------------------- | -------------------------- |
| L301 (`method="BDF"`)               | BDF solver ~12x медленнее LSODA              | Каждый вызов ODE           |
| L190–210 (`integration_timeout`)    | threading.Thread для timeout ~50мс overhead  | Каждый beta                |
| L230–261 (`ode_function`)           | Чистый Python без `@njit`                    | ~100x медленнее Numba      |
| L200 (`@integration_timeout(50.0)`) | 50мс лимит слишком короткий                  | Потеря валидных решений    |
| L428–542 (`ModelBasedScenario`)     | `multiprocessing.Manager()` для shared state | Излишний overhead          |
| L238–261                            | Цикл по реакциям в Python                    | Медленнее vectorized/Numba |
