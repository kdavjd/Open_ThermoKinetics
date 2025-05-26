# План рефакторинга UI

## Цель рефакторинга

Разбить большие файлы UI на более мелкие модули, каждый из которых содержит не более 300 строк кода. Каждый файл должен содержать отдельную сущность, а не группу связанного кода. Все импорты должны быть абсолютными.

## Принципы рефакторинга

### Именование модулей
- Файлы называются по содержащейся в них **сущности**, а не по функциональности
- Избегаем названий типа `components`, `widgets`, `buttons` 
- Используем имена конкретных классов: `reaction_table.py`, `file_transfer_buttons.py`

### Импорты
- Все импорты должны быть **абсолютными**
- Формат: `from src.gui.module.submodule import ClassName`
- Никаких относительных импортов (`.`, `..`)

## Анализ текущего состояния

### Файлы, требующие рефакторинга (>300 строк):

1. **model_based.py** - 864 строки
2. **deconvolution_sub_bar.py** - 790 строк  
3. **models_scheme.py** - 612 строк
4. **plot_canvas.py** - 505 строк
5. **main_window.py** - 476 строк
6. **sidebar.py** - 348 строк
7. **model_free_sub_bar.py** - 312 строк

### Файлы в приемлемом диапазоне (<300 строк):

- model_fit_sub_bar.py - 263 строки
- series_sub_bar.py - 251 строка
- anchor_group.py - 207 строк
- load_file_button.py - 180 строк
- main_tab.py - 148 строк
- experiment_sub_bar.py - 148 строк

## План рефакторинга по файлам

### 1. model_based.py (864 строки → ~300 строк)

**Текущая структура:**
- `ReactionTable` - таблица реакций
- `AdjustmentRowWidget` - виджет настройки параметров
- `AdjustingSettingsBox` - блок настроек корректировки
- `ModelCalcButtons` - кнопки расчетов
- `RangeAndCalculateWidget` - виджет диапазона и расчетов
- `ModelBasedTab` - основной виджет вкладки
- `CalculationSettingsDialog` - диалог настроек расчета

**План разбиения (по сущностям):**

```
src/gui/main_tab/sub_sidebar/model_based/
├── __init__.py
├── model_based_tab.py (~150 строк)  # ModelBasedTab
├── reaction_table.py (~100 строк)   # ReactionTable
├── adjustment_row_widget.py (~80 строк)  # AdjustmentRowWidget  
├── adjusting_settings_box.py (~100 строк)  # AdjustingSettingsBox
├── model_calc_buttons.py (~100 строк)  # ModelCalcButtons
├── range_and_calculate_widget.py (~80 строк)  # RangeAndCalculateWidget
├── calculation_settings_dialog.py (~250 строк)  # CalculationSettingsDialog
├── models_selection_dialog.py (~100 строк)  # ModelsSelectionDialog
└── models_scheme.py (требует рефакторинга)
```

**Детали разбиения:**

1. **reaction_table.py**
   - Класс `ReactionTable`
   - Dataclass `ReactionDefaults`, `LayoutSettings`

2. **adjustment_row_widget.py**
   - Класс `AdjustmentRowWidget`
   - Dataclass `AdjustmentDefaults`

3. **adjusting_settings_box.py**
   - Класс `AdjustingSettingsBox`
   - Dataclass `ReactionAdjustmentParameters`

4. **model_calc_buttons.py**
   - Класс `ModelCalcButtons`

5. **range_and_calculate_widget.py**
   - Класс `RangeAndCalculateWidget`

6. **calculation_settings_dialog.py**
   - Класс `CalculationSettingsDialog`

7. **models_selection_dialog.py**
   - Класс `ModelsSelectionDialog`

8. **model_based_tab.py** (обновленный)
   - Класс `ModelBasedTab` (координатор)

**Импорты в model_based_tab.py:**
```python
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable
from src.gui.main_tab.sub_sidebar.model_based.adjusting_settings_box import AdjustingSettingsBox
from src.gui.main_tab.sub_sidebar.model_based.calculation_settings_dialog import CalculationSettingsDialog
from src.gui.main_tab.sub_sidebar.model_based.models_scheme import ModelsScheme
from src.gui.main_tab.sub_sidebar.model_based.model_calc_buttons import ModelCalcButtons
from src.gui.main_tab.sub_sidebar.model_based.range_and_calculate_widget import RangeAndCalculateWidget
```

