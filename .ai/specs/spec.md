# Plot Canvas — интеграция в дизайн-систему

> **Дата создания:** 2026-02-23
> **Ветка:** `feature/plot-canvas-design-system`
> **Статус:** 🟡 В работе
> **IEEE 29148 Score:** 93/100
> **Коммит ТЗ:** `b9baee5`

---

## Workflow выполнения

| Шаг | Действие            | Навык              | Статус      |
| --- | ------------------- | ------------------ | ----------- |
| а   | Создание ТЗ + Ветка | —                  | ✅ Завершён  |
| б   | Реализация          | `spec-implementer` | ⬜ Не начат  |
| в   | Написание тестов    | `test-writer`      | ❌ Не начат  |
| г   | GUI тестирование    | `gui-testing`      | ❌ Не начат  |
| д   | Мерж                | `merge-helper`     | ❌ Не начат  |

**Следующий шаг:** б (Реализация) → `spec-implementer`

---

## Видение

PlotCanvas синхронно переключается между light/dark темами вместе с QSS-темой приложения. Отображает научные графики **без внешней зависимости scienceplots** — весь базовый стиль задаётся через `BASE_STYLE_PARAMS` (matplotlib rcParams). Используется собственная научная палитра (адаптированная NPG с улучшенной видимостью на тёмном фоне). Дизайн строится в два слоя:

1. **Слой BASE_STYLE_PARAMS** — глобальные базовые параметры matplotlib (применяются один раз при импорте через `plt.rcParams.update()`): шрифт, размеры, сетка, видимость шипов, отступы
2. **Слой apply_theme()** — цветовой оверрайд поверх базового стиля: фоны, текст, оси, легенда, аннотации — всё тема-зависимое

**Ключевые требования:**
- scienceplots **удаляется** из зависимостей: import убирается из `plot_canvas.py`, пакет убирается из `pyproject.toml`
- `plt.style.use()` заменяется на `plt.rcParams.update(PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS)`
- `PlotCanvas.changeEvent()` ловит `QEvent.StyleChange` → вызывает `apply_theme()`
- `apply_theme()` обновляет ВСЕ существующие matplotlib-художники (artists) БЕЗ очистки данных
- `NavigationToolbar2QT` получает QSS-стилизацию + программное обновление иконок через `_icon()`
- `load_theme()` вызывается **до** создания `MainWindow`, чтобы тулбар создавался с правильной палитрой
- Время перерисовки при смене темы ≤ 300 мс (до 10 линий)
- Смена темы при активных drag-anchors не вызывает crash

---

## Удаление scienceplots

**Решение:** заменяем `plt.style.use(["science", "no-latex", "nature", "grid"])` на явные `plt.rcParams.update(BASE_STYLE_PARAMS)`.

| Что делал scienceplots | Чем заменяем |
|------------------------|--------------|
| Типографика (засечки, размеры шрифтов) | `BASE_STYLE_PARAMS`: `font.family`, `font.size`, `axes.titlesize` и т.д. |
| `no-latex` — без LaTeX-рендеринга | `"text.usetex": False` в BASE_STYLE_PARAMS |
| Стиль `grid` — отображение сетки | `"axes.grid": True` в BASE_STYLE_PARAMS |
| `nature` — NPG цвета как базовый cycle | Явный `NPG_PALETTE` через `cycler` в `apply_theme()` |
| Параметры линий (`linewidth` и т.д.) | `"lines.linewidth": 1.0` в BASE_STYLE_PARAMS |
| Скрытие верхнего/правого шипа | `"axes.spines.top": False`, `"axes.spines.right": False` |

Graceful degradation больше не нужна — зависимость от scienceplots полностью отсутствует.

---

## Функциональные требования

