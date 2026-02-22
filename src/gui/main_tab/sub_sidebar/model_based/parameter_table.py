"""
Parameter table component for model-based analysis.
Contains the ReactionTable widget for editing kinetic parameters.
"""

from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.app_settings import PARAMETER_BOUNDS

from .config import MODEL_BASED_CONFIG


@dataclass
class ReactionDefaults:
    """Default reaction parameter values."""

    def __init__(self):
        bounds = PARAMETER_BOUNDS.model_based
        self.Ea_default = bounds.ea_default
        self.log_A_default = bounds.log_a_default
        self.contribution_default = bounds.contribution_default
        self.Ea_range = (bounds.ea_min, bounds.ea_max)
        self.log_A_range = (bounds.log_a_min, bounds.log_a_max)
        self.contribution_range = (bounds.contribution_min, bounds.contribution_max)


class ReactionTable(QTableWidget):
    """Table widget for editing kinetic parameters of reactions."""

    def __init__(self, parent=None):
        """Initialize reaction table with parameter rows."""
        config = MODEL_BASED_CONFIG.table_config
        super().__init__(config.DEFAULT_ROWS, config.DEFAULT_COLS, parent)

        self.setHorizontalHeaderLabels(config.COLUMN_HEADERS)

        # Hide vertical header (row numbers 1, 2, 3)
        self.verticalHeader().hide()

        # Set consistent row height for embedded QLineEdit widgets
        self.verticalHeader().setDefaultSectionSize(30)

        # Disable mouse tracking — prevents hover from triggering selection/cell signals
        self.setMouseTracking(False)

        # Prevent accidental editing of label cells (editing is via embedded QLineEdits only)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Column resize modes: Parameter label fixed, Value stretches to fill available width
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Hide min/max columns by default
        for col in config.HIDDEN_COLUMNS:
            self.setColumnHidden(col, True)

        # Create parameter rows
        self._setup_ea_row(config)
        self._setup_log_a_row(config)
        self._setup_contribution_row(config)

        self.defaults = ReactionDefaults()

    def _create_centered_widget(self, widget: QLineEdit) -> QWidget:
        """Wrap widget in a container for vertical centering in cell."""
        widget.setFixedHeight(26)  # Fixed height prevents vertical stretching
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(widget)
        return container

    def _setup_ea_row(self, config):
        """Setup activation energy parameter row."""
        self.setItem(0, 0, QTableWidgetItem(config.EA_LABEL))
        self.activation_energy_edit = QLineEdit()
        self.setCellWidget(0, 1, self._create_centered_widget(self.activation_energy_edit))

        self.ea_min_item = QLineEdit()
        self.setCellWidget(0, 2, self._create_centered_widget(self.ea_min_item))
        self.ea_max_item = QLineEdit()
        self.setCellWidget(0, 3, self._create_centered_widget(self.ea_max_item))

    def _setup_log_a_row(self, config):
        """Setup log(A) parameter row."""
        self.setItem(1, 0, QTableWidgetItem(config.LOG_A_LABEL))
        self.log_a_edit = QLineEdit()
        self.setCellWidget(1, 1, self._create_centered_widget(self.log_a_edit))

        self.log_a_min_item = QLineEdit()
        self.setCellWidget(1, 2, self._create_centered_widget(self.log_a_min_item))
        self.log_a_max_item = QLineEdit()
        self.setCellWidget(1, 3, self._create_centered_widget(self.log_a_max_item))

    def _setup_contribution_row(self, config):
        """Setup contribution parameter row."""
        self.setItem(2, 0, QTableWidgetItem(config.CONTRIBUTION_LABEL))
        self.contribution_edit = QLineEdit()
        self.setCellWidget(2, 1, self._create_centered_widget(self.contribution_edit))

        self.contribution_min_item = QLineEdit()
        self.setCellWidget(2, 2, self._create_centered_widget(self.contribution_min_item))
        self.contribution_max_item = QLineEdit()
        self.setCellWidget(2, 3, self._create_centered_widget(self.contribution_max_item))

    def set_ranges_visible(self, visible: bool):
        """Show or hide the min/max range columns."""
        config = MODEL_BASED_CONFIG.table_config
        for col in config.HIDDEN_COLUMNS:
            self.setColumnHidden(col, not visible)
        self.viewport().update()

    def update_value_with_best(self, best_data: dict):
        """Update parameter values with optimization results."""
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
        """Update table with reaction parameter data."""
        if not reaction_data:
            self._clear_table()
            return

        # Update parameter values
        self.activation_energy_edit.setText(str(reaction_data.get("Ea", self.defaults.Ea_default)))
        self.log_a_edit.setText(str(reaction_data.get("log_A", self.defaults.log_A_default)))
        self.contribution_edit.setText(str(reaction_data.get("contribution", self.defaults.contribution_default)))

        # Update range values
        self.ea_min_item.setText(str(reaction_data.get("Ea_min", self.defaults.Ea_range[0])))
        self.ea_max_item.setText(str(reaction_data.get("Ea_max", self.defaults.Ea_range[1])))

        self.log_a_min_item.setText(str(reaction_data.get("log_A_min", self.defaults.log_A_range[0])))
        self.log_a_max_item.setText(str(reaction_data.get("log_A_max", self.defaults.log_A_range[1])))

        self.contribution_min_item.setText(
            str(reaction_data.get("contribution_min", self.defaults.contribution_range[0]))
        )
        self.contribution_max_item.setText(
            str(reaction_data.get("contribution_max", self.defaults.contribution_range[1]))
        )

    def _clear_table(self):
        """Clear all parameter values."""
        self.activation_energy_edit.clear()
        self.log_a_edit.clear()
        self.contribution_edit.clear()
        self.ea_min_item.clear()
        self.ea_max_item.clear()
        self.log_a_min_item.clear()
        self.log_a_max_item.clear()
        self.contribution_min_item.clear()
        self.contribution_max_item.clear()
