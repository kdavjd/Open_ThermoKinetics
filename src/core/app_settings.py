from enum import Enum

import numpy as np
from numba import njit


class OperationType(Enum):
    ADD_REACTION = "add_reaction"
    REMOVE_REACTION = "remove_reaction"
    HIGHLIGHT_REACTION = "highlight_reaction"
    TO_A_T = "to_a_t"
    TO_DTG = "to_dtg"
    RESET_FILE_DATA = "reset_file_data"
    IMPORT_REACTIONS = "import_reactions"
    EXPORT_REACTIONS = "export_reactions"
    DECONVOLUTION = "deconvolution"
    STOP_CALCULATION = "stop_calculation"
    MODEL_BASED_CALCULATION = "model_based_calculation"
    GET_FILE_NAME = "get_file_name"
    PLOT_DF = "plot_df"
    PLOT_MSE_LINE = "plot_mse_line"
    CALCULATION_FINISHED = "calculation_finished"
    UPDATE_VALUE = "update_value"
    ADD_NEW_SERIES = "add_new_series"
    UPDATE_SERIES = "update_series"
    GET_SERIES_VALUE = "get_series_value"
    DELETE_SERIES = "delete_series"
    GET_ALL_SERIES = "get_all_series"
    GET_SERIES = "get_series"
    RENAME_SERIES = "rename_series"
    UPDATE_REACTIONS_PARAMS = "update_reactions_params"
    GET_VALUE = "get_value"
    SET_VALUE = "set_value"
    REMOVE_VALUE = "remove_value"
    GET_FULL_DATA = "get_full_data"
    CHECK_OPERATION = "check_differential"
    GET_DF_DATA = "get_df_data"
    GET_ALL_DATA = "get_all_data"
    LOAD_FILE = "load_file"
    SCHEME_CHANGE = "scheme_change"
    MODEL_PARAMS_CHANGE = "model_params_change"
    SELECT_SERIES = "select_series"
    LOAD_DECONVOLUTION_RESULTS = "load_deconvolution_results"
    MODEL_FIT_CALCULATION = "model_fit_calculation"
    MODEL_FREE_CALCULATION = "model_free_calculation"
    GET_MODEL_FIT_REACTION_DF = "get_model_fit_reaction_df"
    GET_MODEL_FREE_REACTION_DF = "get_model_free_reaction_df"
    PLOT_MODEL_FIT_RESULT = "plot_model_fit_result"
    PLOT_MODEL_FREE_RESULT = "plot_model_free_result"


MODEL_BASED_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS = {
    "strategy": "best1bin",
    "maxiter": 60,
    "popsize": 3,
    "tol": 0.01,
    "mutation": (0.5, 1),
    "recombination": 0.7,
    "seed": None,
    "callback": None,
    "disp": False,
    "polish": True,
    "init": "latinhypercube",
    "atol": 0,
    "updating": "deferred",
    "workers": 1,
    "constraints": (),
}

MODEL_FREE_DIFFERENTIAL_EVOLUTION_DEFAULT_KWARGS = {
    "strategy": "best1bin",
    "maxiter": 1000,
    "popsize": 15,
    "tol": 0.01,
    "mutation": (0.5, 1),
    "recombination": 0.7,
    "seed": None,
    "callback": None,
    "disp": False,
    "polish": True,
    "init": "latinhypercube",
    "atol": 0,
    "updating": "deferred",
    "workers": 1,
    "constraints": (),
}


def ensure_array(func):
    def wrapper(e, *args, **kwargs):
        e_array = np.asarray(e)
        return func(e_array, *args, **kwargs)

    return wrapper


@njit
def clip_fraction(e, eps=1e-8):
    return np.clip(e, eps, 1 - eps)


@ensure_array
@njit
def differential_F1_3(e):
    e = clip_fraction(e)
    return (3.0 / 2.0) * e ** (1.0 / 3.0)


