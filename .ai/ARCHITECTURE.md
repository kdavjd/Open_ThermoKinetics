# Архитектура приложения Open ThermoKinetics

> **Последнее обновление:** 2026-02-13
> **Ветка:** feature/claude-integration

---

## Обзор

**Open ThermoKinetics** — desktop GUI приложение для расчёта кинетических моделей твердофазных химических реакций. Построено на модульной сигнально-управляемой архитектуре PyQt6 с централизованным диспетчером сообщений.

### Ключевые принципы

- **Signal-Slot коммуникация** — все компоненты обмениваются данными через слабосвязанные Qt сигналы
- **Request-Response паттерн** — синхронные операции поверх асинхронных сигналов через `QEventLoop`
- **Разделение слоёв** — GUI (`src/gui/`) отделён от бизнес-логики (`src/core/`)
- **Strategy Pattern** — различные сценарии расчётов реализованы как независимые стратегии

---

## Структура проекта

```
src/
├── gui/                          # GUI слой (PyQt6)
│   ├── main_window.py            # Главное окно
│   ├── main_tab/                 # Главная вкладка анализа
│   │   ├── main_tab.py           # 4-панельный layout
│   │   ├── sidebar.py            # Навигация
│   │   ├── sub_sidebar/          # Панели анализа
│   │   └── plot_canvas/          # Matplotlib визуализация
│   └── user_guide_tab/           # Документация
│
└── core/                         # Бизнес-логика
    ├── base_signals.py           # Центральный диспетчер сигналов
    ├── app_settings.py           # Конфигурация и модели
    ├── calculation.py            # Оркестрация оптимизации
    ├── calculation_scenarios.py  # Сценарии расчётов
    ├── file_data.py              # Данные файлов
    ├── calculation_data.py       # Параметры реакций
    ├── series_data.py            # Серии экспериментов
    ├── curve_fitting.py          # Математические функции
    ├── model_fit_calculation.py  # Model-fitting
    └── model_free_calculation.py # Model-free анализ
```

---

## Система коммуникации

### BaseSignals — Центральный диспетчер