### 2. deconvolution_sub_bar.py (790 строк → ~300 строк)

**Текущая структура:**
- `FileTransferButtons` - кнопки импорта/экспорта
- `ReactionTableWidget` - таблица реакций
- `ButtonsWidget` - кнопки управления
- `DeconvolutionSubBar` - основной виджет
- Множество диалогов и вспомогательных классов

**План разбиения (по сущностям):**

```
src/gui/main_tab/sub_sidebar/deconvolution/
├── __init__.py
├── deconvolution_sub_bar.py (~150 строк)  # DeconvolutionSubBar
├── file_transfer_buttons.py (~100 строк)   # FileTransferButtons
├── reaction_table_widget.py (~120 строк)   # ReactionTableWidget
├── buttons_widget.py (~100 строк)          # ButtonsWidget
├── add_reaction_dialog.py (~150 строк)     # AddReactionDialog
├── edit_reaction_dialog.py (~120 строк)    # EditReactionDialog
├── deconvolution_settings_dialog.py (~150 строк)  # DeconvolutionSettingsDialog
└── reaction_utils.py (~100 строк)          # утилиты для работы с реакциями
```

**Детали разбиения:**

1. **file_transfer_buttons.py**
   - Класс `FileTransferButtons`
   - Логика импорта/экспорта файлов

2. **reaction_table_widget.py**
   - Класс `ReactionTableWidget`
   - Управление таблицей реакций

3. **buttons_widget.py**
   - Класс `ButtonsWidget`
   - Кнопки управления операциями

4. **add_reaction_dialog.py**
   - Класс `AddReactionDialog`
   - Валидация параметров

5. **edit_reaction_dialog.py**
   - Класс `EditReactionDialog`

6. **deconvolution_settings_dialog.py**
   - Класс `DeconvolutionSettingsDialog`
   - Параметры оптимизации

7. **reaction_utils.py**
   - Утилиты для работы с реакциями
   - Вспомогательные функции

8. **deconvolution_sub_bar.py** (обновленный)
   - Класс `DeconvolutionSubBar` (координатор)

**Импорты в deconvolution_sub_bar.py:**
```python
from src.gui.main_tab.sub_sidebar.deconvolution.file_transfer_buttons import FileTransferButtons
from src.gui.main_tab.sub_sidebar.deconvolution.reaction_table_widget import ReactionTableWidget
from src.gui.main_tab.sub_sidebar.deconvolution.buttons_widget import ButtonsWidget
from src.gui.main_tab.sub_sidebar.deconvolution.add_reaction_dialog import AddReactionDialog
from src.gui.main_tab.sub_sidebar.deconvolution.edit_reaction_dialog import EditReactionDialog
from src.gui.main_tab.sub_sidebar.deconvolution.deconvolution_settings_dialog import DeconvolutionSettingsDialog
```

### 3. models_scheme.py (612 строк → ~300 строк)

**Текущая структура:**
- `DiagramConfig` - конфигурация диаграммы
- `ReactionGraphicsRect` - графический элемент реакции
- `ReactionNode` - узел реакции  
- `ReactionArrow` - стрелка между узлами
- `ModelsScheme` - основная схема моделей

**План разбиения (по сущностям):**

```
src/gui/main_tab/sub_sidebar/model_based/
├── models_scheme.py (~200 строк)    # ModelsScheme
├── diagram_config.py (~50 строк)    # DiagramConfig
├── reaction_graphics_rect.py (~80 строк)  # ReactionGraphicsRect
├── reaction_node.py (~120 строк)    # ReactionNode
├── reaction_arrow.py (~150 строк)   # ReactionArrow
```

**Детали разбиения:**

1. **diagram_config.py**
   - Класс `DiagramConfig`
   - Константы размеров и цветов

2. **reaction_graphics_rect.py**
   - Класс `ReactionGraphicsRect`
   - Обработка событий мыши для графических элементов

3. **reaction_node.py**
   - Класс `ReactionNode`
   - Отрисовка и управление узлами

4. **reaction_arrow.py**
   - Класс `ReactionArrow`
   - Отрисовка стрелок между узлами
   - Вычисление пересечений

5. **models_scheme.py** (обновленный)
   - Класс `ModelsScheme` (основной координатор)
   - Управление схемой и компоновкой

