"""Tests for ModelFreeSubBar and ModelFreeAnnotationSettingsDialog."""

from unittest.mock import patch

import pandas as pd

from src.core.app_settings import MODEL_FREE_METHODS, OperationType
from src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar import (
    ModelFreeAnnotationSettingsDialog,
    ModelFreeSubBar,
)


class TestModelFreeSubBarInit:
    """Tests for ModelFreeSubBar initialization."""

    def test_init_creates_widgets(self, qtbot):
        """ModelFreeSubBar should create all expected widgets."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        assert bar.method_combobox is not None
        assert bar.alpha_min_input is not None
        assert bar.alpha_max_input is not None
        assert bar.ea_min_input is not None
        assert bar.ea_max_input is not None
        assert bar.ea_mean_input is not None
        assert bar.calculate_button is not None
        assert bar.reaction_combobox is not None
        assert bar.beta_combobox is not None
        assert bar.results_table is not None
        assert bar.plot_button is not None
        assert bar.settings_button is not None

    def test_method_combobox_has_methods(self, qtbot):
        """Method combobox should have expected methods."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        items = [bar.method_combobox.itemText(i) for i in range(bar.method_combobox.count())]
        for method in MODEL_FREE_METHODS:
            assert method in items

    def test_default_alpha_values(self, qtbot):
        """Alpha inputs should have default values."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        assert bar.alpha_min_input.text() == "0.005"
        assert bar.alpha_max_input.text() == "0.995"

    def test_default_ea_values(self, qtbot):
        """Ea inputs should have default values."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        assert bar.ea_min_input.text() == "10"
        assert bar.ea_max_input.text() == "2000"

    def test_ea_inputs_hidden_by_default(self, qtbot):
        """Ea min/max inputs should be hidden by default."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        assert bar.ea_min_label.isHidden()
        assert bar.ea_min_input.isHidden()
        assert bar.ea_max_label.isHidden()
        assert bar.ea_max_input.isHidden()

    def test_initial_state(self, qtbot):
        """Initial state should be correctly set."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        assert bar.last_selected_reaction is None
        assert bar.last_selected_beta is None
        assert bar.is_annotate is True

    def test_results_table_columns(self, qtbot):
        """Results table should have correct column count."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        assert bar.results_table.columnCount() == 3


class TestModelFreeSubBarMethodCombobox:
    """Tests for method combobox changes."""

    def test_vyazovkin_shows_ea_inputs(self, qtbot):
        """Vyazovkin method should show Ea min/max inputs."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.method_combobox.setCurrentText("Vyazovkin")

        assert not bar.ea_min_label.isHidden()
        assert not bar.ea_min_input.isHidden()
        assert not bar.ea_max_label.isHidden()
        assert not bar.ea_max_input.isHidden()

    def test_other_method_hides_ea_inputs(self, qtbot):
        """Non-Vyazovkin methods should hide Ea min/max inputs."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        # First show them
        bar.method_combobox.setCurrentText("Vyazovkin")

        # Then switch to another method
        bar.method_combobox.setCurrentText("Friedman")

        assert bar.ea_min_label.isHidden()
        assert bar.ea_min_input.isHidden()
        assert bar.ea_max_label.isHidden()
        assert bar.ea_max_input.isHidden()

    def test_master_plots_shows_special_inputs(self, qtbot):
        """Master plots method should show Ea mean and plot dropdown."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.method_combobox.setCurrentText("master plots")

        assert not bar.ea_mean_label.isHidden()
        assert not bar.ea_mean_input.isHidden()
        assert not bar.master_plot_dropdown.isHidden()
        assert not bar.master_plot_label.isHidden()
        assert bar.results_table.isHidden()
        assert not bar.beta_combobox.isHidden()

    def test_non_master_plots_hides_special_inputs(self, qtbot):
        """Non-master plots methods should hide special inputs."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        # First show them
        bar.method_combobox.setCurrentText("master plots")

        # Then switch to another method
        bar.method_combobox.setCurrentText("Friedman")

        assert bar.ea_mean_label.isHidden()
        assert bar.ea_mean_input.isHidden()
        assert bar.master_plot_dropdown.isHidden()
        assert bar.master_plot_label.isHidden()
        assert not bar.results_table.isHidden()
        assert bar.beta_combobox.isHidden()


class TestModelFreeSubBarCalculate:
    """Tests for calculate button functionality."""

    def test_calculate_button_emits_signal(self, qtbot):
        """Calculate button should emit model_free_calculation_signal."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("0.1")
        bar.alpha_max_input.setText("0.9")

        with qtbot.wait_signal(bar.model_free_calculation_signal) as blocker:
            bar.calculate_button.click()

        assert blocker.args[0]["operation"] == OperationType.MODEL_FREE_CALCULATION
        assert blocker.args[0]["alpha_min"] == 0.1
        assert blocker.args[0]["alpha_max"] == 0.9

    def test_calculate_invalid_alpha_shows_warning(self, qtbot):
        """Invalid alpha values should show warning."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("1.5")

        with patch("src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()

    def test_calculate_alpha_min_greater_than_max_shows_warning(self, qtbot):
        """alpha_min > alpha_max should show warning."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("0.9")
        bar.alpha_max_input.setText("0.1")

        with patch("src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()

    def test_calculate_vyazovkin_includes_ea_params(self, qtbot):
        """Vyazovkin method should include Ea params in signal."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.method_combobox.setCurrentText("Vyazovkin")
        bar.ea_min_input.setText("50")
        bar.ea_max_input.setText("300")

        with qtbot.wait_signal(bar.model_free_calculation_signal) as blocker:
            bar.calculate_button.click()

        assert "ea_min" in blocker.args[0]
        assert "ea_max" in blocker.args[0]
        assert blocker.args[0]["ea_min"] == 50.0
        assert blocker.args[0]["ea_max"] == 300.0

    def test_calculate_master_plots_requires_ea_mean(self, qtbot):
        """Master plots method requires Ea mean value."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.method_combobox.setCurrentText("master plots")
        bar.ea_mean_input.setText("")  # Empty

        with patch("src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()

    def test_calculate_master_plots_requires_reaction(self, qtbot):
        """Master plots method requires reaction selection."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.method_combobox.setCurrentText("master plots")
        bar.ea_mean_input.setText("100")
        bar.reaction_combobox.setCurrentText("select reaction")  # Not selected

        with patch("src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_calculate_clicked()
            mock_warning.assert_called_once()


class TestModelFreeSubBarComboboxUpdates:
    """Tests for combobox update methods."""

    def test_emit_combobox_text(self, qtbot):
        """emit_combobox_text should emit signal with correct data."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.reaction_combobox.addItem("reaction_1")
        bar.reaction_combobox.setCurrentText("reaction_1")
        bar.method_combobox.setCurrentText("Friedman")

        with qtbot.wait_signal(bar.table_combobox_text_changed_signal) as blocker:
            bar.emit_combobox_text()

        assert blocker.args[0]["operation"] == OperationType.GET_MODEL_FREE_REACTION_DF
        assert blocker.args[0]["reaction_n"] == "reaction_1"
        assert blocker.args[0]["fit_method"] == "Friedman"

    def test_update_combobox_with_reactions(self, qtbot):
        """update_combobox_with_reactions should populate reaction combobox."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        reactions = ["reaction_1", "reaction_2"]
        bar.update_combobox_with_reactions(reactions)

        items = [bar.reaction_combobox.itemText(i) for i in range(bar.reaction_combobox.count())]
        assert items == reactions

    def test_update_combobox_preserves_selection(self, qtbot):
        """update_combobox_with_reactions should preserve last selection."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.last_selected_reaction = "reaction_2"
        reactions = ["reaction_1", "reaction_2", "reaction_3"]
        bar.update_combobox_with_reactions(reactions)

        assert bar.reaction_combobox.currentText() == "reaction_2"


class TestModelFreeSubBarResultsTable:
    """Tests for results table functionality."""

    def test_update_results_table(self, qtbot):
        """update_results_table should populate table from DataFrame."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        df = pd.DataFrame(
            {
                "conversion": [0.1, 0.2, 0.3],
                "Friedman": [100.0, 105.0, 110.0],
                "KAS": [95.0, 100.0, 105.0],
            }
        )

        bar.update_results_table(df)

        assert bar.results_table.rowCount() == 2  # 2 methods

    def test_update_fit_results(self, qtbot):
        """update_fit_results should update combobox and table."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        df = pd.DataFrame(
            {
                "conversion": [0.1, 0.2],
                "Friedman": [100.0, 105.0],
            }
        )

        fit_results = {"reaction_1": df}

        bar.update_fit_results(fit_results)

        assert bar.last_selected_reaction == "reaction_1"


class TestModelFreeSubBarPlot:
    """Tests for plot button functionality."""

    def test_plot_button_emits_signal(self, qtbot):
        """Plot button should emit plot_model_free_signal."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("0.1")
        bar.alpha_max_input.setText("0.9")
        bar.reaction_combobox.addItem("reaction_1")
        bar.reaction_combobox.setCurrentText("reaction_1")

        with qtbot.wait_signal(bar.plot_model_free_signal) as blocker:
            bar.plot_button.click()

        assert blocker.args[0]["operation"] == OperationType.PLOT_MODEL_FREE_RESULT
        assert blocker.args[0]["reaction_n"] == "reaction_1"

    def test_plot_invalid_alpha_shows_warning(self, qtbot):
        """Invalid alpha values should show warning on plot."""
        bar = ModelFreeSubBar()
        qtbot.add_widget(bar)

        bar.alpha_min_input.setText("1.5")

        with patch("src.gui.main_tab.sub_sidebar.model_free.model_free_sub_bar.QMessageBox.warning") as mock_warning:
            bar.on_plot_clicked()
            mock_warning.assert_called_once()


class TestModelFreeAnnotationSettingsDialog:
    """Tests for ModelFreeAnnotationSettingsDialog."""

    def test_init_sets_values(self, qtbot):
        """Dialog should initialize with provided values."""
        parent = None
        is_annotate = True
        config = {
            "block_top": 0.95,
            "block_left": 0.3,
            "block_right": 0.7,
            "delta_y": 0.05,
            "fontsize": 10,
            "facecolor": "white",
            "edgecolor": "black",
            "alpha": 0.9,
        }

        dialog = ModelFreeAnnotationSettingsDialog(parent, is_annotate, config)
        qtbot.add_widget(dialog)

        assert dialog.annotate_checkbox.isChecked() is True
        assert dialog.block_top_spin.value() == 0.95
        assert dialog.block_left_spin.value() == 0.3

    def test_get_settings_returns_correct_values(self, qtbot):
        """get_settings should return current dialog values."""
        parent = None
        config = {
            "block_top": 0.98,
            "block_left": 0.4,
            "block_right": 0.6,
            "delta_y": 0.03,
            "fontsize": 8,
            "facecolor": "white",
            "edgecolor": "black",
            "alpha": 1.0,
        }

        dialog = ModelFreeAnnotationSettingsDialog(parent, True, config)
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
        config = {}

        dialog = ModelFreeAnnotationSettingsDialog(parent, True, config)
        qtbot.add_widget(dialog)

        # Test accept
        dialog.button_box.accepted.emit()
        assert dialog.result() == QDialog.DialogCode.Accepted.value

    def test_dialog_reject(self, qtbot):
        """Dialog should reject correctly."""
        from PyQt6.QtWidgets import QDialog

        parent = None
        config = {}

        dialog = ModelFreeAnnotationSettingsDialog(parent, True, config)
        qtbot.add_widget(dialog)

        # Test reject via button box
        dialog.button_box.rejected.emit()
        assert dialog.result() == QDialog.DialogCode.Rejected.value
