"""
Tab container management for the main application window.
Handles tab creation, organization, and navigation between different views.
"""

from PyQt6.QtWidgets import QTabWidget

from src.core.logger_config import logger
from src.gui.config import get_localization
from src.gui.main_tab.main_tab import MainTab
from src.gui.table_tab.table_tab import TableTab


class TabContainer:
    """
    Manages the main application tab container with all tabs.

    Responsibilities:
    - Tab creation and initialization
    - Tab organization and layout
    - Navigation between tabs
    - Tab-specific configuration
    """

    def __init__(self, parent=None):
        """
        Initialize the tab container.

        Args:
            parent: Parent widget for the tab container
        """
        self.parent = parent
        self.loc = get_localization()

        # Create tab widget
        self.tabs = QTabWidget(parent)

        # Initialize tabs
        self._create_tabs()
        self._setup_tabs()

        logger.debug("TabContainer initialized successfully")

    def _create_tabs(self):
        """Create all application tabs."""
        # Main analysis tab
        self.main_tab = MainTab(self.parent)

        # Table/data view tab
        self.table_tab = TableTab(self.parent)

        logger.debug("All tabs created successfully")

    def _setup_tabs(self):
        """Setup tabs in the tab widget with proper titles."""
        # Add tabs with localized titles
        self.tabs.addTab(self.main_tab, self.loc.get_string("application.tabs.main"))
        self.tabs.addTab(self.table_tab, self.loc.get_string("application.tabs.analysis"))

        logger.debug("Tab setup completed")

    def get_widget(self):
        """
        Get the main tab widget for embedding in parent window.

        Returns:
            QTabWidget: The configured tab widget
        """
        return self.tabs

    def get_main_tab(self):
        """
        Get reference to the main analysis tab.

        Returns:
            MainTab: The main analysis tab instance
        """
        return self.main_tab

    def get_table_tab(self):
        """
        Get reference to the table/data view tab.

        Returns:
            TableTab: The table tab instance
        """
        return self.table_tab

    def switch_to_main_tab(self):
        """Switch to the main analysis tab."""
        self.tabs.setCurrentWidget(self.main_tab)
        logger.debug("Switched to main tab")

    def switch_to_table_tab(self):
        """Switch to the table/data view tab."""
        self.tabs.setCurrentWidget(self.table_tab)
        logger.debug("Switched to table tab")

    def current_tab_index(self):
        """
        Get the index of the currently active tab.

        Returns:
            int: Index of the current tab
        """
        return self.tabs.currentIndex()

    def current_tab_name(self):
        """
        Get the name of the currently active tab.

        Returns:
            str: Name of the current tab
        """
        return self.tabs.tabText(self.tabs.currentIndex())
