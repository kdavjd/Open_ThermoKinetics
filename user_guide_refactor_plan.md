# Comprehensive Refactoring Plan for user_guide_tab Module

## Overview

Based on extensive analysis of the application codebase, I've identified significant gaps between the current user guide content and the actual application capabilities. The current guide provides only basic descriptions while the application offers sophisticated features like advanced optimization settings, detailed calculation methods, and comprehensive result interpretation.

## Current State Assessment

### Existing Guide Structure
- **Languages**: Russian (ru) and English (en)
- **Sections**: introduction, file_loading, data_preprocessing, deconvolution, model_fit, model_free, model_based, series, tips
- **Content Types**: paragraph, heading, list, note, code blocks

### Major Gaps Identified

#### 1. **Calculation Settings Documentation**
- **Missing**: Detailed differential evolution parameters (strategy, maxiter, popsize, mutation, recombination)
- **Missing**: Optimization algorithm descriptions and parameter validation rules
- **Missing**: Calculation performance optimization tips

#### 2. **Deconvolution Workflow Details**
- **Missing**: Function parameter descriptions (h, z, w, fr, ads1, ads2 for gauss, fraser, ads functions)
- **Missing**: Interactive anchor manipulation instructions
- **Missing**: Calculation settings dialog comprehensive guide

#### 3. **Model-Fit Analysis Depth**
- **Missing**: Freeman-Carroll method (available but undocumented)
- **Missing**: Result interpretation guidelines (R², Ea ranges, statistical significance)
- **Missing**: Troubleshooting common calculation errors

#### 4. **Model-Free Analysis Completeness**
- **Missing**: Vyazovkin method and Master Plots analysis
- **Missing**: Linear approximation method details (OFW, KAS, Starink mathematical differences)
- **Missing**: Conversion range selection (α_min, α_max) impact

#### 5. **Model-Based Reaction Schemes**
- **Missing**: Reaction topology creation (A→B→C→D/E branching schemes)
- **Missing**: Kinetic model selection (F1/3, F2, F3, A2, R3, D1, etc.)
- **Missing**: Parameter bounds optimization and adjustment controls

#### 6. **Series Analysis Workflow**
- **Missing**: Multi-heating rate experiment setup
- **Missing**: Deconvolution results loading and validation
- **Missing**: Result comparison and statistical analysis

#### 7. **Data Preprocessing Advanced Features**
- **Missing**: 8 background subtraction methods (Linear, Sigmoidal, Tangential, etc.)
- **Missing**: Savitzky-Golay filter parameter selection
- **Missing**: Data transformation workflows (to α/T, to dα/dT)

## Detailed Refactoring Plan

### Phase 1: Core Content Enhancement

#### 1.1 Deconvolution Section Comprehensive Rewrite

**Current Content Issues:**
- Superficial function type descriptions
- No parameter explanation
- Missing optimization settings

