# Архитектура GUI Open ThermoKinetics

> **Последнее обновление:** 2026-02-13
> **Ветка:** feature/claude-integration

---

## Обзор

GUI построен на **PyQt6** с 4-панельным адаптивным layout и интеграцией **Matplotlib** для визуализации. Все компоненты связываются через централизованную сигнально-слотовую систему.

---

## Точка входа

**Файл:** [src/gui/__main__.py](src/gui/__main__.py)

```bash
python -m src.gui
```

---

## MainWindow — Главное окно

**Файл:** [src/gui/main_window.py:15-704](src/gui/main_window.py#L15-L704)

Главное окно управляет вкладками и маршрутизацией сигналов между GUI и core модулями.

### Структура

```
MainWindow (QMainWindow)
├── QTabWidget
│   ├── MainTab (Главная вкладка)
│   └── UserGuideTab (Документация)
└── BaseSignals (маршрутизация)
```

### Инициализация

```python
class MainWindow(QMainWindow):
    to_main_tab_signal = pyqtSignal(dict)
    model_based_calculation_signal = pyqtSignal(dict)

    def __init__(self, signals: BaseSignals):
        self.tabs = QTabWidget(self)
        self.main_tab = MainTab(self)
        self.user_guide_tab = UserGuideTab(self)
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.user_guide_tab, "User Guide")
        self.signals = signals
        self.base_slots = BaseSlots(actor_name="main_window", signals=self.signals)
        self.signals.register_component(self.actor_name, self.process_request, self.process_response)
```

### Центральный диспетчер операций

**Файл:** [src/gui/main_window.py:113-158](src/gui/main_window.py#L113-L158)

```python
@pyqtSlot(dict)
def handle_request_from_main_tab(self, params: dict):
    operation_handlers = {
        OperationType.TO_DTG: self._handle_differential,
        OperationType.TO_A_T: self._handle_to_a_t,
        OperationType.ADD_REACTION: self._handle_add_reaction,
        OperationType.DECONVOLUTION: self._handle_deconvolution,
        OperationType.MODEL_BASED_CALCULATION: self._handle_model_based_calculation,
        OperationType.MODEL_FIT_CALCULATION: self._handle_model_fit_calculation,
        OperationType.MODEL_FREE_CALCULATION: self._handle_model_free_calculation,
        OperationType.ADD_NEW_SERIES: self._handle_add_new_series,
        ...
    }
    handler = operation_handlers.get(operation)
    if handler:
        handler(params)
```

---

## MainTab — Главная вкладка (4-панельный layout)

**Файл:** [src/gui/main_tab/main_tab.py:22-215](src/gui/main_tab/main_tab.py#L22-L215)

### Layout схема

```
┌──────────────┬──────────────┬────────────────────┬──────────────┐
│   Sidebar    │ Sub-Sidebar  │    Plot Canvas     │   Console    │
│  (220px)     │  (220px)     │    (flexible)      │   (150px)    │
│              │  (hidden by  │                    │              │
│              │   default)   │                    │              │
│              │              │                    │              │
│ • Files      │ • Experiment │ • Matplotlib       │ • Log output │
│ • Series     │ • Deconvolut │   figure           │   (colored)  │
│              │ • Model-Fit  │ • Interactive      │              │
│              │ • Model-Free │   anchors          │              │
│              │ • Model-Based│                    │              │
│              │ • Series     │                    │              │
└──────────────┴──────────────┴────────────────────┴──────────────┘
```

### Минимальные размеры

```python
MIN_WIDTH_SIDEBAR = 220
MIN_WIDTH_SUBSIDEBAR = 220
MIN_WIDTH_CONSOLE = 150
MIN_WIDTH_PLOTCANVAS = 500
MIN_HEIGHT_MAINTAB = 700
```

### Инициализация

```python
class MainTab(QWidget):
    to_main_window_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        self.sidebar = SideBar(self)
        self.sub_sidebar = SubSideHub(self)  # Скрыт по умолчанию
        self.plot_canvas = PlotCanvas(self)
        self.console_widget = ConsoleWidget(self)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.sub_sidebar)
        self.splitter.addWidget(self.plot_canvas)
        self.splitter.addWidget(self.console_widget)
```

### Пропорциональное изменение размеров

```python
def initialize_sizes(self):
    total_width = self.width()
    sidebar_ratio = MIN_WIDTH_SIDEBAR / COMPONENTS_MIN_WIDTH
    subsidebar_ratio = MIN_WIDTH_SUBSIDEBAR / COMPONENTS_MIN_WIDTH
    console_ratio = MIN_WIDTH_CONSOLE / COMPONENTS_MIN_WIDTH

    sidebar_width = int(total_width * sidebar_ratio)
    sub_sidebar_width = int(total_width * subsidebar_ratio) if self.sub_sidebar.isVisible() else 0
    canvas_width = total_width - (sidebar_width + sub_sidebar_width + console_width)
    self.splitter.setSizes([sidebar_width, sub_sidebar_width, canvas_width, console_width])
```

---

## Sidebar — Навигация

**Файл:** [src/gui/main_tab/sidebar.py](src/gui/main_tab/sidebar.py)

Деревовидная навигация по файлам и сериям экспериментов.

### Сигналы

```python
class SideBar(QWidget):
    to_main_window_signal = pyqtSignal(dict)
    sub_side_bar_needed = pyqtSignal(str)
    console_show_signal = pyqtSignal(bool)
    active_file_selected = pyqtSignal(str)
    active_series_selected = pyqtSignal(str)
```

### Структура дерева

```
├── Experiments
│   ├── file1.csv
│   └── file2.csv
└── Series
    ├── Series 1
    └── Series 2
```

---

## SubSideHub — Панели анализа

**Файл:** [src/gui/main_tab/sub_sidebar/sub_side_hub.py](src/gui/main_tab/sub_sidebar/sub_side_hub.py)

Переключатель между различными панелями анализа.

### Панели

| Панель | Модуль | Назначение |
|--------|--------|------------|
| **Experiments** | `experiment/` | Операции с данными (α(t), dα/dT) |
| **Deconvolution** | `deconvolution/` | Разделение пиков |
| **Model-Fit** | `model_fit/` | Подгонка к моделям |
| **Model-Free** | `model_free/` | Изоконверсионные методы |
| **Model-Based** | `model_based/` | ODE схемы реакций |
| **Series** | `series/` | Управление сериями |

### Переключение контента

```python
def update_content(self, content_type: str):
    if content_type == SideBarNames.EXPERIMENTS.value:
        self.stacked_widget.setCurrentWidget(self.experiment_sub_bar)
    elif content_type == SideBarNames.DECONVOLUTION.value:
        self.stacked_widget.setCurrentWidget(self.deconvolution_sub_bar)
    # ... и т.д.
```

---

## PlotCanvas — Визуализация

**Файл:** [src/gui/main_tab/plot_canvas/plot_canvas.py:31-245](src/gui/main_tab/plot_canvas/plot_canvas.py#L31-L245)

Виджет Matplotlib с интерактивными якорями для настройки параметров.

### Архитектура (Mixin pattern)

```python
class PlotCanvas(QWidget, PlotInteractionMixin, PlotStylingMixin):
    update_value = pyqtSignal(list)  # Сигнал изменений якорей

    def __init__(self, parent=None):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.lines: Dict[str, Line2D] = {}
```

### Миксины

| Миксин | Файл | Назначение |
|--------|------|------------|
| `PlotInteractionMixin` | [plot_interaction.py](src/gui/main_tab/plot_canvas/plot_interaction.py) | Mouse events, drag & drop |
| `PlotStylingMixin` | [plot_styling.py](src/gui/main_tab/plot_canvas/plot_styling.py) | Стилизация, fill-between |

### Основные методы

```python
def plot_data_from_dataframe(self, data: pd.DataFrame):
    self.axes.clear()
    self.lines.clear()
    x = data["temperature"]
    for column in data.columns:
        if column != "temperature":
            self.add_or_update_line(column, x, data[column], label=column)

def add_or_update_line(self, key, x, y, **kwargs):
    if key in self.lines:
        line = self.lines[key]
        line.set_data(x, y)
    else:
        (line,) = self.axes.plot(x, y, **kwargs)
        self.lines[key] = line
```

---

## Anchor Groups — Интерактивные якоря

**Файл:** [src/gui/main_tab/plot_canvas/anchor_group.py](src/gui/main_tab/plot_canvas/anchor_group.py)

Draggable anchors для визуальной настройки параметров деконволюции.

### Типы якорей

```python
class PositionAnchorGroup:
    """Якоря для позиции (z) и ширины (w) пика"""

class HeightAnchorGroup:
    """Якорь для высоты (h) пика"""
```

### События перетаскивания

```python
def on_motion(self, event):
    if self.dragging_anchor is not None:
        # Обновление координат якоря
        new_x = event.xdata
        new_y = event.ydata
        self.update_anchor_position(new_x, new_y)
        # Отправка сигнала об изменении
        self.update_value.emit(params_list)
```

---

## ConsoleWidget — Консоль вывода

**Файл:** [src/gui/console_widget.py](src/gui/console_widget.py)

Цветной вывод логов и сообщений пользователю.

```python
class ConsoleWidget(QTextEdit):
    def __init__(self, parent=None):
        self.setReadOnly(True)
        LoggerConsole.set_console(self)  # Редирект логов
```

---

## Сигнально-слотовые связи

### MainTab → MainWindow

```python
# В MainTab.__init__
self.sidebar.sub_side_bar_needed.connect(self.toggle_sub_sidebar)
self.sidebar.console_show_signal.connect(self.toggle_console_visibility)
self.plot_canvas.update_value.connect(self.update_anchors_slot)

# Маршрутизация в MainWindow
self.main_tab.to_main_window_signal.connect(self.handle_request_from_main_tab)
```

### Операции деконволюции

```
User: Добавить реакцию
       ↓
DeconvolutionPanel.reaction_added
       ↓
MainTab.to_main_window(params)
       ↓
MainWindow.handle_request_from_main_tab()
       ↓
MainWindow._handle_add_reaction()
       ↓
calculations_data_operations.ADD_REACTION
       ↓
CalculationsDataOperations.process_request()
```

### Интерактивные якоря

```
User: Drag anchor
       ↓
PlotCanvas.on_motion()
       ↓
update_value.emit(params_list)
       ↓
MainTab.update_anchors_slot()
       ↓
MainTab.to_main_window(params)
       ↓
MainWindow._handle_update_value()
       ↓
CalculationsDataOperations.update_value()
       ↓
PlotCanvas.plot_reaction() [визуальное обновление]
```

---

## Deconvolution Panel

**Файл:** [src/gui/main_tab/sub_sidebar/deconvolution/](src/gui/main_tab/sub_sidebar/deconvolution/)

### Компоненты

| Файл | Класс | Назначение |
|------|-------|------------|
| `deconvolution_panel.py` | DeconvolutionPanel | Контейнер панели |
| `reaction_table.py` | ReactionTable | Таблица реакций |
| `calculation_controls.py` | CalculationControls | Кнопки расчёта |
| `coefficients_view.py` | CoefficientsView | Просмотр коэффициентов |
| `settings_dialog.py` | SettingsDialog | Диалог настроек |
| `file_transfer.py` | FileTransferButtons | Импорт/экспорт |

### Сигналы

```python
class DeconvolutionPanel:
    reaction_added = pyqtSignal()
    reaction_removed = pyqtSignal()
    reaction_chosed = pyqtSignal(str)
    update_value = pyqtSignal(dict)
    calculation_started = pyqtSignal(dict)
    calculation_stopped = pyqtSignal()
```

---

## Model-Based Panel

**Файл:** [src/gui/main_tab/sub_sidebar/model_based/](src/gui/main_tab/sub_sidebar/model_based/)

### Компоненты

| Файл | Класс | Назначение |
|------|-------|------------|
| `model_based_panel.py` | ModelBasedPanel | Контейнер |
| `models_scheme.py` | ModelsScene | Визуализация схемы реакций |
| `parameter_table.py` | ParameterTable | Таблица параметров |
| `adjustment_controls.py` | AdjustmentControls | Ручная настройка |
| `calculation_controls.py` | CalculationControls | Запуск оптимизации |
| `calculation_settings_dialogs.py` | *Dialogs | Диалоги настроек |

### Схема реакций

```
A ──(1)──► B ──(2)──► C
     Ea₁        Ea₂
     logA₁      logA₂
```

---

## User Guide Tab

**Файл:** [src/gui/user_guide_tab/](src/gui/user_guide_tab/)

Кастомный фреймворк документации с Markdown-подобным рендерингом.

### Структура фреймворка

```
user_guide_framework/
├── core/
│   ├── content_manager.py      # Управление контентом
│   ├── navigation_manager.py   # Навигация
│   ├── theme_manager.py        # Темизация
│   └── localization_manager.py # Локализация
├── rendering/
│   ├── renderer_manager.py     # Менеджер рендереров
│   └── renderers/
│       ├── text_renderer.py
│       ├── code_renderer.py
│       ├── image_renderer.py
│       └── workflow_renderer.py
└── ui/
    ├── guide_framework.py      # Основной виджет
    ├── navigation_sidebar.py   # Sidebar навигации
    └── content_widget.py       # Область контента
```

---

## Темизация

### Matplotlib стиль

**Файл:** [src/gui/main_tab/plot_canvas/config.py](src/gui/main_tab/plot_canvas/config.py)

```python
class PLOT_CANVAS_CONFIG:
    PLOT_STYLE = ["science", "no-latex"]
    COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
```

### PyQt стили

```python
# В main_window.py
app.setStyle("Fusion")
```

---

## Константы размеров

**Файл:** [src/gui/main_tab/main_tab.py:11-19](src/gui/main_tab/main_tab.py#L11-L19)

```python
MIN_WIDTH_SIDEBAR = 220
MIN_WIDTH_SUBSIDEBAR = 220
MIN_WIDTH_CONSOLE = 150
MIN_WIDTH_PLOTCANVAS = 500
SPLITTER_WIDTH = 100
MIN_HEIGHT_MAINTAB = 700
COMPONENTS_MIN_WIDTH = (
    MIN_WIDTH_SIDEBAR + MIN_WIDTH_SUBSIDEBAR +
    MIN_WIDTH_CONSOLE + MIN_WIDTH_PLOTCANVAS + SPLITTER_WIDTH
)
```

---

## Связанные документы

- [ARCHITECTURE.md](.ai/ARCHITECTURE.md) — архитектура приложения
- [DATA_MODELS.md](.ai/DATA_MODELS.md) — структуры данных
