import logging
import sys
import unittest

from src.core.logger_config import configure_logger

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TestLogger(unittest.TestCase):
    def test_logger_configuration(self):
        log = configure_logger()
        assert isinstance(log, logging.Logger)
        # Child logger level is NOTSET (inherits from parent)
        # Effective level should be DEBUG from parent
        assert log.level == logging.NOTSET or log.level == logging.DEBUG

    def test_logger_has_handlers(self):
        configure_logger()
        # Parent logger has handlers
        parent = logging.getLogger("solid_state_kinetics")
        assert len(parent.handlers) > 0

    def test_logger_returns_valid_name(self):
        log = configure_logger()
        assert log.name.startswith("solid_state_kinetics")


if __name__ == "__main__":
    unittest.main()