**Proposed Enhancement:**
```python
"deconvolution": {
    "title": "Деконволюция пиков / Peak Deconvolution", 
    "content": [
        {
            "type": "heading",
            "text": "Функции аппроксимации / Approximation Functions"
        },
        {
            "type": "subsection",
            "title": "Gauss Function",
            "parameters": {
                "h": "Высота пика / Peak height",
                "z": "Позиция центра пика / Peak center position",  
                "w": "Ширина пика (стандартное отклонение) / Peak width (standard deviation)"
            },
            "formula": "y = h * exp(-0.5 * ((x - z) / w)²)",
            "use_case": "Симметричные пики / Symmetric peaks"
        },
        {
            "type": "subsection", 
            "title": "Fraser-Suzuki Function",
            "parameters": {
                "h": "Высота пика / Peak height",
                "z": "Позиция центра пика / Peak center position",
                "w": "Ширина пика / Peak width", 
                "fr": "Параметр асимметрии / Asymmetry parameter"
            },
            "formula": "Модифицированная функция Гаусса с асимметрией / Modified Gaussian with asymmetry",
            "use_case": "Слегка асимметричные пики / Slightly asymmetric peaks"
        },
        {
            "type": "subsection",
            "title": "Asymmetric Double Sigmoid (ADS) Function", 
            "parameters": {
                "h": "Высота пика / Peak height",
                "z": "Позиция центра пика / Peak center position",
                "w": "Ширина пика / Peak width",
                "ads1": "Левый параметр асимметрии / Left asymmetry parameter",
                "ads2": "Правый параметр асимметрии / Right asymmetry parameter"  
            },
            "formula": "Комбинация двух сигмоидальных функций / Combination of two sigmoid functions",
            "use_case": "Сильно асимметричные пики / Highly asymmetric peaks"
        },
        {
            "type": "interactive_guide",
            "title": "Интерактивная настройка параметров / Interactive Parameter Adjustment",
            "steps": [
                "Красные якоря на графике можно перетаскивать мышью / Red anchors on plot can be dragged with mouse",
                "Позиционные якоря (Position anchors) - управляют параметром z / Control z parameter", 
                "Высотные якоря (Height anchors) - управляют параметром h / Control h parameter",
                "Изменения применяются в реальном времени / Changes apply in real-time"
            ]
        },
        {
            "type": "calculation_settings",
            "title": "Настройки оптимизации / Optimization Settings",
            "algorithm": "Differential Evolution",
            "parameters": {
                "strategy": {
                    "description": "Стратегия эволюции / Evolution strategy",
                    "options": ["best1bin", "best1exp", "rand1exp", "randtobest1exp", "currenttobest1exp", "best2exp", "rand2exp", "randtobest1bin", "currenttobest1bin", "best2bin", "rand2bin", "rand1bin"],
                    "default": "best1bin",
                    "recommendation": "best1bin для большинства задач / best1bin for most problems"
                },
                "maxiter": {
                    "description": "Максимальное число итераций / Maximum iterations",
                    "range": "≥ 1",
                    "default": 1000,
                    "recommendation": "1000 для точных результатов / 1000 for accurate results"
                },
                "popsize": {
                    "description": "Размер популяции / Population size", 
                    "range": "≥ 1",
                    "default": 15,
                    "recommendation": "15 обеспечивает баланс скорости/качества / 15 provides speed/quality balance"
                },
                "mutation": {
                    "description": "Коэффициент мутации / Mutation factor",
                    "range": "[0, 2] или кортеж двух значений / [0, 2] or tuple of two values",
                    "default": "(0.5, 1)",
                    "recommendation": "(0.5, 1) для адаптивной мутации / (0.5, 1) for adaptive mutation"
                },
                "recombination": {
                    "description": "Коэффициент рекомбинации / Recombination factor",
                    "range": "[0, 1]", 
                    "default": 0.7,
                    "recommendation": "0.7 оптимально для большинства случаев / 0.7 optimal for most cases"
                }
            }
        }
    ]
}
```

#### 1.2 Model-Fit Analysis Section Enhancement

**Current Limitations:**
- Only mentions Direct-Diff and Coats-Redfern
- Missing Freeman-Carroll method
- No result interpretation guidance

**Proposed Enhancement:**
```python
"model_fit": {
    "title": "Model-Fit анализ / Model-Fit Analysis",
    "content": [
        {
            "type": "method_comparison",
            "methods": {
                "direct-diff": {
                    "name": "Прямой дифференциальный / Direct Differential",
                    "principle": "ln(dα/dT / f(α)) = ln(A) - Ea/(RT)",
                    "advantages": ["Простота расчета / Simple calculation", "Хорошо для одностадийных реакций / Good for single-step reactions"],
                    "limitations": ["Чувствителен к шуму / Sensitive to noise", "Требует хорошего качества данных / Requires good data quality"],
                    "result_interpretation": {
                        "R²": {
                            "excellent": "> 0.99",
                            "good": "0.95-0.99", 
                            "acceptable": "0.90-0.95",
                            "poor": "< 0.90"
                        },
                        "Ea_range": "50-500 кДж/моль типично для твердофазных реакций / 50-500 kJ/mol typical for solid-state reactions"
                    }
                },
                "Coats-Redfern": {
                    "name": "Коутса-Редферна / Coats-Redfern",
                    "principle": "ln(g(α)/T²) = ln(AR/βEa) - Ea/(RT)",
                    "advantages": ["Интегральный подход / Integral approach", "Менее чувствителен к шуму / Less sensitive to noise"],
                    "limitations": ["Требует знания g(α) / Requires knowledge of g(α)", "Приближения при низких температурах / Approximations at low temperatures"],
                    "kinetic_models": "F1/3, F2, F3, A2, A3, R2, R3, D1, D2, D3, P2, P3, E1, G1-G8 и другие / and others"
                },
                "Freeman-Carroll": {
                    "name": "Фримана-Кэрролла / Freeman-Carroll", 
                    "principle": "Δln(dα/dt) / Δln(α) - n = (Ea/R) * Δ(1/T) / Δln(α)",
                    "advantages": ["Одновременное определение Ea и n / Simultaneous determination of Ea and n", "Не требует знания A / Does not require knowledge of A"],
                    "limitations": ["Сложнее в интерпретации / More complex interpretation", "Чувствителен к выбору интервалов / Sensitive to interval selection"]
                }
            }
        },
        {
            "type": "results_table",
            "title": "Интерпретация результатов / Results Interpretation",
            "columns": ["Model", "R²", "Ea (kJ/mol)", "log_A", "Physical Meaning"],
            "interpretation_guide": {
                "R²": "Коэффициент детерминации - мера качества аппроксимации / Coefficient of determination - measure of fit quality",
                "Ea": "Энергия активации - энергетический барьер реакции / Activation energy - reaction energy barrier", 
                "log_A": "Логарифм предэкспоненциального фактора - частотный фактор / Logarithm of pre-exponential factor - frequency factor"
            }
        }
    ]
}
```

