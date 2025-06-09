# GUI Refactoring Plan - Solid State Kinetics

## Executive Summary

This document outlines a comprehensive refactoring plan for the PyQt6 GUI code to improve maintainability, modularity, and adherence to domain-driven design principles. The refactoring will transform the current 22-file structure with several oversized components into a modular, entity-based architecture.

## Current State Analysis

### File Size Issues
Large files exceeding 350-line limit:
- `main_window.py`: 620 lines
- `plot_canvas.py`: 607 lines  
- `deconvolution_sub_bar.py`: 913 lines
- `model_based.py`: 1114 lines
- `models_scheme.py`: 711 lines

### Architectural Issues
1. **Action-based naming**: Files named by what they do (`deconvolution_sub_bar.py`) rather than what they represent
2. **Mixed responsibilities**: Single files containing multiple unrelated classes
3. **Magic values**: Hardcoded constants scattered throughout the code
4. **Relative imports**: Inconsistent import patterns
5. **String literals**: UI text embedded directly in code
6. **Complex inheritance**: Large widget hierarchies in single files

## Signal and Slot Architecture Mapping

This mermaid diagram maps all current signal/slot connections between GUI components and core systems:

```mermaid
graph TB
    subgraph "Core Signal Dispatcher"
        BS[BaseSignals<br/>request_signal<br/>response_signal]
    end

    subgraph "Main Window"
        MW[MainWindow<br/>to_main_tab_signal<br/>model_based_calculation_signal]
    end

    subgraph "Main Tab"
        MT[MainTab<br/>to_main_window_signal]
        SB[SideBar<br/>file_selected<br/>sub_side_bar_needed<br/>chosen_experiment_signal<br/>console_show_signal<br/>active_file_selected<br/>active_series_selected<br/>to_main_window_signal]
        PC[PlotCanvas<br/>update_value]
        CW[ConsoleWidget]
    end

    subgraph "Sub Sidebars"
        DSB[DeconvolutionSubBar<br/>calculation_started<br/>calculation_stopped<br/>update_value]
        RT[ReactionTable<br/>reaction_added<br/>reaction_removed<br/>reaction_chosed]
        ESB[ExperimentSubBar]
        ABB[ActionButtonsBlock<br/>cancel_changes_clicked<br/>derivative_clicked<br/>deconvolution_clicked]
        SSB[SeriesSubBar<br/>load_deconvolution_results_signal<br/>results_combobox_text_changed_signal]
        MFISB[ModelFitSubBar<br/>model_fit_calculation<br/>table_combobox_text_changed_signal<br/>plot_model_fit_signal]
        MFRSB[ModelFreeSubBar<br/>model_free_calculation_signal<br/>table_combobox_text_changed_signal<br/>plot_model_free_signal]
    end

    subgraph "Model Based Components"
        MBT[ModelBasedTab<br/>model_params_changed]
        MCB[ModelCalcButtons<br/>simulation_started<br/>simulation_stopped]
        MSc[ModelsScheme<br/>scheme_change_signal]
        REV[RangeEditingView<br/>valueChanged]
        RCV[RangeCalculationView<br/>showRangeToggled<br/>calculateToggled]
    end

    subgraph "Core Data Systems"
        FD[FileData<br/>data_loaded_signal]
        CD[CalculationsData<br/>dataChanged]
        SD[SeriesData]
        CALC[Calculations<br/>new_best_result]
        CDO[CalculationsDataOperations<br/>deconvolution_signal<br/>plot_reaction<br/>reaction_params_to_gui]
        CT[CalculationThread<br/>result_ready]
    end

    subgraph "File Operations"
        LB[LoadButton<br/>file_selected]
        AFO[ActiveFileOperations]
    end

    subgraph "Specialized Calculations"
        MFC[ModelFreeCalculation]
        MFIC[ModelFitCalculation]
    end

    %% Main signal connections
    BS -.-> MW
    BS -.-> FD
    BS -.-> CD
    BS -.-> SD
    BS -.-> CALC
    BS -.-> CDO
    BS -.-> AFO
    BS -.-> MFC
    BS -.-> MFIC

    %% GUI component connections
    MW --> MT
    MT --> SB
    MT --> PC
    MT --> CW
    MT --> DSB
    MT --> ESB
    MT --> SSB
    MT --> MFISB
    MT --> MFRSB
    MT --> MBT

    %% Sub-component connections
    SB --> LB
    DSB --> RT
    ESB --> ABB
    MBT --> MCB
    MBT --> MSc
    MBT --> REV
    MBT --> RCV

    %% Core data flow
    FD --> CDO
    CDO --> PC
    CALC --> CT
    CT --> CALC

    %% Key signal flows (selected critical paths)
    LB -.->|file_selected| FD
    FD -.->|data_loaded_signal| MT
    SB -.->|chosen_experiment_signal| FD
    RT -.->|reaction_added/removed| CDO
    DSB -.->|calculation_started| CALC
    CDO -.->|deconvolution_signal| CALC
    CDO -.->|plot_reaction| PC
    CDO -.->|reaction_params_to_gui| PC
    MCB -.->|simulation_started/stopped| CALC
    MSc -.->|scheme_change_signal| SD
    MBT -.->|model_params_changed| SD
    MFISB -.->|model_fit_calculation| MFC
    MFRSB -.->|model_free_calculation_signal| MFC
    SSB -.->|load_deconvolution_results_signal| SD
    PC -.->|update_value| DSB

    %% Console and UI control
    SB -.->|console_show_signal| MT
    SB -.->|sub_side_bar_needed| MT
    ABB -.->|deconvolution_clicked| MT

    style BS fill:#ff9999
    style MW fill:#ffcc99
    style MT fill:#99ccff
    style FD fill:#99ff99
    style CALC fill:#ffff99
    style CDO fill:#cc99ff
```

