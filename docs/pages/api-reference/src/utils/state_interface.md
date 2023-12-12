---
title: state_interface.py
---

# `src.utils.state_interface`


## StateInterface Objects

```python
class StateInterface()
```


#### load

```python
@with_filelock(STATE_FILE_LOCK, timeout=6)
@staticmethod
def load() -> src.types.State
```

Load the state file from the path `project_dir/data/state.json`


#### update

```python
@with_filelock(STATE_FILE_LOCK, timeout=6)
@staticmethod
@contextlib.contextmanager
def update() -> Generator[src.types.State, None, None]
```

Load the state file and update it within a semaphore. Usage:

```python
with State.update() as state:
    state.system.last_boot_time = datetime.datetime.now()
```