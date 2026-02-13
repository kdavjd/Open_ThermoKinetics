# pytest-qt Patterns for solid-state_kinetics

> Примеры тестов для PyQt6 GUI приложения

---

## 1. Базовые fixtures

### conftest.py

```python
import pytest
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Сессионный QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def sample_tga_data():
    """Тестовые TGA данные."""
    temperature = np.linspace(300, 800, 100)
    mass_loss = 100 * np.exp(-0.005 * (temperature - 300))
    return temperature, mass_loss


@pytest.fixture
def temp_csv_file(tmp_path, sample_tga_data):
    """Временный CSV файл с тестовыми данными."""
    temperature, mass_loss = sample_tga_data
    csv_path = tmp_path / "test_data.csv"

    with open(csv_path, "w") as f:
        f.write("Temperature,Mass\n")
        for t, m in zip(temperature, mass_loss):
            f.write(f"{t:.2f},{m:.4f}\n")

    yield csv_path
```

---

## 2. Тестирование MainWindow

```python
import pytest
from PyQt6.QtCore import Qt

@pytest.fixture
def main_window(qtbot, qapp):
    """Fixture главного окна."""
    from src.gui.main_window import MainWindow
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


class TestMainWindow:
    """Тесты главного окна."""

    def test_window_opens(self, main_window):
        """Окно открывается и видно."""
        assert main_window.isVisible()
        assert main_window.size().width() > 0
        assert main_window.size().height() > 0

    def test_tab_widget_exists(self, main_window):
        """Есть вкладки в окне."""
        assert hasattr(main_window, "tab_widget")
        assert main_window.tab_widget.count() >= 1

    def test_switch_tabs(self, main_window, qtbot):
        """Переключение вкладок работает."""
        if main_window.tab_widget.count() < 2:
            pytest.skip("Only one tab")

        main_window.tab_widget.setCurrentIndex(1)
        qtbot.wait(50)

        assert main_window.tab_widget.currentIndex() == 1
```

---

## 3. Тестирование Sidebar

```python
@pytest.fixture
def sidebar(qtbot, qapp):
    """Fixture боковой панели."""
    from src.gui.main_tab.sidebar import Sidebar
    from src.core.base_signals import BaseSignals

    signals = BaseSignals()
    sidebar = Sidebar(signals)
    qtbot.addWidget(sidebar)
    return sidebar


class TestSidebar:
    """Тесты боковой панели."""

    def test_tree_widget_exists(self, sidebar):
        """Дерево навигации существует."""
        assert hasattr(sidebar, "tree_widget")
        assert sidebar.tree_widget is not None

    def test_add_file_to_tree(self, sidebar, qtbot):
        """Добавление файла в дерево."""
        initial_count = sidebar.tree_widget.topLevelItemCount()

        # Добавляем элемент
        sidebar.add_file_item("test_file.csv")

        qtbot.wait(50)
        assert sidebar.tree_widget.topLevelItemCount() == initial_count + 1

    def test_file_selection_signal(self, sidebar, qtbot):
        """Выбор файла эмитирует сигнал."""
        # Добавляем файл
        sidebar.add_file_item("test_file.csv")

        # Слушаем сигнал
        with qtbot.wait_signal(sidebar.file_selected, timeout=1000):
            # Выбираем элемент
            item = sidebar.tree_widget.topLevelItem(0)
            sidebar.tree_widget.setCurrentItem(item)
```

---

## 4. Тестирование PlotCanvas

```python
@pytest.fixture
def plot_canvas(qtbot, qapp):
    """Fixture canvas для графиков."""
    from src.gui.main_tab.plot_canvas.plot_canvas import PlotCanvas
    canvas = PlotCanvas()
    qtbot.addWidget(canvas)
    return canvas


class TestPlotCanvas:
    """Тесты визуализации графиков."""

    def test_canvas_initialization(self, plot_canvas):
        """Canvas инициализирован."""
        assert plot_canvas.figure is not None
        assert plot_canvas.axes is not None

    def test_plot_data(self, plot_canvas, sample_tga_data, qtbot):
        """Отрисовка данных на графике."""
        temperature, mass_loss = sample_tga_data

        plot_canvas.plot_data(temperature, mass_loss, label="Test")
        qtbot.wait(100)

        # Проверяем, что линии на графике есть
        lines = plot_canvas.axes.get_lines()
        assert len(lines) >= 1

    def test_clear_plot(self, plot_canvas, sample_tga_data, qtbot):
        """Очистка графика."""
        temperature, mass_loss = sample_tga_data
        plot_canvas.plot_data(temperature, mass_loss)
        qtbot.wait(50)

        plot_canvas.clear_plot()
        qtbot.wait(50)

        lines = plot_canvas.axes.get_lines()
        assert len(lines) == 0

    def test_legend_display(self, plot_canvas, sample_tga_data, qtbot):
        """Отображение легенды."""
        temperature, mass_loss = sample_tga_data
        plot_canvas.plot_data(temperature, mass_loss, label="TGA Curve")
        plot_canvas.show_legend()
        qtbot.wait(50)

        legend = plot_canvas.axes.get_legend()
        assert legend is not None
```