### Signal Categories and Patterns

**1. Central Dispatcher Pattern**
- `BaseSignals` with `request_signal`/`response_signal` - centralized communication hub
- All core components inherit from `BaseSlots` for standardized messaging

**2. GUI Event Signals**
- File operations: `file_selected`, `data_loaded_signal`
- UI state: `console_show_signal`, `sub_side_bar_needed`, `active_file_selected`
- User actions: `calculation_started`, `simulation_started`, `deconvolution_clicked`

**3. Data Flow Signals**
- Visualization: `plot_reaction`, `plot_data_from_dataframe`, `add_anchors`
- Updates: `update_value`, `dataChanged`, `model_params_changed`
- Results: `reaction_params_to_gui`, `result_ready`, `new_best_result`

**4. Analysis Workflow Signals**
- Calculations: `deconvolution_signal`, `model_fit_calculation`, `model_free_calculation_signal`
- Series operations: `load_deconvolution_results_signal`, `scheme_change_signal`
- Model operations: `simulation_started`, `simulation_stopped`, `valueChanged`

**5. Table/UI Update Signals**
- Reactions: `reaction_added`, `reaction_removed`, `reaction_chosed`
- Dropdowns: `table_combobox_text_changed_signal`, `results_combobox_text_changed_signal`
- Plotting: `plot_model_fit_signal`, `plot_model_free_signal`

### Critical Signal Paths for Refactoring

1. **File Loading Chain**: LoadButton → FileData → PlotCanvas → GUI Updates
2. **Calculation Chain**: GUI → CalculationsDataOperations → Calculations → Results
3. **Model-Based Chain**: ModelsScheme → SeriesData → ModelCalcButtons → Calculations
4. **Visualization Chain**: Data Changes → PlotCanvas → Anchor Updates → GUI Feedback

## Refactoring Principles

### 1. Entity-Based Organization
Transform from action-based to domain entity structure:
```
OLD: deconvolution_sub_bar.py
NEW: experiment/analysis/deconvolution.py
```

### 2. File Size Constraint
- Maximum 350 lines per file
- Split large files into focused modules
- One primary class per file

### 3. Configuration Extraction
- Extract magic values to dataclass structures
- Centralize UI constants and layout parameters
- Move string literals to localization files

### 4. Import Standardization
- Use absolute imports exclusively
- Consistent import organization
- Clear dependency structure

## New Module Structure

### Core Domain Modules

