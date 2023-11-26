---
title: config.py
---

# `src.types.config`

## LoggingVerbosityConfig Objects

```python
class LoggingVerbosityConfig(pydantic.BaseModel)
```

How verbose to log to the different data streams.

For example, If the level is set to "WARNING", only warnings, errors
and exceptions will be written to the respective data stream. If the
level is set to "DEBUG", all logs will be written to the respective
data stream.

Importance: DEBUG > INFO > WARNING > ERROR > EXCEPTION

If the level is set to None, no logs will be written to the respective
data stream.


## Config Objects

```python
class Config(pydantic.BaseModel)
```

Schema of the config file for this version of the software.

A rendered API reference can be found in the documentation at TODO.


#### load

```python
@staticmethod
def load() -> Config
```

Load the config file from the path `project_dir/config/config.json`


#### load\_template

```python
@staticmethod
def load_template() -> Config
```

Load the config file from the path `project_dir/config/config.template.json`


#### dump

```python
def dump() -> None
```

Dump the config file to the path `<ivy_root>/<version>/config/config.json`


#### load\_from\_string

```python
@staticmethod
def load_from_string(c: str) -> Config
```

Load the object from a string


## ForeignConfig Objects

```python
class ForeignConfig(pydantic.BaseModel)
```

Schema of a foreign config file for any other version of the software
to update to.

A rendered API reference can be found in the documentation at TODO.


#### load\_from\_string

```python
@staticmethod
def load_from_string(c: str) -> ForeignConfig
```

Load the object from a string


#### dump

```python
def dump() -> None
```

Dump the config file to the path `<ivy_root>/<version>/config/config.json`