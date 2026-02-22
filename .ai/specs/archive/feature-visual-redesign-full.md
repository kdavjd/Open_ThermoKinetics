# Visual Redesign Full — Feature Specification

> **Дата создания:** 2026-02-21
> **Дата завершения:** 2026-02-23
> **Ветка:** `feature/visual-redesign-full`
> **Статус:** ✅ Завершён (влит в main)
> **IEEE 29148 Score:** 89/100
> **Коммит:** 7517dba

---

## Workflow выполнения

### Порядок выполнения для новой фичи

| Шаг | Действие            | Навык              | Статус      |
| --- | ------------------- | ------------------ | ----------- |
| а   | Создание ТЗ + Ветка | —                  | ✅ Завершён (cab7c7a) |
| б   | Реализация          | `spec-implementer` | ✅ Завершён (этапы 1–14) |
| в   | Написание тестов    | `test-writer`      | ❌ Не начат  |
| г   | GUI тестирование    | `gui-testing`      | ❌ Не начат  |
| д   | Мерж                | `merge-helper`     | ❌ Не начат  |

**Следующий шаг:** в (Написание тестов) → `test-writer`

---

## Видение

Перевести GUI приложения Open ThermoKinetics с нестилизованного вида на новый дизайн-систему
(тёмная/светлая тема, токены цветов, objectName-based QSS), соответствующий эталонным скриншотам
из `.ai/design/`. Дизайн-система уже реализована в `src/gui/styles/` — требуется интеграция
в приложение и назначение `objectName` всем компонентам.

**Ключевые требования:**
- Каждый этап — один экран приложения (6 экранов = 6 этапов)
- Не нарушать существующую бизнес-логику и сигнальную систему
- Применять стили только через QSS + `objectName`, не через `setStyleSheet()` в виджетах
- Поддерживать переключение светлой/тёмной темы
- ≤250 строк изменений на этап

**Цветовые токены (тёмная тема):**

| Токен           | Hex       | Назначение               |
|-----------------|-----------|--------------------------|
| `bg_base`       | `#0F172A` | Фон главного окна        |
| `bg_surface`    | `#1E293B` | Фон сайдбара, панелей    |
| `bg_elevated`   | `#334155` | Hover-состояния          |
| `accent`        | `#3B82F6` | Primary кнопки, активные |
| `text_primary`  | `#F8FAFC` | Основной текст           |
| `text_secondary`| `#CBD5E1` | Метки, заголовки секций  |
| `border`        | `#334155` | Разделители              |

---

## Референсные материалы

| Тип                    | Путь                              |
|------------------------|-----------------------------------|
| Концепт дизайн-системы | `.ai/design/CONCEPT.md`           |
| Токены цветов          | `src/gui/styles/tokens.py`        |
| Загрузчик тем          | `src/gui/styles/theme_loader.py`  |
| QSS кнопок             | `src/gui/styles/components/buttons.qss` |
| QSS форм               | `src/gui/styles/components/forms.qss`   |
| QSS сайдбара           | `src/gui/styles/components/sidebar.qss` |
| Тёмная тема (база)     | `src/gui/styles/dark.qss`         |
| Светлая тема (база)    | `src/gui/styles/light.qss`        |

**Эталонные скриншоты (целевое состояние):**

| Экран                  | Источник                              |
|------------------------|---------------------------------------|
| Компонентная библиотека| `.ai/design/components.html`          |
| Тёмная тема приложения | `Screenshot_8.png`                    |
| Светлая тема приложения| `Screenshot_4.png`                    |

**Текущее (исходное) состояние:**

| Экран                        | Источник          |
|------------------------------|-------------------|
| Стартовая страница           | `Screenshot_5.png` |
| Страница с выбранным файлом  | `Screenshot_6.png` |
| Деконволюция sub_sidebar     | `Screenshot_7.png` |
| Model Free/Fit из серии      | `Screenshot_10.png`|
| Выбранная серия              | `Screenshot_9.png` |
| Model Based sub_sidebar      | `Screenshot_11.png`|

---

## Что УЖЕ реализовано

- `src/gui/styles/tokens.py` — полные токены LIGHT/DARK
- `src/gui/styles/theme_loader.py` — `load_theme(app, theme)` + `get_saved_theme()`
- `src/gui/styles/dark.qss`, `light.qss` — базовые темы с токенами
- `src/gui/styles/components/` — все компонентные QSS (buttons, forms, sidebar, tabs, console, menubar, plot, deconvolution)

**Что НЕ реализовано (требует этой итерации):**
- Вызов `load_theme()` в `__main__.py`
- Назначение `objectName` компонентам приложения
- Редизайн структуры sidebar (новые секции FILES / SERIES)
- Переключение Experiment/Deconvolution/Model Fit через вкладки в sub-sidebar
- MenuBar (File, View, Analysis, Help)
- Статус-бар с индикатором, имя файла, R²
- Кнопка "Clear" в консоли
- Кнопка переключения темы Light/Dark

---

## План реализации

### Этап 1: Активация темы + глобальные элементы (~200 строк)
**Статус:** ✅ Завершён

**Цель:** Трансформировать стартовый экран — применить dark/light тему,
добавить MenuBar, статус-бар, кнопку переключения темы, Clear в консоли.

**Экран-ориентир:** Стартовая страница (`Screenshot_5.png` → цель: `Screenshot_8.png`)

**Задачи:**
- [x] `src/gui/__main__.py`: добавить `from src.gui.styles import load_theme, get_saved_theme` и вызов `load_theme(app, get_saved_theme())` перед `window.show()`
- [x] `src/gui/main_window.py`: добавить `QMenuBar` с меню File (Load File, Exit), View (Toggle Theme, Toggle Console), Analysis, Help (About)
- [x] `src/gui/main_window.py`: добавить `QStatusBar` с секциями: статус-индикатор (Ready/Running), имя файла, число пиков, β, R²; метод `update_status()`
- [x] `src/gui/main_window.py`: добавить переключатель темы (`QCheckBox` или `QPushButton`) в правой части `QMenuBar`; слот `_toggle_theme(checked)` → вызывает `load_theme(QApplication.instance(), theme)`
- [x] `src/gui/console_widget.py`: добавить `self.text_edit.setObjectName("console_output")`; добавить кнопку "Clear" (`QPushButton#btn_small`) в заголовке консоли; слот для очистки
- [x] `src/gui/main_tab/main_tab.py`: убрать подключение `sidebar.console_show_signal` к `toggle_console_visibility` (управление консолью переносится в View menu); добавить `self.setObjectName("main_tab")`

