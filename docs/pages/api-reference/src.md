# `run.py` [#run]

Entrypoint of the automation

1. Load environment variables from `../.env` and `config/.env` (the latter has priority)
2. Lock the automation with a file lock so that only one instance can run at a time
3. Run the automation if the lock could be acquired




<br/>

# `src` [#src]

Package of the sensor system automation software.

Import hierarchy (`a` -> `b` means that `a` cannot import from `b`):
`constants` -> `types` -> `utils` -> `procedures` -> `main`

## `src.constants.py` [#src.constants]

### Variables [#src.constants.variables]

```python
PROJECT_DIR: str
```

The root directory of the project (the parent of `src/`)

```python
VERSION: tum_esm_utils.validators.Version
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

## `src.main.py` [#src.main]

### Functions [#src.main.functions]

**`run`**

```python
def run() -> None:
```

Run the automation.

1. Load the configuration
2. Initialize the logger
3. Initialize the messaging agent
4. Initialize the updater
5. Remove old virtual environments
6. Initialize the lifecycle managers
7. Establish graceful shutdown logic (run teardown for every lifecycle manager)
8. Start the main loop

Inside the mainloop the following steps are performed until termination:

1. Start each procedure/backend if it is not running
2. Check the status of each procedure/backend
3. Perform any pending updates

If an exception is raised in the main loop, it is logged and the main loop
sleeps for an exponentially increasing amount of time before it tries to
continue.

## `src.backend` [#src.backend]

This module provides all backends that the automation software can communicate
with. Every submodule should provide a single function that runs infinitely.

All of the procedures in this module should have the signature:

```python
def run(
    config: src.types.Config,
    logger: src.utils.Logger,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
    ...
```

These are managed by a `src.utils.ProcessManager`, but opposed to "procedures", they
do not receive a SIGTERM signal, but the `teardown_indicator` event is set. This
gives more freedom on how to handle the shutdown of the backend.

### `src.backend.tenta_backend.py` [#src.backend.tenta_backend]

#### Functions [#src.backend.tenta_backend.functions]

**`run`**

```python
def run(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
```

The main procedure for the Tenta backend.

**Arguments:**

 * `config`: The configuration object.
 * `logger`: The logger object.
 * `teardown_indicator`: The event that is set when the procedure should terminate.

### `src.backend.thingsboard_backend.py` [#src.backend.thingsboard_backend]

#### Functions [#src.backend.thingsboard_backend.functions]

**`run`**

```python
def run(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
```

The main procedure for the ThingsBoard backend.

**Arguments:**

 * `config`: The configuration object.
 * `logger`: The logger object.
 * `teardown_indicator`: The event that is set when the procedure should terminate.

## `src.procedures` [#src.procedures]

This modules provides all procedures that the automation software
should run. They should all be run in parallel processes and each file
provides a single funtion that runs infinitely. Functions may implement
graceful teardown steps upon receiving SIGTERM/SIGINT.

All of the procedures in this module should have the signature:

```python
def run(
    config: src.types.Config,
    logger: src.utils.Logger,
) -> None:
    ...
```

### `src.procedures.dummy_procedure.py` [#src.procedures.dummy_procedure]

#### Functions [#src.procedures.dummy_procedure.functions]

**`run`**

```python
def run(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
) -> None:
```

Performs a random walk and sends out the current position.

You can use this as an example for your own procedures and
remove this in your own project

**Arguments:**

 * `config`: The configuration object.
 * `logger`: The logger object.

### `src.procedures.system_checks.py` [#src.procedures.system_checks]

#### Functions [#src.procedures.system_checks.functions]

**`run`**

```python
def run(
    config: src.types.config.Config,
    logger: src.utils.logger.Logger,
) -> None:
```

Logs the system load and last boot time.

**Arguments:**

 * `config`: The configuration object.
 * `logger`: The logger object.

## `src.types` [#src.types]

This module contains all type definitions of the codebase and
may implement loading and dumping functionality like `Config.load`.

### `src.types.config.py` [#src.types.config]

#### Class `Config` [#src.types.config.Config.classes]

```python
class Config(pydantic.BaseModel):
```

Schema of the config file for this version of the software.

A rendered API reference can be found in the documentation.

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

Load the object from a string.

**Arguments:**

 * `c`: The string to load the object from.

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

Convert the config to a `src.types.ForeignConfig` object.

#### Class `ForeignConfig` [#src.types.config.ForeignConfig.classes]

```python
class ForeignConfig(pydantic.BaseModel):
```

Schema of a foreign config file for any other version of the software

to update to. It probably has more fields than listed in the schema. This
schema only includes the fields that are required in any new config to be
accepted by the updater in this version of the software.

A rendered API reference can be found in the documentation.

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

Load the object from a string.

**Arguments:**

 * `c`: The string to load the object from.

#### Class `ForeignGeneralConfig` [#src.types.config.ForeignGeneralConfig.classes]

```python
class ForeignGeneralConfig(pydantic.BaseModel):
```

#### Class `MQTTBrokerConfig` [#src.types.config.MQTTBrokerConfig.classes]

```python
class MQTTBrokerConfig(pydantic.BaseModel):
```

### `src.types.messages.py` [#src.types.messages]

#### Class `ConfigMessageBody` [#src.types.messages.ConfigMessageBody.classes]

```python
class ConfigMessageBody(pydantic.BaseModel):
```

The body of a config message, defined by `body.variant == "config"`.

#### Class `DataMessageBody` [#src.types.messages.DataMessageBody.classes]

```python
class DataMessageBody(pydantic.BaseModel):
```

The body of a data message, defined by `body.variant == "data"`.

#### Class `LogMessageBody` [#src.types.messages.LogMessageBody.classes]

```python
class LogMessageBody(pydantic.BaseModel):
```

The body of a log message, defined by `body.variant == "log"`.

#### Class `MessageArchiveItem` [#src.types.messages.MessageArchiveItem.classes]

```python
class MessageArchiveItem(pydantic.BaseModel):
```

#### Class `MessageQueueItem` [#src.types.messages.MessageQueueItem.classes]

```python
class MessageQueueItem(MessageArchiveItem):
```

### `src.types.state.py` [#src.types.state]

#### Class `State` [#src.types.state.State.classes]

```python
class State(pydantic.BaseModel):
```

Central state used to communicate between prodedures and with the mainloop.

#### Class `SystemState` [#src.types.state.SystemState.classes]

```python
class SystemState(pydantic.BaseModel):
```

State values determined in the system checks procedure.

## `src.utils` [#src.utils]

This module contains all utility functionality of the codebase.

Some of the functions have been used from https://github.com/tum-esm/utils
but this library has not been added as a dependency to reduce the number of
third party libaries this software depends on.

### `src.utils.functions.py` [#src.utils.functions]

#### Functions [#src.utils.functions.functions]

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
    min_log_level: typing.Optional[typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION']],
    log_level: typing.Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'EXCEPTION'],
) -> bool:
```

Checks if a log level is forwarded to the user.

**Arguments:**

 * `min_log_level`: The minimum log level to forward, if None, no log
levels are forwarded.
 * `log_level`:     The log level to check.

**Returns:** Whether `log_level` is at least as important as `min_log_level`

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

**Returns:** A context manager that locks the automation.

**Raises:**

 * `TimeoutError`: If the automation is already running.

### `src.utils.lifecycle_manager.py` [#src.utils.lifecycle_manager]

#### Class `LifecycleManager` [#src.utils.lifecycle_manager.LifecycleManager.classes]

```python
class LifecycleManager():
```

Manages the lifecycle of a procedure or a backend process.

Both procedures and backends run an infinite loop to perform their
respective tasks. The procedure manager is responsible for starting,
stopping and checking the status of the procedure.

Each procedure/backend is wrapped in one instance of the lifecycle
manager.

**`__init__`**

```python
def __init__(
    self,
    config: src.types.config.Config,
    entrypoint: typing.Union[typing.Callable[[src.types.config.Config, src.utils.logger.Logger], None], typing.Callable[[src.types.config.Config, src.utils.logger.Logger, multiprocessing.synchronize.Event], None]],
    procedure_name: str,
    variant: typing.Literal['procedure', 'backend'],
) -> None:
```

Initializes a new procedure manager.

**Arguments:**

 * `config`:         The configuration object.
 * `entrypoint`:     The entrypoint of the procedure or backend.
 * `procedure_name`: The name of the procedure or backend. Used to name
the spawned process.
 * `variant`:        Whether the entrypoint is a procedure or a backend.
The difference is only in the teardown logic.

**Raises:**

 * `ValueError`: If the given variant does not match the entrypoint
signature.

**`check_procedure_status`**

```python
def check_procedure_status(
    self,
) -> None:
```

Checks if the procedure is still running. Logs an error if

the procedure has died unexpectedly.

**Raises:**

 * `RuntimeError`: If the procedure has not been started yet. This
is a wrong usage of the procedure manager.

**`procedure_is_running`**

```python
def procedure_is_running(
    self,
) -> bool:
```

Returns True if the procedure has been started. Does not check

whether the process is still alive.

**`start_procedure`**

```python
def start_procedure(
    self,
) -> None:
```

Starts the procedure in a separate process.

**Raises:**

 * `RuntimeError`: If the procedure is already running. This is a
wrong usage of the procedure manager.

**`teardown`**

```python
def teardown(
    self,
) -> None:
```

Tears down the procedures.

For procedures, it sends a SIGTERM to the process. For backends, it
sets a multiprocessing.Event to signal the backend to shut down. This
gives the backend processes more freedom to manage a shutdown.

The lifecycle manager waits for the process to shut down gracefully
for a certain amount of time. If the process does not shut down in
time, it kills the process forcefully by sending a SIGKILL.

For procedures, the SIGKILL is sent after
`src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN` seconds. For
backends, the SIGKILL is sent after `config.backend.max_drain_time + 120`
seconds.

### `src.utils.logger.py` [#src.utils.logger]

#### Class `Logger` [#src.utils.logger.Logger.classes]

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

Initializes a new Logger instance.

**Arguments:**

 * `config`:  The config object.
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

Formats the log line string and writes it out to the selected

output channels.

The output channels are configured using `config.logging_verbosity`.
You can set the level of detail you want to see in the console, the
file archive and the MQTT message stream.

**Arguments:**

 * `level`:    The log level of the message.
 * `subject`:  The subject of the message.
 * `details`:  Additional details to log, useful for verbose output.

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

 * `message`:  The message to log.
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

 * `message`:  The message to log.
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

 * `e`:       The exception to log.
 * `label`:   A label to prepend to the exception name.
 * `details`: Additional details to log, useful for verbose output
like full log of a failed pytest on a new config.

**`horizontal_line`**

```python
def horizontal_line(
    self,
    fill_char: typing.Literal['-', '=', '.', '_'],
) -> None:
```

Writes a horizontal line.

**Arguments:**

 * `fill_char`:  The character to fill the line with.

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

 * `message`:  The message to log.
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

 * `message`:  The message to log.
 * `details`:  Additional details to log, useful for verbose output.

### `src.utils.mainloop_toggle.py` [#src.utils.mainloop_toggle]

Functions to start and terminate background processes.

#### Variables [#src.utils.mainloop_toggle.variables]

```python
SCRIPT_PATH: str
```

Absolute path of the `run.py` file that starts an infinite mainloop

#### Class `MainloopToggle` [#src.utils.mainloop_toggle.MainloopToggle.classes]

```python
class MainloopToggle:
```

Used to start and stop the mainloop process in the background.

All functionality borrowed from the [`tum-esm-utils` package](https://github.com/tum-esm/utils)

**`get_mainloop_pids`**

```python
@staticmethod
def get_mainloop_pids() -> list[int]:
```

Get the process ID(s) of the mainloop process(es).

Should be used to check if the mainloop process is running.

**Returns:** A list of process IDs. Might have more than one element if
the mainloop process has spawned child process(es).

**`start_mainloop`**

```python
@staticmethod
def start_mainloop() -> None:
```

Start the mainloop process in the background and print

the process ID(s) of the new process(es).

**`stop_mainloop`**

```python
@staticmethod
def stop_mainloop() -> None:
```

Terminate the mainloop process in the background and print

the process ID(s) of the terminated process(es).

### `src.utils.messaging_agent.py` [#src.utils.messaging_agent]

#### Variables [#src.utils.messaging_agent.variables]

```python
ACTIVE_QUEUE_FILE: str
```

The absolute path of the SQLite database that stores the active message queue (`data/active-message-queue.sqlite3`)

```python
MESSAGE_ARCHIVE_DIR: str
```

The absolute path of the directory that stores the message archive (`data/messages/`)

```python
MESSAGE_ARCHIVE_DIR_LOCK: str
```

The absolute path of the lock file that is used to lock the message archive directory (`data/messages.lock`). This is used to make sure that only one process can write to the message archive at a time.

#### Class `MessagingAgent` [#src.utils.messaging_agent.MessagingAgent.classes]

```python
class MessagingAgent():
```

**`__init__`**

```python
def __init__(
    self,
) -> None:
```

Create a new messaging agent.

Sets up a connection to the SQLite database that stores the active
message queue. Creates the SQL tables if they don't exist yet.

**`add_message`**

```python
def add_message(
    self,
    message_body: typing.Union[src.types.messages.DataMessageBody, src.types.messages.LogMessageBody, src.types.messages.ConfigMessageBody],
) -> None:
```

Add a message to the active message queue and the message archive.

Messages are written to the archive right away so they don't get lost
if the backend process fails to send them out.

**Arguments:**

 * `message_body`: The message body.

**`get_message_archive_file`**

```python
@staticmethod
def get_message_archive_file() -> str:
```

Get the file path of the message archive file for the current date.

**`get_n_latest_messages`**

```python
def get_n_latest_messages(
    self,
    n: int,
    excluded_message_ids: set[int] | list[int],
) -> list[src.types.messages.MessageQueueItem]:
```

Get the `n` latest messages from the active message queue.

**Arguments:**

 * `n`:                    The number of messages to get.
 * `excluded_message_ids`: The message IDs to exclude from the result. Can be
used to exclude messages that are already being processed
but are still in the active message queue.

**Returns:** A list of messages from the active queue.

**`load_message_archive`**

```python
@staticmethod
def load_message_archive(
    date: datetime.date,
) -> list[src.types.messages.MessageArchiveItem]:
```

Load the message archive for a specific date.

**Arguments:**

 * `date`: The date for which to load the message archive.

**Returns:** A list of messages from the message archive.

**`remove_messages`**

```python
def remove_messages(
    self,
    message_ids: set[int] | list[int],
) -> None:
```

Remove messages from the active message queue.

**Arguments:**

 * `message_ids`: The message IDs to be removed.

**`teardown`**

```python
def teardown(
    self,
) -> None:
```

Close the connection to the active message queue database.

### `src.utils.state_interface.py` [#src.utils.state_interface]

#### Variables [#src.utils.state_interface.variables]

```python
STATE_FILE: str
```

Points to `data/state.json` where the state is communicated with all threads

```python
STATE_FILE_LOCK: str
```

Points to `data/state.lock` which is used to ensure that only one thread can access the state at a time.

#### Class `StateInterface` [#src.utils.state_interface.StateInterface.classes]

```python
class StateInterface():
```

**`load`**

```python
@tum_esm_utils.decorators.with_filelock(STATE_FILE_LOCK, timeout=6)
@staticmethod
def load() -> src.types.state.State:
```

Load the state file from the path `project_dir/data/state.json`

**`update`**

```python
@tum_esm_utils.decorators.with_filelock(STATE_FILE_LOCK, timeout=6)
@staticmethod
@contextlib.contextmanager
def update() -> typing.Generator[src.types.state.State, None, None]:
```

Load the state file and update it within a semaphore.

This makes sure that only one process can access this section at a time.
If you would do 1. load, 2. modify, 3. save in separate calls, you might
overwrite the changes by another process.

Usage:

```python
with State.update() as state:
    state.system.last_boot_time = datetime.datetime.now()
```

**Returns:** A generator that yields the state object.

### `src.utils.updater.py` [#src.utils.updater]

#### Class `Updater` [#src.utils.updater.Updater.classes]

```python
class Updater:
```

Implementation of the update capabilities of ivy: checks whether

a new config is in a valid format, downloads new source code, creates
virtual environments, installs dependencies, runs pytests, removes
old virtual environments, and updates the cli pointer to the currently
used version of the automation software.

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
    version: tum_esm_utils.validators.Version,
) -> None:
```

Download the source code of the new version to the version

directory. This is currently only implemented for github and
gitlab for private and public repositories. Feel free to request
other providers in the issue tracker.

**Arguments:**

 * `version`: The version of the source code to download.

**`install_dependencies`**

```python
def install_dependencies(
    self,
    version: tum_esm_utils.validators.Version,
) -> None:
```

Create a virtual environment and install the dependencies in the

version directory using PDM. It uses the `pdm sync` command to exactly
create the desired environmont.

Since the `pyproject.toml` file generated by PDM is complying with PEP
standards, one could also use `pip install .`. However, we recommend
using PDM for due to caching and dependency locking.

**Arguments:**

 * `version`: The version of the source code to download.

**`perform_update`**

```python
def perform_update(
    self,
    foreign_config: src.types.config.ForeignConfig,
) -> None:
```

Perform an update for a received config file.

See the [documentation](/core-concepts/over-the-air-updates) for a detailed
explanation of the update process.

**Arguments:**

 * `foreign_config`: The received config.

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
    version: tum_esm_utils.validators.Version,
) -> None:
```

Run all pytests with the mark "version_change" in the version directory.

**Arguments:**

 * `version`: The version of the source code to download.

**`update_cli_pointer`**

```python
def update_cli_pointer(
    self,
    version: tum_esm_utils.validators.Version,
) -> None:
```

Update the cli pointer to a new version.

**Arguments:**

 * `version`: The version of the source code to download.