```
src/gui/
├── __main__.py                    # Entry point (unchanged)
├── application/
│   ├── main_window.py            # Main application window (< 350 lines)
│   ├── tab_container.py          # Tab management
│   └── application_config.py     # App-level configuration dataclasses
├── experiment/
│   ├── data_view.py              # Experiment data display
│   ├── file_operations.py        # File loading and management
│   ├── data_transforms.py        # Data manipulation controls
│   └── experiment_config.py      # Experiment-related constants
├── analysis/
│   ├── deconvolution.py          # Peak deconvolution analysis
│   ├── model_fitting.py          # Model fitting analysis
│   ├── model_free.py             # Model-free analysis
│   ├── series_analysis.py        # Series data analysis
│   └── analysis_config.py        # Analysis constants and defaults
├── modeling/
│   ├── reaction_scheme.py        # Reaction scheme editor
│   ├── reaction_table.py         # Reaction parameter table
│   ├── parameter_adjustment.py   # Parameter adjustment widgets
│   ├── simulation_controls.py    # Simulation controls
│   └── modeling_config.py        # Modeling constants
├── visualization/
│   ├── plot_canvas.py            # Main plotting component
│   ├── anchor_management.py      # Plot anchor controls
│   ├── plot_controls.py          # Plot interaction controls
│   └── visualization_config.py   # Plot styling and constants
├── sidebar/
│   ├── navigation.py             # File/series navigation
│   ├── calculation_menu.py       # Calculation type selection
│   ├── settings_panel.py         # Application settings
│   └── sidebar_config.py         # Sidebar layout constants
├── tables/
│   ├── data_table.py             # Data table display
│   ├── results_table.py          # Results table display
│   └── table_config.py           # Table formatting constants
├── dialogs/
│   ├── file_dialogs.py           # File selection dialogs
│   ├── settings_dialogs.py       # Configuration dialogs
│   ├── calculation_dialogs.py    # Calculation parameter dialogs
│   └── dialog_config.py          # Dialog constants
├── controls/
│   ├── buttons.py                # Reusable button components
│   ├── inputs.py                 # Form input components
│   ├── selection.py              # Selection components
│   └── controls_config.py        # Control styling constants
├── localization/
│   ├── strings_en.py             # English strings
│   ├── strings_ru.py             # Russian strings (optional)
│   └── localization_manager.py   # String management
└── resources/
    ├── styles.py                 # UI styling constants
    ├── icons.py                  # Icon resource management
    └── layouts.py                # Layout configuration dataclasses
```

## Configuration Dataclasses

### Application Configuration
```python
# src/gui/application/application_config.py
from dataclasses import dataclass
from typing import Tuple

@dataclass
class WindowConfig:
    title: str = "Open ThermoKinetics"
    min_width: int = 1200
    min_height: int = 800
    default_width: int = 1600
    default_height: int = 1000

@dataclass
class TabConfig:
    main_tab_name: str = "Main"
    table_tab_name: str = "Table"

@dataclass
class SplitterConfig:
    sidebar_ratio: float = 0.2
    sub_sidebar_ratio: float = 0.2
    console_ratio: float = 0.15
    plot_ratio: float = 0.45
```

### Analysis Configuration
```python
# src/gui/analysis/analysis_config.py
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ModelFreeConfig:
    methods: List[str] = ("linear approximation", "Friedman")
    alpha_min_default: float = 0.005
    alpha_max_default: float = 0.995
    ea_min_default: float = 10.0
    ea_max_default: float = 2000.0
    plot_types: List[str] = ("y(α)", "g(α)", "z(α)")

@dataclass
class ModelFitConfig:
    methods: List[str] = ("direct-diff", "Coats-Redfern")
    alpha_min_default: float = 0.005
    alpha_max_default: float = 0.995
    valid_proportion_default: float = 0.8

@dataclass
class DeconvolutionConfig:
    default_functions: List[str] = ("ads", "gauss", "fraser")
    optimization_methods: List[str] = ("differential_evolution", "minimize")
    max_iterations_default: int = 200
    population_size_default: int = 15
```

