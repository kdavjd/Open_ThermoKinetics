# User Guide Tab - Developer Notes

## Архитектура

### Основной класс: `UserGuideTab`
```python
from src.gui.user_guide_tab import UserGuideTab

# Создание с родительским виджетом
guide_tab = UserGuideTab(parent=main_window)
```

### Структура компонентов
```
UserGuideTab (QWidget)
├── QSplitter (horizontal)
    ├── GuideSidebar (navigation)
    │   ├── QComboBox (language selector)
    │   └── QTreeWidget (content navigation)
    └── GuideContentWidget (content display)
        └── QScrollArea (rich text content)
```

## Добавление нового контента

### 1. Добавление раздела
Отредактируйте `guide_content.py`:

```python
GUIDE_CONTENT = {
    "ru": {
        "new_section_id": {
            "title": "Заголовок раздела",
            "content": [
                {
                    "type": "paragraph",
                    "text": "Текст параграфа"
                },
                {
                    "type": "heading", 
                    "text": "Подзаголовок"
                },
                {
                    "type": "list",
                    "items": ["Элемент 1", "Элемент 2"]
                },
                {
                    "type": "code",
                    "text": "console.log('example');"
                },
                {
                    "type": "note",
                    "text": "<b>Важно:</b> Заметка пользователю"
                }
            ]
        }
    },
    "en": {
        # English version...
    }
}
```

### 2. Добавление в навигацию
Обновите `config.py`:

```python
GUIDE_SECTIONS = {
    "ru": {
        "Новый раздел": "new_section_id",
        # или в подкатегории:
        "Категория": {
            "Новый раздел": "new_section_id"
        }
    }
}
```

## Поддерживаемые типы контента

| Тип         | Описание                         | Параметры                    |
| ----------- | -------------------------------- | ---------------------------- |
| `paragraph` | Обычный текст с HTML поддержкой  | `text`                       |
| `heading`   | Подзаголовок                     | `text`                       |
| `list`      | Маркированный список             | `items: []`                  |
| `code`      | Блок кода с моноширинным шрифтом | `text`                       |
| `note`      | Выделенная заметка               | `text` (HTML поддерживается) |
| `image`     | Изображение с подписью           | `path`, `caption`            |

## Настройка стилей

Конфигурация в `config.py`:

```python
@dataclass
class GuideConfig:
    # Шрифты
    HEADING_FONT_SIZE = 16
    BODY_FONT_SIZE = 11
    CODE_FONT_SIZE = 10
    
    # Цвета
    HEADING_COLOR = "#2c3e50"
    CODE_BACKGROUND = "#f8f9fa"
    
    # Размеры
    MIN_WIDTH_SIDEBAR = 250
    MIN_WIDTH_CONTENT = 600
```

## Сигналы

### GuideSidebar
- `section_selected(str)` - выбран раздел
- `language_changed(Language)` - изменен язык

### GuideContentWidget  
- `section_link_clicked(str)` - клик по внутренней ссылке

## Добавление нового языка

1. Добавьте в `config.py`:
```python
class Language(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    GERMAN = "de"  # новый язык
```

2. Добавьте перевод в `guide_content.py`:
```python
GUIDE_CONTENT = {
    "de": {
        "introduction": {
            "title": "Einführung",
            # ...
        }
    }
}
```

3. Обновите селектор в `guide_sidebar.py`:
```python
self.language_combo.addItem("Deutsch", Language.GERMAN)
```

## Интеграция с основным приложением

В `main_window.py`:
```python
from src.gui.user_guide_tab import UserGuideTab

class MainWindow(QMainWindow):
    def __init__(self):
        # ...
        self.user_guide_tab = UserGuideTab(self)
        self.tabs.addTab(self.user_guide_tab, "User Guide")
```
