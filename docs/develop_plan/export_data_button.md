# Техническое задание: Экспорт данных серий экспериментов

## Обзор

Реализация функционала экспорта для кнопки "Export Results" в Series Panel (`SeriesSubBar`). Кнопка уже существует в GUI, необходимо подключить обработчик и реализовать экспорт результатов анализа серий экспериментов с несколькими скоростями нагрева.

## Анализ существующих решений

### Существующий GUI компонент

**Series Panel** (`src/gui/main_tab/sub_sidebar/series/series_sub_bar.py:172`):
```python
self.export_button = QPushButton("Export Results", self)
self.layout.addWidget(self.export_button)
# НЕТ: self.export_button.clicked.connect() - отсутствует подключение
```

### Архитектурные паттерны для экспорта

1. **Deconvolution Panel** - `FileTransferButtons.export_reactions()`:
   - `QFileDialog.getSaveFileName()` для выбора файла
   - JSON формат с `NumpyArrayEncoder` для NumPy массивов
   - Интеграция с `LoggerConsole` для уведомлений

2. **Существующая инфраструктура**:
   - Сигнально-слотовая архитектура через `pyqtSignal`
   - Система `OperationType` для типизации операций
   - BaseSlots паттерн для межмодульной коммуникации

## Технические требования

### 1. Местоположение реализации

**Основной компонент**: `src/gui/main_tab/sub_sidebar/series/series_sub_bar.py`
- Существующая кнопка `self.export_button` 
- Добавить обработчик `self.export_button.clicked.connect(self.export_results)`
- Реализовать метод `export_results()` для экспорта данных серии

### 2. Источники данных для экспорта

**SeriesData структура** (`src/core/series_data.py`):
```python
{
    "series_name": {
        "experimental_data": DataFrame,           # Температура + данные скоростей нагрева
        "experimental_masses": [1.0, 1.0, 1.0],  # Массовые коэффициенты
        "deconvolution_results": {               # Результаты деконволюции по скоростям
            3: {"reaction_0": {...}, "reaction_1": {...}},
            5: {"reaction_0": {...}, "reaction_1": {...}},
            10: {"reaction_0": {...}, "reaction_1": {...}}
        },
        "model_fit_results": {                   # Model-fit результаты 
            "direct-diff": {"reaction_0": DataFrame, "reaction_1": DataFrame},
            "Coats-Redfern": {"reaction_0": DataFrame, "reaction_1": DataFrame}
        },
        "model_free_results": {                  # Model-free результаты
            "linear approximation": {"reaction_0": DataFrame, "reaction_1": DataFrame},
            "Friedman": {"reaction_0": DataFrame, "reaction_1": DataFrame}
        }
    }
}
```

### 3. Формат экспортируемых данных

