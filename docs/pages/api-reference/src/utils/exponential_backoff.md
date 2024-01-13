---
title: exponential_backoff.py
---

# `src.utils.exponential_backoff`


## ExponentialBackoff Objects

```python
class ExponentialBackoff()
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


#### \_\_init\_\_

```python
def __init__(logger: Logger,
             buckets: list[int] = [60, 240, 900, 3600, 14400]) -> None
```

Create a new exponential backoff object.

**Arguments**:

- `logger` - The logger to use for logging when waiting certain amount of time.
- `buckets` - The buckets to use for the exponential backoff.


#### sleep

```python
def sleep() -> None
```

Wait and increase the wait time to the next bucket.


#### reset

```python
def reset() -> None
```

Reset the waiting period to the first bucket