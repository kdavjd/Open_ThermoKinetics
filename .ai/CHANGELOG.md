# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added - Visual Redesign Full
- [src/gui/main_tab/sidebar.py](../src/gui/main_tab/sidebar.py): Переработан в flat-список (QListWidget) с разделами FILES / SERIES
  - Убрано дерево QTreeView, добавлены кнопки Load File / Import Series
  - Раздельный рендеринг файлов и серий
- [src/core/style_manager.py](../src/core/style_manager.py): Загрузка и применение бандловых шрифтов Source Sans 3 и JetBrains Mono
- [src/gui/main_tab/sub_sidebar/sub_side_hub.py](../src/gui/main_tab/sub_sidebar/sub_side_hub.py): QTabWidget с вкладками Experiment / Deconvolution / Model Fit

### Changed - Visual Redesign Full
- [src/gui/styles/](../src/gui/styles/): Активирована тема + глобальные элементы (QFrame, QScrollBar, QSplitter, статус-бар)
- [src/gui/main_tab/sub_sidebar/deconvolution/](../src/gui/main_tab/sub_sidebar/deconvolution/): Стилизация кнопок, таблиц, QComboBox; столбец name только для чтения; mono-шрифт в коэффициентах; скрыт заголовок ANALYSIS
- [src/gui/main_tab/sub_sidebar/experiment/](../src/gui/main_tab/sub_sidebar/experiment/): Uppercase кнопки, красный RESET, плейсхолдеры, dropdown poly, разделитель секций
- [src/gui/main_tab/sub_sidebar/series/](../src/gui/main_tab/sub_sidebar/series/): Uppercase кнопки, удалена метка "calculations"
- [src/gui/main_tab/sub_sidebar/model_based/](../src/gui/main_tab/sub_sidebar/model_based/): Отключены hover-сигналы, фикс ширины столбца Value
- [src/gui/main_tab/sub_sidebar/model_fit/](../src/gui/main_tab/sub_sidebar/model_fit/) и [model_free/](../src/gui/main_tab/sub_sidebar/model_free/): objectName-стилизация кнопок и таблиц

### Fixed - Visual Redesign Full
- [src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py](../src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py): Фикс позиционирования ячеек — скрыт verticalHeader, высота строки 28px, padding
- [src/core/style_manager.py](../src/core/style_manager.py): Заменён Source Sans Pro на Source Sans 3 (variable font TTF) для корректной загрузки на Windows
- [src/core/calculation_data_operations.py](../src/core/calculation_data_operations.py): Защита от пустого y-массива в аккумуляции кумулятивной кривой (ValueError shapes mismatch)

### Changed - Move Calculations to Series
- [src/gui/main_tab/sidebar.py](../src/gui/main_tab/sidebar.py): Удалён раздел "calculation" из навигационного дерева
  - Убран calculation_root и дочерние элементы (model fit, model free, model based)
  - Упрощена обработка кликов в on_item_clicked()

- [src/gui/main_tab/sub_sidebar/series/series_sub_bar.py](../src/gui/main_tab/sub_sidebar/series/series_sub_bar.py): Добавлен CalculationButtonsBlock
  - 3 кнопки перехода к расчётам: Model Fit, Model Free, Model Based
  - Сигнал calculation_clicked для переключения панелей
  - Валидация выбора серии перед переходом к расчёту
  - Сообщение в console при отсутствии выбранной серии

- [src/gui/main_tab/main_tab.py](../src/gui/main_tab/main_tab.py): Подключены сигналы расчётов
  - Связь calculation_buttons_block.calculation_clicked с toggle_sub_sidebar

---

## [0.3.0] - 2026-02-18

### Added - Release Stabilization
- [README.md](../README.md): Полная документация проекта
  - Features с эмодзи и badges (Python 3.13, MIT, uv)
  - Installation: uv, pip, from source, Windows exe
  - Quick Start с примером использования
  - ASCII mockups интерфейса
  - Таблица кинетических методов
  - Contributing и License секции

### Changed - Release Stabilization
- [pyproject.toml](../pyproject.toml): Версия обновлена до 0.3.0
- [.github/workflows/pre-commit.yml](../.github/workflows/pre-commit.yml): Миграция на uv + Python 3.13
  - setup-uv action вместо Poetry
  - uv sync && uv run для всех команд
