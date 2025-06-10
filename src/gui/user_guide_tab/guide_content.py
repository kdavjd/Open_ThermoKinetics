"""
Guide Content Data
Contains all user guide content in both Russian and English languages.
Content is organized by sections with structured blocks for rich text display.
"""

# Guide content structure for both languages
GUIDE_CONTENT = {
    "ru": {
        "introduction": {
            "title": "Введение",
            "content": [
                {
                    "type": "paragraph",
                    "text": (
                        "Open ThermoKinetics - это специализированное приложение для анализа кинетики "
                        "твердофазных реакций. Программа предназначена для обработки экспериментальных "
                        "данных термического анализа и определения кинетических параметров реакций "
                        "различными методами."
                    ),
                },
                {"type": "heading", "text": "Основные возможности приложения:"},
                {
                    "type": "list",
                    "items": [
                        "Загрузка и предобработка экспериментальных данных",
                        "Деконволюция сложных пиков на отдельные реакции",
                        "Model-fit анализ (прямой дифференциальный метод, Коутса-Редферна)",
                        "Model-free анализ (изоконверсионные методы: Фридман, KAS, Старинк)",
                        "Model-based анализ многостадийных реакционных схем",
                        "Работа с сериями экспериментов при разных скоростях нагрева",
                    ],
                },
            ],
        },
        "file_loading": {
            "title": "Загрузка файлов",
            "content": [
                {"type": "heading", "text": "Подготовка данных"},
                {
                    "type": "paragraph",
                    "text": "Перед загрузкой убедитесь, что ваши экспериментальные данные соответствуют требованиям:",
                },
                {
                    "type": "list",
                    "items": [
                        "CSV файл с разделителем запятая (,)",
                        "Первая строка содержит заголовки столбцов",
                        "Обязательные столбцы: temperature (температура) и данные скорости",
                    ],
                },
                {
                    "type": "code",
                    "text": "temperature,rate_3\\n32.18783,99.47196\\n33.14274,99.46862\\n34.09766,99.46740",
                },
                {"type": "heading", "text": "Процесс загрузки"},
                {
                    "type": "list",
                    "items": [
                        "Откройте приложение - запустится главное окно с вкладками Main и User Guide",
                        "В левой панели навигации найдите раздел experiments",
                        "Нажмите на add file data",
                        "Выберите ваш CSV файл с экспериментальными данными",
                    ],
                },
            ],
        },
        "data_preprocessing": {
            "title": "Предобработка данных",
            "content": [
                {"type": "heading", "text": "Переход в режим предобработки"},
                {
                    "type": "list",
                    "items": [
                        "Выберите нужный файл в дереве навигации",
                        "Файл станет активным (выделится жирным шрифтом)",
                        "Автоматически откроется панель Experiments в правой части окна",
                    ],
                },
                {"type": "heading", "text": "Преобразование данных"},
                {
                    "type": "list",
                    "items": [
                        "Нажмите кнопку to α/T в блоке действий",
                        "После преобразования в α нажмите кнопку to dα/dT",
                        "Используйте кнопку reset changes для возврата к исходным данным",
                    ],
                },
                {"type": "note", "text": "<b>Важно:</b> Данные dα/dT необходимы для деконволюции пиков."},
            ],
        },
        "deconvolution": {
            "title": "Деконволюция пиков",
            "content": [
                {"type": "paragraph", "text": "Деконволюция позволяет разделить сложные пики на отдельные реакции."},
                {"type": "heading", "text": "Добавление реакций"},
                {
                    "type": "list",
                    "items": [
                        "Нажмите кнопку Add Reaction в панели деконволюции",
                        "Выберите тип функции: gauss, ads, или fraser",
                        "Настройте параметры: высота (h), позиция (z), ширина (w)",
                    ],
                },
                {
                    "type": "note",
                    "text": "<b>Интерактивная настройка:</b> Красные точки на графике можно перетаскивать мышью.",
                },
            ],
        },
        "model_fit": {
            "title": "Model-Fit анализ",
            "content": [
                {
                    "type": "paragraph",
                    "text": "Model-Fit анализ определяет кинетические параметры на основе результатов деконволюции.",
                },
                {"type": "heading", "text": "Доступные методы"},
                {
                    "type": "list",
                    "items": [
                        "Direct-Diff метод: прямая дифференциальная обработка",
                        "Coats-Redfern метод: интегральный метод анализа",
                    ],
                },
                {"type": "heading", "text": "Результаты"},
                {
                    "type": "list",
                    "items": [
                        "Ea - энергия активации (кДж/моль)",
                        "log_A - логарифм предэкспоненциального фактора",
                        "R² - коэффициент детерминации",
                    ],
                },
            ],
        },
        "model_free": {
            "title": "Model-Free анализ",
            "content": [
                {"type": "paragraph", "text": "Изоконверсионный анализ не требует знания механизма реакции."},
                {"type": "heading", "text": "Методы"},
                {
                    "type": "list",
                    "items": [
                        "Friedman метод: дифференциальный",
                        "KAS: интегральный метод",
                        "Starink: модифицированный интегральный",
                    ],
                },
                {"type": "note", "text": "<b>Требования:</b> Необходимы эксперименты при минимум 3 скоростях нагрева."},
            ],
        },
        "model_based": {
            "title": "Model-Based анализ",
            "content": [
                {"type": "paragraph", "text": "Анализ сложных многостадийных реакционных схем."},
                {"type": "heading", "text": "Типы схем"},
                {
                    "type": "list",
                    "items": ["Последовательные: A→B→C→D", "Параллельные: A→B, A→C", "С ветвлением: A→B→C→(D,E)"],
                },
            ],
        },
        "series": {
            "title": "Работа с сериями",
            "content": [
                {"type": "paragraph", "text": "Серии объединяют эксперименты при разных скоростях нагрева."},
                {"type": "heading", "text": "Создание серии"},
                {
                    "type": "list",
                    "items": [
                        "Загрузите файлы с разными скоростями",
                        "Выполните деконволюцию для каждого",
                        "Выберите series → add new series",
                    ],
                },
            ],
        },
        "tips": {
            "title": "Советы и рекомендации",
            "content": [
                {"type": "heading", "text": "Подготовка данных"},
                {
                    "type": "list",
                    "items": [
                        "Убедитесь в качестве экспериментальных данных",
                        "Удалите выбросы и артефакты",
                        "Используйте достаточное количество точек (>200)",
                    ],
                },
                {"type": "heading", "text": "Критерии качества"},
                {
                    "type": "list",
                    "items": [
                        "R² > 0.95 для хорошей подгонки",
                        "Физически разумные значения Ea (50-300 кДж/моль)",
                        "Согласованность результатов разных методов",
                    ],
                },
            ],
        },
    },
    "en": {
        "introduction": {
            "title": "Introduction",
            "content": [
                {
                    "type": "paragraph",
                    "text": (
                        "Open ThermoKinetics is a specialized application for analyzing solid-state "
                        "reaction kinetics. The program processes experimental thermal analysis data "
                        "and determines kinetic parameters using various methods."
                    ),
                },
                {"type": "heading", "text": "Main features:"},
                {
                    "type": "list",
                    "items": [
                        "Loading and preprocessing experimental data",
                        "Deconvolution of complex peaks into individual reactions",
                        "Model-fit analysis (direct differential, Coats-Redfern)",
                        "Model-free analysis (isoconversional methods: Friedman, KAS, Starink)",
                        "Model-based analysis of multi-stage reaction schemes",
                        "Working with experimental series at different heating rates",
                    ],
                },
            ],
        },
        "file_loading": {
            "title": "File Loading",
            "content": [
                {"type": "heading", "text": "Data Preparation"},
                {"type": "paragraph", "text": "Ensure your experimental data meets the requirements:"},
                {
                    "type": "list",
                    "items": [
                        "CSV file with comma separator",
                        "First row contains column headers",
                        "Required columns: temperature and rate data",
                    ],
                },
                {
                    "type": "code",
                    "text": "temperature,rate_3\\n32.18783,99.47196\\n33.14274,99.46862\\n34.09766,99.46740",
                },
                {"type": "heading", "text": "Loading Process"},
                {
                    "type": "list",
                    "items": [
                        "Open the application - main window with Main and User Guide tabs",
                        "In the left navigation panel, find experiments section",
                        "Click on add file data",
                        "Select your CSV file with experimental data",
                    ],
                },
            ],
        },
        "data_preprocessing": {
            "title": "Data Preprocessing",
            "content": [
                {"type": "heading", "text": "Entering Preprocessing Mode"},
                {
                    "type": "list",
                    "items": [
                        "Select the desired file in the navigation tree",
                        "File becomes active (highlighted in bold)",
                        "Experiments panel opens automatically on the right",
                    ],
                },
                {"type": "heading", "text": "Data Transformation"},
                {
                    "type": "list",
                    "items": [
                        "Click to α/T button in the actions block",
                        "After conversion to α, click to dα/dT button",
                        "Use reset changes button to return to original data",
                    ],
                },
                {"type": "note", "text": "<b>Important:</b> dα/dT data is necessary for peak deconvolution."},
            ],
        },
        "deconvolution": {
            "title": "Peak Deconvolution",
            "content": [
                {"type": "paragraph", "text": "Deconvolution separates complex peaks into individual reactions."},
                {"type": "heading", "text": "Adding Reactions"},
                {
                    "type": "list",
                    "items": [
                        "Click Add Reaction button in deconvolution panel",
                        "Select function type: gauss, ads, or fraser",
                        "Adjust parameters: height (h), position (z), width (w)",
                    ],
                },
                {"type": "note", "text": "<b>Interactive adjustment:</b> Red dots on graph can be dragged with mouse."},
            ],
        },
        "model_fit": {
            "title": "Model-Fit Analysis",
            "content": [
                {
                    "type": "paragraph",
                    "text": "Model-Fit analysis determines kinetic parameters based on deconvolution results.",
                },
                {"type": "heading", "text": "Available Methods"},
                {
                    "type": "list",
                    "items": [
                        "Direct-Diff method: direct differential processing",
                        "Coats-Redfern method: integral analysis method",
                    ],
                },
                {"type": "heading", "text": "Results"},
                {
                    "type": "list",
                    "items": [
                        "Ea - activation energy (kJ/mol)",
                        "log_A - logarithm of pre-exponential factor",
                        "R² - coefficient of determination",
                    ],
                },
            ],
        },
        "model_free": {
            "title": "Model-Free Analysis",
            "content": [
                {
                    "type": "paragraph",
                    "text": "Isoconversional analysis requires no prior knowledge of reaction mechanism.",
                },
                {"type": "heading", "text": "Methods"},
                {
                    "type": "list",
                    "items": ["Friedman method: differential", "KAS: integral method", "Starink: modified integral"],
                },
                {"type": "note", "text": "<b>Requirements:</b> Experiments at least 3 different heating rates needed."},
            ],
        },
        "model_based": {
            "title": "Model-Based Analysis",
            "content": [
                {"type": "paragraph", "text": "Analysis of complex multi-stage reaction schemes."},
                {"type": "heading", "text": "Scheme Types"},
                {"type": "list", "items": ["Sequential: A→B→C→D", "Parallel: A→B, A→C", "Branched: A→B→C→(D,E)"]},
            ],
        },
        "series": {
            "title": "Working with Series",
            "content": [
                {"type": "paragraph", "text": "Series combine experiments at different heating rates."},
                {"type": "heading", "text": "Creating Series"},
                {
                    "type": "list",
                    "items": [
                        "Load files with different heating rates",
                        "Perform deconvolution for each",
                        "Select series → add new series",
                    ],
                },
            ],
        },
        "tips": {
            "title": "Tips and Recommendations",
            "content": [
                {"type": "heading", "text": "Data Preparation"},
                {
                    "type": "list",
                    "items": [
                        "Ensure quality of experimental data",
                        "Remove outliers and artifacts",
                        "Use sufficient number of data points (>200)",
                    ],
                },
                {"type": "heading", "text": "Quality Criteria"},
                {
                    "type": "list",
                    "items": [
                        "R² > 0.95 for good fit",
                        "Physically reasonable Ea values (50-300 kJ/mol)",
                        "Consistency of results from different methods",
                    ],
                },
            ],
        },
    },
}
