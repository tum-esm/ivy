
# src/modules/updater


## Updater Objects

```python
class Updater()
```

TODO


#### \_\_init\_\_

```python
def __init__(
        config: src.types.Config,
        distribute_new_config: Callable[[src.types.Config], None]) -> None
```

TODO


#### perform\_update

```python
def perform_update(config_file_content: str) -> None
```

TODO


#### download\_source\_code

```python
def download_source_code(version: str) -> None
```

TODO


#### install\_dependencies

```python
def install_dependencies(version: str) -> None
```

TODO


#### dump\_config\_file

```python
def dump_config_file(version: str, config_file_content: str) -> None
```

TODO


#### run\_pytests

```python
def run_pytests(version: str) -> None
```

TODO


#### remove\_old\_venvs

```python
def remove_old_venvs() -> None
```

TODO


#### update\_cli\_pointer

```python
def update_cli_pointer(version: str) -> None
```

make the file pointing to the used cli to the new version's cli