from functools import reduce
from typing import Any, Optional

from src.core.app_settings import OPTIMIZATION_CONFIG, PARAMETER_BOUNDS, OperationType
from src.core.base_signals import BaseSlots
from src.core.logger_config import logger


class SeriesData(BaseSlots):
    """
    Manages experimental series with multiple heating rates and kinetic analysis results.

    Handles creation, modification, and deletion of experimental series containing
    data from multiple heating rates. Stores deconvolution results, model-fit parameters,
    model-free analysis, and reaction schemes for comprehensive kinetic studies.

    Attributes
    ----------
    series : dict[str, dict]
        Dictionary containing all experimental series with complete analysis data.
    default_name_counter : int
        Counter for auto-generating unique series names.
    """

    def __init__(self, actor_name: str = "series_data", signals=None):
        super().__init__(actor_name=actor_name, signals=signals)
        self.series = {}
        self.default_name_counter: int = 1

    def process_request(self, params: dict) -> None:  # noqa: C901
        """
        Central dispatcher for series operations and data management.

        Handles ADD_NEW_SERIES, DELETE_SERIES, UPDATE_SERIES, GET_SERIES_VALUE,
        and other series-related operations through internal handler functions.
        Manages experimental data integration and analysis result storage.

        Parameters
        ----------
        params : dict
            Request parameters including operation type, series names, and data payloads.
        """
        operation = params.get("operation")
        logger.debug(f"{self.actor_name} processing operation: {operation}")

        response = {
            "actor": self.actor_name,
            "target": params.get("actor"),
            "request_id": params.get("request_id"),
            "data": None,
            "operation": operation,
        }

        def handle_add_new_series(p: dict, r: dict) -> None:
            data = p.get("data")
            name = p.get("name")
            masses = p.get("experimental_masses")
            success, assigned_name = self.add_series(
                data=data,
                experimental_masses=masses,
                name=name,
            )
            r["data"] = success

        def handle_delete_series(p: dict, r: dict) -> None:
            name = p.get("series_name")
            success = self.delete_series(series_name=name)
            r["data"] = success

        def handle_rename_series(p: dict, r: dict) -> None:
            old_name = p.get("old_name")
            new_name = p.get("new_name")
            success = self.rename_series(old_series_name=old_name, new_series_name=new_name)
            r["data"] = success

        def handle_get_all_series(p: dict, r: dict) -> None:
            r["data"] = self.get_all_series()

        def handle_get_series(p: dict, r: dict) -> None:
            series_name = p.get("series_name")
            info_type = p.get("info_type", "experimental")
            series_data = self.get_series(series_name=series_name, info_type=info_type)
            r["data"] = series_data

        def handle_scheme_change(p: dict, r: dict):
            series_name = p.get("series_name")
            update_data = {
                "reaction_scheme": p.get("reaction_scheme", {}),
                "calculation_settings": p.get("calculation_settings", {}),
            }
            success = self.update_series(series_name, update_data)
            r["data"] = success

        def handle_update_series(p: dict, r: dict) -> None:
            series_name = p.get("series_name")
            update_data = p.get("update_data", {})
            success = self.update_series(series_name, update_data)
            r["data"] = success

        def handle_get_series_value(p: dict, r: dict) -> None:
            keys = p.get("keys")
            if not isinstance(keys, list):
                logger.error("Operation GET_SERIES_VALUE requires passing the 'keys' as a list.")
                r["data"] = {}
            else:
                r["data"] = self.get_value(keys)

        operations_map = {
            OperationType.ADD_NEW_SERIES: handle_add_new_series,
            OperationType.DELETE_SERIES: handle_delete_series,
            OperationType.RENAME_SERIES: handle_rename_series,
            OperationType.GET_ALL_SERIES: handle_get_all_series,
            OperationType.GET_SERIES: handle_get_series,
            OperationType.SCHEME_CHANGE: handle_scheme_change,
            OperationType.UPDATE_SERIES: handle_update_series,
            OperationType.GET_SERIES_VALUE: handle_get_series_value,
        }

        handler = operations_map.get(operation)
        if handler is not None:
            handler(params, response)
        else:
            logger.error(f"Unknown operation '{operation}' received by {self.actor_name}")

        self.signals.response_signal.emit(response)

    def _get_default_reaction_params(self, series_name: str):
        """Set default kinetic parameters for all reactions in series scheme."""
        bounds = PARAMETER_BOUNDS.model_based
        default_params = {
            "reaction_type": "F2",
            "allowed_models": ["F1/3", "F3/4", "F3/2", "F2", "F3"],
            "Ea": bounds.ea_default,
            "log_A": bounds.log_a_default,
            "contribution": bounds.contribution_default,
            "Ea_min": bounds.ea_min,
            "Ea_max": bounds.ea_max,
            "log_A_min": bounds.log_a_min,
            "log_A_max": bounds.log_a_max,
            "contribution_min": bounds.contribution_min,
            "contribution_max": bounds.contribution_max,
        }

        series_entry = self.series.get(series_name)
        if not series_entry:
            logger.warning(f"Series '{series_name}' not found for adding default reaction params.")
            return

        reaction_scheme = series_entry.get("reaction_scheme", {})
        reactions = reaction_scheme.get("reactions", [])

        for reaction in reactions:
            for key, value in default_params.items():
                if key not in reaction:
                    reaction[key] = value

        self.series[series_name]["reaction_scheme"] = reaction_scheme

    def add_series(
        self,
        data: Any,
        experimental_masses: list[float],
        name: Optional[str] = None,
    ):
        """
        Create new experimental series with default configuration.

        Initializes series with experimental data, reaction scheme, and optimization
        settings. Auto-generates unique names if not provided and prevents duplicates.
        Sets up default two-component reaction scheme (A→B) with parameter bounds.

        Parameters
        ----------
        data : Any
            Experimental data (typically DataFrame with multiple heating rates).
        experimental_masses : list[float]
            Mass coefficients for each heating rate experiment.
        name : str, optional
            Series name. Auto-generated if None.

        Returns
        -------
        tuple[bool, str or None]
            (Success status, assigned series name)
        """
        if name is None:
            name = f"Series {self.default_name_counter}"
            self.default_name_counter += 1
            logger.debug(f"Assigned default name: {name}")

        if name in self.series:
            logger.error(f"Series with name '{name}' already exists.")
            return False, None

        reaction_scheme = {
            "components": [{"id": "A"}, {"id": "B"}],
            "reactions": [
                {
                    "from": "A",
                    "to": "B",
                }
            ],
        }

        self.series[name] = {
            "experimental_data": data,
            "experimental_masses": experimental_masses,
            "reaction_scheme": reaction_scheme,
            "calculation_settings": {
                "method": "differential_evolution",
                "method_parameters": OPTIMIZATION_CONFIG.model_based.to_dict(),
            },
        }

        self._get_default_reaction_params(name)

        return True, name

    def update_series(self, series_name: str, update_data: dict) -> bool:
        """
        Update existing series with new data and configuration.

        Supports updating reaction schemes, calculation settings, results, and other
        series properties. Handles nested dictionary merging and reaction parameter
        validation. Automatically refreshes default parameters after updates.

        Parameters
        ----------
        series_name : str
            Name of series to update.
        update_data : dict
            New data to merge into series configuration.

        Returns
        -------
        bool
            True if update successful, False if series not found.
        """
        series_entry = self.series.get(series_name)
        if not series_entry:
            logger.error(f"Series '{series_name}' not found; update failed.")
            return False

        if "reaction_scheme" in update_data:
            self._update_reaction_scheme(series_entry, update_data["reaction_scheme"])

        for key, value in update_data.items():
            if key == "reaction_scheme":
                continue
            if isinstance(value, dict):
                existing_value = series_entry.get(key, {})
                if not isinstance(existing_value, dict):
                    existing_value = {}
                existing_value.update(value)
                series_entry[key] = existing_value
            else:
                series_entry[key] = value

        self._get_default_reaction_params(series_name)
        return True

    def _update_reaction_scheme(self, series_entry: dict, new_scheme: dict) -> None:
        """Merge new reaction scheme with existing one, preserving old reaction parameters."""
        old_scheme = series_entry.get("reaction_scheme", {})

        for key, value in new_scheme.items():
            if key != "reactions":
                old_scheme[key] = value

        if "reactions" in new_scheme:
            new_reactions = new_scheme["reactions"]
            old_reactions = old_scheme.get("reactions", [])
            old_reactions_map = {(r.get("from"), r.get("to")): r for r in old_reactions}
            updated_reactions = []
            for nr in new_reactions:
                reaction_key = (nr.get("from"), nr.get("to"))
                if reaction_key in old_reactions_map:
                    merged_reaction = {**old_reactions_map[reaction_key], **nr}
                    updated_reactions.append(merged_reaction)
                else:
                    updated_reactions.append(nr)
            old_scheme["reactions"] = updated_reactions
        series_entry["reaction_scheme"] = old_scheme

    def delete_series(self, series_name: str) -> bool:
        """Remove series from storage."""
        if series_name in self.series:
            del self.series[series_name]
            logger.info(f"Deleted series: {series_name}")
            return True
        else:
            logger.error(f"Series with name '{series_name}' not found.")
            logger.debug(f"{self.series=}")
            return False

    def rename_series(self, old_series_name: str, new_series_name: str) -> bool:
        """Rename existing series with validation."""
        if old_series_name not in self.series:
            logger.error(f"Series with name '{old_series_name}' not found.")
            return False

        if new_series_name in self.series:
            logger.error(f"Series with name '{new_series_name}' already exists.")
            return False

        self.series[new_series_name] = self.series.pop(old_series_name)
        logger.info(f"Renamed series from '{old_series_name}' to '{new_series_name}'")
        return True

    def get_series(self, series_name: str, info_type: str = "experimental"):
        """Retrieve specific series data by name and type."""
        series_entry: dict = self.series.get(series_name)
        if not series_entry:
            return None

        if info_type == "experimental":
            return series_entry.get("experimental_data", None)
        elif info_type == "scheme":
            return series_entry.get("reaction_scheme", None)
        elif info_type == "all":
            return series_entry.copy()
        else:
            logger.warning(f"Unknown info_type='{info_type}'. Returning all data by default.")
            return series_entry.copy()

    def get_all_series(self):
        """Return copy of all series data."""
        return self.series.copy()

    def get_value(self, keys: list[str]) -> dict[str, Any]:
        """Get nested value from series data using path keys."""
        return reduce(lambda data, key: data.get(key, {}), keys, self.series)
