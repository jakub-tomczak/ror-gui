from typing import Callable, Dict
from ror.Dataset import RORDataset
from ror.RORResult import RORResult
from ror.loader_utils import RORParameter
from ror.ror_solver import solve_model, ProcessingCallbackData

from utils.Severity import Severity


def solve_problem(
    dataset: RORDataset,
    parameters: RORParameter,
    logger_callback: Callable[[str, Severity], None],
    calculations_callback: Callable[[ProcessingCallbackData], None],
    aggregation_method: str
) -> RORResult:
    logger_callback('Starting calculations')

    result = None
    try:
        result = solve_model(dataset, parameters, aggregation_method, progress_callback=calculations_callback)
    except Exception as e:
        calculations_callback(ProcessingCallbackData(-1, e))
        logger_callback(f'Failed during calculations: {e}', Severity.ERROR)
    logger_callback('Finished calculations', Severity.SUCCESS)

    return result