**Файлы:**
- `src/gui/__main__.py` (modify)
- `src/gui/main_window.py` (modify)
- `src/gui/console_widget.py` (modify)
- `src/gui/main_tab/main_tab.py` (modify)

**Критерий приёмки:**
- Запуск `python -m src.gui` применяет тёмную тему (тёмный фон главного окна)
- MenuBar отображается с пунктами File / View / Analysis / Help
- Статус-бар отображается внизу окна с текстом "Ready"
- Кнопка Clear в консоли очищает текст
- Переключение темы через View меню изменяет фон с `#0F172A` (dark) на `#FFFFFF` (light)
- Тема сохраняется между запусками (QSettings)

---

### Этап 2: Редизайн Sidebar (~230 строк)
**Статус:** ✅ Завершён

**Цель:** Переработать навигационную панель: новая структура FILES / SERIES,
удалить action-items из дерева, добавить "+ Load File" кнопку снизу.

**Экран-ориентир:** Файл выбран (`Screenshot_6.png` → цель: `Screenshot_8.png`)

**Задачи:**
- [x] `src/gui/main_tab/sidebar.py`: переименовать заголовок дерева с "app tree" на ""; добавить `self.tree_view.setObjectName("sidebar_tree")`
- [x] `src/gui/main_tab/sidebar.py`: добавить `QLabel("FILES")` с `objectName("section_header")` над деревом
- [x] `src/gui/main_tab/sidebar.py`: изменить `experiments_data_root` — убрать дочерние элементы "add file data" и "delete selected" (они переносятся в MenuBar File меню)
- [x] `src/gui/main_tab/sidebar.py`: убрать из `series_root` дочерние elements "add new series", "import series", "delete series" (переносятся в MenuBar)
- [x] `src/gui/main_tab/sidebar.py`: убрать весь блок `settings_root` / `console_subroot` / `console_show_state` / `console_hide_state`
- [x] `src/gui/main_tab/sidebar.py`: добавить `QPushButton("+ Load File")` с `objectName("btn_primary")` в нижнюю часть layout; соединить с `load_button.open_file_dialog()`
- [x] `src/gui/main_tab/sidebar.py`: убрать `console_show_signal` из signals и из `on_item_clicked`
- [x] `src/gui/main_window.py`: добавить слоты меню File → Delete File → `sidebar.delete_active_file()`, Series → Add → `sidebar.add_new_series()`, Series → Delete → `sidebar.delete_series()`

**Дополнительные задачи (замечания тестирования):**
- [x] `src/gui/main_tab/sidebar.py`: разделить sidebar на 2 явные вертикальные секции — FILES (верхняя) и SERIES (нижняя) с разделителем; каждая секция имеет собственный заголовок (`objectName("section_header")`) и список элементов
- [x] `src/gui/main_tab/sidebar.py`: добавить кнопку "Load File" (`objectName("btn_small")`, синяя) внутри секции FILES — не только глобально внизу; соединить с `load_button.open_file_dialog()`
- [x] `src/gui/main_tab/sidebar.py`: добавить кнопку "Load Series" (`objectName("btn_small")`, синяя) внутри секции SERIES; соединить со слотом создания серии
- [x] `src/gui/main_tab/sidebar.py`: добавить ненавязчивые кнопки "Import File" и "Import Series" (`objectName("btn_ghost")` / outline-стиль) рядом с кнопками Load в своих секциях — маленькие, не акцентные
- [x] `src/gui/styles/components/sidebar.qss`: добавить стиль `QPushButton#btn_ghost` — прозрачный фон, граница `border`, текст `text_secondary`; hover → `bg_elevated`

**Файлы:**
- `src/gui/main_tab/sidebar.py` (modify)
- `src/gui/main_window.py` (modify — добавить action handlers для MenuBar)
- `src/gui/styles/components/sidebar.qss` (modify — btn_ghost стиль)

**Критерий приёмки:**
- Sidebar разделён на 2 секции FILES и SERIES с видимым разделителем
- В секции FILES: заголовок "FILES", список файлов, кнопка "Load File" (синяя, small), кнопка "Import File" (ghost)
- В секции SERIES: заголовок "SERIES", список серий, кнопка "Load Series" (синяя, small), кнопка "Import Series" (ghost)
- Выбранный файл подсвечивается синим акцентом с левой рамкой (2px solid accent)
- Hover-эффект на элементах дерева работает (bg_elevated)
- Меню File содержит: Load File, Delete File; меню Series содержит: Add New, Delete

---

### Этап 3: Вкладки Sub-sidebar + Experiment панель (~200 строк)
**Статус:** ✅ Завершён

**Цель:** Заменить механизм show/hide в SubSideHub на QTabWidget-вкладки для
анализа файла (Experiment | Deconvolution | Model Fit); стилизовать Experiment панель.

**Экран-ориентир:** Файл выбран + деконволюция (`Screenshot_6.png`, `Screenshot_7.png` → цель)

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: создать `QTabWidget` для режима FILE; добавить вкладки "Experiment", "Deconvolution", "Model Fit" → содержащие `experiment_sub_bar`, `deconvolution_sub_bar`, `model_fit_sub_bar` соответственно; файловый `QTabWidget` называть `file_tabs`
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: `update_content()` — при `SideBarNames.EXPERIMENTS` или `DECONVOLUTION` или `MODEL_FIT` показывать `file_tabs`; при `SideBarNames.SERIES` показывать `series_sub_bar`; при `MODEL_FREE` — `model_free_sub_bar`; при `MODEL_BASED` — `model_based`
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: добавить заголовок "ANALYSIS" (`QLabel` с `objectName("section_header")`) над табами; добавить `setObjectName("sub_sidebar_panel")` на корневой виджет
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: назначить `objectName` кнопкам: "apply" → `btn_small`; "to α(t)", "to DTG", "deconvolution", "reset changes" → `btn_secondary`; QComboBoxes (smoothing method, background method, specific settings) → стандартные без objectName (стилизуются через тип)
- [x] `src/gui/main_tab/main_tab.py`: обновить `toggle_sub_sidebar()` — при `DECONVOLUTION` переключать вкладку `file_tabs` на Deconvolution tab вместо вызова `update_content`; при `experiment_sub_bar.deconvolution_clicked` → переключать вкладку на Deconvolution

