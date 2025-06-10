"""
Content Display Widget for User Guide
Displays formatted guide content with rich text, images, and interactive elements.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from .config import GuideConfig, Language
from .guide_content import GUIDE_CONTENT


class GuideContentWidget(QWidget):
    """
    Widget for displaying formatted user guide content with rich text support.
    Handles content switching based on language and section selection.
    """

    section_link_clicked = pyqtSignal(str)  # Emits section_id when internal link is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = GuideConfig()
        self.current_language = Language.ENGLISH
        self.current_section = "introduction"
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setMinimumWidth(self.config.MIN_WIDTH_CONTENT)
        layout = QVBoxLayout(self)

        # Scroll area for content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget inside scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(self.config.PARAGRAPH_SPACING)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Load initial content
        self.update_content()

    def set_language(self, language: Language):
        """Change display language and refresh content"""
        if language != self.current_language:
            self.current_language = language
            self.update_content()

    def set_section(self, section_id: str):
        """Change displayed section and refresh content"""
        if section_id != self.current_section:
            self.current_section = section_id
            self.update_content()

    def update_content(self):
        """Update the displayed content based on current language and section"""
        # Clear existing content
        self._clear_content()

        # Get content for current language and section
        lang_content = GUIDE_CONTENT.get(self.current_language.value, {})
        section_content = lang_content.get(self.current_section, {})

        if not section_content:
            self._show_error_content()
            return

        # Display title
        title = section_content.get("title", "")
        if title:
            title_label = self._create_title_label(title)
            self.content_layout.addWidget(title_label)

        # Display content blocks
        content_blocks = section_content.get("content", [])
        for block in content_blocks:
            widget = self._create_content_block(block)
            if widget:
                self.content_layout.addWidget(widget)

        # Add stretch to push content to top
        self.content_layout.addStretch()

        # Scroll to top
        self.scroll_area.verticalScrollBar().setValue(0)

    def _clear_content(self):
        """Remove all widgets from content layout"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_error_content(self):
        """Display error message when content is not found"""
        error_msg = (
            "Content not found for this section."
            if self.current_language == Language.ENGLISH
            else "Содержимое для данного раздела не найдено."
        )
        error_label = QLabel(error_msg)
        error_label.setFont(self._create_font(self.config.BODY_FONT_SIZE))
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #e74c3c; font-style: italic;")
        self.content_layout.addWidget(error_label)

    def _create_title_label(self, title: str) -> QLabel:
        """Create a formatted title label"""
        label = QLabel(title)
        label.setFont(self._create_font(self.config.HEADING_FONT_SIZE, bold=True))
        label.setStyleSheet(f"color: {self.config.HEADING_COLOR}; margin-bottom: {self.config.SECTION_SPACING}px;")
        label.setWordWrap(True)
        return label

    def _create_content_block(self, block: dict) -> QWidget:
        """Create a widget for a content block based on its type"""
        block_type = block.get("type", "")

        if block_type == "heading":
            return self._create_heading(block.get("text", ""))
        elif block_type == "paragraph":
            return self._create_paragraph(block.get("text", ""))
        elif block_type == "list":
            return self._create_list(block.get("items", []))
        elif block_type == "code":
            return self._create_code_block(block.get("text", ""))
        elif block_type == "image":
            return self._create_image(block.get("path", ""), block.get("caption", ""))
        elif block_type == "note":
            return self._create_note(block.get("text", ""))

        return None

    def _create_heading(self, text: str) -> QLabel:
        """Create a subheading label"""
        label = QLabel(text)
        label.setFont(self._create_font(self.config.SUBHEADING_FONT_SIZE, bold=True))
        label.setStyleSheet(
            f"color: {self.config.SUBHEADING_COLOR}; "
            f"margin-top: {self.config.SECTION_SPACING}px; "
            f"margin-bottom: {self.config.PARAGRAPH_SPACING}px;"
        )
        label.setWordWrap(True)
        return label

    def _create_paragraph(self, text: str) -> QLabel:
        """Create a paragraph label with rich text support"""
        label = QLabel(text)
        label.setFont(self._create_font(self.config.BODY_FONT_SIZE))
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(True)
        label.setMargin(5)
        return label

    def _create_list(self, items: list) -> QWidget:
        """Create a list widget with bullet points"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(self.config.LIST_INDENT, 0, 0, 0)
        layout.setSpacing(5)

        for item in items:
            item_label = QLabel(f"• {item}")
            item_label.setFont(self._create_font(self.config.BODY_FONT_SIZE))
            item_label.setWordWrap(True)
            item_label.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(item_label)

        return widget

    def _create_code_block(self, text: str) -> QLabel:
        """Create a code block with monospace font and background"""
        label = QLabel(text)
        font = QFont("Consolas", self.config.CODE_FONT_SIZE)
        font.setStyleHint(QFont.StyleHint.Monospace)
        label.setFont(font)
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            background-color: {self.config.CODE_BACKGROUND};
            border: 1px solid {self.config.CODE_BORDER};
            border-radius: 4px;
            padding: 10px;
            margin: 5px 0px;
        """)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def _create_image(self, path: str, caption: str) -> QWidget:
        """Create an image widget with optional caption"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Image label
        image_label = QLabel()
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Scale image to fit content width while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.config.MIN_WIDTH_CONTENT - 50,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText(f"[Image not found: {path}]")
            image_label.setStyleSheet("color: #e74c3c; font-style: italic;")

        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)

        # Caption
        if caption:
            caption_label = QLabel(caption)
            caption_label.setFont(self._create_font(self.config.BODY_FONT_SIZE - 1))
            caption_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption_label.setWordWrap(True)
            layout.addWidget(caption_label)

        return widget

    def _create_note(self, text: str) -> QLabel:
        """Create a highlighted note block"""
        label = QLabel(text)
        label.setFont(self._create_font(self.config.BODY_FONT_SIZE))
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setStyleSheet("""
            background-color: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 4px;
            padding: 10px;
            margin: 5px 0px;
        """)
        return label

    def _create_font(self, size: int, bold: bool = False) -> QFont:
        """Create a font with specified size and weight"""
        font = QFont()
        font.setPointSize(size)
        font.setBold(bold)
        return font
