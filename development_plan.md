# План разработки: Реализация метода оптимизации basinhopping в MODEL_BASED_CALCULATION

## Обзор проекта

Данный план описывает реализацию метода оптимизации `basinhopping` из `scipy.optimize` в систему MODEL_BASED_CALCULATION приложения для анализа кинетики твердофазных реакций. Новый метод будет интегрирован в существующую архитектуру наряду с текущим методом `differential_evolution`.

## Анализ текущей архитектуры

### Текущая система оптимизации

1. **Единственный метод**: В настоящее время используется только `differential_evolution`
2. **Точка входа**: `_handle_model_based_calculation()` в `MainWindow`
3. **Сценарии**: Управляются через `ModelBasedScenario` в `calculation_scenarios.py`
4. **Выполнение**: Вызывается через `start_differential_evolution()` в `Calculations`
5. **GUI настройки**: Управляются через `CalculationSettingsDialog` в модуле model_based

### Архитектурные компоненты

```
src/core/
├── calculation.py                    # Основной движок вычислений
├── calculation_scenarios.py          # Сценарии оптимизации  
└── app_settings.py                  # Константы и настройки

src/gui/main_tab/sub_sidebar/model_based/
├── model_based.py                   # GUI для model-based вычислений
├── calculation_settings_dialog.py  # Диалог настроек оптимизации
└── components/                      # Компоненты GUI
```

## Этапы реализации

### Этап 1: Расширение ядра оптимизации (1-2 дня)

#### 1.1 Обновление calculation.py

**Файл**: `src/core/calculation.py`

**Изменения**:

1. Добавить импорт `basinhopping`:
```python
from scipy.optimize import differential_evolution, basinhopping, OptimizeResult
```

2. Добавить новый метод `start_basinhopping()`:
```python
def start_basinhopping(self, x0, target_function, **kwargs):
    """
    Запуск оптимизации методом basinhopping
    
    Args:
        x0: Начальная точка для оптимизации
        target_function: Целевая функция для минимизации  
        **kwargs: Дополнительные параметры для basinhopping
    """
    self.start_calculation_thread(
        basinhopping,
        target_function,
        x0=x0,
        **kwargs,
    )
```

3. Обновить `run_calculation_scenario()` для поддержки нового метода:
```python
if optimization_method == "differential_evolution":
    calc_params = params.get("calculation_settings", {}).get("method_parameters", {}).copy()
    # ... существующий код
    self.start_differential_evolution(bounds=bounds, target_function=target_function, **calc_params)
elif optimization_method == "basinhopping":
    calc_params = params.get("calculation_settings", {}).get("method_parameters", {}).copy()
    
    if scenario_key == "model_based_calculation":
        calc_params["callback"] = make_basinhopping_callback(target_function, self)
    
    # Генерация начальной точки из границ
    x0 = self._generate_initial_point_from_bounds(bounds)
    self.start_basinhopping(x0=x0, target_function=target_function, **calc_params)
else:
    logger.error(f"Unsupported optimization method: {optimization_method}")
```

4. Добавить вспомогательный метод для генерации начальной точки:
```python
def _generate_initial_point_from_bounds(self, bounds):
    """Генерирует случайную начальную точку в пределах boundaries"""
    import random
    x0 = []
    for low, high in bounds:
        x0.append(random.uniform(low, high))
    return x0
```

5. Добавить callback функцию для basinhopping:
```python
def make_basinhopping_callback(target_function, calculations_instance):
    """Создает callback функцию для basinhopping оптимизации"""
    def callback(x, f, accept):
        if not calculations_instance.calculation_active:
            return True  # Останавливает оптимизацию
        
        # Логирование прогресса
        console.log(f"Basinhopping step: f={f:.6f}, accept={accept}")
        return False  # Продолжает оптимизацию
    
    return callback
```

#### 1.2 Обновление calculation_scenarios.py

