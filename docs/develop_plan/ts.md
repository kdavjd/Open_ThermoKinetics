# Техническое задание: Добавление вывода MSE в model-based симуляцию

## Описание задачи

Добавить логику вывода MSE (Mean Squared Error) в console.log при каждом вызове функции `_simulate_reaction_model` в ModelBasedPanel. MSE должен рассчитываться как сравнение экспериментальных данных текущей серии с симулированными данными модели.

## Техническая реализация

### 1. Модификация функции `_simulate_reaction_model`

**Файл:** `src\gui\main_tab\sub_sidebar\model_based\model_based_panel.py`

Добавить расчет MSE после получения симулированных данных для каждой скорости нагрева:

```python
def _simulate_reaction_model(self, experimental_data: pd.DataFrame, reaction_scheme: dict):
    """Simulate reaction model using core functions with MSE output."""
    # ...existing validation code...
    
    # Use core functions with adapted parameters
    simulation_results = {"temperature": sim_params["T"]}
    total_mse = 0.0
    valid_rates_count = 0

    for beta_col in sim_params["beta_columns"]:
        beta_value = self._validate_heating_rate(beta_col)
        if beta_value is None:
            continue

        try:
            # ...existing simulation code...
            
            # Calculate MSE for current heating rate
            if beta_col in simulation_results and len(simulation_results[beta_col]) == len(experimental_data[beta_col]):
                mse_single = self._calculate_mse(
                    experimental_data[beta_col].values, 
                    simulation_results[beta_col]
                )
                total_mse += mse_single
                valid_rates_count += 1
                
        except Exception as e:
            # ...existing error handling...

    # Output total MSE to console
    if valid_rates_count > 0:
        average_mse = total_mse / valid_rates_count
        console.log(f"MSE for current simulation: {average_mse:.6f}")
    
    return pd.DataFrame(simulation_results)
```

### 2. Использование существующей логики MSE из core

Модификация функции `_simulate_reaction_model` для использования существующей функции `integrate_ode_for_beta`, которая уже возвращает MSE:

```python
def _simulate_reaction_model(self, experimental_data: pd.DataFrame, reaction_scheme: dict):
    """Simulate reaction model using core functions with MSE output."""
    # ...existing validation code...
    
    # Use core functions with adapted parameters
    simulation_results = {"temperature": sim_params["T"]}
    total_mse = 0.0
    valid_rates_count = 0

    for beta_col in sim_params["beta_columns"]:
        beta_value = self._validate_heating_rate(beta_col)
        if beta_value is None:
            continue

        try:
            # Direct use of core function integrate_ode_for_beta
            mse_result = integrate_ode_for_beta(
                beta_value,  # Pass β directly (K/min)
                sim_params["contributions"],
                core_params,  # Adapted parameters
                sim_params["species_list"],
                sim_params["reactions"],
                sim_params["num_species"],
                sim_params["num_reactions"],
                sim_params["T_K"],
                experimental_data[beta_col].values,
                R=8.314,
            )

            # integrate_ode_for_beta returns MSE directly
            if isinstance(mse_result, (int, float)) and mse_result < 1e12:
                total_mse += mse_result
                valid_rates_count += 1
                # Store simulated data for visualization (optional)
                # simulation_results[beta_col] = simulated_mass_values
                
        except Exception as e:
            logger.error(f"Simulation failed for heating rate {beta_value}: {e}")

    # Output total MSE to console
    if valid_rates_count > 0:
        average_mse = total_mse / valid_rates_count
        console.log(f"MSE for current simulation: {average_mse:.6f}")
    
    return pd.DataFrame(simulation_results)
```

### 3. Точки вызова функции

Функция `_simulate_reaction_model` вызывается в следующих случаях:

1. **При изменении параметров:** через `_on_params_changed()` → `model_params_changed.emit()` → `MainWindow._handle_model_params_change()` → `update_model_simulation()`

2. **При изменении схемы:** через `ModelsScheme` → `scheme_changed` сигнал → `MainWindow._handle_scheme_change()` → `update_model_simulation()`

3. **При расчете оптимизации:** через `ModelCalcButtons` → model-based calculation workflow

### 4. Формат вывода

Вывод MSE в консоль должен иметь формат:
```
MSE for current simulation: 0.001234
```

### 5. Обработка ошибок

- При ошибках интеграции ОДУ - функция `integrate_ode_for_beta` возвращает `1e12`
- При отсутствии валидных скоростей нагрева - пропуск вывода MSE  
- При ошибках симуляции - логирование ошибки и продолжение обработки других скоростей

### 6. Интеграция с существующей архитектурой

**Импорты**: Функция `integrate_ode_for_beta` уже импортирована в файле:
```python
from src.core.calculation_scenarios import integrate_ode_for_beta, ode_function
```

**Логирование**: Использовать существующую систему логирования через `src.core.logger_config.logger`

**Валидация**: Использовать существующую функцию `_validate_heating_rate()` для проверки скоростей нагрева

**MSE расчет**: Использовать существующую логику из `integrate_ode_for_beta()`, которая:
- Интегрирует ОДУ для model-based симуляции  
- Возвращает MSE между экспериментальными и симулированными массовыми значениями
- Обрабатывает ошибки интеграции (возвращает 1e12 при неудаче)

## Ожидаемый результат

После внесения изменений при любом изменении параметров серии в model-based расчете будет автоматически рассчитываться и выводиться MSE между экспериментальными и симулированными данными, что поможет пользователю оценивать качество подгонки модели в режиме реального времени.

## Зависимости

- `numpy` для математических операций
- `src.core.logger_console.LoggerConsole` для вывода в консоль  
- `src.core.calculation_scenarios.integrate_ode_for_beta` для расчета MSE
- Существующая архитектура сигналов для обновления симуляции

## Тестирование

Тестировать изменения можно:
1. Загрузив экспериментальные данные серии
2. Изменив параметры реакции (Ea, log_A, contribution)
3. Проверив появление сообщения MSE в консоли приложения

## Команды для запуска

Для тестирования изменений использовать:
```powershell
poetry run ssk-gui
```
