from typing import Callable, Dict
from ror.Dataset import RORDataset
from ror.loader_utils import AvailableParameters
from ror.ror_solver import solve_model

from utils.logging import Severity


def solve_problem(dataset: RORDataset, parameters: Dict[AvailableParameters, float], logger_callback: Callable[[str, Severity], None]):
    logger_callback('Starting calculations')

    result = solve_model(dataset, parameters)

    logger_callback(f'Final rank is {result.final_rank}')