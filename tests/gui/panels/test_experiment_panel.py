"""Tests for ExperimentSubBar and its sub-components."""

from src.core.app_settings import OperationType, SideBarNames
from src.gui.main_tab.sub_sidebar.experiment.experiment_sub_bar import (
    ActionButtonsBlock,
    BackgroundSubtractionBlock,
    ExperimentSubBar,
    SmoothingBlock,
)


class TestSmoothingBlock:
    """Tests for SmoothingBlock widget."""

    def test_init_creates_widgets(self, qtbot):
        """SmoothingBlock should create all expected widgets."""
        block = SmoothingBlock()
        qtbot.add_widget(block)

        assert block.smoothing_method is not None
        assert block.n_window is not None
        assert block.n_poly is not None
        assert block.spec_settings is not None
        assert block.apply_button is not None

    def test_smoothing_method_has_items(self, qtbot):
        """Smoothing method combobox should have expected items."""
        block = SmoothingBlock()
        qtbot.add_widget(block)

        items = [block.smoothing_method.itemText(i) for i in range(block.smoothing_method.count())]
        assert "Savitzky-Golay" in items
        assert "Other" in items

    def test_window_size_default_value(self, qtbot):
        """Window size input should have default value '1'."""
        block = SmoothingBlock()
        qtbot.add_widget(block)

        assert block.n_window.text() == "1"

    def test_polynomial_order_default_value(self, qtbot):
        """Polynomial order input should have default value '0'."""
        block = SmoothingBlock()
        qtbot.add_widget(block)

        assert block.n_poly.text() == "0"

    def test_spec_settings_has_items(self, qtbot):
        """Spec settings combobox should have expected items."""
        block = SmoothingBlock()
        qtbot.add_widget(block)

        items = [block.spec_settings.itemText(i) for i in range(block.spec_settings.count())]
        assert "Nearest" in items
        assert "Other" in items

    def test_apply_button_text(self, qtbot):
        """Apply button should have 'apply' text."""
        block = SmoothingBlock()
        qtbot.add_widget(block)

        assert block.apply_button.text() == "apply"


class TestBackgroundSubtractionBlock:
    """Tests for BackgroundSubtractionBlock widget."""

    def test_init_creates_widgets(self, qtbot):
        """BackgroundSubtractionBlock should create all expected widgets."""
        block = BackgroundSubtractionBlock()
        qtbot.add_widget(block)

        assert block.background_method is not None
        assert block.range_left is not None
        assert block.range_right is not None
        assert block.apply_button is not None

    def test_background_method_has_items(self, qtbot):
        """Background method combobox should have expected items."""
        block = BackgroundSubtractionBlock()
        qtbot.add_widget(block)

        items = [block.background_method.itemText(i) for i in range(block.background_method.count())]
        assert "Linear" in items
        assert "Sigmoidal" in items
        assert "Tangential" in items
        assert "Bezier" in items

    def test_apply_button_text(self, qtbot):
        """Apply button should have 'apply' text."""
        block = BackgroundSubtractionBlock()
        qtbot.add_widget(block)

        assert block.apply_button.text() == "apply"

    def test_range_inputs_empty_by_default(self, qtbot):
        """Range inputs should be empty by default."""
        block = BackgroundSubtractionBlock()
        qtbot.add_widget(block)

        assert block.range_left.text() == ""
        assert block.range_right.text() == ""