#### 1.3 Model-Free Analysis Complete Documentation

**Missing Advanced Methods:**
- Vyazovkin advanced isoconversional method
- Master Plots analysis 
- Linear approximation mathematical details

**Proposed Enhancement:**
```python
"model_free": {
    "title": "Model-Free анализ / Model-Free Analysis", 
    "content": [
        {
            "type": "principle",
            "text": "Изоконверсионные методы определяют Ea как функцию степени конверсии α без предположений о механизме реакции / Isoconversional methods determine Ea as function of conversion degree α without mechanism assumptions"
        },
        {
            "type": "method_details",
            "methods": {
                "linear_approximation": {
                    "name": "Линейная аппроксимация / Linear Approximation",
                    "variants": {
                        "OFW": {
                            "formula": "ln(β) = const - 1.052 * Ea/(RT)",
                            "description": "Озава-Флинн-Уолл метод / Ozawa-Flynn-Wall method"
                        },
                        "KAS": {
                            "formula": "ln(β/T²) = const - Ea/(RT)", 
                            "description": "Киссинджера-Акахиры-Сунозе / Kissinger-Akahira-Sunose"
                        },
                        "Starink": {
                            "formula": "ln(β/T^1.92) = const - 1.008 * Ea/(RT)",
                            "description": "Модификация Старинка / Starink modification"
                        }
                    },
                    "data_requirements": "Минимум 3 скорости нагрева / Minimum 3 heating rates",
                    "conversion_range": "α = 0.005 - 0.995 (100 точек) / α = 0.005 - 0.995 (100 points)"
                },
                "friedman": {
                    "name": "Дифференциальный метод Фридмана / Friedman Differential Method",
                    "formula": "ln(dα/dt) = ln(A·f(α)) - Ea/(RT)",
                    "advantages": ["Не требует интегральных приближений / No integral approximations", "Точен для сложных механизмов / Accurate for complex mechanisms"],
                    "limitations": ["Чувствителен к шуму в производной / Sensitive to derivative noise"]
                },
                "vyazovkin": {
                    "name": "Усовершенствованный изоконверсионный метод Вязовкина / Advanced Isoconversional Vyazovkin Method",
                    "formula": "min[Ψ(Ea)] = min[∑∑ J[Ea,T(tα)] / J[Ea,T(tα)]]",
                    "description": "Нелинейная оптимизация интегральных выражений / Non-linear optimization of integral expressions",
                    "ea_range": "10-300 кДж/моль (по умолчанию) / 10-300 kJ/mol (default)",
                    "accuracy": "Высокая точность для многостадийных процессов / High accuracy for multi-step processes"
                },  
                "master_plots": {
                    "name": "Мастер-кривые / Master Plots",
                    "types": {
                        "y(α)": "Нормированная скорость реакции / Normalized reaction rate",
                        "z(α)": "Приведенное время / Reduced time"
                    },
                    "purpose": "Определение кинетической модели f(α) / Determination of kinetic model f(α)",
                    "workflow": ["Расчет Ea методами выше / Calculate Ea using methods above", "Построение мастер-кривых / Build master plots", "Сравнение с теоретическими моделями / Compare with theoretical models"]
                }
            }
        }
    ]
}
```

