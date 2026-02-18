"""Tests for DeconvolutionPanel and its sub-components."""

from unittest.mock import MagicMock

from src.gui.main_tab.sub_sidebar.deconvolution.deconvolution_panel import DeconvolutionPanel


class TestDeconvolutionPanelInit:
    """Tests for DeconvolutionPanel initialization."""

    def test_init_creates_child_components(self, qtbot):
        """DeconvolutionPanel should create all child components."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        assert panel.reactions_table is not None
        assert panel.coeffs_table is not None
        assert panel.file_transfer_buttons is not None
        assert panel.calc_buttons is not None

    def test_init_creates_config(self, qtbot):
        """DeconvolutionPanel should create config instance."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        assert panel.config is not None

    def test_update_value_signal_exists(self, qtbot):
        """DeconvolutionPanel should have update_value signal."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        assert hasattr(panel, "update_value")
        assert panel.update_value is not None


class TestDeconvolutionPanelSignalHandling:
    """Tests for DeconvolutionPanel signal handling."""

    def test_handle_coeffs_update_emits_signal(self, qtbot):
        """_handle_coeffs_update should emit update_value signal with data."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        test_data = {"path_keys": ["reaction_1", "init", "h"], "value": 0.5}

        with qtbot.wait_signal(panel.update_value) as blocker:
            panel._handle_coeffs_update(test_data)

        assert blocker.args[0] == test_data

    def test_handle_function_update_emits_signal(self, qtbot):
        """_handle_function_update should emit update_value when active reaction exists."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock active_reaction
        panel.reactions_table.active_reaction = "reaction_1"

        test_data = {"path_keys": ["reaction_1"], "function": "gauss"}

        with qtbot.wait_signal(panel.update_value) as blocker:
            panel._handle_function_update(test_data)

        assert blocker.args[0] == test_data

    def test_handle_function_update_no_signal_without_active_reaction(self, qtbot):
        """_handle_function_update should not emit when no active reaction."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Ensure no active reaction
        panel.reactions_table.active_reaction = None

        test_data = {"path_keys": ["reaction_1"], "function": "gauss"}

        # Should not emit signal
        with qtbot.assert_not_emitted(panel.update_value):
            panel._handle_function_update(test_data)


class TestDeconvolutionPanelBackwardCompatibility:
    """Tests for backward compatibility methods."""

    def test_active_file_property(self, qtbot):
        """active_file property should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        panel.reactions_table.active_file = "test_file.csv"
        assert panel.active_file == "test_file.csv"

    def test_active_reaction_property(self, qtbot):
        """active_reaction property should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        panel.reactions_table.active_reaction = "reaction_1"
        assert panel.active_reaction == "reaction_1"

    def test_switch_file_delegates(self, qtbot):
        """switch_file should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.reactions_table.switch_file = MagicMock()

        panel.switch_file("test_file.csv")

        panel.reactions_table.switch_file.assert_called_once_with("test_file.csv")

    def test_add_reaction_delegates(self, qtbot):
        """add_reaction should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.reactions_table.add_reaction = MagicMock()

        panel.add_reaction(checked=False, reaction_name="reaction_1", emit_signal=True)

        panel.reactions_table.add_reaction.assert_called_once_with(False, "reaction_1", None, True)

    def test_on_fail_add_reaction_delegates(self, qtbot):
        """on_fail_add_reaction should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.reactions_table.on_fail_add_reaction = MagicMock()

        panel.on_fail_add_reaction()

        panel.reactions_table.on_fail_add_reaction.assert_called_once()

    def test_fill_coeffs_table_delegates(self, qtbot):
        """fill_coeffs_table should delegate to coeffs_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.coeffs_table.fill_table = MagicMock()

        test_params = {"h": {"init": 0.1, "bound": "fixed"}}
        panel.fill_coeffs_table(test_params)

        panel.coeffs_table.fill_table.assert_called_once_with(test_params)

    def test_handle_update_coeffs_value_delegates(self, qtbot):
        """handle_update_coeffs_value should delegate to coeffs_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.coeffs_table.handle_update_value = MagicMock()

        test_updates = [{"path_keys": ["h"], "value": 0.2}]
        panel.handle_update_coeffs_value(test_updates)

        panel.coeffs_table.handle_update_value.assert_called_once_with(test_updates)

    def test_get_reactions_for_file_delegates(self, qtbot):
        """get_reactions_for_file should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.reactions_table.get_reactions_for_file = MagicMock(return_value={"r1": MagicMock()})

        result = panel.get_reactions_for_file("test.csv")

        panel.reactions_table.get_reactions_for_file.assert_called_once_with("test.csv")
        assert "r1" in result

    def test_open_settings_dialog_delegates(self, qtbot):
        """open_settings_dialog should delegate to reactions_table."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock the method
        panel.reactions_table.open_settings = MagicMock()

        panel.open_settings_dialog()

        panel.reactions_table.open_settings.assert_called_once()


class TestDeconvolutionPanelReactionSelection:
    """Tests for reaction selection handling."""

    def test_handle_reaction_selection_updates_context(self, qtbot):
        """_handle_reaction_selection should update coeffs_table context."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock methods
        panel.reactions_table.active_file = "test.csv"
        panel.coeffs_table.set_context = MagicMock()

        test_data = {"path_keys": ["reaction_1"]}
        panel._handle_reaction_selection(test_data)

        panel.coeffs_table.set_context.assert_called_once_with("test.csv", "reaction_1")

    def test_handle_reaction_selection_no_path_keys(self, qtbot):
        """_handle_reaction_selection should do nothing without path_keys."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock method
        panel.coeffs_table.set_context = MagicMock()

        test_data = {"path_keys": []}
        panel._handle_reaction_selection(test_data)

        panel.coeffs_table.set_context.assert_not_called()

    def test_handle_reaction_selection_empty_path_keys(self, qtbot):
        """_handle_reaction_selection should do nothing with empty path_keys."""
        panel = DeconvolutionPanel()
        qtbot.add_widget(panel)

        # Mock method
        panel.coeffs_table.set_context = MagicMock()

        test_data = {}
        panel._handle_reaction_selection(test_data)

        panel.coeffs_table.set_context.assert_not_called()
