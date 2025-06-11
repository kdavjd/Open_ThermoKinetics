"""
User Guide Tab
Complete implementation of the user guide interface using the new framework.
"""

from pathlib import Path

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from ..user_guide_framework import GuideFramework


class UserGuideTab(QWidget):
    """
    Main user guide tab widget that provides comprehensive documentation
    for Open ThermoKinetics application using the new framework.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Get data directory path
        data_dir = Path(__file__).parent.parent / "user_guide_framework" / "data"

        # Create and add the guide framework
        self.guide_framework = GuideFramework(data_dir, self)
        layout.addWidget(self.guide_framework)

        # Set minimum size
        self.setMinimumSize(1200, 700)

    def change_language(self, language_code: str):
        """Change the interface language"""
        self.guide_framework.set_language(language_code)

    def set_section(self, section_id: str):
        """Set current section programmatically"""
        self.guide_framework.set_section(section_id)

    def get_current_section(self):
        """Get current section"""
        return self.guide_framework.get_current_section()

    def get_current_language(self):
        """Get current language"""
        return self.guide_framework.get_current_language()
