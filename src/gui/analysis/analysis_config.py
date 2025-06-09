"""
Analysis Configuration Module
Contains dataclasses for deconvolution, model-fit, and model-free analysis configurations.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ModelFreeConfig:
    """Configuration for model-free analysis"""

    methods: List[str] = None
    alpha_min_default: float = 0.005
    alpha_max_default: float = 0.995
    ea_min_default: float = 10.0
    ea_max_default: float = 2000.0
    ea_mean_default: float = 120.0
    plot_types: List[str] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = ["linear approximation", "Friedman", "Kissinger", "Vyazovkin", "master plots"]
        if self.plot_types is None:
            self.plot_types = ["y(α)", "g(α)", "z(α)"]


@dataclass
class ModelFitConfig:
    """Configuration for model-fit analysis"""

    methods: List[str] = None
    alpha_min_default: float = 0.005
    alpha_max_default: float = 0.995
    valid_proportion_default: float = 0.8

    def __post_init__(self):
        if self.methods is None:
            self.methods = ["direct-diff", "Coats-Redfern", "Freeman-Carroll"]


@dataclass
class DeconvolutionConfig:
    """Configuration for deconvolution analysis"""

    default_functions: List[str] = None
    optimization_methods: List[str] = None
    max_iterations_default: int = 200
    population_size_default: int = 15
    tolerance_default: float = 0.01

    def __post_init__(self):
        if self.default_functions is None:
            self.default_functions = ["ads", "gauss", "fraser"]
        if self.optimization_methods is None:
            self.optimization_methods = ["differential_evolution", "minimize"]


@dataclass
class AnnotationConfig:
    """Configuration for plot annotations"""

    model_fit_top: float = 0.98
    model_fit_left: float = 0.4
    model_fit_right: float = 0.6
    model_free_top: float = 0.98
    model_free_left: float = 0.35
    model_free_right: float = 0.65
    delta_y: float = 0.03
    fontsize: int = 8
    facecolor: str = "white"
    edgecolor: str = "black"
    alpha: float = 1.0


@dataclass
class SeriesConfig:
    """Configuration for series analysis"""

    dialog_min_width: int = 300
    field_width: int = 290
    heating_rate_width: int = 80
    file_input_row_height: int = 50
    add_button_height: int = 40
    window_padding: int = 50
    default_mass: float = 1.0


@dataclass
class CalculationDefaultsConfig:
    """Default calculation parameters"""

    # Differential evolution defaults
    strategy: str = "best1bin"
    maxiter: int = 200
    popsize: int = 15
    tol: float = 0.01
    mutation: Tuple[float, float] = (0.5, 1.0)
    recombination: float = 0.7
    polish: bool = False
    workers: int = 1  # Single worker to avoid multiprocessing issues


@dataclass
class AnalysisConfig:
    """Main analysis configuration combining all analysis settings"""

    model_free: ModelFreeConfig = None
    model_fit: ModelFitConfig = None
    deconvolution: DeconvolutionConfig = None
    annotation: AnnotationConfig = None
    series: SeriesConfig = None
    calculation_defaults: CalculationDefaultsConfig = None

    def __post_init__(self):
        """Initialize nested configurations with defaults"""
        if self.model_free is None:
            self.model_free = ModelFreeConfig()
        if self.model_fit is None:
            self.model_fit = ModelFitConfig()
        if self.deconvolution is None:
            self.deconvolution = DeconvolutionConfig()
        if self.annotation is None:
            self.annotation = AnnotationConfig()
        if self.series is None:
            self.series = SeriesConfig()
        if self.calculation_defaults is None:
            self.calculation_defaults = CalculationDefaultsConfig()
