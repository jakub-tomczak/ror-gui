from typing import Callable, Dict
from ror.Dataset import RORDataset
from ror.RORResult import RORResult
from ror.loader_utils import RORParameter
from ror.ror_solver import solve_model, ProcessingCallbackData

from utils.logging import Severity


def solve_problem(
    dataset: RORDataset,
    parameters: RORParameter,
    logger_callback: Callable[[str, Severity], None],
    calculations_callback: Callable[[ProcessingCallbackData], None]
) -> RORResult:
    logger_callback('Starting calculations')

    result = solve_model(dataset, parameters, calculations_callback)

    logger_callback('Finished calculations')

    return result
