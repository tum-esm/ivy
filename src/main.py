"""Main loop of the automation"""

import os
import time
import src


def run() -> None:
    """Run the automation"""

    config = src.types.Config.load()
    logger = src.utils.Logger(config=config, origin="main")
    messaging_agent = src.utils.MessagingAgent()

    # log that automation is starting up

    logger.info(
        f"Starting automation with PID {os.getpid()}",
        details=f"config = {config.model_dump_json(indent=4)}"
    )
    messaging_agent.add_message(
        src.types.ConfigMessageBody(config=config, status="startup")
    )

    # remove old venvs

    # TODO

    # initialize procedure managers that are responsible for
    # starting and stopping the processes for each procedure

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
        # TODO: MQTT agent
    ]

    # establish graceful shutdown logic

    # TODO

    # start the main loop

    while True:
        for pm in procedure_managers:
            new_process_started = pm.start_process_if_not_running()
            if not new_process_started:
                pm.check_process_status()

        time.sleep(5)