**JSON структура экспорта серии**:
```python
{
    "metadata": {
        "series_name": "test_series",
        "export_timestamp": "2025-09-02T10:30:00Z",
        "data_type": "series_results",
        "software_version": "1.0.0",
        "exported_by": "Open ThermoKinetics"
    },
    "experimental_setup": {
        "experimental_data": {
            "temperature": [32.18783, 33.14274, 34.09765, ...],  # Температурный массив
            "heating_rates": {
                "3": [0.001, 0.002, 0.003, ...],    # Данные для 3 K/min
                "5": [0.002, 0.004, 0.006, ...],    # Данные для 5 K/min  
                "10": [0.004, 0.008, 0.012, ...]    # Данные для 10 K/min
            }
        },
        "experimental_masses": [1.0, 1.0, 1.0],  # Массовые коэффициенты
        "heating_rate_units": "K/min",
        "temperature_units": "°C"
    },
    "deconvolution_results": {
        "3": {  # Скорость нагрева 3 K/min
            "reaction_0": {
                "function": "ads",
                "coeffs": {"h": 0.005392, "z": 296.1846, "w": 47.058, "ads1": 26.129, "ads2": 1.916},
                "upper_bound_coeffs": {...},
                "lower_bound_coeffs": {...},
                "x": [32.18783, 33.14274, ...]  # Температурный массив реакции
            },
            "reaction_1": {...}
        },
        "5": {...},   # Результаты для 5 K/min
        "10": {...}   # Результаты для 10 K/min
    },
    "analysis_results": {
        "model_fit_results": {
            "direct-diff": {
                "reaction_0": {
                    "models": ["D4", "G7", "D2", "R2", ...],
                    "R2_scores": [0.9985, 0.9978, 0.9970, 0.9967, ...],
                    "activation_energies": [199082.0, 202106.0, 193655.0, 99724.0, ...],  # Дж/моль
                    "pre_exponential_factors": [2.106e+16, 4.024e+17, 2.451e+16, 8.225e+07, ...]  # 1/s
                },
                "reaction_1": {...}
            },
            "Coats-Redfern": {
                "reaction_0": {
                    "models": ["G7", "G6", "D3", "G5", ...],
                    "R2_scores": [0.9753, 0.9753, 0.9749, 0.9749, ...], 
                    "activation_energies": [189562.0, 332740.0, 142610.0, 247554.0, ...],
                    "pre_exponential_factors": [5.301e+15, 1.377e+29, 1.100e+10, 2.732e+21, ...]
                },
                "reaction_1": {...}
            }
        },
        "model_free_results": {
            "linear approximation": {
                "reaction_0": {
                    "conversion": [0.005, 0.01, 0.015, 0.02, ..., 0.995],  # 100 точек от 0.005 до 0.995
                    "Friedman": [95000, 98000, 101000, 104000, ...],       # Ea в Дж/моль
                    "KAS": [92000, 95000, 98000, 101000, ...],             # Ea в Дж/моль
                    "Starink": [93000, 96000, 99000, 102000, ...]          # Ea в Дж/моль
                },
                "reaction_1": {...}
            },
            "Friedman": {
                "reaction_0": {
                    "conversion": [0.005, 0.01, 0.015, 0.02, ..., 0.995],
                    "activation_energy": [95000, 98000, 101000, 104000, ...]  # Ea в Дж/моль
                },
                "reaction_1": {...}
            }
        }
    },
    "summary_statistics": {
        "total_reactions": 2,
        "heating_rates_count": 3,
        "temperature_range": {"min": 32.18, "max": 450.0, "units": "°C"},
        "analysis_methods": ["direct-diff", "Coats-Redfern", "Friedman", "linear approximation"]
    }
}
```

### 4. Доступ к данным серии

**Получение данных через SeriesData API**:
```python
# В SeriesSubBar метод export_results()
def export_results(self):
    # Получить имя активной серии
    active_series_name = self.get_active_series_name()
    
    # Запросить полные данные серии через сигнал
    request = {
        "operation": OperationType.EXPORT_SERIES_RESULTS,
        "series_name": active_series_name
    }
    self.export_series_signal.emit(request)
```

### 5. Система именования файлов

**Автогенерация имени файла**:
```python
def generate_export_filename(series_name: str) -> str:
    """
    Генерирует имя файла для экспорта серии.
    
    Пример: "test_series_results_20250902_103000.json"
    """
    # Очистка имени от недопустимых символов
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', series_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{clean_name}_results_{timestamp}.json"
```

## Архитектурная интеграция

### 1. Новая операция в OperationType

```python
# src/core/app_settings.py
class OperationType(Enum):
    # Существующие операции...
    EXPORT_SERIES_RESULTS = "export_series_results"
```

### 2. Обновление SeriesSubBar

```python
# src/gui/main_tab/sub_sidebar/series/series_sub_bar.py

class SeriesSubBar(QWidget):
    # Добавить новый сигнал
    export_series_signal = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        # Существующий код...
        
        # Подключить обработчик к кнопке экспорта  
        self.export_button.clicked.connect(self.export_results)
    
    def export_results(self):
        """Обработчик нажатия кнопки экспорта."""
        # Получить имя активной серии из MainTab через сигнал
        # Инициировать экспорт через export_series_signal
        
    def handle_export_complete(self, file_path: str, success: bool):
        """Обработчик завершения экспорта."""
        # Показать уведомление об успехе/ошибке
```

### 3. Обработка в SeriesData

