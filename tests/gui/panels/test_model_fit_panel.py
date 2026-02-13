"""Tests for ModelFitSubBar and ModelFitAnnotationSettingsDialog."""

from unittest.mock import patch

import pandas as pd

from src.core.app_settings import MODEL_FIT_METHODS, OperationType
from src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar import (
    ModelFitAnnotationSettingsDialog,
    ModelFitSubBar,
)


class TestModelFitSubBarInit:
    """Tests for ModelFitSubBar initialization."""

    def test_init_creates_widgets(self, qtbot):
        """ModelFitSubBar should create all expected widgets."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        assert bar.model_combobox is not None
        assert bar.alpha_min_input is not None
        assert bar.alpha_max_input is not None
        assert bar.valid_proportion_input is not None
        assert bar.calculate_button is not None
        assert bar.beta_combobox is not None
        assert bar.reaction_combobox is not None
        assert bar.results_table is not None
        assert bar.plot_model_combobox is not None
        assert bar.plot_button is not None
        assert bar.settings_button is not None

    def test_model_combobox_has_methods(self, qtbot):
        """Model combobox should have expected methods."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        items = [bar.model_combobox.itemText(i) for i in range(bar.model_combobox.count())]
        for method in MODEL_FIT_METHODS:
            assert method in items

    def test_default_alpha_values(self, qtbot):
        """Alpha inputs should have default values."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        # Default values from config
        assert bar.alpha_min_input.text() == "0.005"
        assert bar.alpha_max_input.text() == "0.995"

    def test_default_valid_proportion(self, qtbot):
        """Valid proportion input should have default value."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        assert bar.valid_proportion_input.text() == "0.8"

    def test_initial_state(self, qtbot):
        """Initial state should be correctly set."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        assert bar.last_selected_reaction is None
        assert bar.last_selected_beta is None
        assert bar.is_annotate is True

    def test_results_table_columns(self, qtbot):
        """Results table should have correct column count."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        assert bar.results_table.columnCount() == 4


