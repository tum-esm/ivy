# API Reference of the `src` Module

# `src`

Package of the sensor system automation software.

Import hierarchy (`a` -> `b` means that `a` cannot import from `b`):
`constants` -> `types` -> `utils` -> `procedures` -> `main`

## `src.constants`

### Variables

```python
VERSION_REGEX: str
```

Valid version name examples `1.2.3`, `4.5.6-alpha.78`, `7.8.9-beta.10`, `11.12.13-rc.14`

```python
PROJECT_DIR: str
```

The root directory of the project (the parent of `src/`)

```python
VERSION: str
```

The current version of the project

```python
NAME: str
```

The name of the project

```python
IVY_ROOT_DIR: str
```

The root directory of the project on a production system = `~/Documents/{NAME}`

```python
LOGGING_LEVEL_PRIORITIES: dict[typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION'], int]
```

Order of the logging levels from the lowest to the highest, high number means high priority

```python
SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN: int
```

Number of seconds to wait for a procedure process to tear down gracefully before killing it

## `src.main`

Main loop of the automation

### Functions

**`run`**

```python
def run() -> None:
```

Run the automation

## `src.backend`

### `src.backend.tenta_backend`

#### Functions

**`run_tenta_backend`**

```python
def run_tenta_backend(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
) -> None:
```

### `src.backend.thingsboard_backend`

#### Functions

**`run_thingsboard_backend`**

```python
def run_thingsboard_backend(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
) -> None:
```

## `src.procedures`

This modules provides all procedures that the automation software
should run. They should all be run in parallel processes and each file
provides a single funtion that runs infinitely. Functions may implement
graceful teardown steps upon receiving SIGTERM.

All of the procedures in this module should have the signature:

```python
def run(config: src.types.Config, logger: src.utils.Logger) -> None:
    ...
```

### `src.procedures.dummy_procedure`

#### Functions

**`run`**

```python
def run(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
) -> None:
```

Fetches the weather from a weather API. You can simply remove

this in your own project and use it as an exaple for your own
procedures.

### `src.procedures.system_checks`

#### Functions

**`run`**

```python
def run(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
) -> None:
```

Logs the system load and last boot time.

## `src.types`

This module contains all type definitions of the codebase and
may implement loading and dumping functionality like `Config.load`.

### `src.types.config`

#### Classes

**`Config`**

```python
class Config(pydantic.BaseModel):
```

Schema of the config file for this version of the software.

A rendered API reference can be found in the documentation at TODO.

**`dump`**

```python
def dump(
    self,
) -> None:
```

Dump the config file to the path `<ivy_root>/<version>/config/config.json`

**`load`**

```python
@staticmethod
def load() -> src.types.config.Config:
```

Load the config file from the path `project_dir/config/config.json`

**`load_from_string`**

```python
@staticmethod
def load_from_string(
    c: str,
) -> src.types.config.Config:
```

Load the object from a string

**`load_template`**

```python
@staticmethod
def load_template() -> src.types.config.Config:
```

Load the config file from the path `project_dir/config/config.template.json`

**`to_foreign_config`**

```python
def to_foreign_config(
    self,
) -> src.types.config.ForeignConfig:
```

**`ForeignConfig`**

```python
class ForeignConfig(pydantic.BaseModel):
```

Schema of a foreign config file for any other version of the software

to update to.

A rendered API reference can be found in the documentation at TODO.

**`dump`**

```python
def dump(
    self,
) -> None:
```

Dump the config file to the path `<ivy_root>/<version>/config/config.json`

**`load_from_string`**

```python
@staticmethod
def load_from_string(
    c: str,
) -> src.types.config.ForeignConfig:
```

Load the object from a string

### `src.types.messages`

#### Classes

**`ConfigMessageBody`**

```python
class ConfigMessageBody(pydantic.BaseModel):
```

**`DataMessageBody`**

```python
class DataMessageBody(pydantic.BaseModel):
```

**`LogMessageBody`**

```python
class LogMessageBody(pydantic.BaseModel):
```

**`MessageArchiveItem`**

```python
class MessageArchiveItem(pydantic.BaseModel):
```