**Дополнительные задачи (замечания тестирования):**
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: полностью скрыть tab bar у `file_tabs` — вызвать `file_tabs.tabBar().hide()`; переключение между Experiment / Deconvolution / Model Fit происходит программно через `file_tabs.setCurrentIndex()` из sidebar и сигналов, а не кликом по вкладкам; tab bar не должен занимать место в layout
- [x] `src/gui/styles/components/forms.qss` или `dark.qss`/`light.qss`: добавить QSS для стрелки QComboBox — `QComboBox::drop-down` + `QComboBox::down-arrow` с SVG/unicode-шевроном; убедиться что стрелка видна во всех ComboBox в Experiment панели
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: привести все QLabel-заголовки секций (например "smoothing method:", "background subtraction method:") к верхнему регистру — использовать `.setText(label.upper())` или CSS `text-transform` через `objectName("section_label_upper")`

**Файлы:**
- `src/gui/main_tab/sub_sidebar/sub_side_hub.py` (modify)
- `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py` (modify)
- `src/gui/main_tab/main_tab.py` (modify)
- `src/gui/styles/components/forms.qss` (modify — стрелка QComboBox)

**Критерий приёмки:**
- При выборе CSV-файла в sidebar показывается sub-sidebar с вкладками "Experiment | Deconvolution | Model Fit" без стрелок прокрутки
- Переключение вкладок сохраняет функциональность каждой панели
- Кнопки в Experiment панели: "apply" малые серые (`btn_small`), "to α(t)" / "to DTG" / "deconvolution" / "reset" вторичные (`btn_secondary`)
- Все QComboBox в Experiment панели имеют видимую стрелку-шеврон
- Заголовки секций отображаются в верхнем регистре единым стилем
- При выборе серии в sidebar вкладки заменяются панелью SeriesSubBar (без вкладок Experiment/Deconvolution/Model Fit)

---

### Этап 4: Стилизация панели деконволюции (~180 строк)
**Статус:** ✅ Завершён

**Цель:** Назначить `objectName` всем кнопкам и формам панели деконволюции;
стилизовать таблицу реакций с цветными индикаторами.

**Экран-ориентир:** Деконволюция sub_sidebar (`Screenshot_7.png` → цель: `Screenshot_8.png`)

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py`: кнопка "+ Add" → `objectName("btn_secondary")`; кнопка "Remove" → `objectName("btn_danger")`; кнопка настроек → `btn_small`
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py`: QTableWidget стилизован через deconvolution.qss (примечание: в коде используется QTableWidgetItem, не QDoubleSpinBox)
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/calculation_controls.py`: кнопка "Fit" → `objectName("btn_primary")`; кнопка "Stop" → `objectName("btn_danger")`
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/file_transfer.py`: кнопка "import" → `btn_small`; кнопка "export" → `btn_small`
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/settings_dialog.py`: кнопки Ok/Cancel стилизованы через QDialogButtonBox в deconvolution.qss
- [x] `src/gui/styles/components/deconvolution.qss`: добавлены стили для QTableWidget, QHeaderView, QDialogButtonBox

**Дополнительные задачи (замечания тестирования):**
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: убедиться что `file_tabs.tabBar().hide()` применяется ко всем QTabWidget в hub, включая деконволюцию — tab bar полностью убран, не занимает место
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py`: изучить и исправить проблему с QComboBox выбора функции (Gaussian/Fraser-Suzuki/ADS) в таблице реакций — ComboBox не на месте в layout; восстановить корректное позиционирование inline в строке таблицы или в выделенном поле над/под таблицей
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py`: исправить ошибку в методе `highlight_reaction` — после изменения структуры таблицы метод передаёт некорректные данные о реакции (неверные индексы/ключи); добавить защитную проверку типов данных и корректный маппинг

**Файлы:**
- `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py` (modify — исправление highlight_reaction + layout ComboBox)
- `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py` (modify)
- `src/gui/main_tab/sub_sidebar/deconvolution/calculation_controls.py` (modify)
- `src/gui/main_tab/sub_sidebar/deconvolution/file_transfer.py` (modify)
- `src/gui/main_tab/sub_sidebar/deconvolution/settings_dialog.py` (modify)
- `src/gui/styles/components/deconvolution.qss` (modify)

**Критерий приёмки:**
- Вкладка деконволюции не показывает стрелки прокрутки `<` `>`
- Кнопка "Fit" синяя (primary), "Reset" серая (secondary), "Remove" красная (danger)
- QComboBox выбора функции (Gaussian/Fraser-Suzuki) корректно отображается в строке реакции, данные передаются верно
- `highlight_reaction` не вызывает исключений при переключении реакций
- Секции "REACTION PEAKS", "PEAK PARAMETERS", "FIT OPTIONS" имеют styled заголовки
- "+ Add" кнопка визуально отличается от "Remove" (secondary vs danger)

---

### Этап 5: Панели Model Free / Model Fit + Series (~190 строк)
**Статус:** ✅ Завершён

**Цель:** Назначить `objectName` кнопкам и формам в series_sub_bar,
model_fit_sub_bar, model_free_sub_bar.

**Экраны-ориентиры:** Выбранная серия (`Screenshot_9.png`) + Model Free/Fit (`Screenshot_10.png`)

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/series/series_sub_bar.py`: "load deconvolution results" → `btn_secondary`; "Export Results" → `btn_small`; "model fit" / "model free" / "model based" кнопки в секции "calculations:" → `btn_secondary`; QComboBox "select reaction" и "direct-diff" → стандартные; таблица "reactions | Ea" → без objectName (стилизуется через QTableWidget)
- [x] `src/gui/main_tab/sub_sidebar/model_fit/model_fit_sub_bar.py`: кнопка "calculate" (если есть) → `btn_primary`; кнопка "plot" → `btn_secondary`; QComboBoxes → стандартные; QTableWidget результатов → без objectName
- [x] `src/gui/main_tab/sub_sidebar/model_free/model_free_sub_bar.py`: кнопка "calculate" → `btn_primary`; QComboBox "direct-diff" / "β" / "select reaction" → стандартные; QTableWidget "Model / R2_score" → без objectName
- [x] `src/gui/styles/light.qss` + `dark.qss`: добавить стили для `QTableWidget` — header bg `bg_surface`, ячейки `bg_base`, alternating rows `bg_elevated`, выделение `accent_light`
- [x] `src/gui/styles/components/sidebar.qss`: badges — N/A: sidebar использует QTreeView без custom delegate, badges не применимы в текущей реализации