**Импорты в models_scheme.py:**
```python
from src.gui.main_tab.sub_sidebar.model_based.diagram_config import DiagramConfig
from src.gui.main_tab.sub_sidebar.model_based.reaction_graphics_rect import ReactionGraphicsRect
from src.gui.main_tab.sub_sidebar.model_based.reaction_node import ReactionNode
from src.gui.main_tab.sub_sidebar.model_based.reaction_arrow import ReactionArrow
```

### 4. plot_canvas.py (505 строк → ~300 строк)

**Текущая структура:**
- `PlotCanvas` - основной виджет графика
- Множество методов для отрисовки и взаимодействия

**План разбиения (по сущностям):**

```
src/gui/main_tab/
├── plot_canvas.py (~200 строк)    # PlotCanvas (основной класс)
├── data_renderer.py (~150 строк)  # отрисовка данных
├── model_renderer.py (~120 строк) # отрисовка моделей
├── annotation_renderer.py (~100 строк)  # отрисовка аннотаций
├── anchor_interactions.py (~120 строк)  # взаимодействие с якорями
└── anchor_group.py (уже существует)
```

**Детали разбиения:**

1. **data_renderer.py**
   - Класс `DataRenderer` 
   - Методы отрисовки экспериментальных данных

2. **model_renderer.py**
   - Класс `ModelRenderer`
   - Методы отрисовки модельных кривых

3. **annotation_renderer.py**
   - Класс `AnnotationRenderer`
   - Методы создания и управления аннотациями

4. **anchor_interactions.py**
   - Класс `AnchorInteractions`
   - Обработка взаимодействий с якорями

5. **plot_canvas.py** (обновленный)
   - Класс `PlotCanvas` (основной координатор)
   - Управление компоновкой и событиями

**Импорты в plot_canvas.py:**
```python
from src.gui.main_tab.data_renderer import DataRenderer
from src.gui.main_tab.model_renderer import ModelRenderer
from src.gui.main_tab.annotation_renderer import AnnotationRenderer
from src.gui.main_tab.anchor_interactions import AnchorInteractions
from src.gui.main_tab.anchor_group import AnchorGroup
```

### 5. main_window.py (476 строк → ~300 строк)

**Текущая структура:**
- `MainWindow` - основное окно приложения
- Множество слотов и обработчиков сигналов

**План разбиения (по сущностям):**

```
src/gui/
├── main_window.py (~150 строк)       # MainWindow (основной класс)
├── signal_handlers.py (~180 строк)   # обработчики сигналов
├── request_processors.py (~150 строк) # обработчики запросов
├── main_tab/
└── table_tab/
```

**Детали разбиения:**

1. **signal_handlers.py**
   - Класс `SignalHandlers`
   - Методы обработки сигналов от различных компонентов

2. **request_processors.py**
   - Класс `RequestProcessors`
   - Методы обработки запросов к данным

3. **main_window.py** (обновленный)
   - Класс `MainWindow` (основной координатор)
   - Инициализация и управление компонентами

**Импорты в main_window.py:**
```python
from src.gui.signal_handlers import SignalHandlers
from src.gui.request_processors import RequestProcessors
from src.gui.main_tab.main_tab import MainTab
from src.gui.table_tab.table_tab import TableTab
```

### 6. sidebar.py (348 строк → ~300 строк)

**Текущая структура:**
- `SideBar` - боковая панель
- `SelectFileDataDialog` - диалог выбора данных файлов
- Обработка различных типов операций

**План разбиения (по сущностям):**

```
src/gui/main_tab/
├── sidebar.py (~200 строк)  # SideBar
├── select_file_data_dialog.py (~150 строк)  # SelectFileDataDialog
```

**Детали разбиения:**

1. **select_file_data_dialog.py**
   - Класс `SelectFileDataDialog`
   - Логика выбора файлов для серий

2. **sidebar.py** (обновленный)
   - Класс `SideBar` (основной класс)
   - Управление деревом элементов

**Импорты в sidebar.py:**
```python
from src.gui.main_tab.select_file_data_dialog import SelectFileDataDialog
from src.gui.main_tab.load_file_button import LoadButton
```

### 7. model_free_sub_bar.py (312 строк → ~250 строк)

**Текущая структура:**
- `ModelFreeSubBar` - основной виджет
- `ModelFreeAnnotationSettingsDialog` - диалог настроек аннотаций

**План разбиения (по сущностям):**

