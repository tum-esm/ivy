from typing import Any, Generator, Literal, Optional
import datetime
import contextlib
import os
import filelock
import pydantic
import tum_esm_utils
import src


def log_level_is_visible(
    min_log_level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]],
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"],
) -> bool:
    """Checks if a log level is forwarded to the user.

    Args:
        min_log_level: The minimum log level to forward, if None, no log
                       levels are forwarded.
        log_level:     The log level to check.

    Returns:
        Whether `log_level` is at least as important as `min_log_level`
    """

    if min_log_level is None:
        return False
    else:
        return (
            src.constants.LOGGING_LEVEL_PRIORITIES[log_level]
            >= src.constants.LOGGING_LEVEL_PRIORITIES[min_log_level]
        )


@contextlib.contextmanager
def with_automation_lock() -> Generator[None, None, None]:
    """This function will lock the automation with a file lock so that
    only one instance can run at a time.

    Usage:

    ```python
    with with_automation_lock():
        run_automation()
        # or
        run_tests()
    ```

    Returns:
        A context manager that locks the automation.

    Raises:
        TimeoutError: If the automation is already running.
    """

    parent_dir = os.path.dirname(src.constants.PROJECT_DIR)
    lock_path: str

    # if the current project dir (parent of cli.py) is a valid version name, then the lock file
    # is put into the parent directory, otherwise it is put into the project directory
    try:
        tum_esm_utils.validators.Version(os.path.basename(src.constants.PROJECT_DIR))
        lock_path = os.path.join(parent_dir, "run.lock")
    except pydantic.ValidationError:
        lock_path = os.path.join(src.constants.PROJECT_DIR, "run.lock")

    automation_lock = filelock.FileLock(lock_path, timeout=0)

    try:
        with automation_lock:
            yield
    except filelock.Timeout:
        print(f'locked by another process via file at path "{lock_path}"')
        raise TimeoutError("automation is already running")


def get_time_to_next_datapoint(seconds_between_datapoints: int) -> float:
    """Calculates the time until the next measurement should be taken. If the seconds
    between datapoints is 10 and the current time is 12:00:03, the next measurement
    should be taken at 12:00:10. This function starts counting at 00:00:00 system time.
    Hence it returns 00:00:00, 00:00:10, 00:00:20, 00:00:30.

    Args:
        seconds_between_datapoints: The time between two datapoints in seconds.

    Returns:
        The time until the next measurement should be taken in seconds."""

    now = datetime.datetime.now()
    current_seconds_in_day = (
        now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1_000_000
    )

    return seconds_between_datapoints - (current_seconds_in_day % seconds_between_datapoints)
