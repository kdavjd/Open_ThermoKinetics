import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class LoggerManager:
    """Centralized logger configuration manager following best practices."""

    _configured = False
    _root_logger_name = "solid_state_kinetics"

    @classmethod
    def configure_logging(
        cls,
        log_level: int = logging.INFO,
        console_level: Optional[int] = None,
        file_level: Optional[int] = None,
        log_file: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ) -> None:
        """
        Configure application-wide logging with both console and file handlers.

        Args:
            log_level: Default logging level for all handlers
            console_level: Specific level for console output (defaults to log_level)
            file_level: Specific level for file output (defaults to DEBUG)
            log_file: Path to log file (defaults to logs/solid_state_kinetics.log)
            max_file_size: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        if cls._configured:
            return

        # Set default levels
        console_level = console_level or log_level
        file_level = file_level or logging.DEBUG

        # Get or create root logger for the application
        root_logger = logging.getLogger(cls._root_logger_name)
        root_logger.setLevel(logging.DEBUG)

        # Clear any existing handlers to avoid duplicates
        root_logger.handlers.clear()  # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s", datefmt="%H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File handler with rotation
        if log_file is None:
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            log_file = logs_dir / "solid_state_kinetics.log"

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

        # Log the configuration
        root_logger.info("Logging configured successfully")
        console_level_name = logging.getLevelName(console_level)
        root_logger.info(f"Console level: {console_level_name}")
        file_level_name = logging.getLevelName(file_level)
        root_logger.info(f"File level: {file_level_name}")
        root_logger.info(f"Log file: {log_file}")

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for the specified module.

        Args:
            name: Logger name (typically __name__ of the module)

        Returns:
            Configured logger instance
        """
        # Ensure logging is configured
        if not cls._configured:
            cls.configure_logging()

        # Clean up module name for better readability
        clean_name = cls._clean_module_name(name)

        # Return child logger of the application root logger
        if clean_name.startswith(cls._root_logger_name):
            return logging.getLogger(clean_name)
        else:
            return logging.getLogger(f"{cls._root_logger_name}.{clean_name}")

    @classmethod
    def _clean_module_name(cls, module_name: str) -> str:
        """
        Clean module name to make it more readable in logs.

        Examples:
        - 'src.gui.main_window' -> 'gui.main_window'
        - 'src.core.base_signals' -> 'core.base_signals'
        - '__main__' -> 'main'
        """
        if module_name == "__main__":
            return "main"

        # Remove 'src.' prefix if present
        if module_name.startswith("src."):
            return module_name[4:]

        # Remove full path prefixes like 'solid_state_kinetics.src.'
        if "src." in module_name:
            parts = module_name.split("src.")
            if len(parts) > 1:
                return parts[-1]

        return module_name


def configure_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    Legacy function for backward compatibility with existing code.

    Args:
        log_level: Logging level (now affects console output level)

    Returns:
        Configured logger instance
    """
    # Configure logging if not already done
    LoggerManager.configure_logging(console_level=log_level)

    # Return a logger for the calling module
    import inspect

    frame = inspect.currentframe().f_back
    module_name = frame.f_globals.get("__name__", "unknown")

    return LoggerManager.get_logger(module_name)


# Initialize logging on module import
LoggerManager.configure_logging()


# Provide default logger instance for backward compatibility
# This creates a factory function that returns proper logger for each module
def get_module_logger():
    """Get a logger for the calling module."""
    import inspect

    frame = inspect.currentframe().f_back
    module_name = frame.f_globals.get("__name__", "unknown")
    return LoggerManager.get_logger(module_name)


# For backward compatibility, create a logger that appears to be from this module
logger = LoggerManager.get_logger("core.logger_config")