**`MessageQueueItem`**

```python
class MessageQueueItem(MessageArchiveItem):
```

### `src.types.state`

#### Classes

**`State`**

```python
class State(pydantic.BaseModel):
```

Central state used to communicate between prodedures and with the mainloop.

**`SystemState`**

```python
class SystemState(pydantic.BaseModel):
```

State values determined in the system checks procedure.

## `src.utils`

This module contains all utility functionality of the codebase.

Some of the functions have been used from https://github.com/tum-esm/utils
but this library has not been added as a dependency to reduce the number of
third party libaries this software depends on.

### `src.utils.exponential_backoff`

#### Classes

**`ExponentialBackoff`**

```python
class ExponentialBackoff:
```

Exponential backoff e.g. when errors occur. First try again in 1 minute,

then 4 minutes, then 15 minutes, etc.. Usage:

```python
import src
exponential_backoff = src.utils.ExponentialBackoff(logger)
while True:
    try:
        # do something
        exponential_backoff.reset()
    except Exception as e:
        logger.exception(e)
        exponential_backoff.sleep()
```

**`__init__`**

```python
def __init__(
    self,
    logger: src.utils.logger.Logger,
    buckets: list[int],
) -> None:
```

Create a new exponential backoff object.

**Arguments:**

 * `logger`: The logger to use for logging when waiting certain amount of time.
 * `buckets`: The buckets to use for the exponential backoff.

**`reset`**

```python
def reset(
    self,
) -> None:
```

Reset the waiting period to the first bucket

**`sleep`**

```python
def sleep(
    self,
) -> None:
```

Wait and increase the wait time to the next bucket.

### `src.utils.functions`

#### Functions

**`get_time_to_next_datapoint`**

```python
def get_time_to_next_datapoint(
    seconds_between_datapoints: int,
) -> float:
```

Calculates the time until the next measurement should be taken. If the seconds

between datapoints is 10 and the current time is 12:00:03, the next measurement
should be taken at 12:00:10. This function starts counting at 00:00:00 system time.
Hence it returns 00:00:00, 00:00:10, 00:00:20, 00:00:30.

**Arguments:**

 * `seconds_between_datapoints`: The time between two datapoints in seconds.

**Returns:** The time until the next measurement should be taken in seconds.

**`log_level_is_visible`**

```python
def log_level_is_visible(
    min_visible_log_level: typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION', None],
    log_level: typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION'],
) -> bool:
```

Checks if a log level is forwarded to the user.

**Arguments:**

 * `min_log_level`:  The minimum log level to forward, if None, no log
levels are forwarded.
 * `log_level`:      The log level to check

**`run_shell_command`**

```python
def run_shell_command(
    command: str,
    working_directory: typing.Optional[str],
    executable: str,
) -> str:
```

runs a shell command and raises a `CommandLineException`

if the return code is not zero, returns the stdout. Uses
`/bin/bash` by default.

**`string_is_valid_version`**

```python
def string_is_valid_version(
    version_string: str,
) -> bool:
```

Check if the version string is valid = should match

`src.constants.VERSION_REGEX`

**Arguments:**

 * `version_string`: version string to check.

**Returns:** True if the version string is valid, False otherwise.

**`with_automation_lock`**

```python
@contextlib.contextmanager
def with_automation_lock() -> typing.Generator[None, None, None]:
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

#### Classes

**`CommandLineException`**

```python
class CommandLineException(Exception):
```

Raised when a shell command fails.

**`__init__`**

```python
def __init__(
    self,
    value: str,
    details: typing.Optional[str],
) -> None:
```

**`with_filelock`**

```python
class with_filelock:
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

**`__init__`**

```python
def __init__(
    self,
    lockfile_path: str,
    timeout: float,
) -> None:
```

A timeout of -1 means that the code waits forever.

### `src.utils.logger`

#### Functions

**`_pad_str_right`**

```python
def _pad_str_right(
    text: str,
    min_width: int,
    fill_char: typing.Literal['0', ' ', '-'],
) -> str:
```

#### Classes

**`Logger`**

