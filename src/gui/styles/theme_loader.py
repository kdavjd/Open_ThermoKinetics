"""
Theme loader for Open ThermoKinetics.

Handles theme switching, QSS loading, and persistence via QSettings.
"""

from pathlib import Path

from PyQt6.QtCore import QSettings

from .tokens import DARK, LIGHT

_STYLES_DIR = Path(__file__).parent
_COMPONENTS_DIR = _STYLES_DIR / "components"


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

    combined = "\n".join(qss_parts)
    app.setStyleSheet(combined)

    # Persist theme choice
    settings = QSettings("OpenThermoKinetics", "App")
    settings.setValue("theme", theme)


def get_saved_theme() -> str:
    """
    Get the previously saved theme from QSettings.

    Returns:
        "light" or "dark" (defaults to "light")
    """
    settings = QSettings("OpenThermoKinetics", "App")
    return settings.value("theme", "light")
