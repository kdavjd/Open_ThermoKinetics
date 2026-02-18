# Структуры данных Open ThermoKinetics

> **Последнее обновление:** 2026-02-13
> **Ветка:** feature/claude-integration

---

## Обзор

Приложение использует три основные структуры данных, наследующие от `BaseSlots` и управляемые через централизованную сигнальную систему:

| Класс | Файл | Назначение |
|-------|------|------------|
| **FileData** | [file_data.py](src/core/file_data.py) | Экспериментальные данные файлов |
| **CalculationsData** | [calculation_data.py](src/core/calculation_data.py) | Параметры реакций (деконволюция) |
| **SeriesData** | [series_data.py](src/core/series_data.py) | Серии экспериментов |

---

## FileData — Экспериментальные данные

**Файл:** [src/core/file_data.py:46-337](src/core/file_data.py#L46-L337)

Управление загрузкой, модификацией и хранением экспериментальных данных.

### Атрибуты

```python
class FileData(BaseSlots):
    data_loaded_signal = pyqtSignal(pd.DataFrame)

    def __init__(self, signals):
        self.data = None                          # Текущий DataFrame
        self.original_data = {}                   # Оригинальные данные по файлам
        self.dataframe_copies = {}                # Рабочие копии для модификаций
        self.file_path = None                     # Путь к текущему файлу
        self.delimiter = ","                      # Разделитель CSV
        self.skip_rows = 0                        # Пропуск строк
        self.columns_names = None                 # Имена колонок
        self.operations_history = {}              # История операций
        self.loaded_files = set()                 # Загруженные файлы
```

### Структура DataFrame

```python
# Экспериментальные данные
DataFrame({
    "temperature": [T1, T2, T3, ...],  # Температура (K или °C)
    "mass_loss": [m1, m2, m3, ...],    # Потеря массы / конверсия
})
```

### Операции

| Метод | Описание |
|-------|----------|
| `load_file(file_info)` | Загрузка CSV/TXT с автоопределением кодировки |
| `load_csv()` / `load_txt()` | Парсинг файлов |
| `modify_data(func, params)` | Применение функции трансформации |
| `reset_dataframe_copy(key)` | Сброс к оригинальным данным |
| `plot_dataframe_copy(key)` | Запрос на отображение данных |

### История операций

```python
self.operations_history = {
    "experiment.csv": [
        {"params": {"operation": OperationType.TO_A_T, ...}},
        {"params": {"operation": OperationType.TO_DTG, ...}},
    ]
}
```

### process_request

```python
def process_request(self, params: dict):
    operation = params.get("operation")

    if operation == OperationType.TO_A_T:
        if not self.check_operation_executed(file_name, OperationType.TO_A_T):
            self.modify_data(func, params)
        params["data"] = True

    elif operation == OperationType.GET_DF_DATA:
        params["data"] = self.dataframe_copies.get(file_name)

    elif operation == OperationType.RESET_FILE_DATA:
        self.reset_dataframe_copy(file_name)
        params["data"] = True
```

---

## CalculationsData — Параметры реакций

**Файл:** [src/core/calculation_data.py:14-181](src/core/calculation_data.py#L14-L181)

Иерархическое хранение параметров реакций для деконволюции с использованием системы path_keys.

### Атрибуты

```python
class CalculationsData(BaseSlots):
    dataChanged = pyqtSignal(dict)

    def __init__(self, signals):
        self._data: Dict[str, Any] = {}  # Иерархическое хранилище
        self._filename: str = ""          # Имя файла для сохранения
```

### path_keys система

Доступ к вложенным данным через список ключей:

```python
# Пример path_keys
["experiment.csv", "reaction_0", "coeffs", "h"]

# Соответствует структуре:
{
    "experiment.csv": {
        "reaction_0": {
            "coeffs": {
                "h": 0.15,
                "z": 300.0,
                "w": 50.0
            }
        }
    }
}
```

### Методы доступа

```python
def get_value(self, keys: List[str]) -> Dict[str, Any]:
    """Навигация по вложенной структуре"""
    return reduce(lambda data, key: data.get(key, {}), keys, self._data)

def set_value(self, keys: List[str], value: Any) -> None:
    """Сохранение значения по пути"""
    last_key = keys.pop()
    nested_dict = reduce(lambda data, key: data.setdefault(key, {}), keys, self._data)
    nested_dict[last_key] = value

def exists(self, keys: List[str]) -> bool:
    """Проверка существования пути"""
    try:
        _ = reduce(lambda data, key: data[key], keys, self._data)
        return True
    except KeyError:
        return False

def remove_value(self, keys: List[str]) -> None:
    """Удаление значения по пути"""
```

### Структура данных реакции

```python
{
    "experiment.csv": {
        "reaction_0": {
            "function": "gauss",
            "x": np.ndarray([...]),
            "coeffs": {
                "h": 0.15,      # Высота
                "z": 300.0,     # Позиция (температура)
                "w": 50.0,      # Ширина
                "fr": 1.0,      # Fraser-Suzuki параметр
                "ads1": 25.0,   # ADS параметр 1
                "ads2": 2.0,    # ADS параметр 2
            },
            "upper_bound_coeffs": {...},
            "lower_bound_coeffs": {...}
        },
        "reaction_1": {...}
    }
}
```

### Импорт/экспорт

```python
def load_reactions(self, load_file_name: str, file_name: str) -> Dict[str, Any]:
    """Загрузка реакций из JSON с конвертацией numpy массивов"""
    with open(load_file_name, "r", encoding="utf-8") as file:
        data = json.load(file)

    for reaction_key, reaction_data in data.items():
        if "x" in reaction_data:
            reaction_data["x"] = np.array(reaction_data["x"])

    self.set_value([file_name], data)
    return data
```

---

## SeriesData — Серии экспериментов

**Файл:** [src/core/series_data.py:9-333](src/core/series_data.py#L9-L333)

Управление сериями экспериментов с несколькими скоростями нагрева.

### Атрибуты

```python
class SeriesData(BaseSlots):
    def __init__(self, actor_name: str = "series_data", signals=None):
        self.series = {}                 # Все серии
        self.default_name_counter: int = 1  # Счётчик имён
```

### Структура серии

```python
{
    "Series 1": {
        "experimental_data": DataFrame({
            "temperature": [...],
            "5": [...],      # Heating rate β=5 K/min
            "10": [...],     # Heating rate β=10 K/min
            "20": [...],     # Heating rate β=20 K/min
        }),
        "experimental_masses": [0.5, 0.5, 0.5],  # Массы образцов

        "reaction_scheme": {
            "components": [
                {"id": "A"},
                {"id": "B"},
                {"id": "C"}
            ],
            "reactions": [
                {
                    "from": "A",
                    "to": "B",
                    "reaction_type": "F2",
                    "allowed_models": ["F1/3", "F2", "F3"],
                    "Ea": 120.0,
                    "log_A": 8.0,
                    "contribution": 0.5,
                    "Ea_min": 1.0,
                    "Ea_max": 250.0,
                    "log_A_min": -15.0,
                    "log_A_max": 30.0,
                },
                {
                    "from": "B",
                    "to": "C",
                    ...
                }
            ]
        },

        "calculation_settings": {
            "method": "differential_evolution",
            "method_parameters": {
                "strategy": "best1bin",
                "maxiter": 1000,
                "popsize": 50,
                ...
            }
        },

        "deconvolution_results": {
            "reaction_0": {...},
            "reaction_1": {...}
        },

        "model_fit_results": {
            "direct-diff": {
                "reaction_0": {
                    "5": DataFrame(...),
                    "10": DataFrame(...),
                }
            }
        },

        "model_free_results": {
            "Friedman": {
                "reaction_0": DataFrame(...)
            },
            "Kissinger": {...}
        }
    }
}
```

### Операции

```python
def add_series(self, data, experimental_masses, name=None):
    """Создание новой серии с дефолтной схемой A→B"""
    reaction_scheme = {
        "components": [{"id": "A"}, {"id": "B"}],
        "reactions": [{"from": "A", "to": "B"}]
    }
    self.series[name] = {
        "experimental_data": data,
        "experimental_masses": experimental_masses,
        "reaction_scheme": reaction_scheme,
        "calculation_settings": {...}
    }
    self._get_default_reaction_params(name)

def update_series(self, series_name: str, update_data: dict) -> bool:
    """Обновление серии с поддержкой вложенных словарей"""
    if "reaction_scheme" in update_data:
        self._update_reaction_scheme(series_entry, update_data["reaction_scheme"])

def delete_series(self, series_name: str) -> bool:
    """Удаление серии"""

def rename_series(self, old_series_name: str, new_series_name: str) -> bool:
    """Переименование серии"""

def get_series(self, series_name: str, info_type: str = "experimental"):
    """Получение данных серии по типу"""
    if info_type == "experimental":
        return series_entry.get("experimental_data")
    elif info_type == "scheme":
        return series_entry.get("reaction_scheme")
    elif info_type == "all":
        return series_entry.copy()
```

### Дефолтные параметры реакций

```python
def _get_default_reaction_params(self, series_name: str):
    bounds = PARAMETER_BOUNDS.model_based
    default_params = {
        "reaction_type": "F2",
        "allowed_models": ["F1/3", "F3/4", "F3/2", "F2", "F3"],
        "Ea": bounds.ea_default,           # 120.0
        "log_A": bounds.log_a_default,     # 8.0
        "contribution": bounds.contribution_default,  # 0.5
        "Ea_min": bounds.ea_min,           # 1.0
        "Ea_max": bounds.ea_max,           # 250.0
        ...
    }
```

---

## Связь между структурами

### Диаграмма зависимостей

```
FileData (экспериментальные файлы)
       ↓
    [merge by temperature]
       ↓
SeriesData (серии с multiple heating rates)
       ↓
    [deconvolution]
       ↓
CalculationsData (параметры реакций)
       ↓
    [model-based/model-free]
       ↓
SeriesData (результаты расчётов)
```

### Пример workflow

```
1. Загрузка файлов → FileData.load_file()
2. Создание серии → SeriesData.add_series(merged_df)
3. Деконволюция → CalculationsData.set_value([...])
4. Сохранение результатов → SeriesData.update_series({deconvolution_results: ...})
5. Model-based расчёт → SeriesData.update_series({model_based_results: ...})
```

---

## Декораторы FileData

**Файл:** [src/core/file_data.py:16-44](src/core/file_data.py#L16-L44)

### detect_encoding

Автоопределение кодировки файла через chardet:

```python
@detect_encoding
def load_csv(self, **kwargs):
    # kwargs["encoding"] автоматически установлен
    self.data = pd.read_csv(..., **kwargs)
```

### detect_decimal

Автоопределение десятичного разделителя:

```python
@detect_decimal
def load_csv(self, **kwargs):
    # kwargs["decimal"] = "," или "."
    self.data = pd.read_csv(..., **kwargs)
```

---

## CurveFitting — Генерация данных

**Файл:** [src/core/curve_fitting.py:64-127](src/core/curve_fitting.py#L64-L127)

### Генерация дефолтных параметров

```python
@staticmethod
def generate_default_function_data(df) -> dict:
    x = df["temperature"].copy()
    y = df[y_columns[0]]

    h = 0.3 * y.max()       # 30% от максимума
    z = x.mean()            # Центр диапазона
    w = 0.1 * (x.max() - x.min())  # 10% от диапазона

    return {
        "function": "gauss",
        "x": x.to_numpy(),
        "coeffs": {"h": h, "z": z, "w": w, ...},
        "upper_bound_coeffs": {...},
        "lower_bound_coeffs": {...}
    }
```

### Парсинг параметров реакции

```python
@staticmethod
def parse_reaction_params(reaction_params: dict) -> Dict[str, Tuple]:
    """Конвертация dict в tuple формат для расчётов"""
    x: np.ndarray = reaction_params.get("x", np.array([]))
    function_type: str = reaction_params.get("function", "")
    coeffs: dict = reaction_params.get("coeffs", {})

    x_range = (np.min(x), np.max(x))
    allowed_keys = CurveFitting._get_allowed_keys_for_type(function_type)
    coeffs_tuple = tuple(coeffs.get(key) for key in allowed_keys if key in coeffs)

    return {
        "coeffs": (x_range, function_type, coeffs_tuple),
        "upper_bound_coeffs": (x_range, function_type, upper_coeffs_tuple),
        "lower_bound_coeffs": (x_range, function_type, lower_coeffs_tuple),
    }
```

---

## Конфигурация bounds

**Файл:** [src/core/app_settings.py:8-85](src/core/app_settings.py#L8-L85)

### ModelBasedParameterBounds

```python
@dataclass(frozen=True)
class ModelBasedParameterBounds:
    ea_min: float = 1.0
    ea_max: float = 250.0
    ea_default: float = 120.0

    log_a_min: float = -15.0
    log_a_max: float = 30.0
    log_a_default: float = 8.0

    contribution_min: float = 0.01
    contribution_max: float = 1.0
    contribution_default: float = 0.5
```

### DeconvolutionParameterBounds

```python
@dataclass(frozen=True)
class DeconvolutionParameterBounds:
    h_min: float = 0.0
    h_max: float = 1.0
    h_default: float = 0.1

    z_min: float = 0.0
    z_max: float = 1000.0
    z_default: float = 300.0

    w_min: float = 1.0
    w_max: float = 200.0
    w_default: float = 50.0

    ads1_default: float = 25.0
    ads2_default: float = 2.0
    fr_default: float = 1.0
```

### Использование

```python
PARAMETER_BOUNDS = ParameterBoundsConfig()

# Доступ к bounds
bounds = PARAMETER_BOUNDS.model_based
default_Ea = bounds.ea_default  # 120.0
```

---

## Связанные документы

- [ARCHITECTURE.md](.ai/ARCHITECTURE.md) — архитектура приложения
- [UI_ARCHITECTURE.md](.ai/UI_ARCHITECTURE.md) — архитектура GUI