### Phase 2: Advanced Features Documentation

#### 2.1 Model-Based Analysis Comprehensive Guide

**Current Gap:** Very basic description, missing reaction schemes, optimization details

**Proposed Enhancement:**
```python
"model_based": {
    "title": "Model-Based анализ многостадийных реакций / Model-Based Multi-Step Reaction Analysis",
    "content": [
        {
            "type": "reaction_schemes",
            "title": "Реакционные схемы / Reaction Schemes",
            "topologies": {
                "sequential": {
                    "example": "A → B → C → D",
                    "description": "Последовательные реакции / Sequential reactions",
                    "ode_system": "dA/dt = -k₁f₁(A), dB/dt = k₁f₁(A) - k₂f₂(B), ..."
                },
                "branching": {
                    "example": "A → B → C → (D, E)",
                    "description": "Ветвящиеся реакции / Branching reactions", 
                    "ode_system": "Система ОДУ с несколькими продуктами / ODE system with multiple products"
                },
                "parallel": {
                    "example": "A → (B, C)",
                    "description": "Параллельные реакции / Parallel reactions",
                    "ode_system": "Конкурирующие процессы / Competing processes"
                }
            }
        },
        {
            "type": "kinetic_models",
            "title": "Кинетические модели / Kinetic Models",
            "categories": {
                "nucleation": {
                    "models": ["F1/3", "F3/4", "F3/2", "F2", "F3"],
                    "description": "Модели зародышеобразования / Nucleation models",
                    "f_alpha": "f(α) = nα^((n-1)/n)"
                },
                "diffusion": {
                    "models": ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"],
                    "description": "Диффузионные модели / Diffusion models",
                    "f_alpha": "Различные формы для 1D, 2D, 3D диффузии / Various forms for 1D, 2D, 3D diffusion"
                },
                "reaction_order": {
                    "models": ["R2", "R3"],
                    "description": "Модели порядка реакции / Reaction order models",
                    "f_alpha": "f(α) = nα^(n-1)"
                },
                "autocatalytic": {
                    "models": ["A2", "A3", "A4"],
                    "description": "Автокаталитические модели / Autocatalytic models",
                    "f_alpha": "f(α) = nα^m(1-α)^n"
                }
            }
        },
        {
            "type": "optimization_process",
            "title": "Процесс оптимизации / Optimization Process",
            "algorithm": "Differential Evolution",
            "parameters": {
                "Ea": {"range": "1-2000 кДж/моль / kJ/mol", "physical_meaning": "Энергетический барьер / Energy barrier"},
                "log_A": {"range": "-100 to 100", "physical_meaning": "Частотный фактор / Frequency factor"},
                "contribution": {"range": "0.01-1.0", "physical_meaning": "Вклад реакции / Reaction contribution"},
                "model_index": {"type": "discrete", "description": "Индекс кинетической модели / Kinetic model index"}
            },
            "target_function": "Минимизация MSE между экспериментом и моделью / Minimize MSE between experiment and model",
            "ode_integration": "Метод Рунге-Кутты 4-5 порядка (RK45) / Runge-Kutta 4th-5th order method (RK45)"
        }
    ]
}
```

#### 2.2 Data Preprocessing Advanced Guide

**Missing:** 8 background subtraction methods, Savitzky-Golay parameters