```
src/gui/main_tab/sub_sidebar/model_free/
├── __init__.py
├── model_free_sub_bar.py (~200 строк)  # ModelFreeSubBar
└── model_free_annotation_settings_dialog.py (~120 строк)  # ModelFreeAnnotationSettingsDialog
```

**Детали разбиения:**

1. **model_free_annotation_settings_dialog.py**
   - Класс `ModelFreeAnnotationSettingsDialog`
   - Настройки отображения аннотаций

2. **model_free_sub_bar.py** (обновленный)
   - Класс `ModelFreeSubBar` (основной класс)
   - Управление вычислениями model-free методов

**Импорты в model_free_sub_bar.py:**
```python
from src.gui.main_tab.sub_sidebar.model_free.model_free_annotation_settings_dialog import ModelFreeAnnotationSettingsDialog
```

## Общие принципы рефакторинга

### 1. Именование сущностей

- **Один файл = одна сущность** (класс/dataclass)
- Файлы называются точно по имени содержащегося класса: `reaction_table.py` → `ReactionTable`
- Избегаем групповых названий: `widgets.py`, `components.py`, `dialogs.py`
- Исключение: утилиты с префиксом по области: `reaction_utils.py`

### 2. Абсолютные импорты

Все импорты должны быть абсолютными от корня проекта:

```python
# ✅ Правильно
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable
from src.gui.main_tab.sub_sidebar.model_based.adjusting_settings_box import AdjustingSettingsBox
from src.gui.main_tab.sub_sidebar.model_based.calculation_settings_dialog import CalculationSettingsDialog

# ❌ Неправильно - относительные импорты
from .reaction_table import ReactionTable
from ..dialogs.calculation_settings_dialog import CalculationSettingsDialog
```

### 3. Структура модулей

- **Основной модуль** содержит главный класс-координатор
- **Отдельные файлы** для каждой сущности (виджета, диалога, dataclass)
- **Utilities** только для вспомогательных функций, не классов
- **Конфигурация** выделяется в отдельные файлы: `diagram_config.py`

### 4. Инициализация __init__.py

Основные классы экспортируются через __init__.py для удобства:

```python
# src/gui/main_tab/sub_sidebar/model_based/__init__.py
from src.gui.main_tab.sub_sidebar.model_based.model_based_tab import ModelBasedTab
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable

__all__ = ['ModelBasedTab', 'ReactionTable']
```

### 5. Сохранение функциональности

- Все сигналы и слоты должны работать как прежде
- API основных классов не должно измениться
- Тесты должны проходить без изменений

## Примеры рефакторинга

### Пример 1: Разбиение model_based.py

**Было (один файл):**
```python
# model_based.py (864 строки)
@dataclass
class ReactionDefaults:
    # ... настройки по умолчанию

class ReactionTable(QTableWidget):
    # ... 100+ строк

class AdjustmentRowWidget(QWidget):
    # ... 80+ строк

class ModelBasedTab(QWidget):
    # ... остальной код
```

**Стало (несколько файлов):**
```python
# reaction_table.py (~100 строк)
from dataclasses import dataclass
from PyQt6.QtWidgets import QTableWidget
from src.core.app_settings import OperationType

@dataclass
class ReactionDefaults:
    # ... настройки

class ReactionTable(QTableWidget):
    # ... только код таблицы

# adjustment_row_widget.py (~80 строк)
from PyQt6.QtWidgets import QWidget
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionDefaults

class AdjustmentRowWidget(QWidget):
    # ... только код виджета

# model_based_tab.py (~150 строк)
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable
from src.gui.main_tab.sub_sidebar.model_based.adjustment_row_widget import AdjustmentRowWidget

class ModelBasedTab(QWidget):
    # ... только координация компонентов
```

### Пример 2: Правильное именование файлов

**❌ Неправильно (по функциональности):**
```
components/
├── tables.py          # содержит ReactionTable, DataTable
├── widgets.py         # содержит AdjustmentRowWidget, CalculateWidget  
├── dialogs.py         # содержит SettingsDialog, AddDialog
```

**✅ Правильно (по сущностям):**
```
├── reaction_table.py           # содержит ReactionTable
├── adjustment_row_widget.py    # содержит AdjustmentRowWidget
├── calculate_widget.py         # содержит CalculateWidget
├── settings_dialog.py          # содержит SettingsDialog
├── add_dialog.py              # содержит AddDialog
```

## Порядок выполнения рефакторинга

