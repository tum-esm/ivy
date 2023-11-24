---
title: config.py
---

# `src/types/config.py`
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