- [.github/workflows/release.yml](../.github/workflows/release.yml): Миграция на uv + Python 3.13
  - Windows-only сборка (убран Linux из matrix)
  - setup-uv action вместо pipx + Poetry
  - Артефакт OTK.exe

### Removed - Release Stabilization
- `.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md`: Устаревший feasibility-документ
- `docs/develop_plan/ts.md`: Устаревший план
- `docs/ru/4_pygmo_optimization.ipynb`: Устаревший ноутбук
- `docs/ru/pygmo_udp.py`: Устаревший модуль
- 15 remote веток (cleanup origin)

---

### Added - Optimized Model-Based Calculation
- [src/core/kinetic_models_numba.py](../src/core/kinetic_models_numba.py): Numba-совместимые кинетические модели
  - 39 моделей реакций с `@njit(cache=True, fastmath=True)`
  - `model_f_e(model_idx, e)` для ODE интеграции
  - `ode_function_numba()` — JIT-компилированная ODE функция
  - `compute_ode_mse()` с deadline-based inline timeout
  - `SciPyObjective` — picklable класс для parallel DE optimization
  - Enabled models management API

- [src/core/model_based_calculation.py](../src/core/model_based_calculation.py): Refactored model-based API
  - Упрощён callback для differential_evolution
  - Интеграция с SciPyObjective

- [tests/test_kinetic_models_numba.py](../tests/test_kinetic_models_numba.py): Unit tests для Numba модулей
- [tests/test_model_based_calculation.py](../tests/test_model_based_calculation.py): Обновлённые тесты

- [.ai/ARCHITECTURE.md](../.ai/ARCHITECTURE.md): Документация kinetic_models_numba модуля

### Changed - Optimized Model-Based Calculation
- [src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py](../src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py): Интеграция с новым API
- [src/core/calculation.py](../src/core/calculation.py): Обновлён для parallel DE optimization

### Removed - Optimized Model-Based Calculation
- `ModelBasedTargetFunction` class — заменён на SciPyObjective
- `integration_timeout` decorator — заменён на deadline-based timeout
- `ode_function` Python version — заменена на ode_function_numba
- `model_based_objective_function` — интегрирована в SciPyObjective

### Added - PyGMO Feasibility Analysis
- [.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md](../.ai/PARALLEL_OPTIMIZATION_FEASIBILITY.md): Feasibility-документ по параллельной оптимизации
  - Раздел 1: Анализ совместимости PyGMO (Python 3.13, pip, PyInstaller, Windows)
  - Раздел 2: Спецификация GUI-параметров для Model-Based расчётов
  - Раздел 3: Cost/Benefit матрица и рекомендации
  - Вердикт: PyGMO НЕ пригоден для прямой интеграции (pip-incompatible)

- [docs/ru/pygmo_udp.py](../docs/ru/pygmo_udp.py): SciPyObjective класс для picklable оптимизации
  - Wrapper для SciPy differential_evolution с multiprocessing поддержкой
  - Picklable альтернатива для PyGMO mp_island (pip-совместимая)

- [docs/ru/3_model_based.ipynb](../docs/ru/3_model_based.ipynb): Рефакторинг ноутбука
  - Упрощена структура, убран дублирующий код
  - Обновлены benchmarks с LSODA solver

- [.ai/specs/feature-pygmo-feasibility.md](../.ai/specs/feature-pygmo-feasibility.md): ТЗ feasibility-анализа

### Added - PyGMO Research Notebook
- [docs/ru/4_pygmo_optimization.ipynb](../docs/ru/4_pygmo_optimization.ipynb): Исследовательский ноутбук для PyGMO оптимизации
  - Этап 1: Установка PyGMO, загрузка данных, warm-up Numba JIT
  - Этап 2: Baseline сравнение SciPy DE vs PyGMO single-island (de, de1220, sade)
  - Этап 3: Расширенное сравнение 7 алгоритмов (de, de1220, sade, cmaes, pso, sea, bee_colony)
  - Этап 4: Archipelago с mp_island — multiprocessing параллелизация, топологии миграции (ring, fully_connected)
  - Этап 5: Тюнинг solver — BDF/LSODA/Radau с разными tolerance, 9 конфигураций

- [docs/ru/pygmo_udp.py](../docs/ru/pygmo_udp.py): Обновлён вспомогательный модуль
  - LSODA solver по умолчанию (12x быстрее BDF для данной задачи)
  - Threading timeout 50мс для зависающих ODE интеграций
  - ModelBasedUDP класс для PyGMO island model