**Файл**: `src/core/calculation_scenarios.py`

**Изменения**:

1. Обновить `BaseCalculationScenario` для поддержки метода оптимизации из параметров:
```python
def get_optimization_method(self) -> str:
    """Возвращает метод оптимизации из параметров или значение по умолчанию"""
    calculation_settings = self.params.get("calculation_settings", {})
    return calculation_settings.get("optimization_method", "differential_evolution")
```

2. Обновить `ModelBasedScenario` для обработки специфичных настроек basinhopping:
```python
def get_basinhopping_parameters(self) -> dict:
    """Возвращает параметры для basinhopping оптимизации"""
    calculation_settings = self.params.get("calculation_settings", {})
    method_params = calculation_settings.get("method_parameters", {})
    
    # Параметры по умолчанию для basinhopping
    default_params = {
        "niter": 100,
        "T": 1.0,
        "stepsize": 0.5,
        "minimizer_kwargs": {"method": "L-BFGS-B"},
        "take_step": None,
        "accept_test": None,
        "interval": 50,
        "disp": False,
        "niter_success": None,
        "seed": None,
    }
    
    # Обновляем параметрами от пользователя
    default_params.update(method_params)
    return default_params
```

#### 1.3 Обновление app_settings.py

**Файл**: `src/core/app_settings.py`

**Изменения**:

1. Добавить константы для методов оптимизации:
```python
# Методы оптимизации
OPTIMIZATION_METHODS = {
    "differential_evolution": "Differential Evolution",
    "basinhopping": "Basin-hopping",
}

# Параметры по умолчанию для basinhopping
DEFAULT_BASINHOPPING_PARAMS = {
    "niter": 100,
    "T": 1.0,
    "stepsize": 0.5,
    "minimizer_kwargs": {"method": "L-BFGS-B"},
    "interval": 50,
    "disp": False,
}

# Параметры по умолчанию для differential_evolution  
DEFAULT_DE_PARAMS = {
    "maxiter": 1000,
    "popsize": 15,
    "tol": 0.01,
    "atol": 0,
    "seed": None,
    "disp": False,
    "polish": True,
    "init": "latinhypercube",
    "mutation": (0.5, 1),
    "recombination": 0.7,
}
```

### Этап 2: Реализация GUI компонентов (2-3 дня)

#### 2.1 Обновление CalculationSettingsDialog

**Файл**: `src/gui/main_tab/sub_sidebar/model_based/calculation_settings_dialog.py`

**Изменения**:

1. Добавить выбор метода оптимизации:
```python
def _create_optimization_method_group(self):
    """Создает группу для выбора метода оптимизации"""
    group = QGroupBox("Метод оптимизации")
    layout = QVBoxLayout()
    
    self.optimization_method_combo = QComboBox()
    self.optimization_method_combo.addItems([
        "differential_evolution",
        "basinhopping"
    ])
    self.optimization_method_combo.currentTextChanged.connect(self._on_optimization_method_changed)
    
    layout.addWidget(QLabel("Метод:"))
    layout.addWidget(self.optimization_method_combo)
    
    group.setLayout(layout)
    return group
```

2. Добавить контейнер для динамических параметров:
```python
def _create_method_parameters_group(self):
    """Создает группу для параметров выбранного метода"""
    self.method_params_group = QGroupBox("Параметры метода")
    self.method_params_layout = QVBoxLayout()
    self.method_params_group.setLayout(self.method_params_layout)
    
    # Изначально показываем параметры differential_evolution
    self._create_differential_evolution_params()
    
    return self.method_params_group
```

