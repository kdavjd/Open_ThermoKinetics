"""
Configuration usage examples and migration guide.
This file demonstrates how to use the new configuration system and replace hardcoded values.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.gui.config import get_app_config, get_config, get_controls_config, get_localization


# Example 1: Replacing hardcoded window dimensions
def create_main_window_old():
    """OLD WAY: Hardcoded values"""
    window_width = 1600  # Magic number
    window_height = 1000  # Magic number
    min_width = 1200  # Magic number
    min_height = 800  # Magic number
    return window_width, window_height, min_width, min_height


def create_main_window_new():
    """NEW WAY: Using configuration"""
    config = get_app_config()
    return (
        config.window.default_width,
        config.window.default_height,
        config.window.min_width,
        config.window.min_height,
    )


# Example 2: Replacing hardcoded button sizes
def create_button_old():
    """OLD WAY: Hardcoded sizes"""
    button_width = 80  # Magic number
    button_height = 30  # Magic number
    small_button_size = 24  # Magic number
    return button_width, button_height, small_button_size


def create_button_new():
    """NEW WAY: Using configuration"""
    config = get_controls_config()
    return (config.buttons.standard_width, config.buttons.standard_height, config.buttons.small_width)


# Example 3: Replacing hardcoded strings with localization
def create_dialog_old():
    """OLD WAY: Hardcoded strings"""
    title = "calculation settings"  # Hardcoded string
    ok_button = "OK"  # Hardcoded string
    cancel_button = "Cancel"  # Hardcoded string
    return title, ok_button, cancel_button


def create_dialog_new():
    """NEW WAY: Using localization"""
    loc = get_localization()
    return (loc.get_dialog_title("calculation_settings"), loc.get_button_text("ok"), loc.get_button_text("cancel"))


# Example 4: Replacing analysis defaults
def setup_model_free_old():
    """OLD WAY: Hardcoded defaults"""
    alpha_min_default = "0.005"  # Magic value
    alpha_max_default = "0.995"  # Magic value
    ea_min_default = "10"  # Magic value
    ea_max_default = "2000"  # Magic value
    return alpha_min_default, alpha_max_default, ea_min_default, ea_max_default


def setup_model_free_new():
    """NEW WAY: Using configuration"""
    config = get_config()
    defaults = config.analysis.model_free.defaults
    return (str(defaults.alpha_min), str(defaults.alpha_max), str(defaults.ea_min), str(defaults.ea_max))


# Example 5: Replacing table configurations
def setup_table_old():
    """OLD WAY: Hardcoded table setup"""
    headers = ["method", "Ea", "std"]  # Hardcoded headers
    row_count = 3  # Magic number
    col_count = 3  # Magic number
    return headers, row_count, col_count


def setup_table_new():
    """NEW WAY: Using configuration"""
    config = get_controls_config()
    table_config = config.tables
    return (table_config.results_headers, table_config.results_table_cols, table_config.results_table_cols)


# Example 6: Migration pattern for existing GUI components
class ModelFreeSubBarOld:
    """OLD WAY: Hardcoded values throughout"""

    def __init__(self):
        self.alpha_min_default = "0.005"  # Hardcoded
        self.alpha_max_default = "0.995"  # Hardcoded
        self.button_text = "calculate"  # Hardcoded
        self.tooltip_text = "alpha_min - minimum conversion value"  # Hardcoded


class ModelFreeSubBarNew:
    """NEW WAY: Using configuration system"""

    def __init__(self):
        config = get_config()
        loc = config.localization

        # Use configuration defaults
        self.alpha_min_default = str(config.analysis.model_free.defaults.alpha_min)
        self.alpha_max_default = str(config.analysis.model_free.defaults.alpha_max)

        # Use localized strings
        self.button_text = loc.get_button_text("calculate")
        self.tooltip_text = loc.get_tooltip_text("alpha_min")


# Example 7: Using the configuration in dialog creation
def create_annotation_dialog_old():
    """OLD WAY: Hardcoded dialog configuration"""
    dialog_width = 300  # Magic number
    dialog_height = 300  # Magic number
    title = "annotation settings"  # Hardcoded string
    # Hardcoded default values
    block_top_default = 0.98  # Magic number
    block_left_default = 0.4  # Magic number
    fontsize_default = 8  # Magic number

    return {
        "width": dialog_width,
        "height": dialog_height,
        "title": title,
        "defaults": {"block_top": block_top_default, "block_left": block_left_default, "fontsize": fontsize_default},
    }


def create_annotation_dialog_new():
    """NEW WAY: Using configuration system"""
    config = get_config()
    dialog_config = config.dialogs.annotation
    dimensions = config.dialogs.dimensions
    loc = config.localization

    return {
        "width": dimensions.annotation_dialog_width,
        "height": dimensions.annotation_dialog_height,
        "title": loc.get_dialog_title("annotation_settings"),
        "defaults": {
            "block_top": dialog_config.default_block_top,
            "block_left": dialog_config.default_block_left_model_fit,
            "fontsize": dialog_config.default_fontsize,
        },
    }


# Migration checklist for developers:
MIGRATION_CHECKLIST = """
PHASE 1 MIGRATION CHECKLIST:

1. REPLACE HARDCODED DIMENSIONS:
   - Window sizes: Use get_app_config().window.*
   - Button sizes: Use get_controls_config().buttons.*
   - Table dimensions: Use get_controls_config().tables.*
   - Dialog sizes: Use get_dialogs_config().dimensions.*

2. REPLACE HARDCODED STRINGS:
   - Button texts: Use get_localization().get_button_text()
   - Dialog titles: Use get_localization().get_dialog_title()
   - Label texts: Use get_localization().get_label_text()
   - Error messages: Use get_localization().get_validation_error()

3. REPLACE MAGIC NUMBERS:
   - Analysis defaults: Use get_config().analysis.*
   - Modeling defaults: Use get_config().modeling.*
   - Plot settings: Use get_config().visualization.*

4. UPDATE IMPORTS:
   - Add: from src.gui.config import get_config, get_localization
   - Replace hardcoded values with config calls

5. VALIDATION:
   - Test that UI still looks and behaves the same
   - Verify that localization switching works
   - Check that configuration changes are applied
"""


if __name__ == "__main__":
    # Demonstration of the configuration system
    print("=== Configuration System Demo ===")

    # Show old vs new approaches
    print("\nWindow configuration:")
    print(f"Old: {create_main_window_old()}")
    print(f"New: {create_main_window_new()}")

    print("\nButton configuration:")
    print(f"Old: {create_button_old()}")
    print(f"New: {create_button_new()}")

    print("\nDialog configuration:")
    print(f"Old: {create_dialog_old()}")
    print(f"New: {create_dialog_new()}")

    print("\nLocalization demo:")
    loc = get_localization()
    print(f"Current locale: {loc.get_current_locale()}")
    print(f"Button OK: {loc.get_button_text('ok')}")

    # Switch to Russian
    if loc.set_locale("ru"):
        print(f"Switched to: {loc.get_current_locale()}")
        print(f"Button OK (RU): {loc.get_button_text('ok')}")
        print(f"Dialog title (RU): {loc.get_dialog_title('calculation_settings')}")

    print("\n=== Configuration loaded successfully! ===")
    print(f"\nMigration checklist:\n{MIGRATION_CHECKLIST}")
