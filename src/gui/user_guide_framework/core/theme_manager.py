"""
ThemeManager - управление темами и стилизацией
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from .exceptions import GuideFrameworkError, ThemeNotFoundError


class ThemeManager(QObject):
    """
    Manages themes and styling for the user guide framework.
    Supports loading themes from JSON files and applying styles to widgets.
    """

    theme_changed = pyqtSignal(str)  # Emitted when theme changes

    def __init__(self, themes_directory: Optional[Path] = None):
        """
        Initialize ThemeManager.

        Args:
            themes_directory: Path to themes directory, if None uses default
        """
        super().__init__()
        self.themes_dir = themes_directory
        self.current_theme: Dict[str, Any] = {}
        self.current_theme_name: str = "default"
        self.available_themes: Dict[str, str] = {}

        # Default theme as fallback
        self._default_theme = self._get_default_theme()
        self.current_theme = self._default_theme.copy()

        if self.themes_dir:
            self.load_available_themes()

    def load_available_themes(self) -> None:
        """Discover and load available theme files"""
        if not self.themes_dir or not self.themes_dir.exists():
            return

        self.available_themes.clear()

        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)

                theme_name = theme_data.get("name", theme_file.stem)
                self.available_themes[theme_name] = str(theme_file)

            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading theme {theme_file}: {e}")

    def set_theme(self, theme_name: str) -> None:
        """
        Set the current theme.

        Args:
            theme_name: Name of the theme to activate
        """
        if theme_name == "default":
            self.current_theme = self._default_theme.copy()
            self.current_theme_name = theme_name
            self.theme_changed.emit(theme_name)
            return

        if theme_name not in self.available_themes:
            raise ThemeNotFoundError(f"Theme '{theme_name}' not found")

        theme_file = self.available_themes[theme_name]

        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)

            # Merge with default theme to ensure all properties exist
            self.current_theme = self._merge_with_default(theme_data)
            self.current_theme_name = theme_name
            self.theme_changed.emit(theme_name)

        except json.JSONDecodeError as e:
            raise GuideFrameworkError(f"Invalid JSON in theme file {theme_file}: {e}")
        except Exception as e:
            raise GuideFrameworkError(f"Error loading theme file {theme_file}: {e}")

    def get_color(self, color_key: str) -> QColor:
        """
        Get color from current theme.

        Args:
            color_key: Key for the color in theme

        Returns:
            QColor object
        """
        colors = self.current_theme.get("colors", {})
        color_value = colors.get(color_key, "#000000")

        if isinstance(color_value, str):
            return QColor(color_value)
        elif isinstance(color_value, dict):
            # RGB format: {"r": 255, "g": 255, "b": 255}
            return QColor(color_value.get("r", 0), color_value.get("g", 0), color_value.get("b", 0))
        else:
            return QColor("#000000")

    def get_font(self, font_key: str) -> QFont:
        """
        Get font from current theme.

        Args:
            font_key: Key for the font in theme

        Returns:
            QFont object
        """
        fonts = self.current_theme.get("fonts", {})
        font_config = fonts.get(font_key, {})

        font = QFont()

        if "family" in font_config:
            font.setFamily(font_config["family"])

        if "size" in font_config:
            font.setPointSize(font_config["size"])

        if "weight" in font_config:
            weight = font_config["weight"]
            if weight == "bold":
                font.setBold(True)
            elif weight == "light":
                font.setWeight(QFont.Weight.Light)
            elif weight == "normal":
                font.setWeight(QFont.Weight.Normal)

        if "italic" in font_config and font_config["italic"]:
            font.setItalic(True)

        return font

    def get_spacing(self, spacing_key: str) -> int:
        """
        Get spacing value from current theme.

        Args:
            spacing_key: Key for the spacing value

        Returns:
            Spacing value in pixels
        """
        spacing = self.current_theme.get("spacing", {})
        return spacing.get(spacing_key, 0)

    def get_component_style(self, component_key: str) -> Dict[str, Any]:
        """
        Get component-specific styling.

        Args:
            component_key: Key for the component

        Returns:
            Dictionary with component styling
        """
        components = self.current_theme.get("components", {})
        return components.get(component_key, {})

    def generate_stylesheet(self, widget_type: str) -> str:
        """
        Generate Qt stylesheet for a widget type.

        Args:
            widget_type: Type of widget (e.g., 'QLabel', 'QPushButton')

        Returns:
            CSS-style stylesheet string
        """
        styles = []

        # Basic colors
        bg_color = self.get_color("background")
        text_color = self.get_color("text_primary")
        border_color = self.get_color("border")

        if widget_type == "QLabel":
            styles.append(f"QLabel {{ color: {text_color.name()}; }}")

        elif widget_type == "QPushButton":
            accent_color = self.get_color("accent")
            styles.append(f"""
            QPushButton {{
                background-color: {accent_color.name()};
                color: white;
                border: 1px solid {border_color.name()};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {accent_color.darker(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {accent_color.darker(120).name()};
            }}
            """)

        elif widget_type == "QTreeWidget":
            surface_color = self.get_color("surface")
            styles.append(f"""
            QTreeWidget {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 1px solid {border_color.name()};
                selection-background-color: {surface_color.name()};
            }}
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {surface_color.name()};
            }}
            """)

        elif widget_type == "QScrollArea":
            styles.append(f"""
            QScrollArea {{
                background-color: {bg_color.name()};
                border: none;
            }}
            """)

        return "\n".join(styles)

    def apply_theme_to_widget(self, widget, widget_type: str = None) -> None:
        """
        Apply current theme to a widget.

        Args:
            widget: PyQt widget to style
            widget_type: Optional widget type override
        """
        if widget_type is None:
            widget_type = widget.__class__.__name__

        stylesheet = self.generate_stylesheet(widget_type)
        if stylesheet:
            widget.setStyleSheet(stylesheet)

    def get_available_themes(self) -> List[str]:
        """
        Get list of available theme names.

        Returns:
            List of theme names
        """
        themes = ["default"]
        themes.extend(self.available_themes.keys())
        return themes

    def get_current_theme_name(self) -> str:
        """
        Get current theme name.

        Returns:
            Current theme name
        """
        return self.current_theme_name

    def _get_default_theme(self) -> Dict[str, Any]:
        """Get the default theme configuration"""
        return {
            "name": "default",
            "version": "1.0",
            "colors": {
                "primary": "#2c3e50",
                "secondary": "#34495e",
                "accent": "#3498db",
                "background": "#ffffff",
                "surface": "#f8f9fa",
                "text_primary": "#2c3e50",
                "text_secondary": "#6c757d",
                "border": "#e9ecef",
                "success": "#28a745",
                "warning": "#ffc107",
                "error": "#dc3545",
                "info": "#17a2b8",
            },
            "fonts": {
                "heading": {"family": "Arial", "size": 16, "weight": "bold"},
                "subheading": {"family": "Arial", "size": 14, "weight": "bold"},
                "body": {"family": "Arial", "size": 11, "weight": "normal"},
                "code": {"family": "Consolas", "size": 10, "weight": "normal"},
            },
            "spacing": {"section": 15, "paragraph": 8, "list_indent": 20, "code_padding": 10},
            "components": {
                "navigation": {"min_width": 250, "max_width": 375, "item_height": 32},
                "content": {"min_width": 600, "padding": 20},
                "code_block": {"background": "#f8f9fa", "border": "#e9ecef", "border_radius": 4, "padding": 10},
            },
        }

    def _merge_with_default(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge theme data with default theme to ensure completeness"""
        merged_theme = self._default_theme.copy()

        def deep_merge(default: Dict, custom: Dict) -> Dict:
            result = default.copy()
            for key, value in custom.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(merged_theme, theme_data)

    def export_theme(self, theme_name: str, file_path: Path) -> None:
        """
        Export current theme to a JSON file.

        Args:
            theme_name: Name for the exported theme
            file_path: Path where to save the theme file
        """
        export_data = self.current_theme.copy()
        export_data["name"] = theme_name

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise GuideFrameworkError(f"Error exporting theme: {e}")

    def create_custom_theme(self, base_theme: str = "default", **overrides) -> Dict[str, Any]:
        """
        Create a custom theme based on existing theme with overrides.

        Args:
            base_theme: Base theme to start with
            **overrides: Theme properties to override

        Returns:
            New theme dictionary
        """
        # Load base theme
        if base_theme == "default":
            base = self._default_theme.copy()
        elif base_theme in self.available_themes:
            with open(self.available_themes[base_theme], "r", encoding="utf-8") as f:
                base = json.load(f)
        else:
            base = self._default_theme.copy()

        # Apply overrides
        custom_theme = base.copy()
        for key, value in overrides.items():
            if "." in key:  # Nested property like "colors.primary"
                parts = key.split(".")
                current = custom_theme
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                custom_theme[key] = value

        return custom_theme