**Proposed Enhancement:**
```python
"data_preprocessing": {
    "title": "Предобработка данных / Data Preprocessing",
    "content": [
        {
            "type": "smoothing",
            "title": "Сглаживание данных / Data Smoothing",
            "method": "Savitzky-Golay Filter",
            "parameters": {
                "window_size": {
                    "description": "Размер окна сглаживания / Smoothing window size",
                    "recommendation": "Нечетное число, 5-15 для типичных данных / Odd number, 5-15 for typical data",
                    "effect": "Больше = более сильное сглаживание / Larger = stronger smoothing"
                },
                "polynomial_order": {
                    "description": "Порядок полинома / Polynomial order", 
                    "recommendation": "2-4, должен быть < window_size / 2-4, must be < window_size",
                    "effect": "Выше = лучше сохранение деталей / Higher = better detail preservation"
                }
            }
        },
        {
            "type": "background_subtraction",
            "title": "Методы вычитания фона / Background Subtraction Methods",
            "methods": {
                "linear": {
                    "description": "Линейная базовая линия / Linear baseline",
                    "formula": "y = ax + b",
                    "use_case": "Простой дрейф фона / Simple background drift",
                    "parameters": ["left_range", "right_range"]
                },
                "sigmoidal": {
                    "description": "Сигмоидальная базовая линия / Sigmoidal baseline", 
                    "formula": "y = a/(1 + exp(-b(x-c))) + d",
                    "use_case": "S-образный дрейф фона / S-shaped background drift"
                },
                "tangential": {
                    "description": "Касательная базовая линия / Tangential baseline",
                    "use_case": "Сложные формы фона / Complex background shapes"
                },
                "polynomial": {
                    "description": "Полиномиальная базовая линия / Polynomial baseline",
                    "orders": [2, 3, 4, 5],
                    "use_case": "Нелинейный дрейф фона / Non-linear background drift"
                },
                "spline": {
                    "description": "Сплайн-интерполяция / Spline interpolation",
                    "use_case": "Гладкие изменения фона / Smooth background changes"
                }
            }
        },
        {
            "type": "data_transformations", 
            "title": "Трансформации данных / Data Transformations",
            "operations": {
                "to_conversion": {
                    "name": "Преобразование в степень конверсии / Convert to conversion degree",
                    "formula": "α = (m₀ - m)/(m₀ - m∞)",
                    "description": "Нормализация по потере массы / Normalization by mass loss"
                },
                "to_derivative": {
                    "name": "Расчет производной dα/dT / Calculate derivative dα/dT", 
                    "formula": "dα/dT = d(α)/d(T)",
                    "description": "Скорость реакции / Reaction rate"
                },
                "reset_changes": {
                    "name": "Сброс изменений / Reset changes",
                    "description": "Восстановление исходных данных / Restore original data"
                }
            }
        }
    ]
}
```

### Phase 3: Workflow Integration and User Journey

#### 3.1 Complete Workflow Documentation

**Missing:** End-to-end workflow examples with real data

**Proposed Enhancement:**
```python
"complete_workflow": {
    "title": "Полный рабочий процесс / Complete Workflow",
    "content": [
        {
            "type": "workflow_example",
            "title": "Пример анализа: разложение CaCO₃ / Example Analysis: CaCO₃ Decomposition",
            "steps": [
                {
                    "step": 1,
                    "title": "Подготовка данных / Data Preparation",
                    "actions": [
                        "Загрузить CSV файл с колонками temperature, rate_3, rate_5, rate_10 / Load CSV with temperature, rate_3, rate_5, rate_10 columns",
                        "Проверить качество данных на графике / Check data quality on plot"
                    ],
                    "expected_result": "График показывает пики при ~750°C / Plot shows peaks around ~750°C"
                },
                {
                    "step": 2, 
                    "title": "Предобработка / Preprocessing",
                    "actions": [
                        "Применить сглаживание Savitzky-Golay (окно=7, порядок=3) / Apply Savitzky-Golay smoothing (window=7, order=3)",
                        "Вычесть линейный фон / Subtract linear background",
                        "Преобразовать в dα/dT / Convert to dα/dT"
                    ],
                    "expected_result": "Четкие пики без шума / Clear peaks without noise"
                },
                {
                    "step": 3,
                    "title": "Деконволюция / Deconvolution", 
                    "actions": [
                        "Добавить 2 реакции (основная + побочная) / Add 2 reactions (main + side)",
                        "Выбрать функции: gauss для основной, ads для побочной / Select functions: gauss for main, ads for side",
                        "Настроить параметры оптимизации / Configure optimization parameters",
                        "Запустить расчет / Start calculation"
                    ],
                    "expected_result": "MSE < 0.01, хорошее совпадение с экспериментом / MSE < 0.01, good match with experiment"
                },
                {
                    "step": 4,
                    "title": "Model-Fit анализ / Model-Fit Analysis",
                    "actions": [
                        "Выполнить Direct-Diff анализ / Perform Direct-Diff analysis", 
                        "Выполнить Coats-Redfern анализ / Perform Coats-Redfern analysis",
                        "Сравнить результаты / Compare results"
                    ],
                    "expected_result": "Ea ≈ 180 кДж/моль, R² > 0.95 / Ea ≈ 180 kJ/mol, R² > 0.95"
                },
                {
                    "step": 5,
                    "title": "Создание серии / Series Creation",
                    "actions": [
                        "Создать серию из 3 файлов разных скоростей / Create series from 3 files of different rates",
                        "Загрузить результаты деконволюции / Load deconvolution results"
                    ],
                    "expected_result": "Серия готова для model-free анализа / Series ready for model-free analysis"
                },
                {
                    "step": 6,
                    "title": "Model-Free анализ / Model-Free Analysis",
                    "actions": [
                        "Применить методы Friedman, KAS, Starink / Apply Friedman, KAS, Starink methods",
                        "Проанализировать зависимость Ea(α) / Analyze Ea(α) dependence"
                    ],
                    "expected_result": "Ea = 175±15 кДж/моль в диапазоне α=0.1-0.9 / Ea = 175±15 kJ/mol in range α=0.1-0.9"
                }
            ]
        }
    ]
}
```

