"""
Model-Based Analysis Module

This module serves as a compatibility wrapper for refactored model-based kinetics
analysis components. The functionality has been distributed into focused modules:

- Dialog components: src/gui/dialogs/model_dialogs.py
- Control components: src/gui/controls/model_calculation_controls.py, adjustment_controls.py
- Table components: src/gui/main_tab/sub_sidebar/model_based/reaction_table.py (ModelReactionTable)
- Main coordinator: src/gui/tabs/model_based_tab.py

This file maintains backward compatibility with existing imports.
"""

# Import main coordinator
from src.gui.controls.adjustment_controls import AdjustingSettingsBox, AdjustmentRowWidget

# Import control components for backward compatibility
from src.gui.controls.model_calculation_controls import ModelCalcButtons

# Import dialog components for backward compatibility
from src.gui.dialogs.model_dialogs import CalculationSettingsDialog, ModelsSelectionDialog

# Import table components for backward compatibility
from src.gui.main_tab.sub_sidebar.model_based.reaction_table import ModelReactionTable

# Re-export all components for backward compatibility
__all__ = [
    "CalculationSettingsDialog",
    "ModelsSelectionDialog",
    "ModelReactionTable",
    "ModelCalcButtons",
    "AdjustmentRowWidget",
    "AdjustingSettingsBox",
]

# Legacy aliases for backward compatibility
ReactionTable = ModelReactionTable  # Alias for the original ReactionTable class
