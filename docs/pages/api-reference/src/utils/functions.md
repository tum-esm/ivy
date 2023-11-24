---
title: functions.py
---

# `src.utils.functions`

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