| ID    | Требование                                                                                          | Приоритет  |
| ----- | --------------------------------------------------------------------------------------------------- | ---------- |
| FR-01 | PlotCanvas переопределяет `changeEvent()`, при `QEvent.StyleChange` вызывает `apply_theme()`        | Must-have  |
| FR-02 | `PlotCanvasConfig.NPG_PALETTE` содержит 10 цветов (адаптированная NPG), применяется через `prop_cycle` | Must-have  |
| FR-03 | light: bg `#FFFFFF`, текст `#0F172A`, сетка `#E2E8F0`; dark: bg `#0F172A`, текст `#F8FAFC`, сетка `#334155` | Must-have  |
| FR-04 | `apply_theme()` обновляет все существующие artists: figure, axes, spines, ticks, labels, title, grid, legend, patches, texts | Must-have  |
| FR-05 | Аннотации используют `ANNOTATION_THEME_PARAMS[self._current_theme]` вместо хардкода `"white"`/`"black"` | Must-have  |
| FR-06 | `load_theme()` вызывается в `__main__.py` при запуске, применяя сохранённую тему                    | Must-have  |
| FR-07 | `plot.qss` содержит стили для `NavigationToolbar2QT`, `NavigationToolbar2QT QToolButton` и `#plot_container` | Should     |
| FR-08 | scienceplots **удаляется** из зависимостей: import убирается из `plot_canvas.py`, пакет убирается из `pyproject.toml`; `BASE_STYLE_PARAMS` заменяет его функциональность | Must-have  |
| FR-09 | `apply_theme()` вызывает `_rebuild_toolbar_icons()` для программного обновления иконок тулбара при смене темы | Should     |
| FR-10 | `load_theme()` в `__main__.py` вызывается **до** `MainWindow(...)`, чтобы тулбар создавался с правильной `QPalette.Window` | Must-have  |
| FR-11 | `PlotCanvasConfig.BASE_STYLE_PARAMS` содержит все параметры, ранее предоставляемые scienceplots (font, grid, spines, linewidth, text.usetex) | Must-have  |
| FR-12 | Все 10 цветов `NPG_PALETTE` имеют достаточный контраст на dark bg `#0F172A` (визуально различимы) | Must-have  |

---

## Архитектура решения

### Два слоя стилизации

```
Слой 1: BASE_STYLE_PARAMS (один раз при импорте)
  plt.rcParams.update(PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS)
  ↓ задаёт: типографику, grid presence, linewidth defaults, no-latex, скрытие шипов

Слой 2: apply_theme() (при каждой смене темы)
  rcParams.update(THEME_PARAMS[theme])     ← будущие plot-вызовы
  + явное обновление existing artists      ← текущий контент
```

### Цепочка смены темы (Qt-native)

```
QApplication.setStyleSheet(qss)       # load_theme() в __main__.py или при смене темы
  └── Qt рассылает QEvent.StyleChange всем виджетам
        └── PlotCanvas.changeEvent()  # переопределён
              └── apply_theme(get_saved_theme())
                    ├── rcParams.update(THEME_PARAMS[theme])
                    ├── figure.set_facecolor(...)
                    ├── axes.set_facecolor(...)
                    ├── spines → set_edgecolor(...)
                    ├── tick_params(colors=...)
                    ├── axis labels set_color(...)
                    ├── axes.title set_color(...)
                    ├── grid(color=...)
                    ├── legend frame + texts
                    ├── patches (annotation backgrounds)
                    ├── texts (annotation text color)
                    └── canvas.draw_idle()
```

`BaseSignals` не затрагивается. `FigureCanvasQTAgg` → `QWidget` → получает `QEvent.StyleChange` автоматически.

### Базовые параметры стиля (BASE_STYLE_PARAMS)

```python
BASE_STYLE_PARAMS = {
    # Типографика
    "font.family":        "sans-serif",
    "font.size":          9,
    "axes.titlesize":     10,
    "axes.labelsize":     9,
    "xtick.labelsize":    8,
    "ytick.labelsize":    8,
    "legend.fontsize":    8,
    # Линии
    "lines.linewidth":    1.0,
    # Сетка
    "axes.grid":          True,
    "grid.alpha":         0.4,
    "grid.linewidth":     0.5,
    # Шипы (убираем верхний и правый — научный стиль)
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    # Прочее
    "figure.autolayout":  True,
    "text.usetex":        False,
    "axes.axisbelow":     True,   # сетка под данными
}
```

### Палитра (адаптированная NPG с видимостью на dark bg)

