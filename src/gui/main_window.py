from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from src.core.basic_signals import BasicSignals, SignalDispatcher
from src.core.logger_config import logger
from src.core.logger_console import LoggerConsole as console
from src.gui.main_tab.main_tab import MainTab
from src.gui.table_tab.table_tab import TableTab


class MainWindow(QMainWindow):
    to_main_tab_signal = pyqtSignal(dict)

    def __init__(self, dispatcher: SignalDispatcher):
        super().__init__()
        self.setWindowTitle("Кинетика твердофазных реакций")

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.main_tab = MainTab(self)
        self.table_tab = TableTab(self)

        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.table_tab, "Table")

        self.dispatcher = dispatcher
        self.actor_name = "main_window"

        # Экземпляр BasicSignals для делегирования запросов
        self.basic_signals = BasicSignals(actor_name=self.actor_name, dispatcher=self.dispatcher)

        # Регистрация методов в диспетчере
        self.dispatcher.register_component(self.actor_name, self.process_request, self.process_response)

        # Подключение сигналов
        self.main_tab.to_main_window_signal.connect(self.handle_request_from_main_tab)
        self.to_main_tab_signal.connect(self.main_tab.response_slot)

        logger.debug(f"{self.actor_name} инициализирован и подключен к сигналам диспетчера.")

    @pyqtSlot(dict)
    def process_request(self, params: dict):
        """
        Обработка входящих запросов.
        """
        operation = params.get("operation")
        actor = params.get("actor")
        logger.debug(f"{self.actor_name} обрабатывает запрос '{operation}' от '{actor}'")

    @pyqtSlot(dict)
    def process_response(self, params: dict):
        """
        Обработка входящих ответов.
        """
        logger.debug(f"{self.actor_name} received response: {params}")
        self.basic_signals.process_response(params)

    def handle_request_cycle(self, target: str, operation: str, **kwargs):
        """
        Делегирование вызова handle_request_cycle из BasicSignals.
        """
        result = self.basic_signals.handle_request_cycle(target, operation, **kwargs)
        logger.debug(f"handle_request_cycle result for '{operation}': {result}")
        return result

    @pyqtSlot(dict)
    def handle_request_from_main_tab(self, params: dict):  # noqa: C901
        """
        Обработка запросов от main_tab и их маршрутизация через BasicSignals.
        """
        operation = params.pop("operation")

        logger.debug(f"{self.actor_name} получил запрос на '{operation}")

        if operation == "differential":
            params["function"] = self.handle_request_cycle("active_file_operations", operation)
            is_modifyed = self.handle_request_cycle("file_data", operation, **params)
            if is_modifyed:
                df = self.handle_request_cycle("file_data", "get_df_data", **params)
                self.main_tab.plot_canvas.plot_file_data_from_dataframe(df)
            else:
                logger.error(f"{self.actor_name} не получил ответ от file_data")

        if operation == "add_reaction":
            is_ok = self.handle_request_cycle("calculations_data_operations", operation, **params)
            if not is_ok:
                console.log(
                    "Перед добвлением реакции необходимо привести данные к da/dT. Данные экспериментов ->\
                     выберите эксперимент -> Привести к da/dT"
                )
                self.main_tab.sub_sidebar.deconvolution_sub_bar.reactions_table.on_fail_add_reaction()
                return

        if operation == "highlight_reaction":
            df = self.handle_request_cycle("file_data", "get_df_data", **params)
            self.main_tab.plot_canvas.plot_file_data_from_dataframe(df)
            is_ok = self.handle_request_cycle("calculations_data_operations", operation, **params)
            logger.debug(f"{operation=} {is_ok=}")

        if operation == "remove_reaction":
            is_ok = self.handle_request_cycle("calculations_data_operations", operation, **params)
            logger.debug(f"{operation=} {is_ok=}")

        if operation == "update_value":
            is_ok = self.handle_request_cycle("calculations_data_operations", operation, **params)
            logger.debug(f"{operation=} {is_ok=}")

        if operation == "reset":
            is_ok = self.handle_request_cycle("file_data", operation, **params)
            df = self.handle_request_cycle("file_data", "get_df_data", **params)
            self.main_tab.plot_canvas.plot_file_data_from_dataframe(df)
            logger.debug(f"{operation=} {is_ok=}")

        if operation == "import_reactions":
            data = self.handle_request_cycle("calculations_data", operation, **params)
            self.main_tab.update_reactions_table(data)

        if operation == "export_reactions":
            data = self.handle_request_cycle("calculations_data", "get_value", **params)
            suggested_file_name = params["function"](params["file_name"], data)
            self.main_tab.sub_sidebar.deconvolution_sub_bar.file_transfer_buttons.export_reactions(
                data, suggested_file_name
            )

        if operation == "deconvolution":
            data = self.handle_request_cycle("calculations_data_operations", operation, **params)
            logger.debug(f"{data=}")
        else:
            logger.error(f"{self.actor_name} не знает как обработать {operation},\n\n {params=}")