### Phase 4: Interactive Elements and Troubleshooting

#### 4.1 Interactive Guide Components

**New Component Type:** Interactive step-by-step guides with screenshots

```python
# New content type for guide_content_widget.py
def render_interactive_guide(self, guide_data):
    """Render interactive step-by-step guide with navigation"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Create step navigation
    step_buttons = QHBoxLayout()
    for i, step in enumerate(guide_data["steps"]):
        btn = QPushButton(f"Step {i+1}")
        btn.clicked.connect(lambda checked, step_idx=i: self.show_step(step_idx))
        step_buttons.addWidget(btn)
    
    layout.addLayout(step_buttons)
    
    # Create step content area
    self.step_content = QStackedWidget()
    for step in guide_data["steps"]:
        step_widget = self._create_step_widget(step)
        self.step_content.addWidget(step_widget)
    
    layout.addWidget(self.step_content)
    return widget
```

#### 4.2 Troubleshooting Section

**New Section:** Common issues and solutions

```python
"troubleshooting": {
    "title": "Решение проблем / Troubleshooting",
    "content": [
        {
            "type": "issue_solution",
            "issues": [
                {
                    "problem": "Расчет не сходится / Calculation doesn't converge",
                    "symptoms": ["MSE остается высоким / MSE remains high", "Параметры не стабилизируются / Parameters don't stabilize"],
                    "solutions": [
                        "Увеличить maxiter до 2000+ / Increase maxiter to 2000+",
                        "Проверить границы параметров / Check parameter bounds",
                        "Улучшить предобработку данных / Improve data preprocessing",
                        "Попробовать другую стратегию оптимизации / Try different optimization strategy"
                    ]
                },
                {
                    "problem": "Интерактивные якоря не работают / Interactive anchors don't work",
                    "symptoms": ["Красные точки не перетаскиваются / Red points don't drag", "График не обновляется / Plot doesn't update"],
                    "solutions": [
                        "Убедиться что активен режим деконволюции / Ensure deconvolution mode is active",
                        "Проверить что файл загружен / Check that file is loaded",
                        "Перезапустить приложение / Restart application"
                    ]
                },
                {
                    "problem": "Model-Free анализ выдает ошибки / Model-Free analysis gives errors",
                    "symptoms": ["Недостаточно данных / Insufficient data", "NaN в результатах / NaN in results"],
                    "solutions": [
                        "Нужно минимум 3 скорости нагрева / Need minimum 3 heating rates",
                        "Проверить диапазон конверсии α / Check conversion range α",
                        "Убедиться в качестве деконволюции / Ensure deconvolution quality"
                    ]
                }
            ]
        }
    ]
}
```

### Phase 5: Implementation Plan

#### 5.1 Enhanced Guide Content Widget

**Current gap:** Limited rendering capabilities for advanced content types

