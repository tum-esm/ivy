import os
from typing import Literal, Annotated

# TODO: use a class for version numbers (with classes `as_version` and `as_v_tag`) and comparison operator

VERSION_REGEX: Annotated[
    str,
    "Valid version name examples `1.2.3`, `4.5.6-alpha.78`, `7.8.9-beta.10`, `11.12.13-rc.14`"
] = r"^\d+\.\d+\.\d+(-(alpha|beta|rc)\.\d+)?$"

PROJECT_DIR: Annotated[
    str,
    "The root directory of the project (the parent of `src/`)",
] = os.path.dirname(os.path.dirname(__file__))

VERSION: Annotated[
    Literal["1.0.0"],
    "The current version of the project",
] = "1.0.0"

NAME: Annotated[str, "The name of the project"] = "ivy"

IVY_ROOT_DIR: Annotated[
    str,
    "The root directory of the project on a production system = `~/Documents/{NAME}`",
] = os.path.join(os.path.expanduser('~'), "Documents", NAME)

LOGGING_LEVEL_PRIORITIES: Annotated[
    dict[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"],
        int,
    ],
    "Order of the logging levels from the lowest to the highest, high number means high priority",
] = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "EXCEPTION": 4}

SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN: Annotated[
    int,
    "Number of seconds to wait for a procedure process to tear down gracefully before killing it"
] = 30
