import os
from typing import Literal

VERSION_REGEX: str = r"^\d+\.\d+\.\d+(-(alpha|beta|rc)\.\d+)?$"
"""Valid version name examples `1.2.3`, `4.5.6-alpha.78`, `7.8.9-beta.10`, `11.12.13-rc.14`"""

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
"""The root directory of the project (the parent of `src/`)"""

VERSION = "0.1.0"
"""The current version of the project"""

NAME = "ivy-seed"
"""The name of the project"""

IVY_ROOT_DIR = os.path.join(os.path.expanduser('~'), "Documents", NAME)
"""The root directory of the project on a production system = `~/Documents/{NAME}`"""

LOGGING_LEVEL_PRIORITIES: dict[
    Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"],
    int,
] = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "EXCEPTION": 4}
"""Order of the logging levels from the lowest to
the highest, high number means high priority"""

SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN: int = 10
"""Number of seconds to wait for a procedure process
to tear down gracefully before killing it"""