1. **Этап 1:** model_based.py (самый сложный)
2. **Этап 2:** deconvolution_sub_bar.py
3. **Этап 3:** models_scheme.py  
4. **Этап 4:** plot_canvas.py
5. **Этап 5:** main_window.py
6. **Этап 6:** sidebar.py
7. **Этап 7:** model_free_sub_bar.py

## Критерии успеха

- ✅ Все файлы содержат менее 300 строк
- ✅ Функциональность сохранена полностью
- ✅ Код стал более читаемым и модульным
- ✅ Легче добавлять новые компоненты
- ✅ Улучшена тестируемость отдельных модулей

## Дополнительные рекомендации

### Именование файлов

- Используйте snake_case для файлов
- Имена должны отражать содержащуюся сущность, а не функциональность
- Избегайте слишком длинных имен
- Примеры: `reaction_table.py`, `adjustment_row_widget.py`, `calculation_settings_dialog.py`

### Документация

- Каждый новый модуль должен иметь docstring с описанием содержащейся сущности
- Публичные методы должны быть документированы
- Добавьте примеры использования для сложных компонентов

### Тестирование

- Создайте unit-тесты для новых модулей
- Проверьте интеграционные тесты
- Убедитесь, что все сигналы работают корректно

### Обратная совместимость

- Старые импорты должны продолжать работать через __init__.py
- Добавьте deprecation warnings если нужно
- Обновите документацию с новой структурой

### Дополнительные правила именования

**✅ Правильно:**
- `reaction_table.py` → класс `ReactionTable`
- `adjustment_row_widget.py` → класс `AdjustmentRowWidget`
- `calculation_settings_dialog.py` → класс `CalculationSettingsDialog`
- `diagram_config.py` → класс `DiagramConfig`

**❌ Неправильно:**
- `table_widgets.py` (группировка по типу)
- `ui_components.py` (группировка по назначению)
- `model_based_widgets.py` (группировка по области)
- `dialog_windows.py` (группировка по функциональности)

## Заключение

Этот план рефакторинга позволит значительно улучшить структуру UI кода, сделав его более поддерживаемым и расширяемым. Каждый этап можно выполнять независимо, что минимизирует риски и позволяет постепенно улучшать кодовую базу.

## Детальные принципы архитектуры

### Принцип "Одна сущность = один файл"

Каждый файл должен содержать ровно одну основную сущность:

**✅ Правильная структура:**
```
src/gui/main_tab/sub_sidebar/model_based/
├── model_based_tab.py          # class ModelBasedTab
├── reaction_table.py           # class ReactionTable + dataclass ReactionDefaults
├── adjustment_row_widget.py    # class AdjustmentRowWidget + dataclass AdjustmentDefaults  
├── adjusting_settings_box.py   # class AdjustingSettingsBox + dataclass ReactionAdjustmentParameters
├── model_calc_buttons.py       # class ModelCalcButtons
├── range_and_calculate_widget.py # class RangeAndCalculateWidget
├── calculation_settings_dialog.py # class CalculationSettingsDialog
├── models_selection_dialog.py  # class ModelsSelectionDialog
├── models_scheme.py            # class ModelsScheme
├── diagram_config.py           # class DiagramConfig
├── reaction_graphics_rect.py   # class ReactionGraphicsRect
├── reaction_node.py            # class ReactionNode
└── reaction_arrow.py           # class ReactionArrow
```

**❌ Неправильная структура (группировка):**
```
src/gui/main_tab/sub_sidebar/model_based/
├── widgets.py                  # ReactionTable + AdjustmentRowWidget + ModelCalcButtons
├── dialogs.py                  # CalculationSettingsDialog + ModelsSelectionDialog
├── graphics.py                 # ReactionNode + ReactionArrow + ReactionGraphicsRect
└── model_based_tab.py
```

### Именование файлов по содержащемуся классу

Файл всегда называется точно по основному классу, который в нем содержится:

```python
# reaction_table.py
class ReactionTable(QTableWidget):
    pass

# adjustment_row_widget.py  
class AdjustmentRowWidget(QWidget):
    pass

# calculation_settings_dialog.py
class CalculationSettingsDialog(QDialog):
    pass

# diagram_config.py
class DiagramConfig:
    pass
```

### Правильное размещение dataclass и вспомогательных сущностей

Dataclass размещаются в том же файле, что и основной класс, который их использует:

