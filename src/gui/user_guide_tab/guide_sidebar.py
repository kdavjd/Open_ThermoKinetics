"""
Guide Sidebar Widget
Navigation sidebar for the user guide with hierarchical section tree and language switching.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from .config import GUIDE_SECTIONS, GuideConfig, Language


class GuideSidebar(QWidget):
    """
    Sidebar widget for user guide navigation with language switching
    and hierarchical section tree.
    """

    section_selected = pyqtSignal(str)  # Emits section_id when section is selected
    language_changed = pyqtSignal(Language)  # Emits when language is changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = GuideConfig()
        self.current_language = Language.RUSSIAN
        self.section_items = {}  # Maps section_id to QTreeWidgetItem
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setMinimumWidth(self.config.MIN_WIDTH_SIDEBAR)
        self.setMaximumWidth(int(self.config.MIN_WIDTH_SIDEBAR * 1.5))

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Language selection
        self.setup_language_selector(layout)

        # Navigation tree
        self.setup_navigation_tree(layout)

    def setup_language_selector(self, parent_layout):
        """Create language selection controls"""
        lang_layout = QHBoxLayout()

        # Language label
        lang_label = QLabel("Язык / Language:")
        lang_label.setFont(QFont("Arial", self.config.BODY_FONT_SIZE, QFont.Weight.Bold))
        lang_layout.addWidget(lang_label)

        # Language combo box
        self.language_combo = QComboBox()
        self.language_combo.addItem("Русский", Language.RUSSIAN)
        self.language_combo.addItem("English", Language.ENGLISH)
        self.language_combo.setCurrentIndex(0)  # Default to Russian
        lang_layout.addWidget(self.language_combo)

        parent_layout.addLayout(lang_layout)

    def setup_navigation_tree(self, parent_layout):
        """Create the navigation tree widget"""
        # Tree label
        tree_label = QLabel("Содержание:")
        tree_label.setFont(QFont("Arial", self.config.BODY_FONT_SIZE, QFont.Weight.Bold))
        parent_layout.addWidget(tree_label)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(20)

        # Set tree font
        tree_font = QFont("Arial", self.config.BODY_FONT_SIZE)
        self.tree.setFont(tree_font)

        parent_layout.addWidget(self.tree)

        # Populate tree with sections
        self.populate_tree()

    def setup_connections(self):
        """Connect signals for user interactions"""
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.tree.itemClicked.connect(self._on_tree_item_clicked)

    def populate_tree(self):
        """Populate the tree widget with guide sections"""
        self.tree.clear()
        self.section_items.clear()

        sections = GUIDE_SECTIONS.get(self.current_language.value, {})
        self._add_tree_items(sections, self.tree)

        # Expand all items by default
        self.tree.expandAll()

        # Select first item
        if self.tree.topLevelItemCount() > 0:
            first_item = self.tree.topLevelItem(0)
            self._select_first_leaf_item(first_item)

    def _add_tree_items(self, sections, parent):
        """Recursively add items to the tree"""
        for title, content in sections.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, title)

            if isinstance(content, dict):
                # This is a category with subsections
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                font = item.font(0)
                font.setBold(True)
                item.setFont(0, font)
                self._add_tree_items(content, item)
            else:
                # This is a leaf item with section_id
                item.setData(0, Qt.ItemDataRole.UserRole, content)
                self.section_items[content] = item

    def _select_first_leaf_item(self, item):
        """Select the first selectable leaf item"""
        if item.childCount() > 0:
            self._select_first_leaf_item(item.child(0))
        else:
            section_id = item.data(0, Qt.ItemDataRole.UserRole)
            if section_id:
                self.tree.setCurrentItem(item)
                self.section_selected.emit(section_id)

    def set_language(self, language: Language):
        """Change the display language"""
        if language != self.current_language:
            self.current_language = language

            # Update language combo
            index = 0 if language == Language.RUSSIAN else 1
            self.language_combo.setCurrentIndex(index)

            # Repopulate tree
            self.populate_tree()

    def select_section(self, section_id: str):
        """Programmatically select a section"""
        item = self.section_items.get(section_id)
        if item:
            self.tree.setCurrentItem(item)
            self.tree.scrollToItem(item)

    def _on_language_changed(self, index: int):
        """Handle language combo box changes"""
        language = self.language_combo.itemData(index)
        if language and language != self.current_language:
            self.language_changed.emit(language)

    def _on_tree_item_clicked(self, item, column):
        """Handle tree item clicks"""
        section_id = item.data(0, Qt.ItemDataRole.UserRole)
        if section_id:
            self.section_selected.emit(section_id)
