from typing import Any, Callable, Generator, Literal, Optional, TypeVar, cast
import datetime
import functools
import contextlib
import os
import re
import subprocess
import filelock
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


def string_is_valid_version(version_string: str) -> bool:
    """Check if the version string is valid = should match
    `src.constants.VERSION_REGEX`
    
    Args:
        version_string: version string to check.
    
    Returns:
        Whether the version string is valid.
    """

    return re.match(src.constants.VERSION_REGEX, version_string) is not None


def run_shell_command(
    command: str,
    working_directory: Optional[str] = None,
    executable: str = "/bin/bash",
) -> str:
    """Runs a shell command and raises a `CommandLineException`
    if the return code is not zero, returns the stdout. Uses
    `/bin/bash` by default.
    
    Args:
        command:           The command to run.
        working_directory: The working directory for the command.
        executable:        The shell to use.
    
    Returns:
        The stdout of the command.
    
    Raises:
        CommandLineException: If the command fails.
    """

    p = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_directory,
        env=os.environ.copy(),
        executable=executable,
    )
    stdout = p.stdout.decode("utf-8", errors="replace").strip()
    stderr = p.stderr.decode("utf-8", errors="replace").strip()

    if p.returncode != 0:
        raise CommandLineException(
            f"command '{command}' failed with exit code {p.returncode}",
            details=f"\nstderr:\n{stderr}\nstout:\n{stdout}",
        )

    return stdout


class CommandLineException(Exception):
    """Raised when a shell command fails.
    
    Provides more details than a normal exception:

    ```python   
    e = CommandLineException("command failed", details="stderr: ...")
    print(e) # command failed
    print(e.details) # stderr: ...
    ```
    """
    def __init__(self, value: str, details: Optional[str] = None) -> None:
        """Initializes the exception.

        Args:
            value:   The message to log.
            details: Additional details to log, useful for verbose output.
        """

        self.value = value
        self.details = details
        Exception.__init__(self)

    def __str__(self) -> str:
        return repr(self.value)


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

    lock_path = os.path.join(
        parent_dir if src.utils.functions.string_is_valid_version(
            os.path.basename(src.constants.PROJECT_DIR)
        ) else src.constants.PROJECT_DIR, "run.lock"
    )
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
    current_seconds_in_day = now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1_000_000

    return seconds_between_datapoints - (
        current_seconds_in_day % seconds_between_datapoints
    )


# typing of higher level decorators:
# https://github.com/python/mypy/issues/1551#issuecomment-253978622
F = TypeVar("F", bound=Callable[..., Any])


class with_filelock:
    """FileLock = Mark, that a file is being used and other programs
    should not interfere. A file "*.lock" will be created and the
    content of this file will make the wrapped function possibly
    wait until other programs are done using it.

    See https://en.wikipedia.org/wiki/Semaphore_(programming). Usage:

    ```python
    @with_filelock(lockfile_path="path/to/lockfile.lock", timeout=10)
    def some_function():
        pass
        
    some_function() # will be executed within a semaphore 
    ```"""
    def __init__(self, lockfile_path: str, timeout: float = -1) -> None:
        """A timeout of -1 means that the code waits forever.
        
        Args:
            lockfile_path: The path to the lockfile.
            timeout:       The time to wait for the lock in seconds.
        
        """

        self.lockfile_path: str = lockfile_path
        self.timeout: float = timeout

    def __call__(self, f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            with filelock.FileLock(self.lockfile_path, timeout=self.timeout):
                return f(*args, **kwargs)

        return cast(F, wrapper)
