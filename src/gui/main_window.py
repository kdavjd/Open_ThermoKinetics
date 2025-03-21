from functools import reduce

import pandas as pd
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from src.core.app_settings import OperationType
from src.core.base_signals import BaseSignals, BaseSlots
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console
from src.gui.main_tab.main_tab import MainTab
from src.gui.table_tab.table_tab import TableTab


class MainWindow(QMainWindow):
    to_main_tab_signal = pyqtSignal(dict)
    model_based_calculation_signal = pyqtSignal(dict)

    def __init__(self, signals: BaseSignals):
        super().__init__()
        self.setWindowTitle("Open ThermoKinetics")

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.main_tab = MainTab(self)
        self.table_tab = TableTab(self)

        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.table_tab, "Table")

        self.signals = signals
        self.actor_name = "main_window"

        self.base_slots = BaseSlots(actor_name=self.actor_name, signals=self.signals)

        self.signals.register_component(self.actor_name, self.process_request, self.process_response)

        self.main_tab.to_main_window_signal.connect(self.handle_request_from_main_tab)
        self.main_tab.sidebar.to_main_window_signal.connect(self.handle_request_from_main_tab)
        self.to_main_tab_signal.connect(self.main_tab.response_slot)

        logger.debug(f"{self.actor_name} init signals and slots.")

    @pyqtSlot(dict)
    def process_request(self, params: dict):
        operation = params.get("operation")
        actor = params.get("actor")
        response = params.copy()
        logger.debug(f"{self.actor_name} handle request '{operation}' from '{actor}'")
        if operation == OperationType.GET_FILE_NAME:
            response["data"] = self.main_tab.sidebar.active_file_item.text()

        elif operation == OperationType.PLOT_DF:
            df = params.get("df", None)
            self.main_tab.plot_canvas.plot_data_from_dataframe(df) if df is not None else logger.error(
                f"{self.actor_name} no df"
            )
            response["data"] = df is not None

        elif operation == OperationType.PLOT_MSE_LINE:
            mse_data = params.get("mse_data", [])
            self.main_tab.plot_canvas.plot_mse_history(mse_data)
            response["data"] = True

        elif operation == OperationType.CALCULATION_FINISHED:
            self.main_tab.sub_sidebar.deconvolution_sub_bar.calc_buttons.revert_to_default()
            response["data"] = True

        else:
            logger.warning(f"{self.actor_name} received unknown operation '{operation}'")
        response["target"], response["actor"] = response["actor"], response["target"]
        self.signals.response_signal.emit(response)

    @pyqtSlot(dict)
    def process_response(self, params: dict):
        logger.debug(f"{self.actor_name} received response: {params}")
        self.base_slots.process_response(params)

    def handle_request_cycle(self, target: str, operation: str, **kwargs):
        result = self.base_slots.handle_request_cycle(target, operation, **kwargs)
        logger.debug(f"handle_request_cycle result for '{operation}': {result}")
        return result

    @pyqtSlot(dict)
    def handle_request_from_main_tab(self, params: dict):
        operation = params.pop("operation")

        logger.info(f"{self.actor_name} handle_request_from_main_tab '{operation}' with {params=}")

        operation_handlers = {
            OperationType.DIFFERENTIAL: self._handle_differential,
            OperationType.ADD_REACTION: self._handle_add_reaction,
            OperationType.HIGHLIGHT_REACTION: self._handle_highlight_reaction,
            OperationType.REMOVE_REACTION: self._handle_remove_reaction,
            OperationType.UPDATE_VALUE: self._handle_update_value,
            OperationType.RESET_FILE_DATA: self._handle_reset_file_data,
            OperationType.IMPORT_REACTIONS: self._handle_import_reactions,
            OperationType.EXPORT_REACTIONS: self._handle_export_reactions,
            OperationType.DECONVOLUTION: self._handle_deconvolution,
            OperationType.STOP_CALCULATION: self._handle_stop_calculation,
            OperationType.ADD_NEW_SERIES: self._handle_add_new_series,
            OperationType.DELETE_SERIES: self._handle_delete_series,
            OperationType.SCHEME_CHANGE: self._handle_scheme_change,
            OperationType.MODEL_PARAMS_CHANGE: self._handle_model_params_change,
            OperationType.SELECT_SERIES: self._handle_select_series,
            OperationType.LOAD_DECONVOLUTION_RESULTS: self._handle_load_deconvolution_results,
            OperationType.GET_MODEL_FIT_REACTION_DF: self._handle_get_model_fit_reaction_df,
            OperationType.GET_MODEL_FREE_REACTION_DF: self._handle_get_model_free_reaction_df,
            OperationType.PLOT_MODEL_FIT_RESULT: self._handle_plot_model_fit_result,
            OperationType.PLOT_MODEL_FREE_RESULT: self._handle_plot_model_free_result,
            OperationType.MODEL_BASED_CALCULATION: self._handle_model_based_calculation,
            OperationType.MODEL_FIT_CALCULATION: self._handle_model_fit_calculation,
            OperationType.MODEL_FREE_CALCULATION: self._handle_model_free_calculation,
        }

        handler = operation_handlers.get(operation)
        if handler:
            handler(params)
        else:
            logger.error(f"{self.actor_name} unknown operation: {operation},\n\n {params=}")

    def _handle_model_free_calculation(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            console.log("\nIt is necessary to select a series for calculation\n")
            return

        series_entry = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        experimental_df = series_entry.get("experimental_data")
        deconvolution_results = series_entry.get("deconvolution_results", {})
        if not deconvolution_results:
            console.log(
                f"\nSeries '{series_name}' should be divided into reactions by deconvolution.\n"
                "Load deconvolution data in series working space.\n"
            )
            return
        reactions, _ = self.main_tab.sub_sidebar.series_sub_bar.check_missing_reactions(
            experimental_df, deconvolution_results
        )
        params["reaction_data"] = {
            reaction: self.main_tab.sub_sidebar.series_sub_bar.get_reaction_dataframe(
                experimental_df, deconvolution_results, reaction_n=reaction
            )
            for reaction in reactions
        }
        fit_results = self.handle_request_cycle(
            "model_free_calculation", OperationType.MODEL_FREE_CALCULATION, calculation_params=params
        )
        if not fit_results:
            console.log("\nThere are not enough beta columns for model free calculation.\n")
            return
        update_data = {"model_free_results": {params["fit_method"]: fit_results}}
        self.handle_request_cycle(
            "series_data", OperationType.UPDATE_SERIES, series_name=series_name, update_data=update_data
        )
        self.main_tab.sub_sidebar.model_free_sub_bar.update_fit_results(fit_results)

    def _handle_plot_model_fit_result(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            console.log("\nIt is necessary to select a series for plot model fit result\n")
            return
        fit_method = params.get("fit_method")
        reaction_n = params.get("reaction_n")
        beta = params.get("beta")
        model = params.get("model")
        is_annotate = params.get("is_annotate")

        keys = [series_name, "model_fit_results", fit_method, reaction_n, beta]
        result_df = self.handle_request_cycle("series_data", OperationType.GET_SERIES_VALUE, keys=keys)
        if not self._is_valid_result_data(result_df, series_name, fit_method):
            return
        params["model_series"] = result_df[result_df["Model"] == model].copy()

        series_entry: dict = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        experimental_df = series_entry.get("experimental_data")
        deconvolution_results = series_entry.get("deconvolution_results", {})
        reaction_df = self.main_tab.sub_sidebar.series_sub_bar.get_reaction_dataframe(
            experimental_df, deconvolution_results, reaction_n=reaction_n
        )
        params["reaction_df"] = reaction_df[["temperature", int(beta)]]
        plot_data_and_kwargs = self.handle_request_cycle(
            "model_fit_calculation", OperationType.PLOT_MODEL_FIT_RESULT, calculation_params=params
        )
        if plot_data_and_kwargs == []:
            console.log(f"\nNo plot results were found for {fit_method}: {model}\n")
            return
        if not is_annotate:
            plot_data_and_kwargs[0]["plot_kwargs"]["annotation"] = is_annotate
        self.main_tab.plot_canvas.plot_model_fit_result(plot_data_and_kwargs)

    def _handle_plot_model_free_result(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            console.log("\nIt is necessary to select a series for plot model fit result\n")
            return
        fit_method = params.get("fit_method")
        reaction_n = params.get("reaction_n")
        is_annotate = params.get("is_annotate")

        keys = [series_name, "model_free_results", fit_method, reaction_n]
        result_data = self.handle_request_cycle("series_data", OperationType.GET_SERIES_VALUE, keys=keys)
        if not self._is_valid_result_data(result_data, series_name, fit_method):
            return

        if fit_method == "master plots":
            master_plot = params.get("master_plot")
            beta = params.get("beta")
            result_data = result_data[master_plot][int(beta)]

        params["result_df"] = result_data
        plot_data_and_kwargs = self.handle_request_cycle(
            "model_free_calculation", OperationType.PLOT_MODEL_FREE_RESULT, calculation_params=params
        )
        if not is_annotate:
            plot_data_and_kwargs[0]["plot_kwargs"]["annotation"] = is_annotate
        self.main_tab.plot_canvas.plot_model_free_result(plot_data_and_kwargs)

    def _handle_get_model_free_reaction_df(self, params: dict):
        series_name = params.get("series_name")
        fit_method = params.get("fit_method")
        reaction_n = params.get("reaction_n")

        if fit_method == "master plots":
            return

        keys = [series_name, "model_free_results", fit_method, reaction_n]

        result_df = self.handle_request_cycle("series_data", OperationType.GET_SERIES_VALUE, keys=keys)
        if not self._is_valid_result_data(result_df, series_name, fit_method):
            return
        self.main_tab.sub_sidebar.model_free_sub_bar.update_results_table(result_df)

    def _handle_get_model_fit_reaction_df(self, params: dict):
        series_name = params.get("series_name")
        fit_method = params.get("fit_method")
        reaction_n = params.get("reaction_n")
        beta = params.get("beta")

        keys = [series_name, "model_fit_results", fit_method, reaction_n, beta]

        result_df = self.handle_request_cycle("series_data", OperationType.GET_SERIES_VALUE, keys=keys)
        if not self._is_valid_result_data(result_df, series_name, fit_method):
            return
        self.main_tab.sub_sidebar.model_fit_sub_bar.update_results_table(result_df)

    def _handle_model_fit_calculation(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            console.log("\nIt is necessary to select a series for calculation\n")
            return

        series_entry = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        experimental_df = series_entry.get("experimental_data")
        deconvolution_results = series_entry.get("deconvolution_results", {})
        if not deconvolution_results:
            console.log(
                f"\nSeries '{series_name}' should be divided into reactions by deconvolution.\n"
                "Load deconvolution data in series working space.\n"
            )
            return

        reactions, _ = self.main_tab.sub_sidebar.series_sub_bar.check_missing_reactions(
            experimental_df, deconvolution_results
        )
        params["reaction_data"] = {
            reaction: self.main_tab.sub_sidebar.series_sub_bar.get_reaction_dataframe(
                experimental_df, deconvolution_results, reaction_n=reaction
            )
            for reaction in reactions
        }
        fit_results = self.handle_request_cycle(
            "model_fit_calculation", OperationType.MODEL_FIT_CALCULATION, calculation_params=params
        )
        update_data = {"model_fit_results": {params["fit_method"]: fit_results}}
        self.handle_request_cycle(
            "series_data", OperationType.UPDATE_SERIES, series_name=series_name, update_data=update_data
        )
        self.main_tab.sub_sidebar.model_fit_sub_bar.update_fit_results(fit_results)

    def _handle_load_deconvolution_results(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            logger.error("No series_name provided for deconvolution results.")
            return

        deconvolution_results = params.get("deconvolution_results", {})
        update_data = {"deconvolution_results": deconvolution_results}
        is_ok = self.handle_request_cycle(
            "series_data",
            OperationType.UPDATE_SERIES,
            series_name=series_name,
            update_data=update_data,
        )
        if not is_ok:
            logger.error(f"Failed to update deconvolution results for series '{series_name}'.")
        self._handle_select_series(params)

    def _handle_select_series(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            logger.error("No series_name provided for SELECT_SERIES")
            return

        series_entry = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        if not series_entry:
            logger.warning(f"Couldn't get data for the series '{series_name}'")
            return

        reaction_scheme = series_entry.get("reaction_scheme")
        calculation_settings = series_entry.get("calculation_settings")
        series_df = series_entry.get("experimental_data")
        deconvolution_results = series_entry.get("deconvolution_results", {})
        if not reaction_scheme:
            logger.warning(f"Couldn't get a scheme for the series '{series_name}'")
            return

        if deconvolution_results == {}:
            self.main_tab.plot_canvas.plot_data_from_dataframe(series_df)
        else:
            reaction_n = params.get("reaction_n", "reaction_0")
            reaction_df = self.main_tab.sub_sidebar.series_sub_bar.get_reaction_dataframe(
                series_df, deconvolution_results, reaction_n
            )
            self.main_tab.plot_canvas.plot_data_from_dataframe(reaction_df)
        self.main_tab.sub_sidebar.model_based.update_scheme_data(reaction_scheme)
        self.main_tab.sub_sidebar.model_based.update_calculation_settings(calculation_settings)
        self.main_tab.sub_sidebar.series_sub_bar.update_series_ui(series_df, deconvolution_results)

    def _handle_model_params_change(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            logger.error("No series_name provided for MODEL_PARAMS_CHANGE")
            return

        is_ok = self.handle_request_cycle("series_data", OperationType.SCHEME_CHANGE, **params)
        if not is_ok:
            logger.error("Failed to update scheme in series_data for MODEL_PARAMS_CHANGE")
            return

        series_entry = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        if not series_entry["reaction_scheme"]:
            logger.warning(f"Не удалось получить схему серии '{series_name}' после обновления.")
            return

        self.main_tab.sub_sidebar.model_based.update_scheme_data(series_entry["reaction_scheme"])
        self.main_tab.sub_sidebar.model_based.update_calculation_settings(series_entry["calculation_settings"])
        if params.get("is_calculate"):
            self.update_model_simulation(series_name)

    def _handle_scheme_change(self, params: dict):
        is_ok = self.handle_request_cycle("series_data", OperationType.SCHEME_CHANGE, **params)
        if not is_ok:
            logger.error("Failed to update scheme in series_data")

        series_name = params.get("series_name")
        if not series_name:
            logger.error("No series_name provided for SCHEME_CHANGE")
            return

        scheme_data = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="scheme"
        )
        if not scheme_data:
            logger.warning(f"Не удалось получить схему для серии '{series_name}'")
            return

        self.main_tab.sub_sidebar.model_based.update_scheme_data(scheme_data)
        self.update_model_simulation(series_name)

    def _handle_differential(self, params):
        params["function"] = self.handle_request_cycle("active_file_operations", OperationType.DIFFERENTIAL)
        is_modifyed = self.handle_request_cycle("file_data", OperationType.DIFFERENTIAL, **params)
        if is_modifyed:
            df = self.handle_request_cycle("file_data", OperationType.GET_DF_DATA, **params)
            self.main_tab.plot_canvas.plot_data_from_dataframe(df)
        else:
            logger.error(f"{self.actor_name} no response in handle_request_from_main_tab")

    def _handle_add_reaction(self, params):
        is_ok = self.handle_request_cycle("calculations_data_operations", OperationType.ADD_REACTION, **params)
        if not is_ok:
            console.log("\n\nit is necessary to bring the data to da/dT.\nexperiments -> your experiment -> da/dT")
            self.main_tab.sub_sidebar.deconvolution_sub_bar.reactions_table.on_fail_add_reaction()

    def _handle_highlight_reaction(self, params):
        df = self.handle_request_cycle("file_data", OperationType.GET_DF_DATA, **params)
        self.main_tab.plot_canvas.plot_data_from_dataframe(df)
        is_ok = self.handle_request_cycle("calculations_data_operations", OperationType.HIGHLIGHT_REACTION, **params)
        logger.debug(f"{OperationType.HIGHLIGHT_REACTION=} {is_ok=}")

    def _handle_remove_reaction(self, params):
        is_ok = self.handle_request_cycle("calculations_data_operations", OperationType.REMOVE_REACTION, **params)
        logger.debug(f"{OperationType.REMOVE_REACTION=} {is_ok=}")

    def _handle_update_value(self, params):
        target = params.pop("target", "calculations_data_operations")
        is_ok = self.handle_request_cycle(target, OperationType.UPDATE_VALUE, **params)
        logger.debug(f"{OperationType.UPDATE_VALUE=} {is_ok=}")

    def _handle_reset_file_data(self, params):
        is_ok = self.handle_request_cycle("file_data", OperationType.RESET_FILE_DATA, **params)
        df = self.handle_request_cycle("file_data", OperationType.GET_DF_DATA, **params)
        self.main_tab.plot_canvas.plot_data_from_dataframe(df)
        logger.debug(f"{OperationType.RESET_FILE_DATA=} {is_ok=}")

    def _handle_import_reactions(self, params):
        data = self.handle_request_cycle("calculations_data", OperationType.IMPORT_REACTIONS, **params)
        self.main_tab.update_reactions_table(data)

    def _handle_export_reactions(self, params):
        data = self.handle_request_cycle("calculations_data", OperationType.GET_VALUE, **params)
        suggested_file_name = params["function"](params["file_name"], data)
        self.main_tab.sub_sidebar.deconvolution_sub_bar.file_transfer_buttons.export_reactions(
            data, suggested_file_name
        )

    def _handle_deconvolution(self, params):
        data = self.handle_request_cycle("calculations_data_operations", OperationType.DECONVOLUTION, **params)
        logger.debug(f"{data=}")

    def _handle_stop_calculation(self, params):
        _ = self.handle_request_cycle("calculations", OperationType.STOP_CALCULATION)

    def _handle_add_new_series(self, params):
        df_copies = self.handle_request_cycle("file_data", OperationType.GET_ALL_DATA, file_name="all_files")
        series_name, selected_files = self.main_tab.sidebar.open_add_series_dialog(df_copies)
        if not series_name or not selected_files:
            logger.warning(f"{self.actor_name} user canceled or gave invalid input for new series.")
            return

        df_with_rates = {}
        experimental_masses = []
        for file_name, heating_rate, mass in selected_files:
            experimental_masses.append(mass)
            df = df_copies[file_name].copy()
            other_col = None
            for col in df.columns:
                if col.lower() != "temperature":
                    other_col = col

            rate_col_name = str(heating_rate)
            if rate_col_name in df_with_rates:
                logger.error(
                    f"Duplicate heating rate '{heating_rate}' for file '{file_name}'. "
                    "Each heating rate must be unique."
                )
                continue

            df.rename(columns={other_col: rate_col_name}, inplace=True)
            df_with_rates[file_name] = df

        merged_df = reduce(
            lambda left, right: pd.merge(left, right, on="temperature", how="outer"), df_with_rates.values()
        )
        merged_df.sort_values(by="temperature", inplace=True)
        merged_df.interpolate(method="linear", inplace=True)

        self.main_tab.plot_canvas.plot_data_from_dataframe(merged_df)

        is_ok = self.handle_request_cycle(
            "series_data",
            OperationType.ADD_NEW_SERIES,
            experimental_masses=experimental_masses,
            data=merged_df,
            name=series_name,
        )

        if is_ok:
            self.main_tab.sidebar.add_series(series_name)
            series_entry = self.handle_request_cycle(
                "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
            )
            if series_entry["reaction_scheme"]:
                self.main_tab.sub_sidebar.model_based.update_scheme_data(series_entry["reaction_scheme"])
                self.main_tab.sub_sidebar.model_based.update_calculation_settings(series_entry["calculation_settings"])
            else:
                logger.warning("It was not possible to obtain a reaction diagram for added series.")
        else:
            logger.error(f"Couldn't add a series: {series_name}")

    def _handle_delete_series(self, params):
        is_ok = self.handle_request_cycle("series_data", OperationType.DELETE_SERIES, **params)
        logger.debug(f"{OperationType.DELETE_SERIES=} {is_ok=}")

    def _handle_model_based_calculation(self, params: dict):
        series_name = params.get("series_name")
        if not series_name:
            logger.error("No series_name provided for MODEL_BASED_CALCULATION")
            return

        series_entry = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        if not series_entry:
            logger.error(f"Series entry not found for series '{series_name}'")
            return

        params["calculation_scenario"] = "model_based_calculation"
        params["reaction_scheme"] = series_entry.get("reaction_scheme")
        params["experimental_data"] = series_entry.get("experimental_data")
        params["calculation_settings"] = series_entry.get("calculation_settings")

        logger.debug(f"Emitting model_based_calculation_signal with params: {params}")
        self.model_based_calculation_signal.emit(params)

    def update_model_simulation(self, series_name: str):
        series_entry = self.handle_request_cycle(
            "series_data", OperationType.GET_SERIES, series_name=series_name, info_type="all"
        )
        reaction_scheme = series_entry.get("reaction_scheme")
        experimental_data = series_entry.get("experimental_data")
        simulation_df = self.main_tab.sub_sidebar.model_based._simulate_reaction_model(
            experimental_data, reaction_scheme
        )

        for col in simulation_df.columns:
            if col == "temperature":
                continue

            self.main_tab.plot_canvas.add_or_update_line(
                f"simulation_{col}",
                simulation_df["temperature"],
                simulation_df[col],
                linestyle="--",
                label=f"Simulation β={col}",
            )

    def _is_valid_result_data(self, result_df, series_name=None, fit_method=None):
        if not isinstance(result_df, pd.DataFrame):
            if result_df in ({}, None):
                if series_name and fit_method:
                    console.log(f"\nNo calculation results were found for {series_name}: {fit_method}\n")
                return False
        if isinstance(result_df, pd.DataFrame):
            if result_df.empty:
                console.log("\nThe model fit result is empty.\n")
            return False
        return True
