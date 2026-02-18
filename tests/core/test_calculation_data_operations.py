"""Tests for calculation_data_operations module."""

from unittest.mock import patch

import pytest

from src.core.app_settings import OperationType
from src.core.calculation_data_operations import CalculationsDataOperations


class TestCalculationsDataOperationsInit:
    """Tests for CalculationsDataOperations initialization."""

    def test_creation(self, mock_signals):
        """CalculationsDataOperations should initialize correctly."""
        ops = CalculationsDataOperations(mock_signals)

        assert ops.actor_name == "calculations_data_operations"
        assert ops.last_plot_time == 0
        assert ops.calculations_in_progress is False
        assert ops.reaction_variables == {}
        assert ops.reaction_chosen_functions == {}

    def test_has_signals(self, mock_signals):
        """CalculationsDataOperations should store signals reference."""
        ops = CalculationsDataOperations(mock_signals)
        assert ops.signals is mock_signals

    def test_has_pyqt_signals(self, mock_signals):
        """CalculationsDataOperations should have PyQt signals."""
        ops = CalculationsDataOperations(mock_signals)

        assert hasattr(ops, "deconvolution_signal")
        assert hasattr(ops, "plot_reaction")
        assert hasattr(ops, "reaction_params_to_gui")


class TestProcessRequest:
    """Tests for process_request method."""

    def test_invalid_path_keys(self, mock_signals):
        """process_request should handle invalid path_keys."""
        ops = CalculationsDataOperations(mock_signals)

        params = {"path_keys": None, "operation": "test"}
        ops.process_request(params)

        mock_signals.response_signal.emit.assert_not_called()

    def test_empty_path_keys(self, mock_signals):
        """process_request should handle empty path_keys."""
        ops = CalculationsDataOperations(mock_signals)

        params = {"path_keys": [], "operation": "test"}
        ops.process_request(params)

        mock_signals.response_signal.emit.assert_not_called()

    def test_unknown_operation(self, mock_signals):
        """process_request should handle unknown operation."""
        ops = CalculationsDataOperations(mock_signals)

        params = {"path_keys": ["file"], "operation": "unknown_op"}
        ops.process_request(params)

        mock_signals.response_signal.emit.assert_not_called()


class TestProtectedPlotUpdateCurves:
    """Tests for _protected_plot_update_curves method."""

    def test_skip_when_calculations_in_progress(self, mock_signals):
        """Should skip plot update when calculations are in progress."""
        ops = CalculationsDataOperations(mock_signals)
        ops.calculations_in_progress = True

        with patch.object(ops, "highlight_reaction") as mock_highlight:
            ops._protected_plot_update_curves(["file"], {})

            mock_highlight.assert_not_called()

    def test_throttle_plot_updates(self, mock_signals):
        """Should throttle rapid plot updates."""
        ops = CalculationsDataOperations(mock_signals)
        ops.last_plot_time = 100  # Far in the past

        with patch.object(ops, "highlight_reaction") as mock_highlight:
            ops._protected_plot_update_curves(["file"], {})
            mock_highlight.assert_called_once()


class TestUpdateValue:
    """Tests for update_value method."""

    def test_update_value_success(self, mock_signals):
        """update_value should update value and return result."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=True):
            with patch.object(ops, "_update_coeffs_value"):
                result = ops.update_value(["file", "reaction", "coeffs", "h"], {"value": 1.5})

        assert result == {"operation": OperationType.UPDATE_VALUE, "data": None}

    def test_update_value_with_chain(self, mock_signals):
        """update_value should skip coeffs update when is_chain=True."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=True):
            with patch.object(ops, "_update_coeffs_value") as mock_update:
                ops.update_value(["file", "reaction", "coeffs", "h"], {"value": 1.5, "is_chain": True})
                mock_update.assert_not_called()

    def test_update_value_not_found(self, mock_signals):
        """update_value should handle missing data."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=False):
            result = ops.update_value(["file", "reaction", "coeffs", "h"], {"value": 1.5})

        assert result is None


class TestRemoveReaction:
    """Tests for remove_reaction method."""

    def test_remove_reaction_success(self, mock_signals):
        """remove_reaction should remove existing reaction."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=True):
            ops.remove_reaction(["file", "reaction_1"], {})

    def test_remove_reaction_not_found(self, mock_signals):
        """remove_reaction should handle missing reaction."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=False):
            ops.remove_reaction(["file", "reaction_1"], {})

    def test_remove_reaction_insufficient_keys(self, mock_signals):
        """remove_reaction should handle insufficient path_keys."""
        ops = CalculationsDataOperations(mock_signals)

        ops.remove_reaction(["file"], {})  # Only one key, should return early


class TestHighlightReaction:
    """Tests for highlight_reaction method."""

    def test_highlight_no_data(self, mock_signals):
        """highlight_reaction should handle missing data."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=None):
            ops.highlight_reaction(["file"], {})

    def test_highlight_with_data(self, mock_signals):
        """highlight_reaction should plot reactions."""
        ops = CalculationsDataOperations(mock_signals)

        mock_data = {
            "reaction_1": {
                "coeffs": {"h": 1.0, "z": 450.0, "w": 30.0},
            }
        }

        with patch.object(ops, "handle_request_cycle", return_value=mock_data):
            with patch.object(ops, "_extract_reaction_params", return_value={}):
                ops.highlight_reaction(["file"], {})


class TestDeconvolution:
    """Tests for deconvolution method."""

    def test_deconvolution_missing_chosen_functions(self, mock_signals):
        """deconvolution should raise if chosen_functions missing."""
        ops = CalculationsDataOperations(mock_signals)

        with pytest.raises(ValueError, match="chosen_functions"):
            ops.deconvolution(["file"], {})

    def test_deconvolution_empty_chosen_functions(self, mock_signals):
        """deconvolution should raise if chosen_functions empty."""
        ops = CalculationsDataOperations(mock_signals)

        with pytest.raises(ValueError, match="chosen_functions"):
            ops.deconvolution(["file"], {"chosen_functions": {}})

    def test_deconvolution_missing_data(self, mock_signals):
        """deconvolution should raise if data missing."""
        ops = CalculationsDataOperations(mock_signals)

        with patch.object(ops, "handle_request_cycle", return_value=None):
            with pytest.raises(ValueError, match="No functions data"):
                ops.deconvolution(["file"], {"chosen_functions": {"r1": ["gauss"]}})


class TestUpdateReactionsParams:
    """Tests for update_reactions_params method."""

    def test_missing_best_combination(self, mock_signals):
        """Should handle missing best_combination."""
        ops = CalculationsDataOperations(mock_signals)

        ops.update_reactions_params(["file"], {"reactions_params": [1.0, 2.0]})
        # Should return early without error

    def test_missing_reactions_params(self, mock_signals):
        """Should handle missing reactions_params."""
        ops = CalculationsDataOperations(mock_signals)

        ops.update_reactions_params(["file"], {"best_combination": ("gauss",)})
        # Should return early without error

    def test_update_success(self, mock_signals):
        """Should update reaction parameters successfully."""
        ops = CalculationsDataOperations(mock_signals)
        ops.reaction_variables = {"reaction_1": {"h", "z", "w"}}

        with patch.object(ops, "update_value") as mock_update:
            ops.update_reactions_params(
                ["file"],
                {
                    "best_combination": ("gauss",),
                    "reactions_params": [1.0, 450.0, 30.0],
                },
            )
            # update_value should be called for each coefficient
            assert mock_update.called