### Added - Model-Based Performance Optimization
- [docs/ru/3_model_based.ipynb](../docs/ru/3_model_based.ipynb): Performance optimization prototype
  - Baseline profiling (97ms ODE, 102s for 5 DE iterations)
  - Numba JIT compilation of ode_function (10-50x speedup)
  - Solution caching with warm-start (30%+ cache hit rate)
  - DE parallelization with workers=-1
  - Final benchmark and validation

- [docs/ru/pygmo_udp.py](../docs/ru/pygmo_udp.py): PyGMO UDP class for island model optimization
  - Numba-JIT compiled ODE functions
  - Picklable for multiprocessing in PyGMO

- [.github/copilot-instructions.md](../.github/copilot-instructions.md): Synchronized with CLAUDE.md workflow

### Changed - Model-Based Performance Optimization
- [pyproject.toml](../pyproject.toml): Added numba, cma, cmaes dependencies

### Added - Model-Based Notebook Enhancement
- [docs/ru/3_model_based.ipynb](../docs/ru/3_model_based.ipynb): Interactive Jupyter notebook for model-based method
  - Theoretical sections with LaTeX formulas (concentration vs conversion, Arrhenius, ODE systems, BDF method, optimization)
  - Data loading from NH4_parse_TGA.csv with reaction scheme A→B→C→D
  - ODE integration with BDF solver and 50ms timeout decorator
  - Differential evolution optimization with performance metrics
  - Visualization: model vs experiment, concentrations, residuals
  - Performance profiling: execution time, memory, iteration count

### Changed - Model-Based Module Extraction
- [src/core/model_based_calculation.py](../src/core/model_based_calculation.py): New module extracted from calculation_scenarios.py
  - Model-based ODE integration with `ode_function()`, `integrate_ode_for_beta()`
  - Optimization components: `model_based_objective_function()`, `constraint_fun()`
  - Chain extraction: `extract_chains()` for reaction scheme parsing
  - `ModelBasedScenario` class with `ModelBasedTargetFunction`
  - `make_de_callback()` for differential evolution callbacks
  - `TimeoutError` and `integration_timeout()` decorator
  - Mathematical foundation documentation for ODE system

- [src/core/calculation_scenarios.py](../src/core/calculation_scenarios.py): Reduced from ~460 to ~120 lines
  - Retained `BaseCalculationScenario`, `DeconvolutionScenario`, `SCENARIO_REGISTRY`
  - Model-based components now imported from model_based_calculation.py

- [src/core/calculation.py](../src/core/calculation.py): Updated imports
- [src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py](../src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py): Updated imports
- [tests/core/test_calculation_scenarios.py](../tests/core/test_calculation_scenarios.py): Updated imports for model-based components
- [.ai/ARCHITECTURE.md](../..ai/ARCHITECTURE.md): Added model_based_calculation.py to module structure

### Added - Python 3.13 + uv Migration
- [pyproject.toml](../pyproject.toml): Migrated from Poetry to uv (PEP 621)
  - Python 3.13 requirement
  - Updated all dependencies to latest versions
  - NumPy 2.x compatibility
  - Removed Numba dependency

- [src/core/app_settings.py](../src/core/app_settings.py): Removed @njit decorators
  - 81 functions converted from Numba to pure NumPy
  - Maintained numerical accuracy

- [.python-version](../.python-version): Added Python version file for uv

- [uv.lock](../uv.lock): New lockfile format replacing poetry.lock

