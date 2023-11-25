"""Main loop of the automation"""

import time
import src


def run() -> None:
    """Run the automation"""

    config = src.types.Config.load()

    modules: list[src.utils.ModuleBaseClass] = [
        src.modules.SystemCheckModule(config),
        src.modules.DummyProcedureModule(config)
    ]

    # TODO: add graceful teardown

    while True:
        for module in modules:
            module.run()
        time.sleep(5)
