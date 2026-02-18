# PyGMO Research Notebook — Feature Specification

> **Дата создания:** 2026-02-16
> **Дата завершения:** 2026-02-16
> **Ветка:** `feature/pygmo-research-notebook`
> **Статус:** ✅ Завершён и влит в main

---

## Workflow выполнения

Данное ТЗ должно выполняться согласно **генеральному workflow** из [CLAUDE.md](../../CLAUDE.md).

### Определение типа workflow

**Тип:** Новая фича (исследовательский ноутбук)

### Порядок выполнения для новой фичи

| Шаг | Действие            | Навык              | Статус     |
| --- | ------------------- | ------------------ | ---------- |
| а   | Создание ТЗ + Ветка | —                  | ✅ Завершён |
| б   | Реализация          | `spec-implementer` | ✅ Завершён |
| в   | Тестирование        | `gui-testing`      | ⏭️ Пропущен |
| г   | Мерж                | `merge-helper`     | ✅ Завершён |

### Текущий статус и следующий шаг

**Текущий шаг:** б (Реализация) — ✅ Завершён (все этапы ✅)

**Следующий шаг:** г (Мерж)
- Выполнить через навык `merge-helper`

---

## Видение

Создать исследовательский Jupyter-ноутбук `docs/ru/4_pygmo_optimization.ipynb` для изучения PyGMO (Parallel Global Multiobjective Optimizer) как инструмента ускорения model-based кинетических расчётов. Ноутбук продолжает серию оптимизаций из `docs/ru/3_model_based.ipynb` и использует вспомогательный модуль `docs/ru/pygmo_udp.py` с Numba-скомпилированной ODE-функцией и PyGMO UDP-классом.

**Ключевые требования:**
- Исследовать PyGMO island model для **настоящего multiprocessing** (обход GIL)
- Перенести все best practices из `3_model_based.ipynb` (Numba JIT, корректная загрузка данных, benchmarking)
- Сравнить PyGMO алгоритмы (de1220, sade, cmaes, pso) с SciPy DE baseline
- Оценить archipelago (island model) с разными топологиями и числом островов
- Документировать результаты для последующей интеграции в продакшен (`src/core/model_based_calculation.py`)

---

## Контекст и обоснование

### Проблема

В `3_model_based.ipynb` (этап 7) установлено, что `ThreadPoolExecutor` даёт скромный эффект из-за GIL Python. В итоговых рекомендациях (ячейка «Анализ ноутбука») PyGMO отмечен как **высокий приоритет** с ожидаемым ускорением **3-16x** при средних усилиях.

### Текущий baseline

| Метрика          | Значение              | Источник                    |
| ---------------- | --------------------- | --------------------------- |
| 5 итераций DE    | ~102 сек              | 3_model_based.ipynb, этап 1 |
| ODE с Numba      | ~2-5 мс/вызов         | 3_model_based.ipynb, этап 5 |
| 1000 итераций DE | ~5.7ч (чистый Python) | 3_model_based.ipynb, этап 1 |
| Лучший solver    | BDF/LSODA, rtol=1e-4  | 3_model_based.ipynb, этап 8 |

### Почему PyGMO

- **Island model** — несколько оптимизаторов параллельно на всех ядрах CPU, обмен лучшими решениями
- **Настоящий multiprocessing** через `mp_island` (не GIL-limited threading)
- **Встроенные алгоритмы**: DE, self-adaptive DE (sade/de1220), CMA-ES, PSO, COMPASS
- **Batch fitness evaluation** — оценка всей популяции параллельно
- **Pickle-совместимость** через `pygmo_udp.py` (вынесен в отдельный `.py` файл для multiprocessing)

### Best practices из 3_model_based.ipynb

Следующие наработки **обязательны** для переноса в новый ноутбук:

1. **Numba JIT `ode_function_numba`** — используется из `pygmo_udp.py` (уже вынесена)
2. **Формат данных** — загрузка NH4 CSV файлов, нормализация масс к [0,1], температура в K
3. **Схема реакций** A→B→C→D с 3 реакциями, 11 допустимых моделей
4. **Вектор параметров** `[logA..., Ea..., model_idx..., contrib...]`
5. **Benchmarking методология** — n_runs повторений, baseline comparison, таблицы
6. **Solver настройки** — BDF как baseline, тестирование LSODA/Radau с разными rtol/atol
7. **MSE целевая функция** — `compute_ode_mse()` из `pygmo_udp.py`

