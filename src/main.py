"""Main loop of the automation"""

import time
import src


def run() -> None:
    """Run the automation"""

    config = src.types.Config.load()

    procedure_managers: list[src.utils.ProcedureManager] = [
        src.utils.ProcedureManager(
            config=config,
            procedure_entrypoint=src.procedures.dummy_procedure.run,
            procedure_name="dummy-procedure",
        ),
        src.utils.ProcedureManager(
            config=config,
            procedure_entrypoint=src.procedures.system_checks.run,
            procedure_name="system-checks",
        ),
    ]

    # TODO: add graceful teardown

    while True:
        for pm in procedure_managers:
            new_process_started = pm.start_process_if_not_running()
            if not new_process_started:
                pm.check_process_status()

        time.sleep(5)
