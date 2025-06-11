# План исправления ошибок приложения кинетики твердофазных реакций

## Анализ проблем

На основе анализа 1000 строк логов выявлены следующие критические проблемы:

### 1. Каскадные повторяющиеся логи при инициализации
**Проблема**: Одинаковые последовательности логов повторяются множественно при каждом запуске приложения, засоряя логи и усложняя отладку.

**Примеры из логов**:
```
2025-06-11 18:54:05 - DEBUG - renderer_manager.py:64 - Building renderer map
2025-06-11 18:54:05 - DEBUG - renderer_manager.py:45 - RendererManager initialized with 6 renderers
[...повторяется 4 раза подряд...]
```

### 2. Отсутствующие методы в NavigationSidebar
**Ошибки**:
- `'NavigationSidebar' object has no attribute 'update_theme'` (строка 197 guide_framework.py)
- `NavigationSidebar.update_language() missing 1 required positional argument: 'language'` (строка 184 guide_framework.py)

### 3. Отсутствующий метод в StatusWidget (решено)
**Ошибка**: `'StatusWidget' object has no attribute 'update_section_info'` (строка 166 guide_framework.py)
**Статус**: ✅ **РЕШЕНО** - метод `update_section_info` уже существует в StatusWidget

### 4. Проблемы с отображением кодовых блоков
**Проблема**: Code widgets показывают черный фон без видимого контента

### 5. Ошибки типов данных
**Проблема**: Некоторые секции показывают ошибки `'str' has no attribute 'get'`

## План исправления

### Фаза 1: Исправление критических ошибок в NavigationSidebar

#### 1.1 Добавление недостающего метода `update_theme`
```python
def update_theme(self) -> None:
    """Update theme for navigation sidebar."""
    if not self.theme_manager:
        return
    
    # Apply theme colors to UI elements
    bg_color = self.theme_manager.get_color("background")
    text_color = self.theme_manager.get_color("text_primary")
    border_color = self.theme_manager.get_color("border")
    
    if all([bg_color, text_color, border_color]):
        self.setStyleSheet(f"""
            NavigationSidebar {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border-right: 1px solid {border_color.name()};
            }}
        """)
```

#### 1.2 Исправление сигнатуры метода `update_language`
**Проблема**: Метод `update_language()` в guide_framework.py вызывается без параметра `language`

**Исправление**: Обновить вызовы метода в guide_framework.py:
```python
# guide_framework.py строка ~172
self.navigation_sidebar.update_language(language_code)
```

### Фаза 2: Реализация комплексной системы логирования

#### 2.1 Создание StateLogger с assert-логикой
Создать новый модуль `src/core/state_logger.py`:

```python
class StateLogger:
    """Comprehensive state logger with assert functionality."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = LoggerManager.get_logger(f"state.{component_name}")
        self.state_cache = {}
    
    def log_state_change(self, operation: str, before_state: dict, after_state: dict):
        """Log state changes with comprehensive details."""
        changes = self._calculate_changes(before_state, after_state)
        self.logger.info(f"{operation} - State changes: {changes}")
    
    def assert_state(self, condition: bool, message: str, **context):
        """Assert with comprehensive state logging."""
        if not condition:
            self.logger.error(f"ASSERTION FAILED: {message} | Context: {context}")
            raise AssertionError(f"{self.component_name}: {message}")
        else:
            self.logger.debug(f"ASSERTION PASSED: {message}")
```

#### 2.2 Добавление StateLogger в ключевые компоненты
- `GuideFramework` - для трекинга состояния UI
- `NavigationSidebar` - для отслеживания навигации
- `ContentWidget` - для контроля рендеринга
- `BaseSignals` - для мониторинга межмодульной коммуникации

#### 2.3 Реализация интеллектуального дебаунсинга логов
```python
class LogDebouncer:
    """Intelligent log debouncing to prevent cascading identical logs."""
    
    def __init__(self, window_seconds: int = 5):
        self.window_seconds = window_seconds
        self.recent_logs = {}
    
    def should_log(self, message: str, level: str) -> bool:
        """Determine if message should be logged based on recent history."""
        key = f"{level}:{hash(message)}"
        now = time.time()
        
        if key in self.recent_logs:
            if now - self.recent_logs[key] < self.window_seconds:
                return False
        
        self.recent_logs[key] = now
        return True
```