```python
class Logger:
```

A custom logger class that optionally sends out the logs via

MQTT and writes them to a file. One can add details to log messages
of all levels which will be logged on a separate line for better
readability.

You can give each instance a custom origin to distinguish between
the sources of the log messages.

A simple log message will look like this:

```
2021-08-22 16:00:00.000 UTC+2 - origin - INFO - test message
```

A log message with details will look like this:

```
2021-08-22 16:00:00.000 UTC+2 - origin - INFO - test message
--- details ----------------------------
test details
----------------------------------------
```

An exception will be formatted like this:

```
2021-08-22 16:00:00.000 UTC+2 - origin - EXCEPTION - ZeroDivisionError: division by zero
--- exception details ------------------
test details
--- traceback --------------------------
Traceback (most recent call last):
    File "src/utils/logger.py", line 123, in _write_log_line
        raise Exception("test exception")
Exception: test exception
----------------------------------------
```

**`__init__`**

```python
def __init__(
    self,
    config: src.types.config.Config,
    origin: str,
) -> None:
```

Initializes the logger.

**Arguments:**

 * `config`:  The config object
 * `origin`:  The origin of the log messages, will be displayed
in the log lines.

**`_write_log_line`**

```python
def _write_log_line(
    self,
    level: typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION'],
    subject: str,
    details: list[tuple[str, typing.Optional[str]]],
) -> None:
```

formats the log line string and writes it to

`logs/current-logs.log`

**`debug`**

```python
def debug(
    self,
    message: str,
    details: typing.Optional[str],
) -> None:
```

Writes a INFO log line.

**Arguments:**

 * `message`:  The message to log
 * `details`:  Additional details to log, useful for verbose output.

**`error`**

```python
def error(
    self,
    message: str,
    details: typing.Optional[str],
) -> None:
```

Writes an error log line.

**Arguments:**

 * `message`:  The message to log
 * `details`:  Additional details to log, useful for verbose output.

**`exception`**

```python
def exception(
    self,
    e: Exception,
    label: typing.Optional[str],
    details: typing.Optional[str],
) -> None:
```

logs the traceback of an exception, sends the message via

MQTT when config is passed (required for revision number).

The subject will be formatted like this:
`(label, )ZeroDivisionError: division by zero`

**Arguments:**

 * `e`:      The exception to log
 * `label`:  A label to prepend to the exception name.

**`horizontal_line`**

```python
def horizontal_line(
    self,
    fill_char: typing.Literal['-', '=', '.', '_'],
) -> None:
```

Writes a horizontal line.

**`info`**

```python
def info(
    self,
    message: str,
    details: typing.Optional[str],
) -> None:
```

Writes a INFO log line.

**Arguments:**

 * `message`:  The message to log
 * `details`:  Additional details to log, useful for verbose output.

**`warning`**

```python
def warning(
    self,
    message: str,
    details: typing.Optional[str],
) -> None:
```

Writes a WARNING log line.

**Arguments:**

 * `message`:  The message to log
 * `details`:  Additional details to log, useful for verbose output.

### `src.utils.messaging_agent`

#### Classes

**`MessagingAgent`**

```python
class MessagingAgent():
```

**`__init__`**

```python
def __init__(
    self,
) -> None:
```

**`add_message`**

```python
def add_message(
    self,
    message_body: typing.Union[src.types.messages.DataMessageBody, src.types.messages.LogMessageBody, src.types.messages.ConfigMessageBody],
) -> None:
```

**`get_message_archive_file`**

```python
@staticmethod
def get_message_archive_file() -> str:
```

**`get_n_latest_messages`**

```python
def get_n_latest_messages(
    self,
    n: int,
    excluded_message_ids: set[int] | list[int],
) -> list[src.types.messages.MessageQueueItem]:
```

**`load_message_archive`**

```python
@staticmethod
def load_message_archive(
    date: datetime.date,
) -> list[src.types.messages.MessageArchiveItem]:
```

**`remove_messages`**

```python
def remove_messages(
    self,
    message_ids: set[int] | list[int],
) -> None:
```

**`teardown`**

