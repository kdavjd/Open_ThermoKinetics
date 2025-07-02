"""
LocalizationManager - управление многоязычностью
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.logger_config import LoggerManager
from src.gui.user_guide_tab.user_guide_framework.core.exceptions import GuideFrameworkError, LocalizationError

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class LocalizationManager(QObject):
    """
    Manages localization and multi-language support for the user guide framework.
    Handles loading language files and providing translated strings.
    """

    language_changed = pyqtSignal(str)  # Emitted when language changes

    def __init__(self, lang_directory: Optional[Path] = None, default_language: str = "ru"):
        """
        Initialize LocalizationManager.

        Args:
            lang_directory: Path to language files directory
            default_language: Default language code
        """
        super().__init__()
        self.lang_dir = lang_directory
        self.current_language = default_language
        self.available_languages: Dict[str, str] = {}
        self.translations: Dict[str, Dict[str, str]] = {}

        # Default translations as fallback
        self._default_translations = self._get_default_translations()

        if self.lang_dir:
            self.load_available_languages()

        # Load default language
        self.set_language(default_language)

    def load_available_languages(self) -> None:
        """Discover and load available language files"""
        if not self.lang_dir or not self.lang_dir.exists():
            return

        self.available_languages.clear()

        for lang_file in self.lang_dir.glob("*.json"):
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    lang_data = json.load(f)

                lang_code = lang_data.get("language_code", lang_file.stem)
                lang_name = lang_data.get("language_name", lang_code)

                self.available_languages[lang_code] = lang_name

            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading language file {lang_file}: {e}")

    def set_language(self, language_code: str) -> None:
        """
        Set the current language.

        Args:
            language_code: Language code to activate (e.g., 'ru', 'en')
        """
        # Use default translations if no lang directory
        if not self.lang_dir:
            if language_code in self._default_translations:
                self.translations[language_code] = self._default_translations[language_code]
                self.current_language = language_code
                self.language_changed.emit(language_code)
            return

        # Check if language is available
        if language_code not in self.available_languages and language_code not in self._default_translations:
            raise LocalizationError(f"Language '{language_code}' not available")

        # Load language file if not already loaded
        if language_code not in self.translations:
            self._load_language_file(language_code)

        self.current_language = language_code
        self.language_changed.emit(language_code)

    def _load_language_file(self, language_code: str) -> None:
        """Load translations from language file"""
        # Try to load from file first
        if self.lang_dir:
            lang_file = self.lang_dir / f"{language_code}.json"

            if lang_file.exists():
                try:
                    with open(lang_file, "r", encoding="utf-8") as f:
                        lang_data = json.load(f)

                    self.translations[language_code] = lang_data.get("translations", {})
                    return

                except json.JSONDecodeError as e:
                    raise GuideFrameworkError(f"Invalid JSON in language file {lang_file}: {e}")
                except Exception as e:
                    raise GuideFrameworkError(f"Error loading language file {lang_file}: {e}")

        # Fall back to default translations
        if language_code in self._default_translations:
            self.translations[language_code] = self._default_translations[language_code]
        else:
            raise LocalizationError(f"No translations found for language '{language_code}'")

    def get_text(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Get translated text for a key.

        Args:
            key: Translation key
            language: Language code, uses current if None
            **kwargs: Variables for string formatting

        Returns:
            Translated string
        """
        lang = language or self.current_language

        # Get translation
        if lang in self.translations and key in self.translations[lang]:
            text = self.translations[lang][key]
        elif "en" in self.translations and key in self.translations["en"]:
            # Fallback to English
            text = self.translations["en"][key]
        elif "ru" in self.translations and key in self.translations["ru"]:
            # Fallback to Russian
            text = self.translations["ru"][key]
        else:
            # Return key as fallback
            return f"[{key}]"

        # Format with variables if provided
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text

        return text

    def get_current_language(self) -> str:
        """
        Get current language code.

        Returns:
            Current language code
        """
        return self.current_language

    def get_available_languages(self) -> Dict[str, str]:
        """
        Get available languages.

        Returns:
            Dictionary mapping language codes to language names
        """
        # Merge available languages with defaults
        languages = {}

        # Add default languages
        for lang_code in self._default_translations:
            languages[lang_code] = self._get_language_name(lang_code)

        # Add discovered languages
        languages.update(self.available_languages)

        return languages

    def has_translation(self, key: str, language: Optional[str] = None) -> bool:
        """
        Check if translation exists for a key.

        Args:
            key: Translation key
            language: Language code, uses current if None

        Returns:
            True if translation exists
        """
        lang = language or self.current_language

        return (
            (lang in self.translations and key in self.translations[lang])
            or ("en" in self.translations and key in self.translations["en"])
            or ("ru" in self.translations and key in self.translations["ru"])
        )

    def add_translation(self, key: str, text: str, language: Optional[str] = None) -> None:
        """
        Add or update a translation.

        Args:
            key: Translation key
            text: Translated text
            language: Language code, uses current if None
        """
        lang = language or self.current_language

        if lang not in self.translations:
            self.translations[lang] = {}

        self.translations[lang][key] = text

    def add_translations(self, translations: Dict[str, str], language: Optional[str] = None) -> None:
        """
        Add multiple translations at once.

        Args:
            translations: Dictionary of key-value translation pairs
            language: Language code, uses current if None
        """
        lang = language or self.current_language

        if lang not in self.translations:
            self.translations[lang] = {}

        self.translations[lang].update(translations)

    def get_language_info(self, language_code: str) -> Dict[str, str]:
        """
        Get information about a language.

        Args:
            language_code: Language code

        Returns:
            Dictionary with language information
        """
        return {
            "code": language_code,
            "name": self.available_languages.get(language_code, self._get_language_name(language_code)),
            "is_loaded": language_code in self.translations,
            "translation_count": len(self.translations.get(language_code, {})),
        }

    def export_translations(self, language_code: str, file_path: Path) -> None:
        """
        Export translations to a JSON file.

        Args:
            language_code: Language to export
            file_path: Path where to save the file
        """
        if language_code not in self.translations:
            raise LocalizationError(f"No translations loaded for language '{language_code}'")

        export_data = {
            "language_code": language_code,
            "language_name": self.available_languages.get(language_code, self._get_language_name(language_code)),
            "version": "1.0",
            "translations": self.translations[language_code],
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise GuideFrameworkError(f"Error exporting translations: {e}")

    def import_translations(self, file_path: Path) -> str:
        """
        Import translations from a JSON file.

        Args:
            file_path: Path to the translation file

        Returns:
            Language code of imported translations
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lang_data = json.load(f)

            language_code = lang_data.get("language_code")
            if not language_code:
                raise LocalizationError("Language code not found in import file")

            language_name = lang_data.get("language_name", language_code)
            translations = lang_data.get("translations", {})

            self.available_languages[language_code] = language_name
            self.translations[language_code] = translations

            return language_code

        except json.JSONDecodeError as e:
            raise GuideFrameworkError(f"Invalid JSON in translation file: {e}")
        except Exception as e:
            raise GuideFrameworkError(f"Error importing translations: {e}")

    def _get_default_translations(self) -> Dict[str, Dict[str, str]]:
        """Get default translations for common UI elements"""
        return {
            "ru": {
                # Navigation
                "nav_introduction": "Введение",
                "nav_data_management": "Управление данными",
                "nav_analysis_methods": "Методы анализа",
                "nav_file_loading": "Загрузка файлов",
                "nav_preprocessing": "Предобработка",
                "nav_deconvolution": "Деконволюция пиков",
                "nav_model_fit": "Model-Fit анализ",
                "nav_model_free": "Model-Free анализ",
                "nav_model_based": "Model-Based анализ",
                # UI elements
                "ui_search": "Поиск",
                "ui_language": "Язык",
                "ui_theme": "Тема",
                "ui_back": "Назад",
                "ui_next": "Далее",
                "ui_home": "Главная",
                "ui_settings": "Настройки",
                # Content types
                "content_note": "Примечание",
                "content_warning": "Предупреждение",
                "content_tip": "Совет",
                "content_example": "Пример",
                "content_code": "Код",
                # Errors
                "error_content_not_found": "Контент не найден",
                "error_loading": "Ошибка загрузки",
                "error_invalid_section": "Недопустимый раздел",
            },
            "en": {
                # Navigation
                "nav_introduction": "Introduction",
                "nav_data_management": "Data Management",
                "nav_analysis_methods": "Analysis Methods",
                "nav_file_loading": "File Loading",
                "nav_preprocessing": "Preprocessing",
                "nav_deconvolution": "Peak Deconvolution",
                "nav_model_fit": "Model-Fit Analysis",
                "nav_model_free": "Model-Free Analysis",
                "nav_model_based": "Model-Based Analysis",
                # UI elements
                "ui_search": "Search",
                "ui_language": "Language",
                "ui_theme": "Theme",
                "ui_back": "Back",
                "ui_next": "Next",
                "ui_home": "Home",
                "ui_settings": "Settings",
                # Content types
                "content_note": "Note",
                "content_warning": "Warning",
                "content_tip": "Tip",
                "content_example": "Example",
                "content_code": "Code",
                # Errors
                "error_content_not_found": "Content not found",
                "error_loading": "Loading error",
                "error_invalid_section": "Invalid section",
            },
        }

    def _get_language_name(self, language_code: str) -> str:
        """Get display name for language code"""
        names = {
            "ru": "Русский",
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "it": "Italiano",
            "zh": "中文",
            "ja": "日本語",
        }
        return names.get(language_code, language_code.upper())

    def get_missing_translations(self, reference_language: str = "en") -> Dict[str, List[str]]:
        """
        Get missing translations compared to reference language.

        Args:
            reference_language: Language to compare against

        Returns:
            Dictionary mapping language codes to lists of missing keys
        """
        if reference_language not in self.translations:
            return {}

        reference_keys = set(self.translations[reference_language].keys())
        missing = {}

        for lang_code, translations in self.translations.items():
            if lang_code == reference_language:
                continue

            lang_keys = set(translations.keys())
            missing_keys = reference_keys - lang_keys

            if missing_keys:
                missing[lang_code] = list(missing_keys)

        return missing
