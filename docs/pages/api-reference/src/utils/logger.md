---
title: logger.py
---

# `src.utils.logger`


## Logger Objects

```python
class Logger()
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


#### \_\_init\_\_

```python
def __init__(config: src.types.Config,
             origin: str = "insert-name-here") -> None
```

Initializes the logger.

**Arguments**:

- `config` - The config object
- `origin` - The origin of the log messages, will be displayed
  in the log lines.


#### horizontal\_line

```python
def horizontal_line(fill_char: Literal["-", "=", ".", "_"] = "=") -> None
```

Writes a horizontal line.


#### debug

```python
def debug(message: str, details: Optional[str] = None) -> None
```

Writes a INFO log line.

**Arguments**:

- `message` - The message to log
- `details` - Additional details to log, useful for verbose output.


#### info

```python
def info(message: str, details: Optional[str] = None) -> None
```

Writes a INFO log line.

**Arguments**:

- `message` - The message to log
- `details` - Additional details to log, useful for verbose output.


#### warning

```python
def warning(message: str, details: Optional[str] = None) -> None
```

Writes a WARNING log line.

**Arguments**:

- `message` - The message to log
- `details` - Additional details to log, useful for verbose output.


#### error

```python
def error(message: str, details: Optional[str] = None) -> None
```

Writes an error log line.

**Arguments**:

- `message` - The message to log
- `details` - Additional details to log, useful for verbose output.


#### exception

```python
def exception(e: Exception,
              label: Optional[str] = None,
              details: Optional[str] = None) -> None
```

logs the traceback of an exception, sends the message via
MQTT when config is passed (required for revision number).

The subject will be formatted like this:
`(label, )ZeroDivisionError: division by zero`

**Arguments**:

- `e` - The exception to log
- `label` - A label to prepend to the exception name.