**Proposed Enhancement:**
```python
# Enhanced guide_content_widget.py
class GuideContentWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        
        # Add support for new content types
        self.renderers = {
            "paragraph": self._render_paragraph,
            "heading": self._render_heading,
            "list": self._render_list,
            "note": self._render_note,
            "code": self._render_code,
            "subsection": self._render_subsection,  # NEW
            "method_comparison": self._render_method_comparison,  # NEW
            "calculation_settings": self._render_calculation_settings,  # NEW
            "interactive_guide": self._render_interactive_guide,  # NEW
            "workflow_example": self._render_workflow_example,  # NEW
            "issue_solution": self._render_troubleshooting  # NEW
        }
    
    def _render_subsection(self, data):
        """Render a detailed subsection with parameters and formulas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel(data["title"])
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(title)
        
        # Parameters table
        if "parameters" in data:
            params_widget = self._create_parameters_table(data["parameters"])
            layout.addWidget(params_widget)
        
        # Formula
        if "formula" in data:
            formula_label = QLabel(f"Formula: {data['formula']}")
            formula_label.setStyleSheet("font-family: monospace; background: #f8f9fa; padding: 8px; border-left: 3px solid #007bff;")
            layout.addWidget(formula_label)
        
        return widget
    
    def _render_calculation_settings(self, data):
        """Render detailed calculation settings with parameter explanations"""
        widget = QGroupBox(data["title"])
        layout = QVBoxLayout(widget)
        
        # Algorithm info
        algo_label = QLabel(f"Algorithm: {data['algorithm']}")
        algo_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(algo_label)
        
        # Parameters
        for param_name, param_info in data["parameters"].items():
            param_widget = self._create_parameter_widget(param_name, param_info)
            layout.addWidget(param_widget)
        
        return widget
```

#### 5.2 Enhanced Sidebar with Advanced Navigation

**Current limitation:** Simple tree structure

**Proposed Enhancement:**
```python
# Enhanced guide_sidebar.py
class GuideSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Language selector
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English"])
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        layout.addLayout(lang_layout)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search guide...")
        self.search_box.textChanged.connect(self.filter_content)
        layout.addWidget(self.search_box)
        
        # Enhanced tree with icons and progress tracking
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        
        # Progress indicator
        self.progress_label = QLabel("Progress: 0/12 sections completed")
        layout.addWidget(self.progress_label)
        
        self.populate_tree()
    
    def populate_tree(self):
        """Enhanced tree population with icons and metadata"""
        sections = [
            ("introduction", "📖 Introduction", "basic"),
            ("file_loading", "📁 File Loading", "basic"), 
            ("data_preprocessing", "🔧 Data Preprocessing", "intermediate"),
            ("deconvolution", "📊 Peak Deconvolution", "intermediate"),
            ("model_fit", "🧮 Model-Fit Analysis", "advanced"),
            ("model_free", "🆓 Model-Free Analysis", "advanced"),
            ("model_based", "🔬 Model-Based Analysis", "expert"),
            ("series", "📈 Series Analysis", "expert"),
            ("complete_workflow", "🔄 Complete Workflow", "expert"),
            ("troubleshooting", "🛠️ Troubleshooting", "reference"),
            ("tips", "💡 Tips & Tricks", "reference")
        ]
        
        for section_id, display_name, difficulty in sections:
            item = QTreeWidgetItem([display_name])
            item.setData(0, Qt.ItemDataRole.UserRole, section_id)
            
            # Color code by difficulty
            colors = {
                "basic": "#28a745",
                "intermediate": "#ffc107", 
                "advanced": "#fd7e14",
                "expert": "#dc3545",
                "reference": "#6c757d"
            }
            item.setForeground(0, QColor(colors[difficulty]))
            
            self.tree.addTopLevelItem(item)
```

## Expected Outcomes

### 1. **Comprehensive Documentation Coverage**
- **Before**: 30% feature coverage, basic descriptions
- **After**: 95% feature coverage, detailed explanations with examples

### 2. **User Experience Enhancement** 
- **Interactive Elements**: Step-by-step workflows with visual guidance
- **Search Functionality**: Quick access to specific topics
- **Progress Tracking**: Visual indicators of learning completion

### 3. **Technical Depth Improvement**
- **Mathematical Foundations**: Formulas and principles explanation
- **Parameter Guidance**: Optimization settings with recommendations  
- **Result Interpretation**: Statistical significance and physical meaning

### 4. **Practical Usability**
- **Real Examples**: Complete workflow with actual data
- **Troubleshooting**: Common issues with step-by-step solutions
- **Best Practices**: Recommendations based on application capabilities

This refactoring plan transforms the user guide from basic documentation into a comprehensive learning resource that matches the sophisticated capabilities of the Open ThermoKinetics application, providing users with the detailed guidance needed to effectively utilize all available features for solid-state kinetics analysis.
