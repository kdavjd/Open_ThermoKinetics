"""
Model-Based Reaction Table Component

This module provides the ModelReactionTable widget for managing kinetic parameters
in model-based analysis, including activation energy, pre-exponential factor, contribution,
and their optimization bounds.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem

from src.gui.modeling.modeling_config import get_modeling_config


class ModelReactionTable(QTableWidget):
    """
    Table widget for editing kinetic parameters in model-based analysis.

    Provides input fields for:
    - Activation energy (Ea) with bounds
    - Pre-exponential factor (log A) with bounds
    - Contribution with bounds

    Signals:
        valueChanged: Emitted when any parameter value changes
    """

    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the model reaction table with parameter editing fields."""
        config = get_modeling_config()
        table_config = config.table
        super().__init__(table_config.row_count, table_config.column_count, parent)
        self.setHorizontalHeaderLabels(table_config.column_headers)

        self.setColumnHidden(2, True)  # Min column
        self.setColumnHidden(3, True)  # Max column

        # Ea row
        self.setItem(0, 0, QTableWidgetItem(table_config.row_labels[0]))
        self.activation_energy_edit = QLineEdit()
        self.setCellWidget(0, 1, self.activation_energy_edit)

        self.ea_min_item = QLineEdit()
        self.setCellWidget(0, 2, self.ea_min_item)
        self.ea_max_item = QLineEdit()
        self.setCellWidget(0, 3, self.ea_max_item)

        # log(A) row
        self.setItem(1, 0, QTableWidgetItem(table_config.row_labels[1]))
        self.log_a_edit = QLineEdit()
        self.setCellWidget(1, 1, self.log_a_edit)

        self.log_a_min_item = QLineEdit()
        self.setCellWidget(1, 2, self.log_a_min_item)
        self.log_a_max_item = QLineEdit()
        self.setCellWidget(1, 3, self.log_a_max_item)

        # contribution row
        self.setItem(2, 0, QTableWidgetItem(table_config.row_labels[2]))
        self.contribution_edit = QLineEdit()
        self.setCellWidget(2, 1, self.contribution_edit)

        self.contribution_min_item = QLineEdit()
        self.setCellWidget(2, 2, self.contribution_min_item)
        self.contribution_max_item = QLineEdit()
        self.setCellWidget(2, 3, self.contribution_max_item)

        # Store defaults from configuration
        self.defaults = config.reaction_defaults

        # Connect signals for value change notifications
        self._connect_signals()

    def _connect_signals(self):
        """Connect all input field signals to emit valueChanged."""
        self.activation_energy_edit.editingFinished.connect(self.valueChanged.emit)
        self.log_a_edit.editingFinished.connect(self.valueChanged.emit)
        self.contribution_edit.editingFinished.connect(self.valueChanged.emit)
        self.ea_min_item.editingFinished.connect(self.valueChanged.emit)
        self.ea_max_item.editingFinished.connect(self.valueChanged.emit)
        self.log_a_min_item.editingFinished.connect(self.valueChanged.emit)
        self.log_a_max_item.editingFinished.connect(self.valueChanged.emit)
        self.contribution_min_item.editingFinished.connect(self.valueChanged.emit)
        self.contribution_max_item.editingFinished.connect(self.valueChanged.emit)

    def set_ranges_visible(self, visible: bool):
        """Show or hide the min/max bound columns."""
        self.setColumnHidden(2, not visible)  # Min column
        self.setColumnHidden(3, not visible)  # Max column
        self.viewport().update()

    def update_value_with_best(self, best_data: dict):
        """Update the Value fields directly with best optimization results and trigger save."""
        if not best_data:
            return

        # Update Ea value
        ea_val = best_data.get("Ea")
        if ea_val is not None:
            self.activation_energy_edit.setText(f"{ea_val:.1f}")

        # Update log(A) value
        log_a_val = best_data.get("logA")
        if log_a_val is not None:
            self.log_a_edit.setText(f"{log_a_val:.2f}")

        # Update contribution value
        contribution_val = best_data.get("contribution")
        if contribution_val is not None:
            self.contribution_edit.setText(f"{contribution_val:.3f}")

    def update_table(self, reaction_data: dict):
        """Update all table fields with reaction data or clear if empty."""
        if not reaction_data:
            self.activation_energy_edit.clear()
            self.log_a_edit.clear()
            self.contribution_edit.clear()
            self.ea_min_item.clear()
            self.ea_max_item.clear()
            self.log_a_min_item.clear()
            self.log_a_max_item.clear()
            self.contribution_min_item.clear()
            self.contribution_max_item.clear()
            return

        self.activation_energy_edit.setText(str(reaction_data.get("Ea", self.defaults.ea_default)))
        self.log_a_edit.setText(str(reaction_data.get("log_A", self.defaults.log_a_default)))
        self.contribution_edit.setText(str(reaction_data.get("contribution", self.defaults.contribution_default)))

        self.ea_min_item.setText(str(reaction_data.get("Ea_min", self.defaults.ea_range[0])))
        self.ea_max_item.setText(str(reaction_data.get("Ea_max", self.defaults.ea_range[1])))

        self.log_a_min_item.setText(str(reaction_data.get("log_A_min", self.defaults.log_a_range[0])))
        self.log_a_max_item.setText(str(reaction_data.get("log_A_max", self.defaults.log_a_range[1])))

        self.contribution_min_item.setText(
            str(reaction_data.get("contribution_min", self.defaults.contribution_range[0]))
        )
        self.contribution_max_item.setText(
            str(reaction_data.get("contribution_max", self.defaults.contribution_range[1]))
        )

    def get_values(self) -> dict:
        """Get current values from all input fields."""
        return {
            "Ea": float(self.activation_energy_edit.text() or self.defaults.ea_default),
            "log_A": float(self.log_a_edit.text() or self.defaults.log_a_default),
            "contribution": float(self.contribution_edit.text() or self.defaults.contribution_default),
            "Ea_min": float(self.ea_min_item.text() or self.defaults.ea_range[0]),
            "Ea_max": float(self.ea_max_item.text() or self.defaults.ea_range[1]),
            "log_A_min": float(self.log_a_min_item.text() or self.defaults.log_a_range[0]),
            "log_A_max": float(self.log_a_max_item.text() or self.defaults.log_a_range[1]),
            "contribution_min": float(self.contribution_min_item.text() or self.defaults.contribution_range[0]),
            "contribution_max": float(self.contribution_max_item.text() or self.defaults.contribution_range[1]),
        }