### Фаза 3: Исправление проблем с кодовыми блоками

#### 3.1 Обновление цветовой схемы в CodeRenderer
**Проблема**: Неправильные цвета темы приводят к черному фону

**Исправление**:
```python
def _get_safe_theme_color(self, color_key: str, fallback: str) -> str:
    """Get theme color with safe fallback."""
    color = self.get_theme_color(color_key)
    return color.name() if color else fallback

def _render_code_block_simple(self, code_text: str, title: str = "", language: str = "text") -> QWidget:
    # Используем безопасные цвета с фоллбэками
    bg_color = self._get_safe_theme_color("code_background", "#f8f9fa")
    text_color = self._get_safe_theme_color("code_text", "#212529")
    border_color = self._get_safe_theme_color("border_primary", "#dee2e6")
    
    code_widget.setStyleSheet(f"""
        QTextEdit {{
            background-color: {bg_color};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 4px;
            padding: 8px;
        }}
    """)
```

#### 3.2 Добавление валидации контента
```python
def render(self, content: Dict[str, Any]) -> QWidget:
    """Render with comprehensive validation."""
    assert content is not None, "Content cannot be None"
    assert isinstance(content, dict), f"Content must be dict, got {type(content)}"
    
    content_type = content.get("type")
    assert content_type in self.get_supported_types(), f"Unsupported content type: {content_type}"
    
    # Продолжить с рендерингом...
```

### Фаза 4: Обработка ошибок типов данных

#### 4.1 Добавление проверок типов в ContentWidget
```python
def display_section(self, section_id: str) -> None:
    """Display section with type validation."""
    try:
        content = self.content_manager.get_section_content(section_id)
        
        # Валидация типов
        if content is None:
            self.state_logger.log_error(f"No content for section: {section_id}")
            return
            
        if isinstance(content, str):
            # Обработка строкового контента
            content = {"type": "text", "content": content}
        elif not isinstance(content, dict):
            self.state_logger.log_error(f"Invalid content type for {section_id}: {type(content)}")
            return
            
        self._render_content_safely(content)
        
    except Exception as e:
        self.state_logger.log_error(f"Error displaying section {section_id}: {e}")
```

### Фаза 5: Реструктуризация системы логирования

#### 5.1 Создание иерархической структуры логгеров
```python
# Основные категории логгеров
LOGGER_CATEGORIES = {
    "ui": "User interface components",
    "state": "Application state changes", 
    "navigation": "Navigation and routing",
    "rendering": "Content rendering",
    "communication": "Inter-component communication",
    "errors": "Error tracking and recovery"
}
```

#### 5.2 Добавление контекстных логгеров
```python
class ContextLogger:
    """Logger with automatic context injection."""
    
    def __init__(self, base_logger: Logger, context: dict):
        self.base_logger = base_logger
        self.context = context
    
    def log(self, level: str, message: str, **extra_context):
        """Log with full context."""
        full_context = {**self.context, **extra_context}
        enhanced_message = f"{message} | Context: {full_context}"
        getattr(self.base_logger, level)(enhanced_message)
```

## Приоритеты выполнения

1. **Критический (сразу)**: Исправление NavigationSidebar методов
2. **Высокий (1-2 дня)**: Реализация StateLogger и дебаунсинга логов
3. **Средний (3-5 дней)**: Исправление кодовых блоков и валидации контента
4. **Низкий (1 неделя)**: Полная реструктуризация системы логирования

## Критерии успеха

1. ✅ Отсутствие ошибок AttributeError в логах
2. ✅ Видимость всех кодовых блоков с правильным форматированием  
3. ✅ Сокращение объема логов на 70% при сохранении информативности
4. ✅ Comprehensive state tracking во всех критических компонентах
5. ✅ Assert-based валидация в местах потенциальных ошибок

## Следующие шаги

1. Исправить методы NavigationSidebar
2. Реализовать StateLogger для GuideFramework
3. Обновить CodeRenderer с безопасными цветами
4. Добавить assert-логику в критические места
5. Запустить полное тестирование исправлений