```python
# reaction_table.py
from dataclasses import dataclass

@dataclass
class ReactionDefaults:
    Ea_range: tuple[float, float] = (1, 2000)
    log_A_range: tuple[float, float] = (0.1, 100)
    contribution_range: tuple[float, float] = (0.01, 1.0)

@dataclass  
class LayoutSettings:
    reaction_table_column_widths: tuple[int, int, int, int] = (70, 50, 50, 50)
    reaction_table_row_heights: tuple[int, int, int] = (30, 30, 30)

class ReactionTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.defaults = ReactionDefaults()
        self.layout_settings = LayoutSettings()
```

### Абсолютные импорты везде

Все импорты должны быть абсолютными от корня проекта:

```python
# В файле model_based_tab.py
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable
from src.gui.main_tab.sub_sidebar.model_based.adjusting_settings_box import AdjustingSettingsBox
from src.gui.main_tab.sub_sidebar.model_based.calculation_settings_dialog import CalculationSettingsDialog
from src.gui.main_tab.sub_sidebar.model_based.models_scheme import ModelsScheme
from src.gui.main_tab.sub_sidebar.model_based.model_calc_buttons import ModelCalcButtons
from src.gui.main_tab.sub_sidebar.model_based.range_and_calculate_widget import RangeAndCalculateWidget

# В файле adjusting_settings_box.py
from src.gui.main_tab.sub_sidebar.model_based.adjustment_row_widget import AdjustmentRowWidget
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionDefaults

# В файле models_scheme.py  
from src.gui.main_tab.sub_sidebar.model_based.diagram_config import DiagramConfig
from src.gui.main_tab.sub_sidebar.model_based.reaction_graphics_rect import ReactionGraphicsRect
from src.gui.main_tab.sub_sidebar.model_based.reaction_node import ReactionNode
from src.gui.main_tab.sub_sidebar.model_based.reaction_arrow import ReactionArrow
```

### Исключения для утилит

Только для утилитарных функций допускается название с суффиксом по области применения:

```python
# reaction_utils.py - ТОЛЬКО для вспомогательных функций
def validate_reaction_parameters(ea: float, log_a: float) -> bool:
    """Валидирует параметры реакции."""
    pass

def convert_reaction_format(old_format: dict) -> dict:
    """Конвертирует старый формат реакций в новый."""
    pass
```

**❌ НЕ используйте utils для классов:**
```python
# ❌ НЕПРАВИЛЬНО - класс в utils файле
# reaction_utils.py  
class ReactionValidator:  # Должен быть в reaction_validator.py
    pass
```

### Структура каталогов по сущностям

Каталоги создаются только для группировки файлов одной функциональной области, но не для группировки по типу кода:

**✅ Правильно (по функциональным областям):**
```
src/gui/main_tab/sub_sidebar/
├── model_based/              # область model-based расчетов
│   ├── model_based_tab.py
│   ├── reaction_table.py
│   ├── models_scheme.py
│   └── diagram_config.py
├── deconvolution/            # область деконволюции  
│   ├── deconvolution_sub_bar.py
│   ├── file_transfer_buttons.py
│   └── reaction_table_widget.py
└── model_free/               # область model-free расчетов
    ├── model_free_sub_bar.py
    └── model_free_annotation_settings_dialog.py
```

**❌ Неправильно (по типу кода):**
```
src/gui/main_tab/sub_sidebar/
├── widgets/                  # группировка по типу
│   ├── reaction_table.py
│   ├── adjustment_row_widget.py
│   └── model_calc_buttons.py
├── dialogs/                  # группировка по типу
│   ├── calculation_settings_dialog.py
│   └── models_selection_dialog.py
└── graphics/                 # группировка по типу
    ├── reaction_node.py
    └── reaction_arrow.py
```

### Пример полной структуры model_based после рефакторинга

```
src/gui/main_tab/sub_sidebar/model_based/
├── __init__.py                         # экспорт основных классов
├── model_based_tab.py                  # ModelBasedTab (координатор)
├── reaction_table.py                   # ReactionTable + ReactionDefaults + LayoutSettings
├── adjustment_row_widget.py            # AdjustmentRowWidget + AdjustmentDefaults
├── adjusting_settings_box.py           # AdjustingSettingsBox + ReactionAdjustmentParameters
├── model_calc_buttons.py               # ModelCalcButtons
├── range_and_calculate_widget.py       # RangeAndCalculateWidget
├── calculation_settings_dialog.py      # CalculationSettingsDialog
├── models_selection_dialog.py          # ModelsSelectionDialog
├── models_scheme.py                    # ModelsScheme (координатор схемы)
├── diagram_config.py                   # DiagramConfig (конфигурация)
├── reaction_graphics_rect.py           # ReactionGraphicsRect (графический элемент)
├── reaction_node.py                    # ReactionNode (узел схемы)
└── reaction_arrow.py                   # ReactionArrow (стрелка схемы)
```