3. Реализовать параметры для basinhopping:
```python
def _create_basinhopping_params(self):
    """Создает виджеты для параметров basinhopping"""
    self._clear_method_params()
    
    # niter
    niter_layout = QHBoxLayout()
    niter_layout.addWidget(QLabel("Количество итераций (niter):"))
    self.niter_spinbox = QSpinBox()
    self.niter_spinbox.setRange(1, 10000)
    self.niter_spinbox.setValue(100)
    niter_layout.addWidget(self.niter_spinbox)
    self.method_params_layout.addLayout(niter_layout)
    
    # T (температура)
    temp_layout = QHBoxLayout()
    temp_layout.addWidget(QLabel("Температура (T):"))
    self.temperature_spinbox = QDoubleSpinBox()
    self.temperature_spinbox.setRange(0.01, 100.0)
    self.temperature_spinbox.setValue(1.0)
    self.temperature_spinbox.setDecimals(2)
    temp_layout.addWidget(self.temperature_spinbox)
    self.method_params_layout.addLayout(temp_layout)
    
    # stepsize
    step_layout = QHBoxLayout()
    step_layout.addWidget(QLabel("Размер шага (stepsize):"))
    self.stepsize_spinbox = QDoubleSpinBox()
    self.stepsize_spinbox.setRange(0.01, 10.0)
    self.stepsize_spinbox.setValue(0.5)
    self.stepsize_spinbox.setDecimals(2)
    step_layout.addWidget(self.stepsize_spinbox)
    self.method_params_layout.addLayout(step_layout)
    
    # minimizer_method
    minimizer_layout = QHBoxLayout()
    minimizer_layout.addWidget(QLabel("Локальный минимизатор:"))
    self.minimizer_combo = QComboBox()
    self.minimizer_combo.addItems([
        "L-BFGS-B", "BFGS", "CG", "Newton-CG", "TNC", "SLSQP"
    ])
    minimizer_layout.addWidget(self.minimizer_combo)
    self.method_params_layout.addLayout(minimizer_layout)
    
    # interval
    interval_layout = QHBoxLayout()
    interval_layout.addWidget(QLabel("Интервал обновления (interval):"))
    self.interval_spinbox = QSpinBox()
    self.interval_spinbox.setRange(1, 1000)
    self.interval_spinbox.setValue(50)
    interval_layout.addWidget(self.interval_spinbox)
    self.method_params_layout.addLayout(interval_layout)
```

4. Добавить обработчик смены метода:
```python
def _on_optimization_method_changed(self, method):
    """Обработчик смены метода оптимизации"""
    if method == "differential_evolution":
        self._create_differential_evolution_params()
    elif method == "basinhopping":
        self._create_basinhopping_params()
```

5. Обновить метод сбора настроек:
```python
def get_calculation_settings(self):
    """Возвращает настройки вычислений"""
    optimization_method = self.optimization_method_combo.currentText()
    
    settings = {
        "optimization_method": optimization_method,
        "method_parameters": {}
    }
    
    if optimization_method == "differential_evolution":
        settings["method_parameters"] = {
            "maxiter": self.maxiter_spinbox.value(),
            "popsize": self.popsize_spinbox.value(),
            "tol": self.tol_spinbox.value(),
            "seed": self.seed_spinbox.value() if self.seed_spinbox.value() > 0 else None,
            "disp": self.disp_checkbox.isChecked(),
            "polish": self.polish_checkbox.isChecked(),
            "init": self.init_combo.currentText(),
            "mutation": (self.mutation_min_spinbox.value(), self.mutation_max_spinbox.value()),
            "recombination": self.recombination_spinbox.value(),
        }
    elif optimization_method == "basinhopping":
        settings["method_parameters"] = {
            "niter": self.niter_spinbox.value(),
            "T": self.temperature_spinbox.value(),
            "stepsize": self.stepsize_spinbox.value(),
            "minimizer_kwargs": {"method": self.minimizer_combo.currentText()},
            "interval": self.interval_spinbox.value(),
            "disp": False,  # Всегда False для GUI
        }
    
    return settings
```

#### 2.2 Обновление ModelBased GUI

**Файл**: `src/gui/main_tab/sub_sidebar/model_based/model_based.py`

