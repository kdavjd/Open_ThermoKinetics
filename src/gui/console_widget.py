from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from src.core.logger_console import LoggerConsole


class ConsoleWidget(QWidget):
    """Read-only console widget for displaying application log messages."""

    def __init__(self, parent=None):
        """Initialize console with read-only text edit and logger integration."""
        super().__init__(parent)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        LoggerConsole.set_console(self)

    def log_message(self, message: str):
        """Append log message to the console text area."""
        self.text_edit.append(message)