---

## Стейкхолдеры

- **Разработчик** — исследование оптимального подхода для интеграции в продакшен
- **Пользователь приложения** — ожидает ускорение model-based расчётов

---

## Ограничения

- **CPU only** — GPU не требуется
- **Windows** — основная платформа разработки
- **Jupyter/VS Code** — ноутбук должен работать в VS Code notebook editor
- **PyGMO `mp_island`** — требует pickle-совместимые объекты (решено через `pygmo_udp.py`)
- **Зависимость `pygmo`** — устанавливается через `pip install pygmo` (или `conda install pygmo`)

---

## План реализации

### Этап 1: Установка PyGMO и базовая инфраструктура (~50 строк)
**Статус:** ✅ Завершён

**Цель:** Подготовить окружение и загрузить данные в формате, совместимом с `pygmo_udp.py`.

**Задачи:**
- [x] Markdown-заголовок ноутбука с описанием целей и ссылкой на `3_model_based.ipynb`
- [x] Установка `pygmo` (`pip install pygmo`) с проверкой версии
- [x] Импорт зависимостей: `pygmo`, `numpy`, `pandas`, `time`, `os`
- [x] Импорт из `pygmo_udp.py`: `ModelBasedUDP`, `compute_ode_mse`, `ode_function_numba`, `MODEL_NAMES`
- [x] Загрузка экспериментальных данных NH4 (3 скорости нагрева: 3, 5, 10 K/min)
- [x] Определение схемы реакций A→B→C→D, `src_indices`, `tgt_indices`
- [x] Определение bounds и начальных параметров (идентично `3_model_based.ipynb`)
- [x] Warm-up Numba JIT (первый вызов `ode_function_numba` для компиляции)

**Файлы:**
- `docs/ru/4_pygmo_optimization.ipynb` (create)

**Критерий приёмки:**
- Импорт `pygmo` работает без ошибок
- Данные загружены, `compute_ode_mse` возвращает валидный MSE для baseline параметров
- Numba JIT скомпилирован (второй вызов <5мс)

---

### Этап 2: Baseline — SciPy DE vs PyGMO single-island (~80 строк)
**Статус:** ✅ Завершён

**Цель:** Установить baseline сравнения SciPy `differential_evolution` с PyGMO на одном потоке (без archipelago).

**Задачи:**
- [x] SciPy DE baseline: `maxiter=15, popsize=5`, замер времени и MSE
- [x] PyGMO single-island DE: `pg.de(gen=15)`, `pop_size=5*n_params`, замер
- [x] PyGMO de1220 (self-adaptive DE): те же параметры
- [x] PyGMO sade (self-adaptive DE variant)
- [x] Таблица результатов: метод, время, MSE, nfev
- [x] Оптимизация solver: LSODA rtol=1e-2 (12x быстрее BDF, результат этапа 8)
- [x] Threading timeout 50мс для зависающих ODE интеграций

**Файлы:**
- `docs/ru/4_pygmo_optimization.ipynb` (modify)

**Критерий приёмки:**
- Таблица с 4+ методами, все возвращают конечный MSE

---

### Этап 3: PyGMO алгоритмы — расширенное сравнение (~100 строк)
**Статус:** ✅ Завершён

**Цель:** Сравнить широкий набор PyGMO алгоритмов при фиксированном бюджете evaluations.

**Задачи:**
- [x] Тестирование алгоритмов: `de`, `de1220`, `sade`, `cmaes`, `pso`, `sea`, `bee_colony`
- [x] Фиксированный бюджет: ~1200 evaluations (pop_size=60, gen=20)
- [x] Для каждого: время, лучший MSE, nfev
- [x] Определение Top-3 алгоритмов по MSE и по efficiency (MSE×time)
- [x] Markdown-ячейка с анализом: какие алгоритмы лучше для stiff ODE задач

**Файлы:**
- `docs/ru/4_pygmo_optimization.ipynb` (modify)

**Критерий приёмки:**
- Таблица с ≥5 алгоритмами
- Определён лучший алгоритм по MSE и по MSE/time

---

### Этап 4: Archipelago (island model) — параллелизация (~120 строк)
**Статус:** ✅ Завершён