### Содержимое __init__.py

```python
# src/gui/main_tab/sub_sidebar/model_based/__init__.py
"""
Модуль model-based расчетов кинетических параметров.

Основные классы:
- ModelBasedTab: основной виджет вкладки
- ReactionTable: таблица реакций
- ModelsScheme: схема реакций
"""

from src.gui.main_tab.sub_sidebar.model_based.model_based_tab import ModelBasedTab
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable
from src.gui.main_tab.sub_sidebar.model_based.models_scheme import ModelsScheme

__all__ = [
    'ModelBasedTab',
    'ReactionTable', 
    'ModelsScheme'
]
```

## Архитектурные паттерны

### Паттерн "Координатор"

Основные классы (например, `ModelBasedTab`) служат координаторами и содержат минимум логики:

```python
# model_based_tab.py
class ModelBasedTab(QWidget):
    """Координатор компонентов model-based расчетов."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Создает и размещает UI компоненты."""
        layout = QVBoxLayout(self)
        
        self.reaction_table = ReactionTable()
        self.adjusting_settings = AdjustingSettingsBox()
        self.models_scheme = ModelsScheme()
        self.calc_buttons = ModelCalcButtons()
        
        layout.addWidget(self.reaction_table)
        layout.addWidget(self.adjusting_settings)
        layout.addWidget(self.models_scheme)
        layout.addWidget(self.calc_buttons)
    
    def _setup_connections(self):
        """Настраивает связи между компонентами."""
        self.reaction_table.params_changed.connect(self._on_params_changed)
        self.calc_buttons.calculate_clicked.connect(self._on_calculate)
```

### Паттерн "Одна ответственность"

Каждый класс отвечает за одну конкретную задачу:

```python
# reaction_table.py - ТОЛЬКО за таблицу реакций
class ReactionTable(QTableWidget):
    """Таблица для отображения и редактирования параметров реакций."""
    pass

# model_calc_buttons.py - ТОЛЬКО за кнопки расчетов  
class ModelCalcButtons(QWidget):
    """Кнопки управления расчетами модели."""
    pass

# diagram_config.py - ТОЛЬКО за конфигурацию диаграммы
class DiagramConfig:
    """Конфигурация отображения диаграммы реакций."""
    pass
```

## Практические примеры проблем и их решения

### Проблема 1: Сложность навигации в больших файлах

**До рефакторинга:**
```python
# model_based.py (864 строки)
class ReactionTable(QTableWidget):
    # 100+ строк кода
    
@dataclass
class ReactionDefaults:
    # настройки по умолчанию

class AdjustmentRowWidget(QWidget):
    # 80+ строк кода
    
class ModelBasedTab(QWidget):
    # 150+ строк кода
    
class CalculationSettingsDialog(QDialog):
    # 250+ строк кода
```

**Проблемы:**
- Трудно найти нужный класс в файле
- IDE тормозит при загрузке больших файлов
- Конфликты при коллективной разработке
- Сложность code review

**После рефакторинга:**
```
model_based/
├── reaction_table.py          # 100 строк - легко найти и отредактировать
├── adjustment_row_widget.py   # 80 строк - быстрая загрузка
├── model_based_tab.py         # 150 строк - четкая ответственность
└── calculation_settings_dialog.py # 250 строк - изолированная логика
```

### Проблема 2: Сложность тестирования

**До рефакторинга:**
```python
# Тестирование требует импорта всего файла
from src.gui.main_tab.sub_sidebar.model_based.model_based import ReactionTable

# При этом загружаются все 864 строки со всеми зависимостями
```

**После рефакторинга:**
```python
# Тестируем только нужную сущность
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable

# Загружается только 100 строк с минимальными зависимостями
```

### Проблема 3: Циклические зависимости

**До рефакторинга:**
```python
# В model_based.py все классы видят друг друга
class ReactionTable:
    def __init__(self):
        # Может обращаться к ModelBasedTab, создавая связность
        pass

class ModelBasedTab:
    def __init__(self):
        # Использует ReactionTable
        self.table = ReactionTable()
```