### Changed - Python 3.13 + uv Migration
- [pyproject.toml](../pyproject.toml): PEP 621 format with [project] section
- [.pre-commit-config.yaml](../.pre-commit-config.yaml): Updated to use `uv run` instead of `poetry run`
- [src/core/*.py](../src/core/): Fixed imports to use `src.core` prefix for src-layout
- [src/gui/main_tab/plot_canvas/anchor_group.py](../src/gui/main_tab/plot_canvas/anchor_group.py): Fixed imports

### Removed - Python 3.13 + uv Migration
- `poetry.lock`: Replaced by uv.lock
- `numba` dependency: No longer compatible with Python 3.13
- `[tool.poetry.*]` sections from pyproject.toml

### Added - Test Coverage Migration
- [tests/](../tests/): Comprehensive test suite with 533 tests
  - pytest + pytest-qt + pytest-cov + pytest-mock infrastructure
  - Core module coverage: key modules ≥80% (curve_fitting 100%, file_operations 100%, model_free 95%, base_signals 94%, model_fit 92%)
  - GUI module coverage: 56% overall
  - Test fixtures with real experimental data (CSV, JSON presets)

- [tests/core/](../tests/core/): Core module tests (P0-P3)
  - `test_curve_fitting.py`: Gaussian, Fraser-Suzuki, asymmetric double sigmoid
  - `test_file_data.py`: CSV loading, encoding, decimal separator
  - `test_file_operations.py`: File I/O operations
  - `test_model_fit_calculation.py`: Model-fitting algorithms
  - `test_model_free_calculation.py`: Friedman, Kissinger, Vyazovkin methods
  - `test_calculation_data.py`: Reaction parameter structures
  - `test_series_data.py`: Multi-heating-rate experiment management
  - `test_app_settings.py`: Configuration, models, bounds
  - `test_calculation.py`: Optimization orchestration
  - `test_base_signals.py`: Signal-slot communication
  - `test_calculation_scenarios.py`: Calculation scenarios
  - `test_calculation_data_operations.py`: High-level data operations
  - `test_calculation_results_strategies.py`: Result processing strategies
  - `test_calculation_thread.py`: Threaded calculation execution
  - `test_state_logger.py`: Log aggregation and state tracking

- [tests/gui/](../tests/gui/): GUI module tests
  - `test_main_window.py`: Main window, tab switching
  - `test_main_tab.py`: 4-panel layout manager
  - `test_sidebar.py`: Navigation tree, file structure
  - `test_plot_canvas.py`: Matplotlib canvas
  - `test_anchor_group.py`: Interactive draggable anchors
  - `test_plot_styling.py`: Plot style configuration
  - `test_sub_side_hub.py`: Panel switching hub
  - `panels/test_experiment_panel.py`: Experiment operations panel
  - `panels/test_deconvolution_panel.py`: Peak deconvolution panel
  - `panels/test_model_fit_panel.py`: Model-fitting panel
  - `panels/test_model_free_panel.py`: Model-free analysis panel

### Added - Claude Configuration Refactor
- [CLAUDE.md](../CLAUDE.md): Complete rewrite for PyQt6 desktop application architecture
  - Signal-slot communication patterns (BaseSignals/BaseSlots)
  - 4-panel adaptive layout (MainTab)
  - Scientific visualization with matplotlib
  - Calculation modules: deconvolution, model-fit, model-free, model-based

- [.ai/ARCHITECTURE.md](../.ai/ARCHITECTURE.md): Application architecture documentation
  - Core modules structure (src/gui/, src/core/)
  - Request-Response pattern implementation
  - Data flow diagrams
  - Calculation orchestration

- [.ai/UI_ARCHITECTURE.md](../.ai/UI_ARCHITECTURE.md): GUI architecture documentation
  - MainWindow and tab structure
  - Sidebar navigation with QTreeView
  - SubSideHub dynamic content switching
  - Interactive matplotlib canvas with draggable anchors

- [.ai/DATA_MODELS.md](../.ai/DATA_MODELS.md): Data structures documentation
  - FileData: experimental data management
  - CalculationsData: reaction configurations with path_keys
  - SeriesData: multi-heating-rate experiments
  - Data operation flows

- [.claude/skills/gui-testing/](../.claude/skills/gui-testing/): New skill for PyQt6 testing
  - pytest + pytest-qt integration
  - Test patterns for Qt widgets
  - CI/CD with pytest-xvfb for headless testing

### Changed
- [CLAUDE.md](../CLAUDE.md): Removed web_portal references, added PyQt6 architecture
- [.claude/skills/spec-implementer/](../.claude/skills/spec-implementer/SKILL.md): Updated next_skill to gui-testing
- [.claude/skills/merge-helper/](../.claude/skills/merge-helper/SKILL.md): Replaced Playwright with pytest-qt
- [.claude/skills/spec-creation/](../.claude/skills/spec-creation/SKILL.md): Updated workflow references

### Removed
- `.claude/skills/parallel-mode/`: Simplified workflow (removed alternative implementation mode)
- `.claude/skills/web-portal-testing/`: Replaced with gui-testing skill