**Изменения**:

1. Обновить обработчик кнопки настроек:
```python
def _on_calculation_settings_clicked(self):
    """Обработчик кнопки настроек вычислений"""
    dialog = CalculationSettingsDialog(
        default_optimization_method="differential_evolution"  # или из сохраненных настроек
    )
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        self.calculation_settings = dialog.get_calculation_settings()
        self._update_settings_display()
```

2. Добавить отображение текущих настроек:
```python
def _update_settings_display(self):
    """Обновляет отображение текущих настроек"""
    if hasattr(self, 'calculation_settings'):
        method = self.calculation_settings.get("optimization_method", "differential_evolution")
        self.settings_label.setText(f"Метод: {OPTIMIZATION_METHODS.get(method, method)}")
```

### Этап 3: Тестирование и документация (1-2 дня)

#### Не требуются

## Детальный план файловых изменений

### Новые файлы

```
tests/
├── core/
│   └── test_basinhopping_integration.py
└── gui/
    └── test_calculation_settings_dialog_basinhopping.py

docs/
├── user_guide/
│   └── basinhopping_optimization.md
└── technical/
    └── optimization_methods_architecture.md
```

### Изменяемые файлы

| Файл | Тип изменения | Описание |
|------|---------------|----------|
| `src/core/calculation.py` | Расширение | Добавление `start_basinhopping()`, обновление `run_calculation_scenario()` |
| `src/core/calculation_scenarios.py` | Модификация | Обновление `get_optimization_method()` для `BaseCalculationScenario` |
| `src/core/app_settings.py` | Дополнение | Константы для методов оптимизации и параметров по умолчанию |
| `src/gui/main_tab/sub_sidebar/model_based/calculation_settings_dialog.py` | Крупная переработка | Добавление поддержки выбора метода и настроек basinhopping |
| `src/gui/main_tab/sub_sidebar/model_based/model_based.py` | Минорные изменения | Обновление обработчиков настроек |

## Критерии приемки

### Функциональные требования

1. ✅ **Выбор метода оптимизации**: Пользователь может выбрать между `differential_evolution` и `basinhopping`
2. ✅ **Настройка параметров**: Доступна полная настройка параметров basinhopping через GUI
3. ✅ **Корректное выполнение**: Basinhopping корректно выполняется для MODEL_BASED_CALCULATION
4. ✅ **Отображение прогресса**: Отображение прогресса оптимизации в консоли
5. ✅ **Обработка результатов**: Корректная обработка и отображение результатов

### Технические требования

1. ✅ **Совместимость**: Сохранение работоспособности существующего кода
2. ✅ **Производительность**: Оптимизация не должна значительно замедлять интерфейс
3. ✅ **Обработка ошибок**: Надежная обработка ошибок и исключений
4. ✅ **Документация**: Полная документация новых возможностей

### Пользовательские требования

1. ✅ **Интуитивность**: Интуитивно понятный интерфейс выбора и настройки
2. ✅ **Информативность**: Четкие подсказки и описания параметров
3. ✅ **Отзывчивость**: Быстрый отклик интерфейса при изменении настроек
4. ✅ **Стабильность**: Стабильная работа при различных входных данных

## Заключение

Данный план обеспечивает систематическую интеграцию метода оптимизации `basinhopping` в существующую архитектуру приложения для анализа кинетики твердофазных реакций. Реализация следует принципам:

1. **Минимальная инвазивность**: Минимальные изменения существующего кода
2. **Расширяемость**: Легкое добавление новых методов оптимизации в будущем
3. **Пользовательская дружелюбность**: Интуитивный интерфейс настройки
4. **Надежность**: Тщательное тестирование и обработка ошибок

Успешная реализация этого плана предоставит пользователям приложения дополнительный мощный инструмент для глобальной оптимизации в задачах кинетического анализа, что может привести к более точным и надежным результатам исследований.
