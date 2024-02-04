"""Main loop of the automation"""

import os
import signal
import time
from typing import Any
import src


def run() -> None:
    """Run the automation"""

    config = src.types.Config.load()
    logger = src.utils.Logger(config=config, origin="main")
    messaging_agent = src.utils.MessagingAgent()
    updater = src.utils.Updater(config=config)

    # log that automation is starting up

    logger.info(
        f"Starting automation with PID {os.getpid()}",
        details=f"config = {config.model_dump_json(indent=4)}"
    )
    messaging_agent.add_message(
        src.types.ConfigMessageBody(status="startup", config=config)
    )

    # remove old venvs

    updater.remove_old_venvs()

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
    ]
    if config.backend is not None:
        if config.backend.provider == "tenta":
            procedure_managers.append(
                src.utils.ProcedureManager(
                    config=config,
                    procedure_entrypoint=src.backend.run_tenta_backend,
                    procedure_name="tenta-backend",
                )
            )
        if config.backend.provider == "thingsboard":
            procedure_managers.append(
                src.utils.ProcedureManager(
                    config=config,
                    procedure_entrypoint=src.backend.run_thingsboard_backend,
                    procedure_name="thingsboard-backend",
                )
            )

    # establish graceful shutdown logic

    def teardown_handler(*args: Any) -> None:
        logger.debug("starting teardown of the main loop")
        for pm in procedure_managers:
            pm.teardown()
        logger.debug("finished teardown of the main loop")

    signal.signal(signal.SIGINT, teardown_handler)
    signal.signal(signal.SIGTERM, teardown_handler)

    # start the main loop

    exponential_backoff = src.utils.ExponentialBackoff(logger, buckets=[60, 240, 900])
    while True:
        try:
            for pm in procedure_managers:
                if not pm.procedure_is_running():
                    pm.start_procedure()
                pm.check_procedure_status()

            pending_configs = src.utils.StateInterface.load().pending_configs
            for pending_config in pending_configs:
                updater.perform_update(pending_config)
            with src.utils.StateInterface.update() as state:
                state.pending_configs = state.pending_configs[len(pending_configs):]

            exponential_backoff.reset()
            time.sleep(10)
        except Exception as e:
            logger.exception(e, label="Exception in main loop")
            exponential_backoff.sleep()
