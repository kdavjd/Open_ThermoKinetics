class LoggerConsole:
    """Singleton console logger for GUI message display."""

    _instance = None
    _console = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerConsole, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_console(cls, console):
        """Set console widget for message output."""
        cls._console = console

    @classmethod
    def log(cls, message: str):
        """Log message to console widget if available."""
        if cls._console is not None:
            cls._console.log_message(message)
