---
title: updater.py
---

# `src.modules.updater`

## Updater Objects

```python
class Updater()
```

Implementation of the update capabilities of the ivy seed: checks
whether a new config is in a valid format, downloads new source code,
creates virtual environments, installs dependencies, runs pytests,
removes old virtual environments, and updates the cli pointer to the
currently used version of the automation software.


#### \_\_init\_\_

```python
def __init__(config: src.types.Config) -> None
```

Initialize an Updater instance.

**Arguments**:

- `config` - The current config.


#### perform\_update

```python
def perform_update(config_file_string: str) -> None
```

Perform an update for a received config file.

1. Parse the received config file string using
`types.ForeignConfig.load_from_string` to check whether
it is an object and contains the key `version`.
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

**Arguments**:

- `config_file_string` - The content of the config file to be processed.
  This is a string, which will be parsed using
  `types.ForeignConfig.load_from_string`. It should
  be a JSON object with at least the `version` field,
  everything else is optional.


#### download\_source\_code

```python
def download_source_code(version: str) -> None
```

Download the source code of the new version to the version
directory. This is currently only implemented for github and
gitlab for private and public repositories. Feel free to request
other providers in the issue tracker.


#### install\_dependencies

```python
def install_dependencies(version: str) -> None
```

Create a virtual environment and install the dependencies in
the version directory using poetry.


#### run\_pytests

```python
def run_pytests(version: str) -> None
```

Run all pytests with the mark "version_change" in the version directory.


#### remove\_old\_venvs

```python
def remove_old_venvs() -> None
```

Remove all old virtual environments, that are not currently in use.


#### update\_cli\_pointer

```python
def update_cli_pointer(version: str) -> None
```

Update the cli pointer to a new version