class TestActionButtonsBlock:
    """Tests for ActionButtonsBlock widget."""

    def test_init_creates_buttons(self, qtbot):
        """ActionButtonsBlock should create all expected buttons."""
        block = ActionButtonsBlock()
        qtbot.add_widget(block)

        assert block.cancel_changes_button is not None
        assert block.conversion_button is not None
        assert block.DTG_button is not None
        assert block.deconvolution_button is not None

    def test_button_texts(self, qtbot):
        """Buttons should have expected text labels."""
        block = ActionButtonsBlock()
        qtbot.add_widget(block)

        assert block.cancel_changes_button.text() == "reset changes"
        assert block.conversion_button.text() == "to α(t)"
        assert block.DTG_button.text() == "to DTG"
        assert block.deconvolution_button.text() == "deconvolution"

    def test_cancel_changes_emits_signal(self, qtbot):
        """Cancel changes button should emit signal with RESET_FILE_DATA operation."""
        block = ActionButtonsBlock()
        qtbot.add_widget(block)

        with qtbot.wait_signal(block.cancel_changes_clicked) as blocker:
            block.cancel_changes_button.click()

        assert blocker.args[0] == {"operation": OperationType.RESET_FILE_DATA}

    def test_conversion_button_emits_signal(self, qtbot):
        """Conversion button should emit signal with TO_A_T operation."""
        block = ActionButtonsBlock()
        qtbot.add_widget(block)

        with qtbot.wait_signal(block.conversion_clicked) as blocker:
            block.conversion_button.click()

        assert blocker.args[0] == {"operation": OperationType.TO_A_T}

    def test_dtg_button_emits_signal(self, qtbot):
        """DTG button should emit signal with TO_DTG operation."""
        block = ActionButtonsBlock()
        qtbot.add_widget(block)

        with qtbot.wait_signal(block.DTG_clicked) as blocker:
            block.DTG_button.click()

        assert blocker.args[0] == {"operation": OperationType.TO_DTG}

    def test_deconvolution_button_emits_signal(self, qtbot):
        """Deconvolution button should emit signal with deconvolution value."""
        block = ActionButtonsBlock()
        qtbot.add_widget(block)

        with qtbot.wait_signal(block.deconvolution_clicked) as blocker:
            block.deconvolution_button.click()

        assert blocker.args[0] == SideBarNames.DECONVOLUTION.value


class TestExperimentSubBar:
    """Tests for ExperimentSubBar main widget."""

    def test_init_creates_sub_components(self, qtbot):
        """ExperimentSubBar should create all sub-components."""
        bar = ExperimentSubBar()
        qtbot.add_widget(bar)

        assert bar.smoothing_block is not None
        assert bar.background_subtraction_block is not None
        assert bar.action_buttons_block is not None

    def test_smoothing_block_type(self, qtbot):
        """Smoothing block should be SmoothingBlock instance."""
        bar = ExperimentSubBar()
        qtbot.add_widget(bar)

        assert isinstance(bar.smoothing_block, SmoothingBlock)

    def test_background_subtraction_block_type(self, qtbot):
        """Background subtraction block should be BackgroundSubtractionBlock instance."""
        bar = ExperimentSubBar()
        qtbot.add_widget(bar)

        assert isinstance(bar.background_subtraction_block, BackgroundSubtractionBlock)

    def test_action_buttons_block_type(self, qtbot):
        """Action buttons block should be ActionButtonsBlock instance."""
        bar = ExperimentSubBar()
        qtbot.add_widget(bar)

        assert isinstance(bar.action_buttons_block, ActionButtonsBlock)

    def test_resize_event_with_parent(self, qtbot):
        """Resize event should set maximum width from parent."""
        from PyQt6.QtWidgets import QWidget

        parent = QWidget()
        parent.setMinimumWidth(300)
        parent.setMaximumWidth(300)
        qtbot.add_widget(parent)

        bar = ExperimentSubBar(parent=parent)
        qtbot.add_widget(bar)

        # Show both widgets to trigger layout
        parent.show()
        bar.show()

        # Verify parent width is accessible
        assert parent.width() == 300

        # Trigger resize on the bar
        bar.resize(200, 400)

        # After resize, bar should have max width set from parent
        assert bar.maximumWidth() == parent.width()

    def test_layout_alignment(self, qtbot):
        """Layout should be aligned to top."""
        from PyQt6.QtCore import Qt

        bar = ExperimentSubBar()
        qtbot.add_widget(bar)

        assert bar.layout().alignment() == Qt.AlignmentFlag.AlignTop