Цвета 4, 6, 8, 9, 10 заменены на более яркие версии — оригинальные NPG-цвета (#3C5488, #8491B4, #DC0000, #7E6148, #B09C85) слишком тёмные для bg `#0F172A`.

```python
NPG_PALETTE = [
    "#E64B35",  # coral red      (NPG-original)
    "#4DBBD5",  # sky cyan       (NPG-original)
    "#00A087",  # emerald teal   (NPG-original)
    "#7B9AFF",  # periwinkle     (brightened from #3C5488)
    "#F39B7F",  # peach salmon   (NPG-original)
    "#B0BCF5",  # soft lavender  (brightened from #8491B4)
    "#91D1C2",  # mint           (NPG-original)
    "#FF6B6B",  # bright coral   (brightened from #DC0000)
    "#C4956A",  # warm caramel   (brightened from #7E6148)
    "#FBBF24",  # amber          (replaces muted beige #B09C85)
]
```

*Все 10 цветов имеют luminance ≥ 35% и различимы на тёмном фоне #0F172A.*

### Параметры matplotlib по теме (THEME_PARAMS)

```python
THEME_PARAMS = {
    "light": {
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor":   "#FFFFFF",
        "axes.edgecolor":   "#0F172A",
        "axes.labelcolor":  "#0F172A",
        "xtick.color":      "#0F172A",
        "ytick.color":      "#0F172A",
        "text.color":       "#0F172A",
        "grid.color":       "#E2E8F0",
        "legend.facecolor": "#F8FAFC",
        "legend.edgecolor": "#E2E8F0",
    },
    "dark": {
        "figure.facecolor": "#0F172A",
        "axes.facecolor":   "#0F172A",
        "axes.edgecolor":   "#F8FAFC",
        "axes.labelcolor":  "#F8FAFC",
        "xtick.color":      "#F8FAFC",
        "ytick.color":      "#F8FAFC",
        "text.color":       "#F8FAFC",
        "grid.color":       "#334155",
        "legend.facecolor": "#1E293B",
        "legend.edgecolor": "#334155",
    },
}
```

### Параметры аннотаций по теме (ANNOTATION_THEME_PARAMS)

```python
ANNOTATION_THEME_PARAMS = {
    "light": {
        "facecolor":  "#F8FAFC",
        "edgecolor":  "#E2E8F0",
        "text_color": "#0F172A",
    },
    "dark": {
        "facecolor":  "#1E293B",
        "edgecolor":  "#334155",
        "text_color": "#F8FAFC",
    },
}
```

*Заменяют хардкод `"white"` / `"black"` из `MODEL_FIT_ANNOTATION_CONFIG` / `MODEL_FREE_ANNOTATION_CONFIG` в `app_settings.py`.*

---

## План реализации

### Этап 1: ~~BaseSignals~~ — ОТМЕНЁН

**Статус:** ✅ Отменён

**Причина:** Отдельный сигнал не нужен. Qt автоматически рассылает `QEvent.StyleChange` всем виджетам при `app.setStyleSheet()`.

---

### Этап 2: PlotCanvasConfig — расширение конфига (~75 строк)

**Статус:** ⬜ Не начат

**Цель:** Вынести все тема-зависимые, палитрные константы и базовые стилевые параметры в конфиг. Заменить `PLOT_STYLE: ["science", ...]` на `BASE_STYLE_PARAMS` + пустой `PLOT_STYLE`.

**Задачи:**
- [ ] Изменить `PLOT_STYLE` → пустой список `[]` (scienceplots не используется)
- [ ] Добавить поле `BASE_STYLE_PARAMS: Dict[str, object]` — базовые matplotlib rcParams (font, grid, spines, linewidth, text.usetex)
- [ ] Добавить поле `NPG_PALETTE: List[str]` — 10 цветов адаптированной NPG (с яркими заменами #4, #6, #8, #9, #10)
- [ ] Добавить поле `THEME_PARAMS: Dict[str, dict]` — matplotlib rcParams для light/dark (10 ключей каждый)
- [ ] Добавить поле `ANNOTATION_THEME_PARAMS: Dict[str, dict]` — facecolor/edgecolor/text_color для light/dark

**Файлы:**
- `src/gui/main_tab/plot_canvas/config.py` (modify)

**Критерий приёмки:**
- `PLOT_CANVAS_CONFIG.PLOT_STYLE == []`
- `PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS["axes.grid"] == True`
- `PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS["text.usetex"] == False`
- `PLOT_CANVAS_CONFIG.NPG_PALETTE` — список из 10 hex-строк, все начинаются с `#`
- `PLOT_CANVAS_CONFIG.THEME_PARAMS["light"]["figure.facecolor"] == "#FFFFFF"`
- `PLOT_CANVAS_CONFIG.THEME_PARAMS["dark"]["figure.facecolor"] == "#0F172A"`
- `PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS["dark"]["facecolor"] == "#1E293B"`

---

### Этап 3: PlotStylingMixin — apply_theme с полным обходом artists (~100 строк)

**Статус:** ⬜ Не начат

**Цель:** Полная стилизация текущего matplotlib-контента без потери данных.

**Алгоритм `apply_theme(self, theme: str)`:**

```
1. params = THEME_PARAMS[theme]
2. matplotlib.rcParams.update(params)                         # будущие plot-вызовы
3. matplotlib.rcParams['axes.prop_cycle'] = cycler(color=NPG_PALETTE)
4. self.figure.set_facecolor(params['figure.facecolor'])
5. self.axes.set_facecolor(params['axes.facecolor'])
6. for spine in self.axes.spines.values():
       spine.set_edgecolor(params['axes.edgecolor'])
7. self.axes.tick_params(colors=params['xtick.color'], which='both')
8. self.axes.xaxis.label.set_color(params['axes.labelcolor'])
9. self.axes.yaxis.label.set_color(params['axes.labelcolor'])
10. self.axes.title.set_color(params['text.color'])
11. self.axes.grid(color=params['grid.color'])               # обновить цвет сетки
12. legend = self.axes.get_legend()
    if legend:
        legend.get_frame().set_facecolor(params['legend.facecolor'])
        legend.get_frame().set_edgecolor(params['legend.edgecolor'])
        for text in legend.get_texts():
            text.set_color(params['text.color'])
13. ann_params = ANNOTATION_THEME_PARAMS[theme]
    for patch in self.axes.patches:
        patch.set_facecolor(ann_params['facecolor'])
        patch.set_edgecolor(ann_params['edgecolor'])
    for text in self.axes.texts:
        text.set_color(ann_params['text_color'])
14. self._current_theme = theme
15. self.canvas.draw_idle()
```

**Задачи:**
- [ ] Реализовать `apply_theme(self, theme: str)` по алгоритму выше с импортом `cycler` из `cycler`
- [ ] Обновить `add_model_fit_annotation()`: использовать `PLOT_CANVAS_CONFIG.ANNOTATION_THEME_PARAMS[self._current_theme]` вместо `MODEL_FIT_ANNOTATION_CONFIG["facecolor"]` / `["edgecolor"]`
- [ ] Обновить `add_model_free_annotation()`: аналогично
- [ ] Инициализировать `self._current_theme: str = "light"` через `getattr(self, '_current_theme', 'light')` fallback

**Файлы:**
- `src/gui/main_tab/plot_canvas/plot_styling.py` (modify)

**Критерий приёмки:**
- После `apply_theme("dark")`: `self.figure.get_facecolor()` → RGBA для `#0F172A`
- Существующие линии на графике не удаляются
- Аннотация-прямоугольник на `apply_theme("dark")` получает `facecolor="#1E293B"`
- Легенда (если есть) обновляет цвета
- Все spines меняют цвет

---

### Этап 4: PlotCanvas — удаление scienceplots + changeEvent + инициализация темы (~45 строк)

**Статус:** ⬜ Не начат

**Цель:** Удалить scienceplots как зависимость из кода; PlotCanvas реагирует на смену темы через Qt-native механизм.

**Задачи:**
- [ ] Удалить строку `import scienceplots  # noqa pylint: disable=unused-import` из `plot_canvas.py`
- [ ] Заменить `plt.style.use(PLOT_CANVAS_CONFIG.PLOT_STYLE)` на `plt.rcParams.update(PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS)` (module-level, после импортов)
- [ ] Удалить `"scienceplots>=2.1.1"` из `pyproject.toml` (секция `dependencies`)
- [ ] Добавить импорты: `from PyQt6.QtCore import QEvent` и `from src.gui.styles import get_saved_theme`
- [ ] В `__init__` после `self.mock_plot()`:
  - `self._current_theme = get_saved_theme()`
  - `self.apply_theme(self._current_theme)`
- [ ] Переопределить `changeEvent(self, event: QEvent)`:
  ```python
  def changeEvent(self, event):
      if event.type() == QEvent.Type.StyleChange:
          self.apply_theme(get_saved_theme())
      super().changeEvent(event)
  ```

**Файлы:**
- `src/gui/main_tab/plot_canvas/plot_canvas.py` (modify)
- `pyproject.toml` (modify — удалить scienceplots из dependencies)

**Критерий приёмки:**
- `import scienceplots` отсутствует в `plot_canvas.py`
- `plt.rcParams.update(PLOT_CANVAS_CONFIG.BASE_STYLE_PARAMS)` присутствует на module-level
- `scienceplots` отсутствует в `pyproject.toml`
- После `app.setStyleSheet(dark_qss)` при `settings.setValue("theme", "dark")` — холст перерисовывается тёмным
- Активные anchors не crash при смене темы (changeEvent не трогает anchor_group)
- Изменения в `main_tab.py` и `main_window.py` **не требуются**

---

### Этап 5: __main__.py + plot.qss — интеграция и NavigationToolbar (~50 строк)

**Статус:** ⬜ Не начат

**Цель:** Подключить `load_theme()` к запуску (уже частично есть); стилизовать toolbar и контейнер; добавить `_rebuild_toolbar_icons`.

#### __main__.py

**Проверка:** `load_theme(app, get_saved_theme())` уже вызывается **после** `QApplication(sys.argv)` но **до** `window.show()`. Нужно убедиться, что он вызывается **до** `MainWindow(...)`.

**Задачи:**
- [ ] Переместить `load_theme(app, get_saved_theme())` **перед** `window = MainWindow(signals=signals)` (если ещё не так)
- [ ] Убрать `load_fonts()` + `load_theme()` из после-MainWindow зоны, разместить оба ДО MainWindow

#### plot.qss — NavigationToolbar2QT и контейнер

**Иконки — как работает auto-recolor (matplotlib 3.10+):**

Метод `_icon()` загружает PNG (чёрные иконки на прозрачном фоне), читает `palette().color(QPalette.Window)` и если luminance < 128 → перекрашивает иконки в foreground цвет.

**Решение для runtime-смены:** `_rebuild_toolbar_icons()` в `PlotCanvas`:

```python
_TOOLBAR_ICON_MAP = {
    "Home": "home.png", "Back": "back.png", "Forward": "forward.png",
    "Pan": "move.png", "Zoom": "zoom_to_rect.png",
    "Subplots": "subplots.png", "Save": "filesave.png",
}

def _rebuild_toolbar_icons(self):
    try:
        for action in self.toolbar.actions():
            filename = _TOOLBAR_ICON_MAP.get(action.text())
            if filename:
                action.setIcon(self.toolbar._icon(filename))
    except AttributeError:
        pass  # graceful degradation for older matplotlib versions
```

**Задачи:**
- [ ] Добавить в `plot.qss` стили для `#plot_container`, `NavigationToolbar2QT`, `NavigationToolbar2QT QToolButton` (hover, pressed/checked), `NavigationToolbar2QT QLabel`
- [ ] Определить `_TOOLBAR_ICON_MAP` (module-level dict) в `plot_canvas.py`
- [ ] Реализовать `_rebuild_toolbar_icons(self)` с `try/except AttributeError` защитой
- [ ] Вызвать `self._rebuild_toolbar_icons()` в конце `apply_theme()`

**Файлы:**
- `src/gui/__main__.py` (verify/modify — `load_theme()` ДО `MainWindow()`)
- `src/gui/styles/components/plot.qss` (modify — добавить NavigationToolbar2QT QSS и `#plot_container`)
- `src/gui/main_tab/plot_canvas/plot_canvas.py` (modify — `_TOOLBAR_ICON_MAP` + `_rebuild_toolbar_icons`)

**QSS для plot.qss:**
```css
/* Plot container */
QWidget#plot_container {
    background-color: {{bg_base}};
    border: 1px solid {{border}};
    border-radius: {{radius_md}};
}

/* NavigationToolbar2QT — matplotlib toolbar */
NavigationToolbar2QT {
    background-color: {{bg_surface}};
    border-bottom: 1px solid {{border}};
    padding: 2px 4px;
    spacing: 2px;
}

NavigationToolbar2QT QToolButton {
    background-color: transparent;
    color: {{text_primary}};
    border: 1px solid transparent;
    border-radius: {{radius_sm}};
    padding: 3px;
    min-width: 22px;
    min-height: 22px;
}

NavigationToolbar2QT QToolButton:hover {
    background-color: {{bg_elevated}};
    border-color: {{border}};
}

NavigationToolbar2QT QToolButton:pressed,
NavigationToolbar2QT QToolButton:checked {
    background-color: {{accent_light}};
    border-color: {{accent}};
}

NavigationToolbar2QT QLabel {
    color: {{text_secondary}};
    font-size: 11px;
    background-color: transparent;
}
```

**Критерий приёмки:**
- При запуске с dark-темой: иконки тулбара светлые
- После runtime-смены dark→light: иконки тёмные
- `NavigationToolbar2QT` в dark: фон `#1E293B`, hover `#334155`
- `PlotCanvas.changeEvent()` срабатывает при `load_theme()`

---

## Граничные случаи (Edge Cases)

| Сценарий | Ожидаемое поведение |
|----------|---------------------|
| Смена темы при drag-anchor активен | `changeEvent` не crash; anchors сохраняют позиции (anchor_group не трогается) |
| `apply_theme` вызван до первого `plot_data_from_dataframe` | Параметры применяются к mock_plot; реальные данные появятся с правильной темой |
| Быстрое переключение light→dark→light | Каждый вызов применяется последовательно; предыдущий draw_idle отменяется |
| scienceplots установлен в .venv | Не используется, не импортируется; приложение работает без него |
| BASE_STYLE_PARAMS не полностью покрывает scienceplots | Matplotlib использует свои дефолты — функционально корректно |
| Аннотации отсутствуют | Циклы по `self.axes.patches` и `self.axes.texts` работают с пустыми списками |
| Легенда не отображается | `self.axes.get_legend()` возвращает `None`; блок обновления пропускается |
| apply_theme при MSE-режиме | MSE линия (`color="red"`) — hardcoded; фон и оси обновятся; цвет линии не меняется |
| Иконка тулбара не найдена в `_TOOLBAR_ICON_MAP` | `_rebuild_toolbar_icons` пропускает action; остальные обновляются |
| `_icon()` в matplotlib < 3.10 | `_rebuild_toolbar_icons` защищён `try/except AttributeError` |

---

## Зависимости между этапами

```
Этап 2 (Config: BASE_STYLE_PARAMS, NPG_PALETTE, THEME_PARAMS, ANNOTATION_THEME_PARAMS)
    └── Этап 3 (PlotStylingMixin: apply_theme, обновление аннотаций)
            └── Этап 4 (PlotCanvas: удаление scienceplots, rcParams.update, changeEvent)
                    └── Этап 5 (__main__: load_theme ДО MainWindow; plot.qss: Toolbar QSS; _rebuild_toolbar_icons)
```

---

## Файлы изменений

| Файл | Тип | Этап | Что меняется |
|------|-----|------|--------------|
| `src/gui/main_tab/plot_canvas/config.py` | modify | 2 | `PLOT_STYLE=[]`; + BASE_STYLE_PARAMS, NPG_PALETTE, THEME_PARAMS, ANNOTATION_THEME_PARAMS |
| `src/gui/main_tab/plot_canvas/plot_styling.py` | modify | 3 | + apply_theme(), обновление аннотаций с тема-зависимыми цветами |
| `src/gui/main_tab/plot_canvas/plot_canvas.py` | modify | 4+5 | - scienceplots import; + rcParams.update(BASE_STYLE_PARAMS); + changeEvent(), _current_theme; + _TOOLBAR_ICON_MAP, _rebuild_toolbar_icons |
| `pyproject.toml` | modify | 4 | - scienceplots из dependencies |
| `src/gui/__main__.py` | verify/modify | 5 | load_theme() + load_fonts() **до** MainWindow() |
| `src/gui/styles/components/plot.qss` | modify | 5 | + NavigationToolbar2QT QSS, #plot_container |

**Не затрагиваются:** `main_window.py`, `main_tab.py`, `base_signals.py`, `app_settings.py`

---

## История изменений

| Дата       | Этап | Коммит  | Описание                                                                              |
| ---------- | ---- | ------- | ------------------------------------------------------------------------------------- |
| 2026-02-23 | -    | -       | ТЗ создано (черновик)                                                                 |
| 2026-02-23 | 1    | -       | Этап 1 отменён: theme_changed не нужен, используем changeEvent                        |
| 2026-02-23 | -    | -       | ТЗ переработано: scienceplots, NavigationToolbar2QT, полный обход artists             |
| 2026-02-23 | -    | b9baee5 | ТЗ финализировано: scienceplots **удалён**, BASE_STYLE_PARAMS, NPG_PALETTE улучшена   |