**Файл:** [src/core/base_signals.py:9-61](src/core/base_signals.py#L9-L61)

```python
class BaseSignals(QObject):
    request_signal = pyqtSignal(dict)
    response_signal = pyqtSignal(dict)
```

Все компоненты регистрируются в диспетчере и обмениваются данными через publisher-subscriber паттерн.

#### Регистрация компонента

```python
def register_component(
    self,
    component_name: str,
    process_request_method: Callable[[dict], None],
    process_response_method: Callable[[dict], None],
) -> None:
    self.components[component_name] = (process_request_method, process_response_method)
```

#### Маршрутизация запросов

```python
@pyqtSlot(dict)
def dispatch_request(self, params: dict) -> None:
    target = params.get("target")
    if target in self.components:
        process_request_method, _ = self.components[target]
        process_request_method(params)
```

### BaseSlots — Базовый класс для компонентов

**Файл:** [src/core/base_signals.py:63-198](src/core/base_signals.py#L63-L198)

Предоставляет синхронный request-response поверх асинхронных Qt сигналов:

```python
def handle_request_cycle(self, target: str, operation: str, **kwargs) -> Any:
    request_id = self.create_and_emit_request(target, operation, **kwargs)
    response_data = self.handle_response_data(request_id, operation)
    return response_data
```

#### Блокировка через QEventLoop

```python
def wait_for_response(self, request_id: str, timeout: int = 1000) -> Optional[dict]:
    loop = QEventLoop()
    self.event_loops[request_id] = loop

    while not self.pending_requests[request_id]["received"] and not timed_out:
        loop.exec()

    return self.pending_requests.pop(request_id)["data"]
```

### Формат сообщений

```python
# Request
{
    "actor": "main_window",        # Отправитель
    "target": "file_data",         # Получатель
    "operation": "GET_DF_DATA",    # Тип операции
    "request_id": "uuid",          # Уникальный ID
    "file_name": "experiment.csv", # Параметры
    ...
}

# Response
{
    "actor": "file_data",          # Отправитель (бывший target)
    "target": "main_window",       # Получатель (бывший actor)
    "operation": "GET_DF_DATA",
    "request_id": "uuid",
    "data": pd.DataFrame(...)      # Результат
}
```

---

## Типы операций (OperationType)

**Файл:** [src/core/app_settings.py:87-130](src/core/app_settings.py#L87-L130)

```python
class OperationType(Enum):
    # Файловые операции
    LOAD_FILE = "load_file"
    GET_DF_DATA = "get_df_data"
    RESET_FILE_DATA = "reset_file_data"

    # Трансформация данных
    TO_A_T = "to_a_t"          # Конверсия в α(t)
    TO_DTG = "to_dtg"          # Производная dα/dT

    # Реакции (деконволюция)
    ADD_REACTION = "add_reaction"
    REMOVE_REACTION = "remove_reaction"
    HIGHLIGHT_REACTION = "highlight_reaction"
    UPDATE_VALUE = "update_value"

    # Расчёты
    DECONVOLUTION = "deconvolution"
    MODEL_BASED_CALCULATION = "model_based_calculation"
    MODEL_FIT_CALCULATION = "model_fit_calculation"
    MODEL_FREE_CALCULATION = "model_free_calculation"
    STOP_CALCULATION = "stop_calculation"

    # Серии
    ADD_NEW_SERIES = "add_new_series"
    UPDATE_SERIES = "update_series"
    GET_SERIES = "get_series"
    ...
```

---

## Модули расчётов

### Calculations — Оркестратор оптимизации

**Файл:** [src/core/calculation.py:18-248](src/core/calculation.py#L18-L248)

Центральный менеджер расчётов с потоковой обработкой и стратегиями результатов:

```python
class Calculations(BaseSlots):
    new_best_result = pyqtSignal(dict)

    def __init__(self, signals):
        self.thread: Optional[CalculationThread] = None
        self.deconvolution_strategy = DeconvolutionStrategy(self)
        self.model_based_calculation_strategy = ModelBasedCalculationStrategy(self)
```

#### Запуск оптимизации

```python
def run_calculation_scenario(self, params: dict):
    scenario_cls = SCENARIO_REGISTRY.get(scenario_key)
    scenario_instance = scenario_cls(params, self)

    bounds = scenario_instance.get_bounds()
    target_function = scenario_instance.get_target_function()
    strategy_type = scenario_instance.get_result_strategy_type()

    self.set_result_strategy(strategy_type)
    self.start_differential_evolution(bounds, target_function, **calc_params)
```

### Сценарии расчётов (Strategy Pattern)

**Файл:** [src/core/calculation_scenarios.py:50-460](src/core/calculation_scenarios.py#L50-L460)

```python
SCENARIO_REGISTRY = {
    "deconvolution": DeconvolutionScenario,
    "model_based_calculation": ModelBasedScenario,
}
```

#### BaseCalculationScenario

```python
class BaseCalculationScenario:
    def get_bounds(self) -> list[tuple]: ...
    def get_target_function(self, **kwargs) -> Callable: ...
    def get_optimization_method(self) -> str: ...
    def get_result_strategy_type(self) -> str: ...
    def get_constraints(self) -> list: ...
```

#### DeconvolutionScenario

Оптимизация пиков деконволюции (Gaussian, Fraser-Suzuki, ADS):

```python
def get_target_function(self, **kwargs) -> Callable:
    def target_function(params_array: np.ndarray) -> float:
        for combination in reaction_combinations:
            cumulative_function = np.zeros(len(experimental_data["temperature"]))
            for (reaction, coeffs), func in zip(reaction_variables.items(), combination):
                if func == "gauss":
                    reaction_values = cft.gaussian(x, h, z, w)
                elif func == "fraser":
                    reaction_values = cft.fraser_suzuki(x, h, z, w, fr)
                elif func == "ads":
                    reaction_values = cft.asymmetric_double_sigmoid(x, h, z, w, ads1, ads2)
                cumulative_function += reaction_values
            mse = np.mean((y_true - cumulative_function) ** 2)
        return best_mse
```

#### ModelBasedScenario

ODE интеграция со схемами реакций и оптимизация через differential_evolution:

```python
def get_target_function(self, **kwargs) -> callable:
    return ModelBasedTargetFunction(
        species_list,
        reactions,
        num_species,
        num_reactions,
        betas,
        all_exp_masses,
        exp_temperature,
        ...
    )
```

### Математические функции

**Файл:** [src/core/curve_fitting.py:9-178](src/core/curve_fitting.py#L9-L178)

```python
class CurveFitting:
    @staticmethod
    def gaussian(x, h, z, w) -> np.ndarray:
        return h * np.exp(-((x - z) ** 2) / (2 * w**2))

    @staticmethod
    def fraser_suzuki(x, h, z, w, fs) -> np.ndarray:
        return h * np.exp(-np.log(2) * ((np.log(1 + 2 * fs * ((x - z) / w)) / fs) ** 2))

    @staticmethod
    def asymmetric_double_sigmoid(x, h, z, w, ads1, ads2) -> np.ndarray:
        left_term = (1 + np.exp(-((x - z + w / 2) / ads1))) ** -1
        right_term = 1 - (1 + np.exp(-((x - z - w / 2) / ads2))) ** -1
        return h * left_term * right_term
```

---

## Кинетические модели (Nucleation Models)

**Файл:** [src/core/app_settings.py:270-876](src/core/app_settings.py#L270-L876)

### Таблица моделей

```python
NUC_MODELS_TABLE = {
    "F1/3": {"differential_form": differential_F1_3, "integral_form": integral_F1_3},
    "F2": {"differential_form": differential_F2, "integral_form": integral_F2},
    "A2": {"differential_form": differential_A2, "integral_form": integral_A2},
    "A3": {"differential_form": differential_A3, "integral_form": integral_A3},
    "R3": {"differential_form": differential_R3, "integral_form": integral_R3},
    "D3": {"differential_form": differential_D3, "integral_form": integral_D3},
    ...
}
```

### Категории моделей

| Категория | Модели | Описание |
|-----------|--------|----------|
| **F (n-th order)** | F1/3, F3/4, F3/2, F2, F3, F1/A1 | N-го порядка |
| **A (Avrami-Erofeev)** | A2, A3, A4, A2/3, A3/2, A3/4, A5/2 | Нуклеация и рост |
| **R (Contracting)** | R2, R3 | Контрактирующая поверхность |
| **P (Power law)** | P3/2, P2, P3, P4 | Степенной закон |
| **D (Diffusion)** | D1-D8 | Диффузионные модели |
| **G** | G1-G8 | Прочие модели |

### Примеры с Numba JIT

```python
@njit
def differential_F2(e):
    e = clip_fraction(e)
    return e**2

@njit
def integral_F2(e):
    e = clip_fraction(e)
    return e ** (-1.0) - 1
```

---

## Конфигурация оптимизации

**Файл:** [src/core/app_settings.py:133-218](src/core/app_settings.py#L133-L218)

### Differential Evolution Config

```python
@dataclass(frozen=True)
class ModelBasedDifferentialEvolutionConfig(DifferentialEvolutionConfig):
    workers: int = 6
    maxiter: int = 1000
    popsize: int = 50
    mutation: tuple = (0.4, 1.2)
    polish: bool = False
    updating: str = "immediate"
```

### Parameter Bounds

```python
@dataclass(frozen=True)
class ModelBasedParameterBounds:
    ea_min: float = 1.0
    ea_max: float = 250.0
    log_a_min: float = -15.0
    log_a_max: float = 30.0
    contribution_min: float = 0.01
    contribution_max: float = 1.0
```

---

## Data Flow

```
User Action (GUI)
       ↓
   pyqtSignal.emit(dict)
       ↓
BaseSignals.dispatch_request()
       ↓
Target.process_request(dict)
       ↓
Business Logic Execution
       ↓
response_signal.emit(dict)
       ↓
BaseSignals.dispatch_response()
       ↓
UI Update (pyqtSlot)
```

### Пример: Загрузка файла

```
1. User: Нажатие кнопки "Load File"
2. LoadFileButton → main_tab → main_window
3. MainWindow.handle_request_from_main_tab()
4. → FileData.load_file()
5. FileData._fetch_data()
6. data_loaded_signal.emit(DataFrame)
7. PlotCanvas.plot_data_from_dataframe()
```

---

## Регистрация компонентов

Все компоненты регистрируются в `BaseSignals` при инициализации:

```python
# В MainWindow.__init__
self.signals.register_component("main_window", self.process_request, self.process_response)

# В FileData.__init__
self.signals.register_component("file_data", self.process_request, self.process_response)

# В Calculations.__init__
self.signals.register_component("calculations", self.process_request, self.process_response)
```

### Активные компоненты

| Компонент | Файл | Назначение |
|-----------|------|------------|
| `main_window` | [main_window.py](src/gui/main_window.py) | Маршрутизация GUI операций |
| `file_data` | [file_data.py](src/core/file_data.py) | Управление экспериментальными данными |
| `calculations_data` | [calculation_data.py](src/core/calculation_data.py) | Параметры реакций |
| `series_data` | [series_data.py](src/core/series_data.py) | Серии экспериментов |
| `calculations` | [calculation.py](src/core/calculation.py) | Запуск оптимизаций |
| `calculations_data_operations` | [calculation_data_operations.py](src/core/calculation_data_operations.py) | Высокоуровневые операции |

---

## Связанные документы

- [UI_ARCHITECTURE.md](.ai/UI_ARCHITECTURE.md) — архитектура GUI
- [DATA_MODELS.md](.ai/DATA_MODELS.md) — структуры данных
- [CLAUDE.md](../CLAUDE.md) — инструкции для Claude Code