@ensure_array
@njit
def integral_F1_3(e):
    e = clip_fraction(e)
    return 1 - e ** (2.0 / 3.0)


@ensure_array
@njit
def differential_F3_4(e):
    e = clip_fraction(e)
    return 4.0 * e ** (3.0 / 4.0)


@ensure_array
@njit
def integral_F3_4(e):
    e = clip_fraction(e)
    return 1 - e ** (1.0 / 4.0)


@ensure_array
@njit
def differential_F3_2(e):
    e = clip_fraction(e)
    return 2.0 * e ** (3.0 / 2.0)


@ensure_array
@njit
def integral_F3_2(e):
    e = clip_fraction(e)
    return e ** (-1.0 / 2.0) - 1


@ensure_array
@njit
def differential_F2(e):
    e = clip_fraction(e)
    return e**2


@ensure_array
@njit
def integral_F2(e):
    e = clip_fraction(e)
    return e ** (-1.0) - 1


@ensure_array
@njit
def differential_F3(e):
    e = clip_fraction(e)
    return e**3


@ensure_array
@njit
def integral_F3(e):
    e = clip_fraction(e)
    return e ** (-2.0) - 1


@ensure_array
@njit
def differential_F1_A1(e):
    e = clip_fraction(e)
    return e


@ensure_array
@njit
def integral_F1_A1(e):
    e = clip_fraction(e)
    return -np.log(e)


@ensure_array
@njit
def differential_A2(e):
    e = clip_fraction(e)
    return 2.0 * e * (-np.log(e)) ** 0.5