---

## 5. Тестирование сигналов BaseSignals

```python
import pytest
from PyQt6.QtCore import QEventLoop


@pytest.fixture
def signals(qtbot, qapp):
    """Fixture центрального диспетчера сигналов."""
    from src.core.base_signals import BaseSignals
    return BaseSignals()


class TestBaseSignals:
    """Тесты сигнал-слот системы."""

    def test_request_signal_emission(self, signals, qtbot):
        """Эмиссия request_signal."""
        request_data = {"action": "load_file", "path": "test.csv"}

        with qtbot.wait_signal(signals.request_signal, timeout=1000) as blocker:
            signals.request_signal.emit(request_data)

        assert blocker.args[0] == request_data

    def test_response_signal_emission(self, signals, qtbot):
        """Эмиссия response_signal."""
        response_data = {"status": "success", "data": [1, 2, 3]}

        with qtbot.wait_signal(signals.response_signal, timeout=1000) as blocker:
            signals.response_signal.emit(response_data)

        assert blocker.args[0]["status"] == "success"

    def test_dispatch_request(self, signals, qtbot):
        """Диспетчеризация запроса."""
        received = []

        signals.request_signal.connect(lambda d: received.append(d))

        signals.dispatch_request({"action": "test"})

        qtbot.wait(50)
        assert len(received) == 1
        assert received[0]["action"] == "test"
```

---

## 6. Unit тесты бизнес-логики

```python
import numpy as np
from numpy.testing import assert_array_almost_equal


class TestCurveFitting:
    """Тесты функций подгонки кривых."""

    def test_gaussian_peak(self):
        """Функция Гаусса имеет пик в центре."""
        from src.core.curve_fitting import gaussian

        x = np.linspace(-5, 5, 100)
        y = gaussian(x, amplitude=1.0, center=0.0, sigma=1.0)

        # Пик в центре
        assert np.argmax(y) == 49 or np.argmax(y) == 50
        assert np.max(y) == pytest.approx(1.0, rel=0.01)

    def test_gaussian_symmetry(self):
        """Функция Гаусса симметрична."""
        from src.core.curve_fitting import gaussian

        x = np.linspace(-5, 5, 100)
        y = gaussian(x, amplitude=1.0, center=0.0, sigma=1.0)

        # Симметрия относительно центра
        left = y[:50]
        right = y[50:][::-1]
        assert_array_almost_equal(left, right, decimal=5)

    def test_fraser_suzuki_asymmetry(self):
        """Функция Fraser-Suzuki асимметрична."""
        from src.core.curve_fitting import fraser_suzuki

        x = np.linspace(-5, 5, 100)
        y_symmetric = fraser_suzuki(x, amplitude=1.0, center=0.0, sigma=1.0, asymmetry=0.0)
        y_asymmetric = fraser_suzuki(x, amplitude=1.0, center=0.0, sigma=1.0, asymmetry=0.5)

        # Асимметричная версия отличается
        assert not np.allclose(y_symmetric, y_asymmetric)


class TestCalculationData:
    """Тесты структур данных расчётов."""

    def test_file_data_creation(self):
        """Создание FileData."""
        from src.core.file_data import FileData

        data = FileData(
            filename="test.csv",
            temperature=np.array([300, 400, 500]),
            mass_loss=np.array([100, 90, 80])
        )

        assert data.filename == "test.csv"
        assert len(data.temperature) == 3

    def test_calculation_data_operations(self):
        """Операции с CalculationData."""
        from src.core.calculation_data_operations import CalculationDataOperations

        ops = CalculationDataOperations()
        # Тест операций...
```

---

## 7. Интеграционные тесты