**Цель:** Исследовать PyGMO archipelago для параллельной оптимизации на всех ядрах CPU.

**Задачи:**
- [x] `pg.archipelago` с `mp_island` (multiprocessing) — N островов = N CPU ядер
- [x] Тестирование с лучшим алгоритмом из Этапа 3
- [x] Сравнение числа островов: 2, 4, 8, `os.cpu_count()`
- [x] Тестирование топологий миграции: `ring`, `fully_connected`, `unconnected`
- [x] Замер wall-clock time и итогового MSE
- [x] Оценка scaling efficiency: speedup vs число островов

**Файлы:**
- `docs/ru/4_pygmo_optimization.ipynb` (modify)

**Критерий приёмки:**
- Archipelago с `mp_island` запускается без ошибок
- Speedup ≥2x по сравнению с single-island при ≥4 ядрах
- Таблица: n_islands, topology, time, MSE, speedup

---

### Этап 5: Тюнинг solver — влияние solver_method на PyGMO (~60 строк)
**Статус:** ✅ Завершён

**Цель:** Проверить влияние solver_method/rtol/atol в ODE на производительность PyGMO.

**Задачи:**
- [x] ModelBasedUDP с разными solver_method: BDF, LSODA, Radau
- [x] Разные tolerance: rtol=1e-2, 1e-3, 1e-4
- [x] Замер: время archipelago + итоговый MSE для каждой конфигурации
- [x] Определение оптимальной комбинации solver + PyGMO algo

**Файлы:**
- `docs/ru/4_pygmo_optimization.ipynb` (modify)

**Критерий приёмки:**
- Таблица с ≥6 конфигурациями (solver × tolerance)
- Определена лучшая комбинация для продакшена

---

## Зависимости между этапами

```
Этап 1 ──► Этап 2 ──► Этап 3 ──► Этап 4 ──► Этап 5
```

- Этапы 1→2→3 — строго последовательные (каждый использует результаты предыдущего)
- Этап 4 зависит от Top-3 алгоритмов из Этапа 3
- Этап 5 зависит от Этапа 4 (archipelago)

---

## Файловая структура

| Файл                                 | Действие | Описание                               |
| ------------------------------------ | -------- | -------------------------------------- |
| `docs/ru/4_pygmo_optimization.ipynb` | create   | Исследовательский ноутбук              |
| `docs/ru/pygmo_udp.py`               | modify   | Вспомогательный модуль (timeout+LSODA) |
| `resources/NH4_rate_3.csv`           | readonly | Экспериментальные данные β=3           |
| `resources/NH4_rate_5.csv`           | readonly | Экспериментальные данные β=5           |
| `resources/NH4_rate_10.csv`          | readonly | Экспериментальные данные β=10          |

---

## Нефункциональные требования

- **Воспроизводимость:** `seed=42` для всех стохастических алгоритмов
- **Jupyter-совместимость:** ноутбук работает в VS Code + Jupyter kernel
- **Windows-совместимость:** `mp_island` использует `spawn` (корректно для `pygmo_udp.py` — pickle-совместимый)
- **Документация:** каждая ячейка с кодом предваряется markdown-ячейкой с описанием
- **Стиль:** русский язык для описаний, технические термины на английском

---

## История изменений

| Дата       | Этап | Коммит | Описание                                               |
| ---------- | ---- | ------ | ------------------------------------------------------ |
| 2026-02-16 | —    | —      | ТЗ создано                                             |
| 2026-02-16 | 1    | —      | Этап 1 завершён: ноутбук создан, инфраструктура готова |
| 2026-02-16 | 2    | —      | Этап 2: timeout+LSODA в pygmo_udp.py, baseline ячейки  |
| 2026-02-16 | 5    | —      | Этап 5: solver×tolerance benchmark, 9 конфигураций     |
| 2026-02-16 | 3    | —      | Этап 3: 7 алгоритмов, сравнительная таблица, Top-3     |
| 2026-02-16 | 4    | —      | Этап 4: archipelago, mp_island, scaling, топологии     |
| 2026-02-16 | —    | —      | ТЗ завершено: этап 6 удалён, все инсайты получены      |
| 2026-02-16 | —    | MERGE  | Влито в main (squash merge)                            |
