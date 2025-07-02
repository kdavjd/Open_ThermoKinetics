"""
User Guide Tab
Complete implementation of the user guide interface using the new framework.
"""

from pathlib import Path

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.core.logger_config import LoggerManager
from src.gui.user_guide_tab.user_guide_framework import GuideFramework

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class UserGuideTab(QWidget):
    """
    Main user guide tab widget that provides comprehensive documentation
    for Open ThermoKinetics application using the new framework.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing UserGuideTab")
        self.setup_ui()
        logger.debug("UserGuideTab initialization completed")

    def setup_ui(self):
        """Initialize the UI components"""
        logger.debug("Setting up UserGuideTab UI components")

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Get data directory path
        data_dir = Path(__file__).parent / "user_guide_framework" / "data"
        logger.debug(f"Loading guide data from: {data_dir}")

        # Create and add the guide framework
        try:
            self.guide_framework = GuideFramework(data_dir, self)
            layout.addWidget(self.guide_framework)
            logger.info("GuideFramework successfully created and added to layout")
        except Exception as e:
            logger.error(f"Failed to create GuideFramework: {e}")
            raise

        # Set minimum size
        self.setMinimumSize(1200, 700)
        logger.debug("UserGuideTab UI setup completed")

    def change_language(self, language_code: str):
        """Change the interface language"""
        logger.info(f"Changing language to: {language_code}")
        try:
            self.guide_framework.set_language(language_code)
            logger.debug(f"Language successfully changed to: {language_code}")
        except Exception as e:
            logger.error(f"Failed to change language to {language_code}: {e}")
            raise

    def set_section(self, section_id: str):
        """Set current section programmatically"""
        logger.info(f"Setting section to: {section_id}")
        try:
            self.guide_framework.set_section(section_id)
            logger.debug(f"Section successfully set to: {section_id}")
        except Exception as e:
            logger.error(f"Failed to set section to {section_id}: {e}")
            raise

    def get_current_section(self):
        """Get current section"""
        try:
            current_section = self.guide_framework.get_current_section()
            logger.debug(f"Current section: {current_section}")
            return current_section
        except Exception as e:
            logger.error(f"Failed to get current section: {e}")
            raise

    def get_current_language(self):
        """Get current language"""
        try:
            current_language = self.guide_framework.get_current_language()
            logger.debug(f"Current language: {current_language}")
            return current_language
        except Exception as e:
            logger.error(f"Failed to get current language: {e}")
            raise
