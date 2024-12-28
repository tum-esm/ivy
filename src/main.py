from typing import Any
import os
import signal
import time

import tum_esm_utils
import src


def run() -> None:
    """Run the automation.

    1. Load the configuration
    2. Initialize the logger
    3. Initialize the messaging agent
    4. Initialize the updater
    5. Remove old virtual environments
    6. Initialize the lifecycle managers
    7. Establish graceful shutdown logic (run teardown for every lifecycle manager)
    8. Start the main loop

    Inside the mainloop the following steps are performed until termination:

    1. Start each procedure/backend if it is not running
    2. Check the status of each procedure/backend
    3. Perform any pending updates

    If an exception is raised in the main loop, it is logged and the main loop
    sleeps for an exponentially increasing amount of time before it tries to
    continue."""

    config = src.types.Config.load()
    logger = src.utils.Logger(config=config, origin="main")
    messaging_agent = src.utils.MessagingAgent()
    updater = src.utils.Updater(config=config)

    # log that automation is starting up

    logger.info(
        f"Starting automation with PID {os.getpid()}",
        details=f"config = {config.model_dump_json(indent=4)}",
    )
    messaging_agent.add_message(
        src.types.ConfigMessageBody(status="startup", config=config.to_foreign_config())
    )

    # remove old venvs

    updater.remove_old_venvs(
        current_version=config.general.software_version,
        log_progress=logger.info,
    )

    # initialize lifecycle managers which are responsible for
    # starting/stopping each procedure/backend in a child process

    lifecycle_managers: list[src.utils.LifecycleManager] = [
        src.utils.LifecycleManager(
            config=config,
            entrypoint=src.procedures.dummy_procedure.run,
            name="dummy-procedure",
            variant="procedure",
        ),
        src.utils.LifecycleManager(
            config=config,
            entrypoint=src.procedures.system_checks.run,
            name="system-checks",
            variant="procedure",
        ),
        # CUSTOM: Add your own procedures here
    ]

    if config.backend is not None:
        if config.backend.provider == "tenta":
            lifecycle_managers.append(
                src.utils.LifecycleManager(
                    config=config,
                    entrypoint=src.backend.tenta_backend.run,
                    name="tenta-backend",
                    variant="backend",
                )
            )
        if config.backend.provider == "thingsboard":
            lifecycle_managers.append(
                src.utils.LifecycleManager(
                    config=config,
                    entrypoint=src.backend.thingsboard_backend.run,
                    name="thingsboard-backend",
                    variant="backend",
                )
            )

        # CUSTOM: Add your own backends here

    # establish graceful shutdown logic

    def teardown_handler(*args: Any) -> None:
        logger.debug("starting teardown of the main loop")
        for lm in lifecycle_managers:
            lm.teardown()
        logger.debug("finished teardown of the main loop")

    signal.signal(signal.SIGINT, teardown_handler)
    signal.signal(signal.SIGTERM, teardown_handler)

    # start the main loop

    exponential_backoff = tum_esm_utils.timing.ExponentialBackoff(
        log_info=logger.info, buckets=[60, 240, 900]
    )
    while True:
        try:
            for lm in lifecycle_managers:
                if not lm.procedure_is_running():
                    lm.start_procedure()
                lm.check_procedure_status()

            pending_configs = src.utils.StateInterface.load().pending_configs
            for pending_config in pending_configs:
                updater.perform_update(pending_config)
            with src.utils.StateInterface.update() as state:
                state.pending_configs = state.pending_configs[len(pending_configs) :]

            exponential_backoff.reset()
            time.sleep(10)
        except Exception as e:
            logger.exception(e, label="Exception in main loop")
            exponential_backoff.sleep()
