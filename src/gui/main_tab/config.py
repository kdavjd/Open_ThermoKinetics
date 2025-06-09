"""
Configuration for MainTab component.
Contains layout settings and constants specific to the main tab.
"""

from dataclasses import dataclass


@dataclass
class MainTabConfig:
    """Configuration for the main tab layout and behavior."""

    # Layout dimensions extracted from main_tab.py
    MIN_WIDTH_SIDEBAR: int = 220
    MIN_WIDTH_SUBSIDEBAR: int = 220
    MIN_WIDTH_CONSOLE: int = 150
    MIN_WIDTH_PLOTCANVAS: int = 500
    SPLITTER_WIDTH: int = 100
    MIN_HEIGHT_MAINTAB: int = 700

    @property
    def COMPONENTS_MIN_WIDTH(self) -> int:
        """Calculate minimum width for all components."""
        return (
            self.MIN_WIDTH_SIDEBAR
            + self.MIN_WIDTH_SUBSIDEBAR
            + self.MIN_WIDTH_CONSOLE
            + self.MIN_WIDTH_PLOTCANVAS
            + self.SPLITTER_WIDTH
        )

    def get_splitter_ratios(self) -> tuple[float, float, float]:
        """Calculate splitter ratios for responsive layout."""
        total = self.COMPONENTS_MIN_WIDTH
        sidebar_ratio = self.MIN_WIDTH_SIDEBAR / total
        subsidebar_ratio = self.MIN_WIDTH_SUBSIDEBAR / total
        console_ratio = self.MIN_WIDTH_CONSOLE / total
        return sidebar_ratio, subsidebar_ratio, console_ratio


# Global instance
MAIN_TAB_CONFIG = MainTabConfig()
