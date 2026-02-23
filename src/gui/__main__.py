"""
Entry point for Open ThermoKinetics GUI application.

Initializes PyQt6 application with all core modules and their signal
communication system for solid-state reaction kinetics analysis.
"""

import multiprocessing
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from PyQt6.QtWidgets import QApplication

from src.core.base_signals import BaseSignals
from src.core.calculation import Calculations
from src.core.calculation_data import CalculationsData
from src.core.calculation_data_operations import CalculationsDataOperations
from src.core.file_data import FileData
from src.core.file_operations import ActiveFileOperations
from src.core.model_fit_calculation import ModelFitCalculation
from src.core.model_free_calculation import ModelFreeCalculation
from src.core.series_data import SeriesData
from src.gui.main_window import MainWindow
from src.gui.styles import get_saved_theme, load_fonts, load_theme


def main():
    """
    Initialize and run the Open ThermoKinetics application.

    Creates PyQt6 application, instantiates all core modules with signal
    communication, establishes module connections, and starts the main window.
    """
    # Required for PyInstaller --onefile with multiprocessing (scipy.optimize)
    multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    signals = BaseSignals()

    # Load fonts and apply theme BEFORE MainWindow so toolbar is created with correct QPalette
    load_fonts()
    load_theme(app, get_saved_theme())

    window = MainWindow(signals=signals)
    file_data = FileData(signals=signals)
    series_data = SeriesData(signals=signals)  # noqa: F841
    calculations_data = CalculationsData(signals=signals)  # noqa: F841
    calculations = Calculations(signals=signals)
    calculations_data_operations = CalculationsDataOperations(signals=signals)
    file_operations = ActiveFileOperations(signals=signals)  # noqa: F841
    model_fit_calculation = ModelFitCalculation(signals=signals)  # noqa: F841
    model_free_calculation = ModelFreeCalculation(signals=signals)  # noqa: F841

    window.main_tab.sidebar.load_button.file_selected.connect(file_data.load_file)
    window.main_tab.sidebar.chosen_experiment_signal.connect(file_data.plot_dataframe_copy)
    file_data.data_loaded_signal.connect(window.main_tab.plot_canvas.plot_data_from_dataframe)
    calculations_data_operations.reaction_params_to_gui.connect(window.main_tab.plot_canvas.add_anchors)
    calculations_data_operations.plot_reaction.connect(window.main_tab.plot_canvas.plot_reaction)
    calculations_data_operations.deconvolution_signal.connect(calculations.run_calculation_scenario)
    calculations_data_operations.reaction_params_to_gui.connect(
        window.main_tab.sub_sidebar.deconvolution_sub_bar.coeffs_table.fill_table
    )
    window.model_based_calculation_signal.connect(calculations.run_calculation_scenario)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
