from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget

from src.core.logger_console import LoggerConsole


class ConsoleWidget(QWidget):
    """Read-only console widget for displaying application log messages."""

    def __init__(self, parent=None):
        """Initialize console with read-only text edit and logger integration."""
        super().__init__(parent)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setObjectName("console_output")

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("btn_small")
        clear_btn.clicked.connect(self.text_edit.clear)

        header = QHBoxLayout()
        header.addStretch()
        header.addWidget(clear_btn)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addLayout(header)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        LoggerConsole.set_console(self)

    def log_message(self, message: str):
        """Append log message to the console text area."""
        self.text_edit.append(message)
