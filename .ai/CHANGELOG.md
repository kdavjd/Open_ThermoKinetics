# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
