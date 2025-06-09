"""
Localization manager for handling internationalization of the application.
Provides centralized string management and locale switching capabilities.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class LocaleInfo:
    """Information about a supported locale."""

    code: str  # Language code (e.g., 'en', 'ru')
    name: str  # Display name (e.g., 'English', 'Русский')
    file_name: str  # JSON file name (e.g., 'en.json')


class LocalizationManager:
    """
    Manager for application localization and string resources.
    Handles loading, caching, and retrieval of localized strings.
    """

    def __init__(self, resources_dir: Optional[Path] = None, default_locale: str = "en"):
        """
        Initialize the localization manager.

        Args:
            resources_dir: Directory containing locale JSON files
            default_locale: Default language code to use
        """
        self.default_locale = default_locale
        self.current_locale = default_locale

        if resources_dir is None:
            # Default to locales directory relative to this file
            self.resources_dir = Path(__file__).parent / "locales"
        else:
            self.resources_dir = Path(resources_dir)

        # Cache for loaded locale data
        self._locale_cache: Dict[str, Dict[str, Any]] = {}

        # Available locales
        self.available_locales = [
            LocaleInfo("en", "English", "en.json"),
            LocaleInfo("ru", "Русский", "ru.json"),
        ]

        # Ensure resources directory exists
        self.resources_dir.mkdir(exist_ok=True)

        # Load default locale
        self._load_locale(self.default_locale)

    def get_string(self, key: str, **kwargs) -> str:
        """
        Get a localized string by key.

        Args:
            key: String key in dot notation (e.g., 'dialogs.buttons.ok')
            **kwargs: Format parameters for the string

        Returns:
            Localized string, or the key itself if not found
        """
        locale_data = self._get_locale_data(self.current_locale)

        # Navigate through nested dictionary using dot notation
        keys = key.split(".")
        value = locale_data

        try:
            for k in keys:
                value = value[k]

            # Format string if parameters provided
            if kwargs and isinstance(value, str):
                return value.format(**kwargs)

            return str(value)

        except (KeyError, TypeError):
            # Fallback to default locale
            if self.current_locale != self.default_locale:
                return self._get_string_from_locale(key, self.default_locale, **kwargs)

            # Return key as fallback
            return f"[{key}]"

    def _get_string_from_locale(self, key: str, locale: str, **kwargs) -> str:
        """Get string from specific locale."""
        locale_data = self._get_locale_data(locale)
        keys = key.split(".")
        value = locale_data

        try:
            for k in keys:
                value = value[k]

            if kwargs and isinstance(value, str):
                return value.format(**kwargs)

            return str(value)

        except (KeyError, TypeError):
            return f"[{key}]"

    def set_locale(self, locale_code: str) -> bool:
        """
        Change the current locale.

        Args:
            locale_code: Language code to switch to

        Returns:
            True if locale was successfully set, False otherwise
        """
        if self._load_locale(locale_code):
            self.current_locale = locale_code
            return True
        return False

    def get_current_locale(self) -> str:
        """Get the current locale code."""
        return self.current_locale

    def get_available_locales(self) -> list[LocaleInfo]:
        """Get list of available locales."""
        return self.available_locales.copy()

    def _get_locale_data(self, locale: str) -> Dict[str, Any]:
        """Get cached locale data, loading if necessary."""
        if locale not in self._locale_cache:
            self._load_locale(locale)

        return self._locale_cache.get(locale, {})

    def _load_locale(self, locale: str) -> bool:
        """
        Load locale data from JSON file.

        Args:
            locale: Language code to load

        Returns:
            True if loaded successfully, False otherwise
        """
        locale_info = None
        for info in self.available_locales:
            if info.code == locale:
                locale_info = info
                break

        if not locale_info:
            return False

        locale_file = self.resources_dir / locale_info.file_name

        try:
            if locale_file.exists():
                with open(locale_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._locale_cache[locale] = data
                    return True
            else:
                # Create default file structure if it doesn't exist
                self._create_default_locale_file(locale_file, locale)
                return True

        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load locale {locale}: {e}")
            return False

    def _create_default_locale_file(self, file_path: Path, locale: str):
        """Create a default locale file with empty structure."""
        default_structure = {
            "application": {
                "title": "Solid State Kinetics",
                "tabs": {"main": "Main", "analysis": "Analysis", "modeling": "Modeling"},
            },
            "dialogs": {
                "buttons": {
                    "ok": "OK",
                    "cancel": "Cancel",
                    "calculate": "Calculate",
                    "plot": "Plot",
                    "settings": "Settings",
                },
                "titles": {
                    "annotation_settings": "Annotation Settings",
                    "calculation_settings": "Calculation Settings",
                    "model_selection": "Select Models",
                },
            },
            "controls": {
                "labels": {
                    "alpha_min": "α_min:",
                    "alpha_max": "α_max:",
                    "ea_min": "Ea min, kJ:",
                    "ea_max": "Ea max, kJ:",
                    "ea_mean": "Ea mean, kJ:",
                    "plot_type": "Plot type:",
                },
                "tooltips": {
                    "alpha_min": "alpha_min - minimum conversion value for calculation",
                    "alpha_max": "alpha_max - maximum conversion value for calculation",
                    "ea_min": "Ea min, kJ",
                    "ea_max": "Ea max, kJ",
                    "ea_mean": "Ea mean, kJ",
                },
            },
            "validation": {
                "errors": {
                    "alpha_min_range": "alpha_min must be between 0 and 0.999",
                    "alpha_max_range": "alpha_max must be between 0 and 1",
                    "alpha_min_greater": "alpha_min cannot be greater than alpha_max",
                    "file_not_selected": "Choose an experiment",
                    "empty_functions": "{functions} must be described by at least one function.",
                }
            },
            "messages": {
                "success": {"settings_updated": "updated for:\n{message}"},
                "warnings": {
                    "unselected_functions": "unselected functions",
                    "file_not_selected": "File is not selected.",
                    "invalid_parameters": "Invalid DE parameters",
                },
            },
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_structure, f, indent=2, ensure_ascii=False)
            self._locale_cache[locale] = default_structure
        except IOError as e:
            print(f"Failed to create default locale file {file_path}: {e}")

    # Convenience methods for common string patterns
    def get_button_text(self, button_name: str) -> str:
        """Get localized button text."""
        return self.get_string(f"dialogs.buttons.{button_name}")

    def get_label_text(self, label_name: str) -> str:
        """Get localized label text."""
        return self.get_string(f"controls.labels.{label_name}")

    def get_tooltip_text(self, tooltip_name: str) -> str:
        """Get localized tooltip text."""
        return self.get_string(f"controls.tooltips.{tooltip_name}")

    def get_validation_error(self, error_name: str, **kwargs) -> str:
        """Get localized validation error message."""
        return self.get_string(f"validation.errors.{error_name}", **kwargs)

    def get_dialog_title(self, dialog_name: str) -> str:
        """Get localized dialog title."""
        return self.get_string(f"dialogs.titles.{dialog_name}")


# Global localization manager instance
_localization_manager: Optional[LocalizationManager] = None


def get_localization_manager() -> LocalizationManager:
    """Get the global localization manager instance."""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager


def set_locale(locale_code: str) -> bool:
    """Set the global locale."""
    return get_localization_manager().set_locale(locale_code)


def get_string(key: str, **kwargs) -> str:
    """Get a localized string using the global manager."""
    return get_localization_manager().get_string(key, **kwargs)


# Convenience functions for common patterns
def _(key: str, **kwargs) -> str:
    """Short alias for get_string."""
    return get_string(key, **kwargs)


def get_button_text(button_name: str) -> str:
    """Get localized button text."""
    return get_localization_manager().get_button_text(button_name)


def get_label_text(label_name: str) -> str:
    """Get localized label text."""
    return get_localization_manager().get_label_text(label_name)


def get_tooltip_text(tooltip_name: str) -> str:
    """Get localized tooltip text."""
    return get_localization_manager().get_tooltip_text(tooltip_name)


def get_validation_error(error_name: str, **kwargs) -> str:
    """Get localized validation error message."""
    return get_localization_manager().get_validation_error(error_name, **kwargs)


def get_dialog_title(dialog_name: str) -> str:
    """Get localized dialog title."""
    return get_localization_manager().get_dialog_title(dialog_name)