```python
def teardown(
    self,
) -> None:
```

### `src.utils.procedure_manager`

#### Classes

**`ProcedureManager`**

```python
class ProcedureManager():
```

**`__init__`**

```python
def __init__(
    self,
    config: src.types.config.Config,
    procedure_entrypoint: typing.Callable[[src.types.config.Config, src.utils.logger.Logger], None],
    procedure_name: str,
) -> None:
```

**`check_procedure_status`**

```python
def check_procedure_status(
    self,
) -> None:
```

**`procedure_is_running`**

```python
def procedure_is_running(
    self,
) -> bool:
```

**`start_procedure`**

```python
def start_procedure(
    self,
) -> None:
```

**`teardown`**

```python
def teardown(
    self,
) -> None:
```

### `src.utils.state_interface`

#### Variables

```python
STATE_FILE: str
```

Points to `data/state.json` where the state is communicated with all threads

```python
STATE_FILE_LOCK: str
```

Points to `data/state.lock` which is used to ensure that only one thread can access the state at a time.

#### Classes

**`StateInterface`**

```python
class StateInterface():
```

**`load`**

```python
@with_filelock(STATE_FILE_LOCK, timeout=6)
@staticmethod
def load() -> src.types.state.State:
```

Load the state file from the path `project_dir/data/state.json`

**`update`**

```python
@with_filelock(STATE_FILE_LOCK, timeout=6)
@staticmethod
@contextlib.contextmanager
def update() -> typing.Generator[src.types.state.State, None, None]:
```

Load the state file and update it within a semaphore. Usage:

```python
with State.update() as state:
    state.system.last_boot_time = datetime.datetime.now()
```

### `src.utils.updater`

#### Classes

**`Updater`**

```python
class Updater:
```

Implementation of the update capabilities of the ivy seed: checks

whether a new config is in a valid format, downloads new source code,
creates virtual environments, installs dependencies, runs pytests,
removes old virtual environments, and updates the cli pointer to the
currently used version of the automation software.

**`__init__`**

```python
def __init__(
    self,
    config: src.types.config.Config,
) -> None:
```

Initialize an Updater instance.

**Arguments:**

 * `config`: The current config.

**`download_source_code`**

```python
def download_source_code(
    self,
    version: str,
) -> None:
```

Download the source code of the new version to the version

directory. This is currently only implemented for github and
gitlab for private and public repositories. Feel free to request
other providers in the issue tracker.

**`install_dependencies`**

```python
def install_dependencies(
    self,
    version: str,
) -> None:
```

Create a virtual environment and install the dependencies in

the version directory using poetry.

**`perform_update`**

```python
def perform_update(
    self,
    foreign_config: src.types.config.ForeignConfig,
) -> None:
```

Perform an update for a received config file.

1. Check whether this config revision has already been processed.
2. If version is equal to the current version:
    * Parse the received config file string using
        `types.Config.load_from_string`
    * If the received config is equal to the current
        config, do nothing
    * Otherwise, dump the received config to the config
        file path and exit with status code 0
3. Otherwise:
    * Download the source code of the new version
    * Create a virtual environment
    * Install dependencies
    * Dump the received config to the config file path
    * Run the integration pytests
    * Update the cli pointer
    * Exit with status code 0

If any of the steps above fails, log the error and return. The
automation will continue with the current config. If the pytests
of the software version to be updated make sure, that the software
runs correctly, it is not possible to update to a new version, that
does not work.

**Arguments:**

 * `config_file_string`: The content of the config file to be processed.
This is a string, which will be parsed using
`types.ForeignConfig.load_from_string`. It should
be a JSON object with at least the `version` field,
everything else is optional.

**`remove_old_venvs`**

```python
def remove_old_venvs(
    self,
) -> None:
```

Remove all old virtual environments, that are not currently in use.

**`run_pytests`**

```python
def run_pytests(
    self,
    version: str,
) -> None:
```

Run all pytests with the mark "version_change" in the version directory.

**`update_cli_pointer`**

```python
def update_cli_pointer(
    self,
    version: str,
) -> None:
```

Update the cli pointer to a new version

