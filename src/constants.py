import os
import tum_esm_utils
from typing import Literal, Annotated

PROJECT_DIR: Annotated[
    str,
    "The root directory of the project (the parent of `src/`)",
] = os.path.dirname(os.path.dirname(__file__))

VERSION: Annotated[
    tum_esm_utils.validators.Version,
    "The current version of the project",
] = tum_esm_utils.validators.Version("1.0.0")

NAME: Annotated[str, "The name of the project"] = "ivy"

IVY_ROOT_DIR: Annotated[
    str,
    "The root directory of the project on a production system = `~/Documents/{NAME}` or the value of the environment variable `IVY_ROOT_DIR` (if set)",
] = os.environ.get(
    "IVY_ROOT_DIR", os.path.join(os.path.expanduser("~"), "Documents", NAME)
)

LOGGING_LEVEL_PRIORITIES: Annotated[
    dict[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"],
        int,
    ],
    "Order of the logging levels from the lowest to the highest, high number means high priority",
] = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "EXCEPTION": 4}

SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN: Annotated[
    int,
    "Number of seconds to wait for a procedure process to tear down gracefully before killing it",
] = 30
