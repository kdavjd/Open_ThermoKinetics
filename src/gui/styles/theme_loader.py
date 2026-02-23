"""
Theme loader for Open ThermoKinetics.

Handles theme switching, QSS loading, font loading, and persistence via QSettings.
"""

from pathlib import Path

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase

from .tokens import DARK, LIGHT

_STYLES_DIR = Path(__file__).parent
_COMPONENTS_DIR = _STYLES_DIR / "components"
_FONTS_DIR = _STYLES_DIR / "fonts"

# Global registry of loaded font families (alias -> family_name)
LOADED_FONTS: dict[str, str] = {}


def _read_qss(file_path: Path) -> str:
    """Read QSS file contents, return empty string if not found."""
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def _substitute_tokens(qss_content: str, tokens: dict) -> str:
    """Replace token placeholders like {{token_name}} with values."""
    result = qss_content
    for name, value in tokens.items():
        result = result.replace(f"{{{{{name}}}}}", value)
    return result


def load_fonts() -> dict[str, str]:
    """
    Load bundled fonts from fonts/ directory using QFontDatabase.

    Call this once at application startup BEFORE load_theme().
    Fonts are bundled with the app and registered system-wide via Qt.

    Returns:
        Dictionary mapping font file aliases to actual font family names.
        E.g., {"SourceSansPro-Regular": "Source Sans 3", ...}
    """
    global LOADED_FONTS

    if not _FONTS_DIR.exists():
        print(f"[fonts] Directory not found: {_FONTS_DIR}")
        return LOADED_FONTS

    for font_file in _FONTS_DIR.glob("*.ttf"):
        font_id = QFontDatabase.addApplicationFont(str(font_file))

        if font_id == -1:
            print(f"[fonts] WARNING: Failed to load: {font_file} (DirectWrite or format error)")
            continue

        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            # Store with file stem as alias (e.g., "SourceSansPro-Regular")
            # and actual family name as value (e.g., "Source Sans 3")
            alias = font_file.stem
            family_name = families[0]
            LOADED_FONTS[alias] = family_name
            print(f"[fonts] OK: {font_file.name} -> family '{family_name}'")
        else:
            print(f"[fonts] WARNING: No family name returned for: {font_file.name}")

    return LOADED_FONTS


def load_theme(app, theme: str) -> None:
    """
    Load and apply theme to the application.

    Args:
        app: QApplication instance
        theme: "light" or "dark"
    """
    tokens = LIGHT if theme == "light" else DARK

    qss_parts = []

    # Base theme file (light.qss or dark.qss)
    base_qss_path = _STYLES_DIR / f"{theme}.qss"
    base_qss = _read_qss(base_qss_path)
    if base_qss:
        qss_parts.append(_substitute_tokens(base_qss, tokens))

    # Component files
    component_files = [
        "buttons.qss",
        "forms.qss",
        "sidebar.qss",
        "tabs.qss",
        "console.qss",
        "menubar.qss",
        "plot.qss",
        "deconvolution.qss",
    ]

    for component_file in component_files:
        component_path = _COMPONENTS_DIR / component_file
        component_qss = _read_qss(component_path)
        if component_qss:
            qss_parts.append(_substitute_tokens(component_qss, tokens))

    # Persist BEFORE applying stylesheet: setStyleSheet() delivers QEvent.StyleChange
    # synchronously, so PlotCanvas.changeEvent() fires before this line if the order
    # is reversed — causing get_saved_theme() to return the OLD theme (anti-phase bug).
    settings = QSettings("OpenThermoKinetics", "App")
    settings.setValue("theme", theme)

    combined = "\n".join(qss_parts)
    app.setStyleSheet(combined)


def get_saved_theme() -> str:
    """
    Get the previously saved theme from QSettings.

    Returns:
        "light" or "dark" (defaults to "light")
    """
    settings = QSettings("OpenThermoKinetics", "App")
    return settings.value("theme", "light")