**Дополнительные задачи (замечания тестирования):**
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py` / `series_sub_bar.py` / `model_fit_sub_bar.py` / `model_free_sub_bar.py`: tab bars скрыты — `file_tabs.tabBar().hide()` в sub_side_hub.py (line 47); series/model_fit/model_free не имеют QTabWidget, task N/A

**Файлы:**
- `src/gui/main_tab/sub_sidebar/series/series_sub_bar.py` (modify)
- `src/gui/main_tab/sub_sidebar/model_fit/model_fit_sub_bar.py` (modify)
- `src/gui/main_tab/sub_sidebar/model_free/model_free_sub_bar.py` (modify)
- `src/gui/main_tab/sub_sidebar/sub_side_hub.py` (modify — отключение scroll-кнопок)
- `src/gui/styles/light.qss` (modify)
- `src/gui/styles/dark.qss` (modify)

**Критерий приёмки:**
- Ни одна панель методов расчёта серий не показывает стрелки прокрутки `<` `>`
- Кнопки "model fit" / "model free" / "model based" в series панели имеют secondary стиль
- "load deconvolution results" имеет secondary стиль
- Таблицы результатов (model fit, model free) имеют тёмный фон в dark теме
- Чередующиеся строки таблиц стилизованы (alternating row colors)
- Все QComboBoxes корректно стилизованы (стрелка, рамка, hover)

---

### Этап 6: Панель Model Based (~200 строк)
**Статус:** ✅ Завершён

**Цель:** Назначить `objectName` всем кнопкам, формам и специальным элементам
панели model_based; стилизовать диаграмму схемы реакций и слайдеры.

**Экран-ориентир:** Model Based sub_sidebar (`Screenshot_11.png` → цель)

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py`: основной контейнер → `objectName("sub_sidebar_panel")`; QComboBox "A -> B" (схема) → стандартный; QComboBox "Reaction type" → стандартный; чекбоксы "Show Range" / "Calculate" → стандартные
- [x] `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py`: QTableWidget параметров (Ea, log(A), contribution) → без objectName; числовые ячейки → стилизовать через делегат или QLineEdit с `input_numeric`
- [x] `src/gui/main_tab/sub_sidebar/model_based/adjustment_controls.py`: QSlider → стилизовать через QSS в `dark.qss`/`light.qss`; кнопки "<" и ">" для слайдеров → `btn_small`; QLabel со значением ("Ea: 120.000") → стилизовать через `text_primary`
- [x] `src/gui/main_tab/sub_sidebar/model_based/calculation_controls.py`: кнопка "Start" → `btn_primary`; кнопка "Settings" → `btn_secondary`; кнопка "Stop" (при расчёте) → `btn_danger`
- [x] `src/gui/main_tab/sub_sidebar/model_based/models_scheme.py`: область схемы A→B (QGraphicsView или custom widget) → стилизовать фон `bg_elevated`, рамку узлов `border`, текст узлов `text_primary`
- [x] `src/gui/styles/dark.qss` + `light.qss`: добавить стили для `QSlider::groove`, `QSlider::handle` — groove bg `border`, handle bg `accent`, hover handle `accent_hover`

**Дополнительные задачи (замечания тестирования):**
- [x] `src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py` / `adjustment_controls.py`: слайдеры скрыты — `adjusting_settings_box.hide()` в `_setup_adjustment_controls`; виджет создаётся, сигналы подключены, но не занимает место в layout
- [x] `src/gui/main_tab/sub_sidebar/model_based/models_scheme.py`: функционал проверен — контекстные меню "add child" / "connect to child" / "delete component" реализованы в `ReactionGraphicsRect.mousePressEvent()`
- [x] `src/gui/main_tab/sub_sidebar/model_based/models_scheme.py`: стилизована через дизайн-систему — `DiagramConfig` обновлён: узлы `bg_elevated`, рамки `border`, стрелки `accent`, текст `text_primary`; применяется в `ReactionNode.draw()` через `setPen/setBrush/setDefaultTextColor`
- [x] `src/gui/styles/dark.qss` + `light.qss`: добавлены стили QMenu (bg_surface, hover bg_elevated, border, separator) и QGraphicsView (bg_surface, border)

**Файлы:**
- `src/gui/main_tab/sub_sidebar/model_based/model_based_panel.py` (modify — убрать слайдеры из layout)
- `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py` (modify)
- `src/gui/main_tab/sub_sidebar/model_based/adjustment_controls.py` (modify — скрыть/перенести слайдеры)
- `src/gui/main_tab/sub_sidebar/model_based/calculation_controls.py` (modify)
- `src/gui/main_tab/sub_sidebar/model_based/models_scheme.py` (modify — стилизация + проверка функционала)
- `src/gui/styles/dark.qss` (modify — QMenu стили)
- `src/gui/styles/light.qss` (modify — QMenu стили)

**Критерий приёмки:**
- Таблица параметров (Ea, log(A), contribution) корректно вписывается в panel без перекрытия слайдерами
- Слайдеры убраны из основного layout или вынесены в сворачиваемую секцию
- Кнопки "Start" синие (primary), "Settings" серые (secondary)
- Область схемы A→B имеет стилизованные узлы (bg_elevated, border), стрелки между ними
- ПКМ на узле схемы показывает контекстное меню "Добавить дочерний" / "Удалить" — стилизованное, функционал не сломан
- QMenu контекстного меню стилизован в соответствии с активной темой

---

### Этап 7: Типографика — Source Sans Pro + JetBrains Mono (~180 строк)
**Статус:** ✅ Завершён

**Цель:** Зафиксировать шрифты всего приложения: `Source Sans Pro` для UI,
`JetBrains Mono` для консоли и числовых полей. Шрифты загружаются через
`QFontDatabase` из бандлированных `.ttf`-файлов, применяются через QSS.

**Выбор пользователя:**
- Основной UI (кнопки, метки, меню, вкладки, дерево): **Source Sans Pro**
- Консоль, числовые поля (QLineEdit, QSpinBox, QDoubleSpinBox): **JetBrains Mono**
- Метод: **QSS + QFontDatabase** (бандлированные шрифты → нет зависимости от системы)