### Modeling Configuration
```python
# src/gui/modeling/modeling_config.py
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class ReactionDefaults:
    ea_default: float = 120.0
    log_a_default: float = 8.0
    contribution_default: float = 0.5
    ea_range: Tuple[float, float] = (1.0, 2000.0)
    log_a_range: Tuple[float, float] = (-100.0, 100.0)
    contribution_range: Tuple[float, float] = (0.01, 1.0)

@dataclass
class AdjustmentConfig:
    button_size: int = 24
    slider_min: int = -5
    slider_max: int = 5
    slider_tick_interval: int = 1
    decimals: int = 3

@dataclass
class SchemeConfig:
    node_width: float = 40.0
    node_height: float = 40.0
    node_spacing_x: float = 80.0
    node_spacing_y: float = 60.0
    arrow_width: float = 2.0
    available_models: List[str] = ("F1/3", "F3/4", "F3/2", "F2", "F3", "A2", "R3", "D1")
```

### Visualization Configuration
```python
# src/gui/visualization/visualization_config.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PlotConfig:
    style: str = "science"
    figure_dpi: int = 100
    default_colors: List[str] = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728")
    line_width: float = 1.5
    marker_size: float = 4.0

@dataclass
class AnnotationConfig:
    default_fontsize: int = 8
    default_facecolor: str = "white"
    default_edgecolor: str = "black"
    default_alpha: float = 1.0
    delta_x_default: float = 0.02
    delta_y_default: float = 0.02

@dataclass
class AnchorConfig:
    anchor_size: float = 8.0
    anchor_color: str = "red"
    line_color: str = "gray"
    line_style: str = "--"
```

## Localization Structure

### String Management
```python
# src/gui/localization/strings_en.py
from dataclasses import dataclass

@dataclass
class UIStrings:
    # Buttons
    calculate: str = "Calculate"
    plot: str = "Plot"
    settings: str = "Settings"
    load: str = "Load"
    save: str = "Save"
    export: str = "Export"
    import_: str = "Import"
    reset: str = "Reset"
    cancel: str = "Cancel"
    
    # Labels
    alpha_min: str = "α_min:"
    alpha_max: str = "α_max:"
    ea_min: str = "Ea min, kJ:"
    ea_max: str = "Ea max, kJ:"
    method: str = "Method:"
    reaction: str = "Reaction:"
    
    # Menu items
    file_menu: str = "File"
    calculation_menu: str = "Calculation"
    model_fit: str = "Model Fit"
    model_free: str = "Model Free"
    model_based: str = "Model Based"
    
    # Error messages
    invalid_input: str = "Invalid input value"
    file_not_found: str = "File not found"
    calculation_error: str = "Calculation error occurred"
    
    # Status messages
    calculation_started: str = "Calculation started"
    calculation_finished: str = "Calculation finished"
    file_loaded: str = "File loaded successfully"

# src/gui/localization/localization_manager.py
from typing import Dict, Any
from .strings_en import UIStrings

class LocalizationManager:
    def __init__(self, language: str = "en"):
        self.language = language
        self.strings = self._load_strings(language)
    
    def _load_strings(self, language: str) -> UIStrings:
        if language == "en":
            return UIStrings()
        # Add other languages as needed
        return UIStrings()
    
    def get(self, key: str) -> str:
        return getattr(self.strings, key, key)
```

## Refactoring Steps

### Phase 1: Extract Configurations (Week 1)
1. Create configuration dataclasses for each domain
2. Extract magic values from existing files
3. Create localization structure
4. Extract string literals

### Phase 2: Split Large Files (Week 2)
1. **main_window.py** → Split into:
   - `application/main_window.py` (core window logic)
   - `application/tab_container.py` (tab management)
   
2. **plot_canvas.py** → Split into:
   - `visualization/plot_canvas.py` (main plotting)
   - `visualization/plot_controls.py` (interaction controls)
   - `visualization/anchor_management.py` (anchor handling)

3. **deconvolution_sub_bar.py** → Split into:
   - `analysis/deconvolution.py` (main UI)
   - `controls/calculation_controls.py` (calculation buttons)
   - `tables/coefficients_table.py` (coefficients table)
   - `dialogs/calculation_dialogs.py` (settings dialog)