```python  
# src/core/series_data.py

class SeriesData(BaseSlots):
    def process_request(self, params: dict) -> None:
        # Существующие обработчики...
        
        def handle_export_series_results(p: dict, r: dict) -> None:
            series_name = p.get("series_name")
            export_data = self._prepare_export_data(series_name)
            file_path = self._save_to_file(export_data, series_name)
            r["data"] = {"file_path": file_path, "success": file_path is not None}
            
    def _prepare_export_data(self, series_name: str) -> dict:
        """Подготовка данных серии для экспорта."""
        series_data = self.get_series(series_name, info_type="all")
        if not series_data:
            return {}
            
        # Форматирование в экспортную структуру
        export_data = {
            "metadata": {
                "series_name": series_name,
                "export_timestamp": datetime.now().isoformat() + "Z",
                "data_type": "series_results",
                "software_version": "1.0.0",
                "exported_by": "Open ThermoKinetics"
            },
            # Структурирование всех данных серии...
        }
        return export_data
        
    def _save_to_file(self, export_data: dict, series_name: str) -> str:
        """Сохранение данных в JSON файл с диалогом выбора места."""
        # Реализация диалога сохранения и записи файла
```

### 4. Подключение сигналов в MainTab

```python
# src/gui/main_tab/main_tab.py

def connect_series_signals(self):
    # Подключение нового сигнала экспорта
    self.sub_sidebar.series_sub_bar.export_series_signal.connect(
        self.handle_export_series_request
    )
    
def handle_export_series_request(self, request: dict):
    """Обработка запроса экспорта серии."""
    # Добавить имя активной серии к запросу
    request["series_name"] = self.get_active_series_name()
    # Отправить запрос в MainWindow
    self.to_main_window_signal.emit(request)
```

## План реализации

### Этап 1: Базовая инфраструктура (1 день)
1. ✅ Добавить `EXPORT_SERIES_RESULTS` в `OperationType`
2. ✅ Создать сигнал `export_series_signal` в `SeriesSubBar`
3. ✅ Подключить обработчик к кнопке: `self.export_button.clicked.connect(self.export_results)`
4. ✅ Реализовать заглушку `export_results()` метода

### Этап 2: Обработчик в SeriesData (2 дня)
1. ✅ Добавить `handle_export_series_results()` в `process_request()`
2. ✅ Реализовать `_prepare_export_data()` для структурирования данных
3. ✅ Реализовать `_save_to_file()` с диалогом сохранения
4. ✅ Использовать `NumpyArrayEncoder` для JSON сериализации

### Этап 3: Интеграция GUI (1 день)
1. ✅ Подключить `export_series_signal` в `MainTab`
2. ✅ Реализовать передачу имени активной серии
3. ✅ Добавить обработку ответа с результатом экспорта
4. ✅ Интеграция с `LoggerConsole` для уведомлений

### Этап 4: Тестирование (1 день) 
1. ✅ Создать тестовую серию с model-fit и model-free результатами
2. ✅ Проверить корректность экспорта всех типов данных
3. ✅ Валидация JSON структуры экспортированного файла
4. ✅ Тестирование обработки ошибок (нет данных, проблемы с файлом)

## Критерии успеха

1. **Функциональность**: Кнопка "Export Results" экспортирует полные данные серии
2. **Формат**: JSON файл со структурированными данными всех типов анализа
3. **UX**: Диалог выбора места сохранения с автогенерацией имени файла
4. **Уведомления**: Успех/ошибка отображается в LoggerConsole
5. **Архитектура**: Соответствие существующим паттернам (BaseSlots, сигналы)
6. **Данные**: Включение experimental_data, deconvolution_results, model_fit_results, model_free_results

## Риски и ограничения

**Риски**:
- Большие объемы данных серий могут замедлить экспорт
- NumPy массивы в deconvolution_results требуют специальной сериализации
- Отсутствие активной серии при нажатии кнопки

**Ограничения**:
- Экспорт только в JSON формате (без CSV/Excel)
- Экспорт полной серии целиком (без выборочного экспорта отдельных реакций)

**Митигация**:
- Использование существующего `NumpyArrayEncoder`
- Валидация наличия активной серии перед экспортом
- Индикация прогресса для больших файлов