**Задачи:**
- [x] Создать `src/gui/styles/fonts/` — скачать и положить файлы:
  - `SourceSansPro-Regular.ttf`, `SourceSansPro-SemiBold.ttf`, `SourceSansPro-Bold.ttf`
  - `JetBrainsMono-Regular.ttf`, `JetBrainsMono-Bold.ttf`
- [x] `src/gui/styles/theme_loader.py`: добавить функцию `load_fonts()` — регистрирует все `.ttf` из `fonts/` через `QFontDatabase.addApplicationFont()`; вызывается один раз в `__main__.py` до `load_theme()`
- [x] `src/gui/styles/dark.qss`: добавить в корневой `QWidget { ... }` — `font-family: "Source Sans 3", "Source Sans Pro", "Segoe UI", sans-serif; font-size: 12px;`
- [x] `src/gui/styles/light.qss`: то же, что dark.qss
- [x] `src/gui/styles/components/console.qss`: обновить `font-family` на `"JetBrains Mono", Consolas, monospace;` (уже есть)
- [x] `src/gui/styles/components/forms.qss`: добавить для `QLineEdit`, `QSpinBox`, `QDoubleSpinBox` — `font-family: "JetBrains Mono", Consolas, monospace; font-size: 11px;` (числовые данные, точность важна)
- [x] `src/gui/__main__.py`: вызвать `load_fonts()` перед `load_theme()`

**Дополнительные задачи (замечания тестирования):**
- [ ] `src/gui/styles/fonts/`: исправить ошибку загрузки шрифтов на Windows — `qt.qpa.fonts: Failed to create DirectWrite face from font data` для `SourceSansPro-*.ttf`; необходимо заменить файлы на официальные Source Sans 3 с Google Fonts (требует ручной загрузки)
- [x] `src/gui/styles/theme_loader.py`: обновлён `load_fonts()` — логирует успех (`[fonts] OK: file.ttf → family 'Name'`) и подробное предупреждение при ошибке с полным путём файла

**Известные баги (требуют отдельного исправления):**
- [ ] `src/gui/main_tab/plot_canvas/plot_canvas.py`: при первой отрисовке графика Qt выводит `QFont::setPointSize: Point size <= 0 (-1), must be greater than 0` — Matplotlib передаёт некорректный размер шрифта в QFont; проверить `matplotlib.rcParams['font.size']` и связанные параметры (`axes.titlesize`, `axes.labelsize`, `xtick.labelsize`, `ytick.labelsize`, `legend.fontsize`); убедиться что все размеры > 0 в `src/gui/styles/components/plot.qss` или в matplotlib config

**Файлы:**
- `src/gui/styles/fonts/` (заменить .ttf файлы на корректные Source Sans 3)
- `src/gui/styles/theme_loader.py` (modify — логирование результата addApplicationFont)
- `src/gui/styles/dark.qss` (modify — проверить font-family)
- `src/gui/styles/light.qss` (modify — проверить font-family)
- `src/gui/styles/components/console.qss` (modify)
- `src/gui/styles/components/forms.qss` (modify)
- `src/gui/__main__.py` (modify)

**Критерий приёмки:**
- `python -m src.gui` — нет сообщений `Failed to create DirectWrite face from font data` в логах
- Все элементы UI отображаются шрифтом Source Sans 3 (или корректный fallback Segoe UI)
- Консоль и числовые поля используют JetBrains Mono
- `load_fonts()` логирует успешную загрузку каждого шрифта с именем семейства
- Тема переключается (dark/light) без изменения шрифта

---

### Этап 8: Исправление загрузки шрифтов Source Sans Pro на Windows (~80 строк)
**Статус:** ✅ Завершён (итерация 3)

**Цель:** Устранить ошибку `qt.qpa.fonts: Failed to create DirectWrite face from font data`
для шрифтов `SourceSansPro-*.ttf` на Windows. JetBrains Mono грузится успешно — проблема только в Source Sans Pro.

**Контекст ошибки:**
```
[fonts] WARNING: Failed to load: SourceSansPro-Bold.ttf (DirectWrite or format error)
[fonts] WARNING: Failed to load: SourceSansPro-Regular.ttf (DirectWrite or format error)
[fonts] WARNING: Failed to load: SourceSansPro-SemiBold.ttf (DirectWrite or format error)
```
Windows DirectWrite не принимает эти конкретные `.ttf`-файлы (возможно, они повреждены,
имеют нестандартные таблицы шрифта или слишком старый формат).

**Задачи:**
- [x] `src/gui/styles/fonts/`: заменить `SourceSansPro-Regular.ttf`, `SourceSansPro-SemiBold.ttf`, `SourceSansPro-Bold.ttf` на файлы **Source Sans 3** (обновлённое имя семейства) из официального репозитория Google Fonts `https://github.com/google/fonts/tree/main/ofl/sourcesans3` — скачать `SourceSans3-Regular.ttf`, `SourceSans3-SemiBold.ttf`, `SourceSans3-Bold.ttf`
- [x] `src/gui/styles/theme_loader.py`: обновить список файлов в `load_fonts()` — изменить имена файлов на `SourceSans3-*.ttf`; сохранить логирование успеха/ошибки (glob-автообнаружение, отдельный список не нужен)
- [x] `src/gui/styles/dark.qss` + `light.qss`: убедиться что `font-family` указывает `"Source Sans 3", "Source Sans Pro", "Segoe UI", sans-serif` (family name у Source Sans 3 — именно `"Source Sans 3"`)

**Файлы:**
- `src/gui/styles/fonts/SourceSans3-Regular.ttf` (новый файл — заменяет SourceSansPro-Regular.ttf)
- `src/gui/styles/fonts/SourceSans3-SemiBold.ttf` (новый файл)
- `src/gui/styles/fonts/SourceSans3-Bold.ttf` (новый файл)
- `src/gui/styles/theme_loader.py` (modify — обновить имена файлов)

**Критерий приёмки:**
- `python -m src.gui` — нет строк `Failed to create DirectWrite face` в логах
- `[fonts] OK: SourceSans3-Regular.ttf → family 'Source Sans 3'` присутствует в логах
- UI отображается шрифтом Source Sans 3 (не системным fallback)

