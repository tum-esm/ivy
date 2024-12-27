from __future__ import annotations
import contextlib
from typing import Annotated, Generator
import os
import pydantic
import src
import tum_esm_utils

STATE_FILE: Annotated[
    str, "Points to `data/state.json` where the state is communicated with all threads"
] = os.path.join(
    src.constants.PROJECT_DIR,
    "data",
    "state.json",
)

STATE_FILE_LOCK: Annotated[
    str,
    "Points to `data/state.lock` which is used to ensure that only one thread can access the state at a time.",
] = os.path.join(
    src.constants.PROJECT_DIR,
    "data",
    "state.lock",
)


class StateInterface:
    @tum_esm_utils.decorators.with_filelock(STATE_FILE_LOCK, timeout=6)
    @staticmethod
    def load() -> src.types.State:
        """Load the state file from the path `project_dir/data/state.json`"""

        try:
            with open(STATE_FILE, "r") as f:
                return src.types.State.model_validate_json(f.read())
        except (FileNotFoundError, pydantic.ValidationError):
            return src.types.State()

    @tum_esm_utils.decorators.with_filelock(STATE_FILE_LOCK, timeout=6)
    @staticmethod
    @contextlib.contextmanager
    def update() -> Generator[src.types.State, None, None]:
        """Load the state file and update it within a semaphore.

        This makes sure that only one process can access this section at a time.
        If you would do 1. load, 2. modify, 3. save in separate calls, you might
        overwrite the changes by another process.

        Usage:

        ```python
        with State.update() as state:
            state.system.last_boot_time = datetime.datetime.now()
        ```

        Returns:
            A generator that yields the state object.
        """

        state: src.types.State

        try:
            with open(STATE_FILE, "r") as f:
                state = src.types.State.model_validate_json(f.read())
        except (FileNotFoundError, pydantic.ValidationError):
            state = src.types.State()

        yield state

        with open(STATE_FILE, "w") as f:
            f.write(state.model_dump_json(indent=4))
