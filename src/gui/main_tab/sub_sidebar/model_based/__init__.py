"""
Model-based analysis module for solid-state kinetics.

This module provides backward compatibility by exposing the main ModelBasedTab class
from the original monolithic model_based.py file structure.
"""

# Import main components for backward compatibility
from .model_based_panel import ModelBasedTab

# Export for external imports
__all__ = ["ModelBasedTab"]