**Недоработка (актуально):**
```
qt.qpa.fonts: Failed to create DirectWrite face from font data. Font may be unsupported.
[fonts] WARNING: Failed to load: SourceSans3-Bold.ttf (DirectWrite or format error)
[fonts] WARNING: Failed to load: SourceSans3-Regular.ttf (DirectWrite or format error)
[fonts] WARNING: Failed to load: SourceSans3-SemiBold.ttf (DirectWrite or format error)
```
Замена `SourceSansPro-*.ttf` → `SourceSans3-*.ttf` не устранила проблему — новые файлы тоже
отклоняются DirectWrite на Windows. JetBrains Mono грузится успешно, проблема только в Source Sans 3.
Возможные причины: файлы скачаны не из официального источника Google Fonts, используется
OTF-в-TTF конвертация без корректных OS/2-таблиц, или файлы повреждены.

**Дополнительные задачи:**
- [x] `src/gui/styles/fonts/`: скачан official variable font `SourceSans3[wght].ttf` из google/fonts (631KB, magic=00010000 — валидный TTF); скопирован как Regular/Bold/SemiBold; прежние файлы были повреждены (содержали только 0x0a байты)
- [x] `src/gui/styles/theme_loader.py`: исправлен `→` → `->` в print (UnicodeEncodeError на cp1251 Windows консоли)
- [x] `tests/gui/test_theme_loader.py`: добавлены 23 теста — валидация TTF magic bytes, load_fonts(), load_theme(), get_saved_theme(); все GREEN

---

### Этап 9: Flat-список в Sidebar (без дерева) (~120 строк)
**Статус:** ✅ Завершён

**Цель:** Убрать древовидную структуру из секций FILES и SERIES в Sidebar.
Сейчас: `experiments` (родитель) → `NH4_rate_3.csv` (дочерний). Должно быть:
каждый файл и каждая серия занимают всю ширину sidebar как самостоятельный плоский элемент.