### Phase 3: Refactor Model-Based Components (Week 3)
1. **model_based.py** → Split into:
   - `modeling/reaction_table.py` (reaction parameters table)
   - `modeling/parameter_adjustment.py` (adjustment widgets)
   - `modeling/simulation_controls.py` (calculation controls)
   - `dialogs/calculation_dialogs.py` (settings dialogs)

2. **models_scheme.py** → Refactor into:
   - `modeling/reaction_scheme.py` (scheme editor)
   - `modeling/scheme_graphics.py` (graphics components)

### Phase 4: Create Domain Modules (Week 4)
1. Create experiment module with file operations
2. Create analysis module with all analysis components
3. Create sidebar module with navigation components
4. Create controls module with reusable components
5. Create dialogs module with all dialog components

### Phase 5: Update Imports and Integration (Week 5)
1. Convert all imports to absolute imports
2. Update signal connections
3. Integrate configuration dataclasses
4. Integrate localization manager
5. Update __main__.py entry point

## Example Refactored Component

### Before (deconvolution_sub_bar.py - 913 lines)
```python
# Multiple classes in one file with hardcoded values
class DeconvolutionSubBar(QWidget):
    def __init__(self, parent=None):
        # ... 200+ lines of UI setup with magic numbers
        self.button.setFixedSize(80, 30)  # Magic values
        self.label.setText("Calculate")   # Hardcoded string
```

### After (analysis/deconvolution.py - <350 lines)
```python
from src.gui.analysis.analysis_config import DeconvolutionConfig
from src.gui.localization.localization_manager import LocalizationManager
from src.gui.controls.buttons import CalculationButton
from src.gui.tables.coefficients_table import CoefficientsTable

class DeconvolutionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = DeconvolutionConfig()
        self.strings = LocalizationManager().strings
        self._setup_ui()
    
    def _setup_ui(self):
        # Clean, focused UI setup using configuration
        self.calc_button = CalculationButton(
            text=self.strings.calculate,
            parent=self
        )
        # ... rest of UI setup
```

## Benefits of Refactoring

### 1. Maintainability
- Smaller, focused files are easier to understand and modify
- Clear separation of concerns reduces coupling
- Configuration centralization simplifies updates

### 2. Testability
- Smaller components are easier to unit test
- Configuration injection enables better mocking
- Clear interfaces improve test coverage

### 3. Extensibility
- Domain-based organization makes feature additions intuitive
- Reusable components reduce code duplication
- Configuration dataclasses enable easy customization

### 4. Internationalization
- Centralized string management enables easy localization
- Consistent UI text across the application
- Dynamic language switching capability

### 5. Code Quality
- Consistent naming conventions improve readability
- Absolute imports clarify dependencies
- Explicit configuration reduces magic values

## Migration Strategy

### Backward Compatibility
- Maintain existing signal/slot interfaces during transition
- Preserve __main__.py entry point structure
- Ensure gradual migration without breaking functionality

### Testing Strategy
- Create unit tests for each new module
- Integration tests for signal/slot connections
- UI tests for critical user workflows

### Documentation Updates
- Update architecture documentation
- Create module-level documentation
- Provide migration guide for future developers

## Risk Mitigation

### Technical Risks
- **Signal/slot connection issues**: Comprehensive testing of all connections
- **Import circular dependencies**: Careful dependency design
- **Performance impact**: Profile critical paths during refactoring

### Project Risks
- **Development time**: Phased approach allows incremental progress
- **Team coordination**: Clear module ownership and interfaces
- **Regression introduction**: Extensive testing at each phase

## Success Metrics

### Quantitative
- All files under 350 lines
- Zero magic values in UI code
- 100% absolute imports
- Complete string externalization

### Qualitative
- Improved code readability scores
- Reduced complexity metrics
- Enhanced developer experience
- Better test coverage

## Conclusion

This refactoring plan transforms the current monolithic GUI structure into a modular, maintainable, and extensible architecture. The entity-based organization, configuration extraction, and localization support will significantly improve the codebase's quality and developer experience while maintaining full functionality and performance.

The phased approach ensures minimal disruption to ongoing development while providing clear milestones and deliverables. Upon completion, the GUI will be well-positioned for future enhancements and maintenance.
