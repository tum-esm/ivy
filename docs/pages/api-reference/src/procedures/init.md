---
title: __init__.py
---

# `src.procedures.__init__`

This modules provides all procedures that the automation software
should run. They should all be run in parallel processes and each file
provides a single funtion that runs infinitely. Functions may implement
graceful teardown steps upon receiving SIGTERM.


All of the procedures in this module should have the signature:

```python
def run(config: src.types.Config) -> None:
    ...
```