class TestModelFitSubBarCalculate:
    """Tests for calculate button functionality."""

    def test_calculate_button_emits_signal(self, qtbot):
        """Calculate button should emit model_fit_calculation signal."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("0.1")
        bar.alpha_max_input.setText("0.9")
        bar.valid_proportion_input.setText("0.95")

        with qtbot.wait_signal(bar.model_fit_calculation) as blocker:
            bar.calculate_button.click()

        assert blocker.args[0]["operation"] == OperationType.MODEL_FIT_CALCULATION
        assert blocker.args[0]["alpha_min"] == 0.1
        assert blocker.args[0]["alpha_max"] == 0.9
        assert blocker.args[0]["valid_proportion"] == 0.95

    def test_calculate_invalid_alpha_min_shows_warning(self, qtbot):
        """Invalid alpha_min should show warning."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("1.5")  # Invalid

        with patch("src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()

    def test_calculate_invalid_alpha_max_shows_warning(self, qtbot):
        """Invalid alpha_max should show warning."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.alpha_max_input.setText("1.5")  # Invalid

        with patch("src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()

    def test_calculate_alpha_min_greater_than_max_shows_warning(self, qtbot):
        """alpha_min > alpha_max should show warning."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("0.9")
        bar.alpha_max_input.setText("0.1")

        with patch("src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()

    def test_calculate_invalid_valid_proportion_shows_warning(self, qtbot):
        """Invalid valid_proportion should show warning."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.valid_proportion_input.setText("2.0")  # Invalid

        with patch("src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()


class TestModelFitSubBarComboboxUpdates:
    """Tests for combobox update methods."""

    def test_update_combobox_with_reactions(self, qtbot):
        """update_combobox_with_reactions should populate reaction combobox."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        reactions = ["reaction_1", "reaction_2", "reaction_3"]
        bar.update_combobox_with_reactions(reactions)

        items = [bar.reaction_combobox.itemText(i) for i in range(bar.reaction_combobox.count())]
        assert items == reactions

    def test_update_combobox_preserves_selection(self, qtbot):
        """update_combobox_with_reactions should preserve last selection if available."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.last_selected_reaction = "reaction_2"
        reactions = ["reaction_1", "reaction_2", "reaction_3"]
        bar.update_combobox_with_reactions(reactions)

        assert bar.reaction_combobox.currentText() == "reaction_2"

    def test_update_beta_combobox(self, qtbot):
        """update_beta_combobox should populate beta combobox."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        beta_values = ["5", "10", "15", "20"]
        bar.update_beta_combobox(beta_values)

        items = [bar.beta_combobox.itemText(i) for i in range(bar.beta_combobox.count())]
        assert items == beta_values

    def test_emit_combobox_text(self, qtbot):
        """emit_combobox_text should emit signal with correct data."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.reaction_combobox.addItem("reaction_1")
        bar.reaction_combobox.setCurrentText("reaction_1")
        bar.beta_combobox.addItem("10")
        bar.beta_combobox.setCurrentText("10")

        with qtbot.wait_signal(bar.table_combobox_text_changed_signal) as blocker:
            bar.emit_combobox_text()

        assert blocker.args[0]["operation"] == OperationType.GET_MODEL_FIT_REACTION_DF
        assert blocker.args[0]["reaction_n"] == "reaction_1"
        assert blocker.args[0]["beta"] == "10"


class TestModelFitSubBarResultsTable:
    """Tests for results table functionality."""

    def test_update_results_table(self, qtbot):
        """update_results_table should populate table from DataFrame."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        df = pd.DataFrame(
            {
                "model": ["F1", "F2"],
                "Ea": [100.0, 150.0],
                "logA": [10.0, 12.0],
                "R2": [0.99, 0.98],
            }
        )

        bar.update_results_table(df)

        assert bar.results_table.rowCount() == 2

    def test_update_fit_results(self, qtbot):
        """update_fit_results should update comboboxes and table."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        df = pd.DataFrame(
            {
                "model": ["F1"],
                "Ea": [100.0],
                "logA": [10.0],
                "R2": [0.99],
            }
        )

        fit_results = {
            "reaction_1": {
                "10": df,
            }
        }

        bar.update_fit_results(fit_results)

        assert bar.reaction_combobox.count() == 1
        assert bar.reaction_combobox.itemText(0) == "reaction_1"


class TestModelFitSubBarPlot:
    """Tests for plot button functionality."""

    def test_plot_button_emits_signal(self, qtbot):
        """Plot button should emit plot_model_fit_signal."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("0.1")
        bar.alpha_max_input.setText("0.9")
        bar.valid_proportion_input.setText("0.95")
        bar.beta_combobox.addItem("10")
        bar.beta_combobox.setCurrentText("10")
        bar.reaction_combobox.addItem("reaction_1")
        bar.reaction_combobox.setCurrentText("reaction_1")

        with qtbot.wait_signal(bar.plot_model_fit_signal) as blocker:
            bar.plot_button.click()

        assert blocker.args[0]["operation"] == OperationType.PLOT_MODEL_FIT_RESULT
        assert blocker.args[0]["beta"] == "10"
        assert blocker.args[0]["reaction_n"] == "reaction_1"

    def test_plot_invalid_alpha_shows_warning(self, qtbot):
        """Invalid alpha values should show warning on plot."""
        bar = ModelFitSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("1.5")

        with patch("src.gui.main_tab.sub_sidebar.model_fit.model_fit_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_plot_clicked()
            mock_warning.assert_called_once()


class TestModelFitAnnotationSettingsDialog:
    """Tests for ModelFitAnnotationSettingsDialog."""

    def _create_mock_config(self, annotation_values=None):
        """Create a mock config object with dialog attribute and get method."""
        if annotation_values is None:
            annotation_values = {}

        class MockDialogConfig:
            annotation_settings_title = "annotation settings"
            annotation_settings_width = 300
            annotation_settings_height = 300

        class MockConfig:
            dialog = MockDialogConfig()

            def get(self, key, default=None):
                return annotation_values.get(key, default)

        return MockConfig()

    def test_init_sets_values(self, qtbot):
        """Dialog should initialize with provided values."""
        parent = None
        is_annotate = True
        config = self._create_mock_config(
            {
                "block_top": 0.95,
                "block_left": 0.3,
                "block_right": 0.7,
                "delta_y": 0.05,
                "fontsize": 10,
                "facecolor": "white",
                "edgecolor": "black",
                "alpha": 0.9,
            }
        )

        dialog = ModelFitAnnotationSettingsDialog(parent, is_annotate, config)
        qtbot.add_widget(dialog)

        assert dialog.annotate_checkbox.isChecked() is True
        assert dialog.block_top_spin.value() == 0.95
        assert dialog.block_left_spin.value() == 0.3

    def test_get_settings_returns_correct_values(self, qtbot):
        """get_settings should return current dialog values."""
        parent = None
        config = self._create_mock_config(
            {
                "block_top": 0.98,
                "block_left": 0.4,
                "block_right": 0.6,
                "delta_y": 0.03,
                "fontsize": 8,
                "facecolor": "white",
                "edgecolor": "black",
                "alpha": 1.0,
            }
        )

        dialog = ModelFitAnnotationSettingsDialog(parent, True, config)
        qtbot.add_widget(dialog)

        dialog.annotate_checkbox.setChecked(False)
        dialog.block_top_spin.setValue(0.9)

        is_annotate, result_config = dialog.get_settings()

        assert is_annotate is False
        assert result_config["block_top"] == 0.9

    def test_dialog_accept(self, qtbot):
        """Dialog should accept correctly."""
        from PyQt6.QtWidgets import QDialog

        parent = None
        config = self._create_mock_config({})

        dialog = ModelFitAnnotationSettingsDialog(parent, True, config)
        qtbot.add_widget(dialog)

        # Test accept
        dialog.button_box.accepted.emit()
        assert dialog.result() == QDialog.DialogCode.Accepted.value

    def test_dialog_reject(self, qtbot):
        """Dialog should reject correctly."""
        from PyQt6.QtWidgets import QDialog

        parent = None
        config = self._create_mock_config({})

        dialog = ModelFitAnnotationSettingsDialog(parent, True, config)
        qtbot.add_widget(dialog)

        # Test reject via button box
        dialog.button_box.rejected.emit()
        assert dialog.result() == QDialog.DialogCode.Rejected.value
