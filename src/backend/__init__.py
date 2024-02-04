"""This module provides all backends that the automation software can communicate
with. Every submodule should provide a single function that runs infinitely.

All of the procedures in this module should have the signature:

```python
def run(
    config: src.types.Config,
    logger: src.utils.Logger,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
    ...
```

These are managed by a `src.utils.ProcessManager`, but opposed to "procedures", they
do not receive a SIGTERM signal, but the `teardown_indicator` event is set. This
gives more freedom on how to handle the shutdown of the backend."""

from . import (
    tenta_backend,
    thingsboard_backend,
)
