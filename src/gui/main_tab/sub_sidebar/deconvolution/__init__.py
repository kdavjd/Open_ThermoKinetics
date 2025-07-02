"""
Deconvolution module for reaction analysis.

This module provides backward compatibility by exposing the main DeconvolutionSubBar
class while maintaining the new modular internal structure.

CRITICAL: This module handles signal routing and path_keys construction properly
to avoid the errors described in SESSION_CHANGES.md
"""

from .deconvolution_panel import DeconvolutionPanel

# Backward compatibility alias
DeconvolutionSubBar = DeconvolutionPanel

__all__ = ["DeconvolutionSubBar", "DeconvolutionPanel"]
