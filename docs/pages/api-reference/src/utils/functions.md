---
title: functions.py
---

# `src.utils.functions`


#### log\_level\_is\_visible

```python
def log_level_is_visible(
    min_visible_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR",
                                   "EXCEPTION", None],
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR",
                       "EXCEPTION"]) -> bool
```

Checks if a log level is forwarded to the user.

**Arguments**:

- `min_log_level` - The minimum log level to forward, if None, no log
  levels are forwarded.
- `log_level` - The log level to check
  
- `Returns` - True if `log_level` is at least as important as `min_log_level`


#### string\_is\_valid\_version

```python
def string_is_valid_version(version_string: str) -> bool
```

Check if the version string is valid = should match
`src.constants.VERSION_REGEX`

**Arguments**:

- `version_string` - version string to check.
  

**Returns**:

  True if the version string is valid, False otherwise.


#### run\_shell\_command

```python
def run_shell_command(command: str,
                      working_directory: Optional[str] = None,
                      executable: str = "/bin/bash") -> str
```

runs a shell command and raises a `CommandLineException`
if the return code is not zero, returns the stdout. Uses
`/bin/bash` by default.


## CommandLineException Objects

```python
class CommandLineException(Exception)
```

Raised when a shell command fails.


#### with\_automation\_lock

```python
@contextlib.contextmanager
def with_automation_lock() -> Generator[None, None, None]
```

This function will lock the automation with a file lock so that
only one instance can run at a time.

Usage:

```python
with with_automation_lock():
    run_automation()
    # or
    run_tests()
```


#### get\_time\_to\_next\_datapoint

```python
def get_time_to_next_datapoint(seconds_between_datapoints: int) -> float
```

Calculates the time until the next measurement should be taken. If the seconds
between datapoints is 10 and the current time is 12:00:03, the next measurement
should be taken at 12:00:10. This function starts counting at 00:00:00 system time.
Hence it returns 00:00:00, 00:00:10, 00:00:20, 00:00:30.

**Arguments**:

- `seconds_between_datapoints` - The time between two datapoints in seconds.
  

**Returns**:

  The time until the next measurement should be taken in seconds.


## with\_filelock Objects

```python
class with_filelock()
```

FileLock = Mark, that a file is being used and other programs
should not interfere. A file "*.lock" will be created and the
content of this file will make the wrapped function possibly
wait until other programs are done using it.

See https://en.wikipedia.org/wiki/Semaphore_(programming). Usage:

```python
@with_filelock(lockfile_path="path/to/lockfile.lock", timeout=10)
def some_function():
    pass

some_function() # will be executed within a semaphore 
```


#### \_\_init\_\_

```python
def __init__(lockfile_path: str, timeout: float = -1) -> None
```

A timeout of -1 means that the code waits forever.