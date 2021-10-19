from typing import Callable
from utils.Severity import Severity


LoggerFunc = Callable[[str, Severity], None]