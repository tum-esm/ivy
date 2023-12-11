---
title: __init__.py
---

# `src.procedures.__init__`

All of the procedures in this module should have the signature:

```python
def run(config: src.types.Config) -> None:
    ...
```

They run in an infinite loop and tear down gracefully on SIGTERM.