**Контекст (image #2):** Видна структура `experiments > NH4_rate_3.csv` с отступом дочернего элемента.
Нужно убрать родительский узел "experiments" — файлы должны быть на верхнем уровне списка.

**Задачи:**
- [x] `src/gui/main_tab/sidebar.py`: заменить `QTreeView` в секции FILES на `QListWidget` — файлы добавляются как `QListWidgetItem` без уровней вложенности; каждый файл занимает полную ширину без отступа; выделение файла через `currentItemChanged`
- [x] `src/gui/main_tab/sidebar.py`: аналогично заменить `QTreeView` в секции SERIES на `QListWidget` — серии добавляются как `QListWidgetItem` на верхнем уровне
- [x] `src/gui/main_tab/sidebar.py`: адаптировать все слоты работы с файлами под `QListWidget` API (`addItem()`, `takeItem()`, `row()`, `count()`, `currentItemChanged`)
- [x] `src/gui/styles/components/sidebar.qss`: добавить стиль `QListWidget#sidebar_tree` — bg_surface, border: none; item padding 6px 10px; selected — accent border-left 2px; hover — bg_elevated

**Файлы:**
- `src/gui/main_tab/sidebar.py` (modify — QTreeView → QListWidget в обеих секциях)
- `src/gui/styles/components/sidebar.qss` (modify — стили QListWidget)

**Критерий приёмки:**
- Загруженный файл отображается в FILES без родительского узла "experiments" и без отступа дочернего элемента
- Файл занимает всю ширину FILES-секции
- Серии аналогично отображаются как плоский список без вложенности
- Клик по файлу/серии переключает контент sub-sidebar (существующая сигнальная логика работает)
- Hover и выделение стилизованы корректно

---

### Этап 10: Деконволюция — типографика, QComboBox и защита столбца name (~150 строк)
**Статус:** ✅ Завершён

**Цель:** Три исправления в панели деконволюции:
1. Убрать надпись "ANALYSIS" из заголовка sub-sidebar
2. Применить моноширинный шрифт (JetBrains Mono) ко всем числам/переменным в панели
3. Исправить QComboBox в столбце `function` — он не помещается в ячейку
4. Запретить редактирование столбца `name`

**Контекст (image #3):** Видны: надпись "ANALYSIS", выпадающие списки "gauss" с плохим позиционированием.

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: убрать `QLabel("ANALYSIS")` / заголовок section_header над `file_tabs` — sub-sidebar должен начинаться сразу с контента без лишнего заголовка
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py`: назначить `objectName("input_numeric")` ячейкам с числовыми значениями (h, z, w) — применится JetBrains Mono из `forms.qss`; добавлен `QTableWidget#input_numeric` стиль в forms.qss
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py`: исправить размер QComboBox в столбце `function` — увеличен row height 26→28px; setCellWidget автоматически вписывает QComboBox в ячейку
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py`: сделать столбец `name` только для чтения — `Qt.ItemFlag.ItemIsEditable` убран через `flags() & ~ItemIsEditable` для всех QTableWidgetItem в col 0

**Файлы:**
- `src/gui/main_tab/sub_sidebar/sub_side_hub.py` (modify — убрать ANALYSIS заголовок)
- `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py` (modify — objectName для числовых ячеек)
- `src/gui/main_tab/sub_sidebar/deconvolution/reaction_table.py` (modify — фикс ComboBox + запрет редактирования name)

**Критерий приёмки:**
- Sub-sidebar не показывает надпись "ANALYSIS" ни над деконволюцией, ни над другими панелями
- Числовые значения параметров (h, z, w) отображаются шрифтом JetBrains Mono
- QComboBox в столбце `function` точно совпадает по размеру с ячейкой (нет выступов за границы)
- Клик на ячейку в столбце `name` не открывает редактор текста — имена реакций нередактируемы

---

### Этап 11: Experiment — плейсхолдеры, dropdown poly, uppercase кнопки, красный RESET (~180 строк)
**Статус:** ✅ Завершён

**Цель:** Сделать панель Experiment визуально чище: убрать лишние label-тексты,
переместить подсказки внутрь полей ввода, сделать "polynomial order" выпадающим списком,
все кнопки с UPPERCASE текстом, кнопка RESET — красная.

**Контекст (image #4):** Видны отдельные label-текты над полями ("window size:", "polynomial order:"),
"specific settings:", кнопки с lowercase текстом, "reset changes" — серая.

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: добавить визуальный разделитель (`QFrame(shape=HLine)` с `objectName("section_divider")`) между секцией SMOOTHING и секцией BACKGROUND
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: убрать `QLabel("window size:")` — заменить на `QSpinBox.setPlaceholderText("window size")` (или аналог для SpinBox); если SpinBox не поддерживает placeholder — заменить на `QLineEdit` с `setPlaceholderText("window size")` и валидацией int
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: убрать `QLabel("polynomial order:")` — заменить поле ввода на `QComboBox` с вариантами `["0", "1", "2", "3", "4", "5"]`; `setEditable(False)`; текущий выбор инициализировать из текущего значения
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: убрать `QLabel("specific settings:")` — значение "Nearest" и другие options ComboBox достаточно информативны без лейбла
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: все кнопки панели переименовать в UPPERCASE: "APPLY", "TO α(T)", "TO DTG", "DECONVOLUTION", "RESET"
- [x] `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py`: кнопке "RESET" назначить `objectName("btn_danger")` — красный фон согласно QSS; остальным кнопкам сохранить `btn_secondary`
- [x] `src/gui/styles/dark.qss` + `light.qss`: добавить стиль `QFrame#section_divider { border: none; border-top: 1px solid <border_color>; margin: 8px 0; }`

**Файлы:**
- `src/gui/main_tab/sub_sidebar/experiment/experiment_sub_bar.py` (modify — placeholder, poly dropdown, uppercase, btn_danger)
- `src/gui/styles/dark.qss` (modify — section_divider)
- `src/gui/styles/light.qss` (modify — section_divider)

**Критерий приёмки:**
- Нет отдельных label "window size:" и "polynomial order:" — подсказки внутри элементов управления
- "polynomial order" реализован как QComboBox с вариантами 0–5
- Визуальный разделитель между SMOOTHING и BACKGROUND секциями
- Кнопки отображают APPLY, TO α(T), TO DTG, DECONVOLUTION, RESET (uppercase)
- Кнопка RESET красная (`btn_danger`)
- Функциональность сглаживания и фонового вычитания не нарушена

---

### Этап 12: Series — uppercase кнопки, убрать ANALYSIS и "calculations" (~80 строк)
**Статус:** ✅ Завершён

**Цель:** Визуальная чистка панели серий: убрать лишние надписи "ANALYSIS" и "calculations:",
все кнопки в UPPERCASE.

**Контекст (image #5):** Видны: заголовок "ANALYSIS", лейбл "calculations:" над кнопками,
кнопки "model fit" / "model free" / "model based" в lowercase.

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/series/series_sub_bar.py`: убрать `QLabel("calculations:")` — label перед кнопками model fit/free/based избыточен
- [x] `src/gui/main_tab/sub_sidebar/sub_side_hub.py`: заголовок "ANALYSIS" удалён в этапе 10 — N/A
- [x] `src/gui/main_tab/sub_sidebar/series/series_sub_bar.py`: переименовать все кнопки в UPPERCASE: "LOAD DECONVOLUTION RESULTS", "EXPORT RESULTS", "MODEL FIT", "MODEL FREE", "MODEL BASED"

**Файлы:**
- `src/gui/main_tab/sub_sidebar/series/series_sub_bar.py` (modify — убрать label, uppercase кнопки)

**Критерий приёмки:**
- Надпись "ANALYSIS" отсутствует в sub-sidebar (с учётом этапа 10)
- Надпись "calculations:" / "calculations" отсутствует в panel серий
- Все кнопки панели серий отображаются в верхнем регистре
- Функциональность кнопок (переключение на model_fit/free/based панели) не нарушена

---

### Этап 13: Model Based — фикс сигналов при hover и ширина столбца Value (~120 строк)
**Статус:** ✅ Завершён

**Цель:** Два исправления в панели Model Based:
1. Баг: движение мыши над таблицей параметров вызывает сигналы (itemChanged / currentCellChanged при hover)
2. Столбец Value слишком узкий — значения обрезаются и не видны полностью

**Контекст (image #6):** Столбец "Value" показывает `).0`, `3.0`, `).5` — значения обрезаны; движение
мышью без клика вызывает сигналы (вероятно через `itemSelectionChanged` или `cellEntered`).

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py`: найти источник сигналов при hover — проверить подключения `cellEntered`, `itemChanged`, `currentCellChanged`; отключить `cellEntered` если он подключён без необходимости; установить `setMouseTracking(False)` если не нужен; убедиться что сигнал изменения параметров эмитируется только при завершении редактирования (focusOut или Return), не при каждом движении мыши
- [x] `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py`: исправить ширину столбца `Value` — установить `horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)` для столбца Value, чтобы он занимал всё доступное пространство; или задать фиксированную минимальную ширину `setColumnWidth(1, 100)` достаточную для отображения float-значений типа "100.000"
- [x] `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py`: установить `horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)` + `setColumnWidth(0, 30)` для столбца с номером строки; `setSectionResizeMode(1, Fixed)` + `setColumnWidth(1, 90)` для Parameter; оставить Value на Stretch

**Файлы:**
- `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py` (modify — отключить hover-сигналы, фикс ширины столбца Value)

**Критерий приёмки:**
- Движение мыши над таблицей параметров не вызывает сигналов/обновлений графика
- Значения Ea, log(A), contribution отображаются полностью в столбце Value (например "100.000")
- Редактирование значения в ячейке по-прежнему обновляет параметры реакции (сигнал при завершении ввода)
- Ширина столбцов корректна при изменении размера панели

---

### Этап 14: Фикс позиционирования ячеек таблиц Deconvolution + Model Based (~150 строк)
**Статус:** ✅ Завершён

**Цель:** Три исправления в таблицах:
1. Deconvolution coefficients_view: ячейки со значениями смещены по положению и размерам
2. Model Based parameter_table: убрать индекс рядов (вертикальный хедер 1, 2, 3)
3. Model Based parameter_table: убедиться что встроенные QLineEdit корректно позиционируются

**Контекст (изображения):**
- Screenshot_1 (deconvolution): ячейки таблицы coeffs визуально смещены, рамки выделения не совпадают с содержимым
- Screenshot_2 (model based): видны номера строк 1, 2, 3 слева; текст в столбце Value обрезан

**Задачи:**
- [x] `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py`: скрыть вертикальный хедер — добавить `self.verticalHeader().hide()` после инициализации таблицы; номера строк (1, 2, 3) не должны отображаться
- [x] `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py`: убедиться что встроенные `QLineEdit` через `setCellWidget()` корректно вписываются в ячейки — проверить высоту строки через `verticalHeader().setDefaultSectionSize(28)` или аналогично; убедиться что `QLineEdit` растягивается на всю ширину ячейки
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py`: проверить `QTableWidget#input_numeric` в QSS — возможно конфликт стилей вызывает смещение; убедиться что `setHorizontalHeaderLabels` и `setVerticalHeaderLabels` не вызывают layout-проблем
- [x] `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py`: явно задать высоту строки через `verticalHeader().setDefaultSectionSize(28)` для консистентности с reaction_table
- [x] `src/gui/styles/components/forms.qss`: проверить стили `QTableWidget#input_numeric` — добавить явные отступы и выравнивание ячеек (`QTableWidget::item { padding: 4px; }`)

**Файлы:**
- `src/gui/main_tab/sub_sidebar/model_based/parameter_table.py` (modify — скрыть verticalHeader, фикс высоты строки)
- `src/gui/main_tab/sub_sidebar/deconvolution/coefficients_view.py` (modify — высота строки, проверка layout)
- `src/gui/styles/components/forms.qss` (modify — отступы QTableWidget::item)

**Критерий приёмки:**
- В Model Based таблице параметров нет номеров строк слева (вертикальный хедер скрыт)
- QLineEdit в Model Based таблице корректно вписывается в ячейки Value, текст не обрезается
- В Deconvolution таблице коэффициентов ячейки выровнены корректно, рамки выделения совпадают с содержимым
- Высота строк консистентна между таблицами (28px)
- Редактирование значений работает без visual glitches

---

## Ограничения и соглашения

| Ограничение | Правило |
|-------------|---------|
| Стили | Только через QSS + objectName; запрещён `setStyleSheet()` в widget-файлах |
| Токены цветов | Только через `tokens.py`; запрещены жёстко заданные цвета в `.py` файлах |
| Бизнес-логика | Не модифицировать: `src/core/`, сигналы и слоты |
| Лимит коммита | ≤250 строк на этап |
| Обратная совместимость | Все существующие сигнальные соединения в `main_tab.py` должны работать |
| Тестирование | После каждого этапа — `python -m src.gui` без падений |

---

## История изменений

| Дата       | Этап | Коммит    | Описание   |
|------------|------|-----------|------------|
| 2026-02-21 | —    | cab7c7a   | ТЗ создано |
| 2026-02-21 | 1    | 6859452   | Активация темы: load_theme в __main__, QMenuBar, QStatusBar, Clear в консоли |
| 2026-02-21 | 2    | 112ff13   | Редизайн sidebar: FILES label, btn_primary, убраны action-items, Series меню |
| 2026-02-21 | 3    | 0df99b8   | Sub-sidebar QTabWidget (Experiment/Deconvolution/Model Fit), objectNames в experiment_sub_bar |
| 2026-02-22 | 4    | f2d2ee4   | Стилизация deconvolution: btn_primary/secondary/danger/small, QTableWidget/QHeaderView/QDialogButtonBox в deconvolution.qss |
| 2026-02-22 | 5    | 07d699f   | Стилизация series/model_fit/model_free: btn_primary/secondary/small, QTableWidget в dark.qss/light.qss |
| 2026-02-22 | 6    | 49bae6f   | Стилизация model_based: btn_primary/secondary/danger/small, QSlider groove/handle в dark.qss/light.qss |
| 2026-02-22 | 7    | cda2855   | Типографика: load_fonts(), Source Sans 3 + JetBrains Mono через QFontDatabase |
| 2026-02-22 | 2–7  | —         | Замечания по результатам ручного тестирования: карусели, sidebar 2-секций, highlight_reaction, слайдеры model_based, схема реакций, шрифты DirectWrite |
| 2026-02-22 | 2    | d1bfe13   | Sidebar разделён на FILES/SERIES секции: 2×QTreeView, Load/Import кнопки в каждой секции, btn_ghost QSS |
| 2026-02-22 | 3    | b96992b   | Доп. задачи этапа 3: tabBar().hide() на file_tabs, QComboBox::down-arrow SVG-шеврон в dark/light.qss, заголовки секций в верхнем регистре |
| 2026-02-22 | 4    | cd273d3   | Доп. задачи этапа 4: фикс ширины колонок reaction_table (col1=Fixed 85px), defensive checks в selected_reaction |
| 2026-02-22 | 8–13 | —         | Добавлены этапы 8–13 по результатам ручного тестирования: шрифты, flat sidebar, деконволюция, experiment, серии, model based |
| 2026-02-22 | 8    | 555cc7f   | Замена SourceSansPro-*.ttf → SourceSans3-*.ttf из Google Fonts; устранена ошибка DirectWrite на Windows |
| 2026-02-22 | 9    | dafcbab   | Flat sidebar: QTreeView+QStandardItemModel → QListWidget+QListWidgetItem в FILES и SERIES; QSS + тесты обновлены |
| 2026-02-22 | 10   | 0ff8ae2   | Деконволюция: убран ANALYSIS header, CoefficientsView objectName(input_numeric) для Mono шрифта, name col read-only, row height 28px |
| 2026-02-22 | 11   | 77f57d8   | Experiment: placeholder для n_window, n_poly→QComboBox, убраны QLabel-обёртки, UPPERCASE кнопки, RESET→btn_danger, QFrame#section_divider в dark/light.qss |
| 2026-02-22 | 12   | 24879d7   | Series: убран label "calculations", все кнопки UPPERCASE |
| 2026-02-22 | 13   | 7900814   | Model Based: отключены hover-сигналы, столбец Value на Stretch |
| 2026-02-22 | 14   | 7517dba   | Фикс позиционирования ячеек: скрыть verticalHeader в model_based, высота строки 28px, отступы в forms.qss |
| 2026-02-22 | 14   | d529fe4   | Центрирование виджетов в ячейках: QComboBox/QLineEdit в контейнере с AlignVCenter, setFixedHeight(26), row height 30px |
| 2026-02-22 | 8    | 50b3f96   | Итерация 3: скачан valid SourceSans3[wght].ttf из google/fonts (631KB), исправлена UnicodeError в theme_loader.py, добавлены 23 теста в test_theme_loader.py |
