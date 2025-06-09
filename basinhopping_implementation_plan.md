# План реализации basinhopping оптимизации в MODEL_BASED_CALCULATION

## Цель
Интегрировать метод `basinhopping` из `scipy.optimize` в существующую систему MODEL_BASED_CALCULATION с максимальным переиспользованием кода и минимальными изменениями архитектуры.

## Архитектурные принципы
- Следовать существующим паттернам BaseSignals/BaseSlots
- Максимально переиспользовать код differential_evolution
- Использовать существующую систему CalculationThread
- Централизовать константы в app_settings.py
- НЕ создавать новые сигналы или модули

## Конкретные изменения

### 1. app_settings.py - ВЫПОЛНЕНО ✓
Добавлены константы BASINHOPPING_PARAMETERS с базовыми параметрами:
```python
BASINHOPPING_PARAMETERS = {
    "niter": 100,
    "T": 1.0,
    "stepsize": 0.5,
    "minimizer_kwargs": {"method": "L-BFGS-B"},
    "take_step": None,
    "accept_test": None,
    "callback": None,
    "interval": 50,
    "disp": False,
    "niter_success": None,
    "seed": None,
}
```

### 2. calculation.py - ТРЕБУЕТ РЕАЛИЗАЦИИ
Добавить единственный новый метод `start_basinhopping()` по аналогии с `start_differential_evolution()`:

```python
def start_basinhopping(self, bounds, target_function, **kwargs):
    from scipy.optimize import basinhopping
    
    # Handle bounds for minimizer
    minimizer_kwargs = kwargs.get("minimizer_kwargs", {}).copy()
    minimizer_kwargs["bounds"] = bounds
    kwargs["minimizer_kwargs"] = minimizer_kwargs
    kwargs.pop("bounds", None)  # Remove from basinhopping kwargs
    
    self.start_calculation_thread(
        basinhopping,
        target_function,
        **kwargs,
    )
```

Обновить `run_calculation_scenario()` для поддержки "basinhopping":
```python
if optimization_method == "differential_evolution":
    # ...existing code...
elif optimization_method == "basinhopping":
    calc_params = params.get("calculation_settings", {}).get("method_parameters", {}).copy()
    if scenario_key == "model_based_calculation":
        calc_params["callback"] = make_de_callback(target_function, self)
    self.start_basinhopping(bounds=bounds, target_function=target_function, **calc_params)
else:
    logger.error(f"Unsupported optimization method: {optimization_method}")
```

### 3. GUI изменения - МИНИМАЛЬНЫЕ
Обновить CalculationSettingsDialog для добавления "basinhopping" в список методов:
- Добавить в combo box метод "basinhopping"
- Добавить UI элементы для основных параметров basinhopping
- Использовать BASINHOPPING_PARAMETERS как значения по умолчанию

### 4. Архитектурная интеграция
- ModelBasedScenario.get_optimization_method() уже поддерживает динамическое получение метода
- Существующая система bounds и target_function остается без изменений
- CalculationThread автоматически обработает basinhopping как любую другую scipy функцию
- Система callback и progress остается той же

## Преимущества подхода
1. **Минимальные изменения**: Только 1 новый метод + обновление условия
2. **Максимальное переиспользование**: Вся инфраструктура остается той же
3. **Архитектурная совместимость**: Полное следование паттернам проекта
4. **Простота тестирования**: Изолированные изменения легко тестировать

## Объем работ
- **Константы**: ✓ ВЫПОЛНЕНО
- **Core логика**: 15-20 строк кода
- **GUI**: Минор обновления в существующем диалоге
- **Тестирование**: Использование существующих MODEL_BASED тестов

## Результат
Пользователь сможет выбрать "basinhopping" в настройках MODEL_BASED расчетов и получить глобальную оптимизацию с возможностью избежать локальных минимумов в многомерном пространстве параметров реакций.

Метод особенно эффективен для сложных реакционных схем с множественными локальными минимумами MSE.
