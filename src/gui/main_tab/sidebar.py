from os import path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import OperationType, SideBarNames
from src.core.logger_config import logger
from src.gui.main_tab.load_file_button import LoadButton


class SideBar(QWidget):
    """
    A sidebar widget that provides flat lists for navigating through project data,
    experiments, and series. It includes actions for adding, deleting, and selecting files
    for experiments, as well as managing series.
    """

    file_selected = pyqtSignal(tuple)
    sub_side_bar_needed = pyqtSignal(str)
    chosen_experiment_signal = pyqtSignal(str)
    active_file_selected = pyqtSignal(str)
    active_series_selected = pyqtSignal(str)
    to_main_window_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize sidebar with FILES and SERIES sections as flat lists."""
        super().__init__(parent)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # FILES section
        files_label = QLabel("FILES")
        files_label.setObjectName("section_header")
        main_layout.addWidget(files_label)

        self.files_list = QListWidget()
        self.files_list.setObjectName("sidebar_tree")
        self.files_list.currentItemChanged.connect(self._on_files_item_changed)
        main_layout.addWidget(self.files_list, stretch=1)

        files_btns = QHBoxLayout()
        files_btns.setContentsMargins(8, 4, 8, 4)
        load_file_btn = QPushButton("Load File")
        load_file_btn.setObjectName("btn_small")
        import_file_btn = QPushButton("Import File")
        import_file_btn.setObjectName("btn_ghost")
        files_btns.addWidget(load_file_btn)
        files_btns.addWidget(import_file_btn)
        main_layout.addLayout(files_btns)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("sidebar_separator")
        main_layout.addWidget(separator)

        # SERIES section
        series_label = QLabel("SERIES")
        series_label.setObjectName("section_header")
        main_layout.addWidget(series_label)

        self.series_list = QListWidget()
        self.series_list.setObjectName("sidebar_tree")
        self.series_list.currentItemChanged.connect(self._on_series_item_changed)
        main_layout.addWidget(self.series_list, stretch=1)

        series_btns = QHBoxLayout()
        series_btns.setContentsMargins(8, 4, 8, 4)
        load_series_btn = QPushButton("Load Series")
        load_series_btn.setObjectName("btn_small")
        import_series_btn = QPushButton("Import Series")
        import_series_btn.setObjectName("btn_ghost")
        series_btns.addWidget(load_series_btn)
        series_btns.addWidget(import_series_btn)
        main_layout.addLayout(series_btns)

        self.setLayout(main_layout)

        self.load_button = LoadButton(self)
        self.load_button.file_selected.connect(self.add_experiment_file)
        load_file_btn.clicked.connect(self.load_button.open_file_dialog)
        import_file_btn.clicked.connect(self._import_file_stub)
        load_series_btn.clicked.connect(self.add_new_series)
        import_series_btn.clicked.connect(self.import_series)

        self.active_file_item = None
        self.active_series_item = None

    def mark_as_active(self, item, is_series=False):
        """
        Marks the provided item as active by making its font bold.
        Differentiates between experiments and series.

        Args:
            item: The QListWidgetItem to mark as active.
            is_series (bool): Whether the item is a series.
        """
        if is_series:
            if self.active_file_item:
                self.unmark_active_state(self.active_file_item)
                self.active_file_item = None
            if self.active_series_item:
                self.unmark_active_state(self.active_series_item)
            self.mark_active_state(item)
            self.active_series_item = item
            self.active_series_selected.emit(item.text())
            logger.debug(f"Active series: {item.text()}")
        else:
            if self.active_series_item:
                self.unmark_active_state(self.active_series_item)
                self.active_series_item = None
            if self.active_file_item:
                self.unmark_active_state(self.active_file_item)
            self.mark_active_state(item)
            self.active_file_item = item
            self.active_file_selected.emit(item.text())
            logger.debug(f"Active file: {item.text()}")

    def mark_active_state(self, item):
        """Applies bold font style to the given item to indicate it's active."""
        font = item.font()
        font.setBold(True)
        item.setFont(font)

    def unmark_active_state(self, item):
        """Removes bold font style from the given item to indicate it's not active anymore."""
        font = item.font()
        font.setBold(False)
        item.setFont(font)

    def _on_files_item_changed(self, current, previous):
        """Handle selection change in the FILES list."""
        if current is not None:
            self.sub_side_bar_needed.emit(SideBarNames.EXPERIMENTS.value)
            self.chosen_experiment_signal.emit(current.text())
            self.mark_as_active(current)

    def _on_series_item_changed(self, current, previous):
        """Handle selection change in the SERIES list."""
        if current is not None:
            self.sub_side_bar_needed.emit(SideBarNames.SERIES.value)
            self.mark_as_active(current, is_series=True)
            logger.debug(f"Selected series: {current.text()}")

    def add_new_series(self):
        """Sends a request to get all data keys for series creation."""
        logger.debug("Add New Series clicked.")
        request = {"operation": OperationType.ADD_NEW_SERIES}
        self.to_main_window_signal.emit(request)

    def open_add_series_dialog(self, df_copies):
        """
        Opens a dialog to allow the user to select files for the new series along with heating rates.

        Args:
            df_copies (dict): A dictionary of file names to their corresponding dataframes.
        """
        while True:
            dialog = SelectFileDataDialog(df_copies, self)
            result = dialog.exec()

            if result == QDialog.DialogCode.Rejected:
                return None, []

            series_name, selected_files = dialog.get_selected_files()

            if series_name and selected_files:
                return series_name, selected_files

    def _import_file_stub(self):
        """Placeholder for Import File — not yet implemented."""
        QMessageBox.information(self, "Import File", "Import File functionality is not yet implemented.")

    def import_series(self):
        """Placeholder for Import Series — not yet implemented."""
        QMessageBox.information(self, "Import Series", "Import Series functionality is not yet implemented.")
        logger.debug("Import Series clicked. Functionality not implemented.")

    def delete_series(self):
        """Deletes the active series if it exists."""
        if self.active_series_item:
            series_name = self.active_series_item.text()
            reply = QMessageBox.question(
                self,
                "Delete Series",
                f"Are you sure you want to delete the series '{series_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                row = self.series_list.row(self.active_series_item)
                self.series_list.takeItem(row)
                self.to_main_window_signal.emit({"operation": OperationType.DELETE_SERIES, "series_name": series_name})
                logger.info(f"Series deleted: {series_name}")
                self.active_series_item = None
        else:
            QMessageBox.warning(self, "Deletion Error", "No active series selected to delete.")
            logger.warning("Delete Series clicked, but no active series is selected.")

    def add_experiment_file(self, file_info):
        """
        Adds a new experiment file to the sidebar and makes it the active file.

        Args:
            file_info: A tuple containing the file path and other relevant info.
        """
        file_name = path.basename(file_info[0])
        new_item = QListWidgetItem(file_name)
        self.files_list.addItem(new_item)
        self.mark_as_active(new_item)
        self.sub_side_bar_needed.emit(SideBarNames.EXPERIMENTS.value)
        logger.debug(f"New file added and set as active: {file_name}")

    def delete_active_file(self):
        """Deletes the currently active file from the list. Shows warning if nothing selected."""
        if not self.active_file_item:
            QMessageBox.warning(self, "Error", "Please select a file to delete.")
            return

        file_name = self.active_file_item.text()
        row = self.files_list.row(self.active_file_item)
        self.files_list.takeItem(row)
        logger.debug(f"File deleted: {file_name}")
        self.active_file_item = None

    def get_experiment_files_names(self) -> list[str]:
        """Returns a list of names of all experiment files currently listed in the sidebar."""
        return [self.files_list.item(i).text() for i in range(self.files_list.count())]

    def get_series_names(self) -> list[str]:
        """Returns a list of names of all series currently listed in the sidebar."""
        return [self.series_list.item(i).text() for i in range(self.series_list.count())]

    def add_series(self, series_name: str):
        """Add new series item to the list if name is valid and unique."""
        if not series_name:
            logger.warning("An empty series name will not be added.")
            return

        for i in range(self.series_list.count()):
            if self.series_list.item(i).text() == series_name:
                logger.warning(f"Series '{series_name}' already exists.")
                QMessageBox.warning(
                    self,
                    "Duplicate series",
                    f"A series with the name '{series_name}' already exists.",
                )
                return

        new_item = QListWidgetItem(series_name)
        self.series_list.insertItem(0, new_item)
        logger.info(f"New series added: {series_name}")


class SelectFileDataDialog(QDialog):
    """
    Dialog for selecting multiple files and heating rates for series creation.

    Provides interface for choosing experiment files and specifying their
    corresponding heating rates for multi-rate kinetic analysis.
    """

    def __init__(self, df_copies, parent=None):
        """Initialize file selection dialog with checkboxes and heating rate inputs."""
        super().__init__(parent)
        self.setWindowTitle("Select Files for Series")
        self.selected_files = []
        self.checkboxes = []
        self.rate_line_edits = []
        layout = QVBoxLayout()

        label = QLabel("Select files to include in the series:")
        layout.addWidget(label)

        self.series_name_line_edit = QLineEdit()
        self.series_name_line_edit.setPlaceholderText("Enter series name")
        layout.addWidget(self.series_name_line_edit)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        for file_name in df_copies.keys():
            file_layout = QHBoxLayout()

            checkbox = QCheckBox(file_name)

            rate_line_edit = QLineEdit()
            rate_line_edit.setPlaceholderText("Enter heating rate")

            file_layout.addWidget(checkbox)
            file_layout.addWidget(rate_line_edit)
            scroll_layout.addLayout(file_layout)

            self.checkboxes.append(checkbox)
            self.rate_line_edits.append(rate_line_edit)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        button_box = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_box.addWidget(self.ok_button)
        button_box.addWidget(self.cancel_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_files(self):
        series_name = self.series_name_line_edit.text().strip()
        if not series_name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a series name.")
            return None, []

        selected_files = []
        for checkbox, rate_line_edit in zip(self.checkboxes, self.rate_line_edits):
            if checkbox.isChecked():
                rate_text = rate_line_edit.text().strip()
                if not rate_text:
                    QMessageBox.warning(self, "Invalid Input", f"Please enter a heating rate for '{checkbox.text()}'")
                    return None, []

                try:
                    heating_rate = float(rate_text)
                except ValueError:
                    QMessageBox.warning(
                        self, "Invalid Input", f"Please enter a valid number heating rate for '{checkbox.text()}'"
                    )
                    return None, []

                selected_files.append((checkbox.text(), heating_rate, 1))  # 1 is mass for future use

        return series_name, selected_files