```python
@pytest.mark.integration
@pytest.mark.slow
class TestWorkflow:
    """Интеграционные тесты полного workflow."""

    def test_load_and_plot_file(self, main_window, temp_csv_file, qtbot):
        """Загрузка файла и отображение на графике."""
        # 1. Находим кнопку загрузки
        load_button = main_window.findChild(
            QPushButton,
            "load_file_button"
        )
        assert load_button is not None

        # 2. Эмулируем выбор файла (через сигнал)
        main_window.sidebar.file_loaded.emit(str(temp_csv_file))
        qtbot.wait(100)

        # 3. Проверяем, что файл появился в дереве
        tree = main_window.sidebar.tree_widget
        assert tree.topLevelItemCount() >= 1

    def test_deconvolution_workflow(self, main_window, sample_tga_data, qtbot):
        """Workflow деконволюции."""
        # 1. Загружаем данные
        temperature, mass_loss = sample_tga_data
        main_window.plot_canvas.plot_data(temperature, mass_loss)
        qtbot.wait(100)

        # 2. Открываем панель деконволюции
        main_window.sub_side_hub.show_panel("deconvolution")
        qtbot.wait(50)

        # 3. Проверяем, что панель видна
        assert main_window.sub_side_hub.current_panel == "deconvolution"
```

---

## 8. Параметризованные тесты

```python
@pytest.mark.parametrize("model,expected_params", [
    ("F1", 1),   # First-order
    ("F2", 1),   # Second-order
    ("F3", 1),   # Third-order
    ("R2", 1),   # 2D phase boundary
    ("R3", 1),   # 3D phase boundary
    ("A2", 1),   # Avrami-Erofeev n=2
    ("A3", 1),   # Avrami-Erofeev n=3
])
def test_kinetic_models(model, expected_params):
    """Тест кинетических моделей."""
    from src.core.model_fit_calculation import get_model_function

    func = get_model_function(model)
    assert func is not None

    # Тест вызова функции
    alpha = np.linspace(0.01, 0.99, 100)
    result = func(alpha, 1.0)  # E=1 для теста

    assert len(result) == len(alpha)
    assert np.all(np.isfinite(result))


@pytest.mark.parametrize("heating_rate", [5, 10, 15, 20])
def test_multi_heating_rate(heating_rate, qtbot, plot_canvas):
    """Тест разных скоростей нагрева."""
    temperature = np.linspace(300, 800, 100)
    # Скорость нагрева влияет на кинетику
    mass_loss = 100 * np.exp(-heating_rate * 0.0005 * (temperature - 300))

    plot_canvas.plot_data(temperature, mass_loss, label=f"{heating_rate} K/min")
    qtbot.wait(50)

    lines = plot_canvas.axes.get_lines()
    assert len(lines) >= 1
```

---

## 9. Тестирование обработки ошибок

```python
class TestErrorHandling:
    """Тесты обработки ошибок."""

    def test_invalid_file_format(self, qtbot, main_window, tmp_path):
        """Обработка неверного формата файла."""
        # Создаём неверный файл
        bad_file = tmp_path / "bad.txt"
        bad_file.write_text("not a valid data file")

        # Пытаемся загрузить
        with pytest.raises(ValueError):
            main_window.load_file(str(bad_file))

    def test_empty_data_handling(self, plot_canvas, qtbot):
        """Обработка пустых данных."""
        with pytest.raises(ValueError):
            plot_canvas.plot_data([], [])

    def test_nan_handling(self, plot_canvas, qtbot):
        """Обработка NaN в данных."""
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([1, 4, 9, 16, 25])

        # Должен либо обработать, либо выбросить ошибку
        with pytest.raises((ValueError, RuntimeWarning)):
            plot_canvas.plot_data(x, y)
```

---

## 10. Маркировка тестов

```python
import pytest

@pytest.mark.gui
def test_requires_display(qtbot):
    """Тест, требующий дисплей."""
    from PyQt6.QtWidgets import QLabel
    label = QLabel("Test")
    qtbot.addWidget(label)
    assert label.text() == "Test"


@pytest.mark.slow
def test_long_calculation():
    """Медленный тест оптимизации."""
    from scipy.optimize import differential_evolution
    import numpy as np

    def objective(x):
        return np.sum(x**2)

    result = differential_evolution(
        objective,
        bounds=[(-10, 10)] * 5,
        maxiter=100
    )
    assert result.fun < 1e-6


@pytest.mark.skipif(
    sys.platform == "linux",
    reason="Linux headless issues"
)
def test_windows_only(qtbot):
    """Тест только для Windows."""
    pass
```

---

## Запуск тестов

```bash
# Все тесты
pytest

# Только GUI
pytest -m gui

# Пропустить медленные
pytest -m "not slow"

# Только unit тесты
pytest tests/unit/

# С покрытием
pytest --cov=src --cov-report=html

# Verbose
pytest -v --tb=long
```
