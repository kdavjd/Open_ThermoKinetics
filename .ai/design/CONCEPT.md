# Open ThermoKinetics — Design System Concept

> **Версия:** 1.0  |  **Дата:** 2026-02-19  |  **Стиль:** Industrial/Technical

---

## 1. Цветовые контрасты (WCAG AA проверка)

Минимум 4.5:1 для основного текста; 3:1 для крупного текста (≥18px / ≥14px bold).

### Light Theme

| Пара                              | Контраст | WCAG AA |
|-----------------------------------|----------|---------|
| `text_primary` / `bg_base`        | 16.1:1   | ✅      |
| `text_secondary` / `bg_base`      | 6.5:1    | ✅      |
| `text_secondary` / `bg_surface`   | 5.9:1    | ✅      |
| `text_muted` / `bg_base`          | 2.4:1    | ⚠️ placeholder only |
| `accent` / `bg_base`              | 4.7:1    | ✅      |
| white / `accent_hover` (#1D4ED8)  | 6.0:1    | ✅ кнопки |
| white / `accent` (#2563EB)        | 4.5:1    | ✅ AA large |
| `error` / `bg_base`               | 5.9:1    | ✅      |

> `text_muted` используется **только** для placeholder-текста и иконок — не для важной информации.

### Dark Theme

| Пара                              | Контраст | WCAG AA |
|-----------------------------------|----------|---------|
| `text_primary` / `bg_base`        | 17.1:1   | ✅      |
| `text_secondary` / `bg_surface`   | 7.2:1    | ✅      |
| `accent` / `bg_surface`           | 4.9:1    | ✅      |

---

## 2. QSS Naming Conventions

### Object Names (`setObjectName`)

| Компонент               | Object Name         | Применение                     |
|-------------------------|---------------------|--------------------------------|
| Основная кнопка         | `btn_primary`       | Главное действие               |
| Вторичная кнопка        | `btn_secondary`     | Альтернативное действие        |
| Деструктивная кнопка    | `btn_danger`        | Удаление, сброс                |
| Малая кнопка            | `btn_small`         | Компактные панели              |
| Sidebar дерево          | `sidebar_tree`      | Навигация файлов/серий         |
| Sub-sidebar панель      | `sub_sidebar_panel` | Панели анализа                 |
| Консольный виджет       | `console_output`    | Логи, вывод расчётов           |
| Заголовок секции        | `section_header`    | Разделители групп              |
| Ввод числа              | `input_numeric`     | QSpinBox, QDoubleSpinBox       |

### QSS Селекторы

```qss
/* По object name */
QPushButton#btn_primary { ... }
QPushButton#btn_primary:hover { ... }
QPushButton#btn_primary:disabled { ... }

/* По иерархии (избегать, предпочитать object names) */
QWidget#sub_sidebar_panel QLabel { ... }
```

### Запрещено

- `setStyleSheet()` непосредственно в widget-файлах
- Inline строки-стили в бизнес-логике
- Жёстко заданные цвета вне токенов

---

## 3. Компонент: Sidebar / Sub-sidebar

**Виджеты:** `QTreeView`, `QTreeWidget`, `QFrame`

| Состояние      | bg                 | border              | text              |
|----------------|--------------------|---------------------|-------------------|
| Normal         | `bg_surface`       | `border`            | `text_primary`    |
| Hover          | `bg_elevated`      | `border`            | `text_primary`    |
| Selected       | `accent_light`     | `accent`            | `accent`          |
| Selected+Focus | `accent_light`     | `accent`            | `accent`          |
| Disabled       | `bg_surface`       | `border`            | `text_muted`      |

Отступы элементов дерева: padding `4px 8px`. Иконки: `16x16px`.
Заголовки секций sidebar: `section_header` — bg `bg_surface`, text `text_secondary`, 12px SemiBold.

---

## 4. Компонент: Кнопки (QPushButton)

| Вариант       | Object Name     | bg (normal)    | bg (hover)     | bg (pressed)   | text      | border        |
|---------------|-----------------|----------------|----------------|----------------|-----------|---------------|
| Primary       | `btn_primary`   | `accent`       | `accent_hover` | `#1E40AF`      | white     | none          |
| Secondary     | `btn_secondary` | `bg_elevated`  | `border`       | `border_strong`| `text_primary` | `border_strong` |
| Danger        | `btn_danger`    | `#FEE2E2`      | `#FECACA`      | `#FCA5A5`      | `error`   | `#FECACA`     |
| Small         | `btn_small`     | `bg_elevated`  | `border`       | —              | `text_secondary` | `border` |

Радиус: `radius_sm` (3px). Высота: primary/secondary `28px`, small `22px`.
Отступы: `4px 12px` (primary), `4px 8px` (small).

---

## 5. Компонент: Формы (QLineEdit, QComboBox, QSpinBox, QCheckBox)

**QLineEdit / QSpinBox / QDoubleSpinBox:**

| Состояние | bg             | border          | text           |
|-----------|----------------|-----------------|----------------|
| Normal    | `bg_base`      | `border`        | `text_primary` |
| Focus     | `bg_base`      | `accent`        | `text_primary` |
| Disabled  | `bg_surface`   | `border`        | `text_muted`   |
| Error     | `#FEF2F2`      | `error`         | `text_primary` |

Высота: `24px`. Border-radius: `radius_sm`. Placeholder: `text_muted`.

**QComboBox:** аналогично QLineEdit + стрелка: `▼` цвет `text_secondary`.

**QCheckBox:** размер индикатора `14x14px`, check-mark цвет `accent`, border `border_strong`.

---

## 6. Компонент: Консоль (ConsoleWidget)

Шрифт: `JetBrains Mono, Consolas, monospace`, 10px.
bg: `bg_base` (light) / `#0D1117` (dark).
Цветовая дифференциация вывода (через `QTextCharFormat`, не QSS):

| Тип          | Цвет hex  |
|--------------|-----------|
| INFO         | `text_secondary` |
| SUCCESS      | `success` |
| WARNING      | `warning` |
| ERROR        | `error`   |
| DEBUG        | `text_muted` |

---

## 7. Компонент: Основное окно (QMainWindow, QTabWidget)

**QTabBar:**

| Состояние  | bg             | border-bottom   | text              |
|------------|----------------|-----------------|-------------------|
| Normal     | `bg_surface`   | `border`        | `text_secondary`  |
| Hover      | `bg_elevated`  | `border`        | `text_primary`    |
| Selected   | `bg_base`      | `accent` (2px)  | `text_primary`    |

Высота вкладки: `32px`. Отступы: `0 16px`.

**QSplitter handle:** ширина `1px`, цвет `border`. При hover: `border_strong`.

**QScrollBar:** ширина `8px`, трек `bg_surface`, thumb `border_strong`, hover thumb `text_muted`.

---

## 8. Применение стилей — порядок загрузки

```python
# src/gui/__main__.py
def load_theme(app: QApplication, theme: str = "light") -> None:
    qss_parts = [
        f"src/gui/styles/{theme}.qss",           # базовая тема
        "src/gui/styles/components/sidebar.qss",
        "src/gui/styles/components/buttons.qss",
        "src/gui/styles/components/forms.qss",
        "src/gui/styles/components/console.qss",
    ]
    combined = "\n".join(_read_qss(p) for p in qss_parts)
    app.setStyleSheet(combined)
```

Конкатенация → единый `setStyleSheet` на `QApplication`. Компонентные файлы переопределяют базовую тему через более специфичные селекторы (object name > тип виджета).
