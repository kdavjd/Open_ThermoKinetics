"""Navigation domain module configuration"""

from dataclasses import dataclass
from typing import List


@dataclass
class NavigationConfig:
    """Configuration for navigation components"""

    # Tree view settings
    tree_header_labels: List[str] = None

    # Console state settings
    console_default_visible: bool = True

    # Item categories
    experiment_categories: List[str] = None
    calculation_categories: List[str] = None
    series_categories: List[str] = None

    def __post_init__(self):
        if self.tree_header_labels is None:
            self.tree_header_labels = ["app tree"]

        if self.experiment_categories is None:
            self.experiment_categories = ["add file data", "delete selected"]

        if self.calculation_categories is None:
            self.calculation_categories = ["model fit", "model free", "model based"]

        if self.series_categories is None:
            self.series_categories = ["add new series", "import series", "delete series"]


@dataclass
class SidebarDimensions:
    """Dimensions and sizing for sidebar components"""

    min_width: int = 220
    button_height: int = 30
    tree_view_height: int = 400