@ensure_array
@njit
def integral_A2(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** 0.5


@ensure_array
@njit
def differential_A3(e):
    e = clip_fraction(e)
    return 3.0 * e * (-np.log(e)) ** (2.0 / 3.0)


@ensure_array
@njit
def integral_A3(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** (1.0 / 3.0)


@ensure_array
@njit
def differential_A4(e):
    e = clip_fraction(e)
    return 4.0 * e * (-np.log(e)) ** (3.0 / 4.0)


@ensure_array
@njit
def integral_A4(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** (1.0 / 4.0)


@ensure_array
@njit
def differential_A2_3(e):
    e = clip_fraction(e)
    return (2.0 / 3.0) * e * (-np.log(e)) ** (-0.5)


@ensure_array
@njit
def integral_A2_3(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** (3.0 / 2.0)


@ensure_array
@njit
def differential_A3_2(e):
    e = clip_fraction(e)
    return (3.0 / 2.0) * e * (-np.log(e)) ** (1.0 / 3.0)


@ensure_array
@njit
def integral_A3_2(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** (2.0 / 3.0)


@ensure_array
@njit
def differential_A3_4(e):
    e = clip_fraction(e)
    return (3.0 / 4.0) * e * (-np.log(e)) ** (-1.0 / 3.0)


@ensure_array
@njit
def integral_A3_4(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** (4.0 / 3.0)


@ensure_array
@njit
def differential_A5_2(e):
    e = clip_fraction(e)
    return (5.0 / 2.0) * e * (-np.log(e)) ** (3.0 / 5.0)


@ensure_array
@njit
def integral_A5_2(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** (2.0 / 5.0)


@ensure_array
@njit
def differential_F0_R1_P1(e):
    e = clip_fraction(e)
    return np.full_like(e, 1)


@ensure_array
@njit
def integral_F0_R1_P1(e):
    e = clip_fraction(e)
    return 1 - e


@ensure_array
@njit
def differential_R2(e):
    e = clip_fraction(e)
    return 2.0 * e**0.5


@ensure_array
@njit
def integral_R2(e):
    e = clip_fraction(e)
    return 1 - e**0.5


@ensure_array
@njit
def differential_R3(e):
    e = clip_fraction(e)
    return 3.0 * e ** (2.0 / 3.0)


@ensure_array
@njit
def integral_R3(e):
    e = clip_fraction(e)
    return 1 - e ** (1.0 / 3.0)


@ensure_array
@njit
def differential_P3_2(e):
    e = clip_fraction(e)
    return (2.0 / 3.0) / (1 - e) ** 0.5


@ensure_array
@njit
def integral_P3_2(e):
    e = clip_fraction(e)
    return (1 - e) ** (3.0 / 2.0)


@ensure_array
@njit
def differential_P2(e):
    e = clip_fraction(e)
    return 2.0 * (1 - e) ** 0.5


@ensure_array
@njit
def integral_P2(e):
    e = clip_fraction(e)
    return (1 - e) ** 0.5


@ensure_array
@njit
def differential_P3(e):
    e = clip_fraction(e)
    return 3.0 * (1 - e) ** (2.0 / 3.0)


@ensure_array
@njit
def integral_P3(e):
    e = clip_fraction(e)
    return (1 - e) ** (1.0 / 3.0)


@ensure_array
@njit
def differential_P4(e):
    e = clip_fraction(e)
    return 4.0 * (1 - e) ** (3.0 / 4.0)


@ensure_array
@njit
def integral_P4(e):
    e = clip_fraction(e)
    return (1 - e) ** (1.0 / 4.0)


@ensure_array
@njit
def differential_E1(e):
    e = clip_fraction(e)
    return 1 - e


@ensure_array
@njit
def integral_E1(e):
    e = clip_fraction(e)
    return np.log(1 - e)


@ensure_array
@njit
def differential_E2(e):
    e = clip_fraction(e)
    return (1 - e) / 2.0


@ensure_array
@njit
def integral_E2(e):
    e = clip_fraction(e)
    return np.log((1 - e) ** 2)


@ensure_array
@njit
def differential_D1(e):
    e = clip_fraction(e)
    return 1.0 / (2.0 * (1 - e))


@ensure_array
@njit
def integral_D1(e):
    e = clip_fraction(e)
    return (1 - e) ** 2


@ensure_array
@njit
def differential_D2(e):
    e = clip_fraction(e)
    return 1.0 / (-np.log(e))


@ensure_array
@njit
def integral_D2(e):
    e = clip_fraction(e)
    return (1 - e) + e * np.log(e)


@ensure_array
@njit
def differential_D3(e):
    e = clip_fraction(e)
    return ((3.0 / 2.0) * e ** (2.0 / 3.0)) / (1 - e ** (1.0 / 3.0))


@ensure_array
@njit
def integral_D3(e):
    e = clip_fraction(e)
    return (1 - e ** (1.0 / 3.0)) ** 2


@ensure_array
@njit
def differential_D4(e):
    e = clip_fraction(e)
    return (3.0 / 2.0) / (e ** (-1.0 / 3.0) - 1)


@ensure_array
@njit
def integral_D4(e):
    e = clip_fraction(e)
    return 1 - (2 * (1 - e) / 3.0) - e ** (2.0 / 3.0)


@ensure_array
@njit
def differential_D5(e):
    e = clip_fraction(e)
    return ((3.0 / 2.0) * e ** (4.0 / 3.0)) / (e ** (-1.0 / 3.0) - 1)


@ensure_array
@njit
def integral_D5(e):
    e = clip_fraction(e)
    return (e ** (-1.0 / 3.0) - 1) ** 2


@ensure_array
@njit
def differential_D6(e):
    e = clip_fraction(e)
    return ((3.0 / 2.0) * (1 + e) ** (2.0 / 3.0)) / ((1 + e) ** (1.0 / 3.0) - 1)


@ensure_array
@njit
def integral_D6(e):
    e = clip_fraction(e)
    return ((1 + e) ** (1.0 / 3.0) - 1) ** 2


@ensure_array
@njit
def differential_D7(e):
    e = clip_fraction(e)
    return (3.0 / 2.0) / (1 - (1 + e) ** (-1.0 / 3.0))


@ensure_array
@njit
def integral_D7(e):
    e = clip_fraction(e)
    return 1 + (2 * (1 - e) / 3.0) - (1 + e) ** (2.0 / 3.0)


@ensure_array
@njit
def differential_D8(e):
    e = clip_fraction(e)
    return ((3.0 / 2.0) * (1 + e) ** (4.0 / 3.0)) / (1 - (1 + e) ** (-1.0 / 3.0))


@ensure_array
@njit
def integral_D8(e):
    e = clip_fraction(e)
    return ((1 + e) ** (-1.0 / 3.0) - 1) ** 2


@ensure_array
@njit
def differential_G1(e):
    e = clip_fraction(e)
    return 1.0 / (2.0 * e)


@ensure_array
@njit
def integral_G1(e):
    e = clip_fraction(e)
    return 1 - e**2


@ensure_array
@njit
def differential_G2(e):
    e = clip_fraction(e)
    return 1.0 / (3.0 * e**2)


@ensure_array
@njit
def integral_G2(e):
    e = clip_fraction(e)
    return 1 - e**3


@ensure_array
@njit
def differential_G3(e):
    e = clip_fraction(e)
    return 1.0 / (4.0 * e**3)


@ensure_array
@njit
def integral_G3(e):
    e = clip_fraction(e)
    return 1 - e**4


@ensure_array
@njit
def differential_G4(e):
    e = clip_fraction(e)
    return (1.0 / 2.0) * e * (-np.log(e))


@ensure_array
@njit
def integral_G4(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** 2


@ensure_array
@njit
def differential_G5(e):
    e = clip_fraction(e)
    return (1.0 / 3.0) * e * (-np.log(e)) ** 2


@ensure_array
@njit
def integral_G5(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** 3


@ensure_array
@njit
def differential_G6(e):
    e = clip_fraction(e)
    return (1.0 / 4.0) * e * (-np.log(e)) ** 3


@ensure_array
@njit
def integral_G6(e):
    e = clip_fraction(e)
    return (-np.log(e)) ** 4


@ensure_array
@njit
def differential_G7(e):
    e = clip_fraction(e)
    return (1.0 / 4.0) * e**0.5 / (1 - e**0.5)


@ensure_array
@njit
def integral_G7(e):
    e = clip_fraction(e)
    return (1 - e**0.5) ** 0.5


@ensure_array
@njit
def differential_G8(e):
    e = clip_fraction(e)
    return (1.0 / 3.0) * e ** (2.0 / 3.0) / (1 - e ** (1.0 / 3.0))


@ensure_array
@njit
def integral_G8(e):
    e = clip_fraction(e)
    return (1 - e ** (1.0 / 3.0)) ** 0.5


@ensure_array
@njit
def differential_B1(e):
    e = clip_fraction(e)
    return 1.0 / ((1 - e) - e)


@ensure_array
@njit
def integral_B1(e):
    e = clip_fraction(e)
    return np.log((1 - e) / e)


# Обновлённый словарь моделей
NUC_MODELS_TABLE = {
    "F1/3": {"differential_form": differential_F1_3, "integral_form": integral_F1_3},
    "F3/4": {"differential_form": differential_F3_4, "integral_form": integral_F3_4},
    "F3/2": {"differential_form": differential_F3_2, "integral_form": integral_F3_2},
    "F2": {"differential_form": differential_F2, "integral_form": integral_F2},
    "F3": {"differential_form": differential_F3, "integral_form": integral_F3},
    "F1/A1": {"differential_form": differential_F1_A1, "integral_form": integral_F1_A1},
    "A2": {"differential_form": differential_A2, "integral_form": integral_A2},
    "A3": {"differential_form": differential_A3, "integral_form": integral_A3},
    "A4": {"differential_form": differential_A4, "integral_form": integral_A4},
    "A2/3": {"differential_form": differential_A2_3, "integral_form": integral_A2_3},
    "A3/2": {"differential_form": differential_A3_2, "integral_form": integral_A3_2},
    "A3/4": {"differential_form": differential_A3_4, "integral_form": integral_A3_4},
    "A5/2": {"differential_form": differential_A5_2, "integral_form": integral_A5_2},
    "F0/R1/P1": {"differential_form": differential_F0_R1_P1, "integral_form": integral_F0_R1_P1},
    "R2": {"differential_form": differential_R2, "integral_form": integral_R2},
    "R3": {"differential_form": differential_R3, "integral_form": integral_R3},
    "P3/2": {"differential_form": differential_P3_2, "integral_form": integral_P3_2},
    "P2": {"differential_form": differential_P2, "integral_form": integral_P2},
    "P3": {"differential_form": differential_P3, "integral_form": integral_P3},
    "P4": {"differential_form": differential_P4, "integral_form": integral_P4},
    "E1": {"differential_form": differential_E1, "integral_form": integral_E1},
    "E2": {"differential_form": differential_E2, "integral_form": integral_E2},
    "D1": {"differential_form": differential_D1, "integral_form": integral_D1},
    "D2": {"differential_form": differential_D2, "integral_form": integral_D2},
    "D3": {"differential_form": differential_D3, "integral_form": integral_D3},
    "D4": {"differential_form": differential_D4, "integral_form": integral_D4},
    "D5": {"differential_form": differential_D5, "integral_form": integral_D5},
    "D6": {"differential_form": differential_D6, "integral_form": integral_D6},
    "D7": {"differential_form": differential_D7, "integral_form": integral_D7},
    "D8": {"differential_form": differential_D8, "integral_form": integral_D8},
    "G1": {"differential_form": differential_G1, "integral_form": integral_G1},
    "G2": {"differential_form": differential_G2, "integral_form": integral_G2},
    "G3": {"differential_form": differential_G3, "integral_form": integral_G3},
    "G4": {"differential_form": differential_G4, "integral_form": integral_G4},
    "G5": {"differential_form": differential_G5, "integral_form": integral_G5},
    "G6": {"differential_form": differential_G6, "integral_form": integral_G6},
    "G7": {"differential_form": differential_G7, "integral_form": integral_G7},
    "G8": {"differential_form": differential_G8, "integral_form": integral_G8},
    "B1": {"differential_form": differential_B1, "integral_form": integral_B1},
}


NUC_MODELS_LIST = sorted(NUC_MODELS_TABLE.keys())


# def clip_fraction_decorator(eps=1e-8):
#     def decorator(func):
#         def wrapper(e, *args, **kwargs):
#             e_clamped = clip_fraction(e, eps=eps)
#             return func(e_clamped, *args, **kwargs)

#         return wrapper

#     return decorator


MODEL_FIT_METHODS = ["direct-diff", "Coats-Redfern", "Freeman-Carroll"]
MODEL_FREE_METHODS = [
    "linear approximation",
    "Friedman",
    "Kissinger",
    "Vyazovkin",
    "master plots",
]

MODEL_FIT_ANNOTATION_CONFIG = {
    "block_top": 0.98,
    "block_left": 0.4,
    "block_right": 0.6,
    "delta_y": 0.03,
    "fontsize": 8,
    "facecolor": "white",
    "edgecolor": "black",
    "alpha": 1.0,
}


MODEL_FREE_ANNOTATION_CONFIG = {
    "block_top": 0.98,
    "block_left": 0.35,
    "block_right": 0.65,
    "delta_y": 0.03,
    "fontsize": 8,
    "facecolor": "white",
    "edgecolor": "black",
    "alpha": 1.0,
}


class SideBarNames(Enum):
    MODEL_BASED = "model based"
    MODEL_FREE = "model free"
    MODEL_FIT = "model fit"
    EXPERIMENTS = "experiments"
    SERIES = "series"
    DECONVOLUTION = "deconvolution"