**После рефакторинга:**
```python
# reaction_table.py - независимый модуль
class ReactionTable:
    # Не знает о существовании ModelBasedTab
    pass

# model_based_tab.py - координатор
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable

class ModelBasedTab:
    def __init__(self):
        self.table = ReactionTable()  # четкая зависимость
```

### Проблема 4: Относительные импорты и путаница

**До рефакторинга:**
```python
# В разных файлах разные способы импорта
from .model_based import ReactionTable           # model_based_tab.py
from ..model_based import ReactionTable         # sidebar.py  
from ...model_based import ReactionTable       # main_window.py
```

**Проблемы:**
- Трудно понять, откуда импорт
- Ошибки при перемещении файлов
- Сложность рефакторинга структуры

**После рефакторинга:**
```python
# Везде единообразные абсолютные импорты
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ReactionTable
```

### Проблема 5: Нарушение принципа единственной ответственности

**До рефакторинга:**
```python
# model_based.py отвечает за ВСЁ:
# - таблицы
# - диалоги  
# - настройки
# - вычисления
# - графику
```

**После рефакторинга:**
```python
# reaction_table.py - только за таблицу реакций
# calculation_settings_dialog.py - только за настройки расчетов
# models_scheme.py - только за схему моделей
# model_based_tab.py - только за координацию компонентов
```

## Метрики качества рефакторинга

### Количественные показатели

| Метрика                    | До рефакторинга | После рефакторинга | Улучшение |
| -------------------------- | --------------- | ------------------ | --------- |
| Средний размер файла       | 580 строк       | 200 строк          | **65%**   |
| Максимальный размер файла  | 864 строки      | 300 строк          | **65%**   |
| Количество классов в файле | 2-5 классов     | 1 класс            | **80%**   |
| Цикломатическая сложность  | Высокая         | Низкая             | **60%**   |
| Время загрузки модуля      | ~200ms          | ~50ms              | **75%**   |

### Качественные показатели

**✅ Читаемость кода:**
- Легко найти нужный класс
- Понятная структура каталогов
- Единообразные паттерны именования

**✅ Поддерживаемость:**
- Изолированная логика
- Четкие зависимости
- Простота модификации

**✅ Тестируемость:**
- Возможность unit-тестирования отдельных компонентов
- Мокирование зависимостей
- Быстрое выполнение тестов

**✅ Масштабируемость:**
- Простота добавления новых компонентов
- Переиспользование кода
- Слабая связанность модулей

### Инструменты контроля качества

```bash
# Проверка размера файлов
find src/gui -name "*.py" -exec wc -l {} + | sort -n

# Анализ цикломатической сложности
radon cc src/gui --min B

# Проверка дублирования кода  
radon raw src/gui --summary

# Линтинг кода
flake8 src/gui --max-line-length=100
pylint src/gui
```

## Дорожная карта внедрения

### Фаза 1: Подготовка (1-2 дня)
- [ ] Создание веток для рефакторинга
- [ ] Настройка инструментов анализа кода
- [ ] Документирование текущего API

### Фаза 2: Рефакторинг ядра (3-5 дней)
- [ ] model_based.py → 13 файлов
- [ ] deconvolution_sub_bar.py → 8 файлов  
- [ ] models_scheme.py → 5 файлов

### Фаза 3: Рефакторинг UI (2-3 дня)
- [ ] plot_canvas.py → 6 файлов
- [ ] main_window.py → 3 файла
- [ ] sidebar.py → 2 файла

### Фаза 4: Завершение (1-2 дня)
- [ ] model_free_sub_bar.py → 2 файла
- [ ] Обновление __init__.py файлов
- [ ] Проверка всех импортов

### Фаза 5: Тестирование (2-3 дня)
- [ ] Запуск всех тестов
- [ ] Проверка функциональности
- [ ] Анализ производительности
- [ ] Code review

### Критерии готовности к продакшену

**Обязательные:**
- ✅ Все тесты проходят
- ✅ Функциональность полностью сохранена
- ✅ Нет критических ошибок линтера
- ✅ Время загрузки не увеличилось

**Желательные:**
- ✅ Покрытие тестами >= 80%
- ✅ Цикломатическая сложность <= B
- ✅ Дублирование кода <= 5%
- ✅ Размер файлов <= 300 строк

## Практические примеры проблем и их решения
