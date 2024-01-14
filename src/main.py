"""Main loop of the automation"""

import os
import time
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
        src.types.ConfigMessageBody(config=config, status="startup")
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

    # establish graceful shutdown logic

    # TODO: shut down all procedures gracefully
    # TODO: prevent new procedures from starting

    # start the main loop

    while True:
        for pm in procedure_managers:
            if not pm.procedure_is_running():
                pm.start_procedure()
            pm.check_procedure_status()

        pending_configs = src.utils.StateInterface.load().pending_configs
        for pending_config in pending_configs:
            updater.perform_update(pending_config)
        with src.utils.StateInterface.update() as state:
            state.pending_configs = state.pending_configs[len(pending_configs):]

        time.sleep(5)
