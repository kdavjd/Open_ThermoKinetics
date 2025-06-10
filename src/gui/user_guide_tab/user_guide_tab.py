"""
User Guide Tab
Complete implementation of the user guide interface for Open ThermoKinetics.
Replaces the table_tab with comprehensive documentation and navigation.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QSplitter, QWidget

from .config import GuideConfig, Language
from .guide_content_widget import GuideContentWidget
from .guide_sidebar import GuideSidebar


class UserGuideTab(QWidget):
    """
    Main user guide tab widget that provides comprehensive documentation
    for Open ThermoKinetics application with navigation and rich content display.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = GuideConfig()
        self.current_language = Language.RUSSIAN  # Default to Russian as per user preference
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setMinimumSize(self.config.MIN_WIDTH_SIDEBAR + self.config.MIN_WIDTH_CONTENT, self.config.MIN_HEIGHT_GUIDE)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for resizable layout
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)

        # Sidebar for navigation
        self.sidebar = GuideSidebar()
        self.sidebar.set_language(self.current_language)
        self.splitter.addWidget(self.sidebar)

        # Content widget for displaying guide content
        self.content_widget = GuideContentWidget()
        self.content_widget.set_language(self.current_language)
        self.splitter.addWidget(self.content_widget)

        # Set initial splitter sizes
        self.initialize_sizes()

    def setup_connections(self):
        """Connect signals between components"""
        # Navigation signals
        self.sidebar.section_selected.connect(self.content_widget.set_section)
        self.sidebar.language_changed.connect(self.change_language)

        # Internal content links
        self.content_widget.section_link_clicked.connect(self.sidebar.select_section)

    def initialize_sizes(self):
        """Set initial splitter sizes with proper proportions"""
        total_width = self.width() or 1000  # Fallback width
        sidebar_width = self.config.MIN_WIDTH_SIDEBAR
        content_width = total_width - sidebar_width

        if content_width < self.config.MIN_WIDTH_CONTENT:
            content_width = self.config.MIN_WIDTH_CONTENT
            total_width = sidebar_width + content_width

        self.splitter.setSizes([sidebar_width, content_width])

    def change_language(self, language: Language):
        """Change the interface language"""
        if language != self.current_language:
            self.current_language = language
            self.sidebar.set_language(language)
            self.content_widget.set_language(language)

    def resizeEvent(self, event):
        """Handle resize events to maintain proper proportions"""
        super().resizeEvent(event)  # Only reinitialize if the widget is visible and has a reasonable size
        if self.isVisible() and event.size().width() > 100:
            self.initialize_sizes()
