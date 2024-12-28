from __future__ import annotations
from typing import Any, Literal, Union, Callable, Optional
import signal
import multiprocessing
import multiprocessing.synchronize
import pydantic
from .logger import Logger
import src


class LifecycleManager:
    """Manages the lifecycle of a procedure or a backend process.

    Both procedures and backends run an infinite loop to perform their
    respective tasks. The procedure manager is responsible for starting,
    stopping and checking the status of the procedure.

    Each procedure/backend is wrapped in one instance of the lifecycle
    manager."""

    def __init__(
        self,
        config: src.types.Config,
        entrypoint: Union[
            Callable[[src.types.Config, str], None],
            Callable[[src.types.Config, str, multiprocessing.synchronize.Event], None],
        ],
        name: str,
        variant: Literal["procedure", "backend"],
    ) -> None:
        """Initializes a new lifecycle manager.

        Args:
            config:         The configuration object.
            entrypoint:     The entrypoint of the procedure or backend.
            name: The name of the procedure or backend. Used to name
                            the spawned process.
            variant:        Whether the entrypoint is a procedure or a backend.
                            The difference is only in the teardown logic.

        Raises:
            ValueError: If the given variant does not match the entrypoint
                        signature.
        """

        self.config = config
        self.process: Optional[multiprocessing.Process] = None

        self.entrypoint: Union[
            Callable[[src.types.Config, str], None],
            Callable[[src.types.Config, str, multiprocessing.synchronize.Event], None],
        ]
        self.variant = variant
        self.teardown_indicator = multiprocessing.Event()
        try:
            if variant == "procedure":
                self.entrypoint = (
                    pydantic.RootModel[
                        Callable[
                            [src.types.Config, str],
                            None,
                        ]
                    ]
                    .model_validate(entrypoint)
                    .root
                )
            else:
                self.entrypoint = (
                    pydantic.RootModel[
                        Callable[
                            [src.types.Config, str, multiprocessing.synchronize.Event],
                            None,
                        ]
                    ]
                    .model_validate(entrypoint)
                    .root
                )
        except pydantic.ValidationError as e:
            raise ValueError(f"Given variant '{variant}' does not match the entrypoint signature")

        self.name = name
        self.logger = Logger(config=config, origin=f"{self.name}-lifecycle-manager")

    def procedure_is_running(self) -> bool:
        """Returns True if the procedure has been started. Does not check
        whether the process is still alive."""

        return self.process is not None

    def start_procedure(self) -> None:
        """Starts the procedure in a separate process.

        Raises:
            RuntimeError: If the procedure is already running. This is a
                          wrong usage of the procedure manager.
        """

        if self.procedure_is_running():
            raise RuntimeError("procedure is already running")
        self.process = multiprocessing.Process(
            target=self.entrypoint,
            args=(
                (self.config, self.name)
                if (self.variant == "procedure")
                else (self.config, self.name, self.teardown_indicator)
            ),
            name=f"{src.constants.NAME}-procedure-{self.name}",
            daemon=True,
        )
        self.process.start()
        self.logger.info(f"started process with pid {self.process.pid}")

    def check_procedure_status(self) -> None:
        """Checks if the procedure is still running. Logs an error if
        the procedure has died unexpectedly.

        Raises:
            RuntimeError: If the procedure has not been started yet. This
                          is a wrong usage of the procedure manager.
        """

        if self.process is None:
            raise RuntimeError("procedure has not been started yet")

        if self.process.is_alive():
            self.logger.debug("process is alive")
        else:
            self.logger.error("process died unexpectedly")
            self.process = None

    def teardown(self) -> None:
        """Tears down the procedures.

        For procedures, it sends a SIGTERM to the process. For backends, it
        sets a multiprocessing.Event to signal the backend to shut down. This
        gives the backend processes more freedom to manage a shutdown.

        The lifecycle manager waits for the process to shut down gracefully
        for a certain amount of time. If the process does not shut down in
        time, it kills the process forcefully by sending a SIGKILL.

        For procedures, the SIGKILL is sent after
        `src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN` seconds. For
        backends, the SIGKILL is sent after `config.backend.max_drain_time + 15`
        seconds."""

        self.logger.info(f"starting teardown of {self.variant}")
        if self.process is not None:
            if not self.process.is_alive():
                self.logger.debug("nothing to tear down, process is already stopped")
                self.process = None
                return

            graceful_shutdown_time: int
            if self.variant == "procedure":
                graceful_shutdown_time = src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN
            else:
                if self.config.backend is not None:
                    graceful_shutdown_time = self.config.backend.max_drain_time + 15
                else:
                    graceful_shutdown_time = 10

            if self.variant == "procedure":
                self.process.terminate()
            else:
                self.teardown_indicator.set()
            self.logger.info(
                f"Waiting up to {graceful_shutdown_time} seconds for process to tear down on its own"
            )
            self.process.join(graceful_shutdown_time)
            if self.process.is_alive():
                self.logger.error(
                    f"process did not gracefully tear down in "
                    + f"{graceful_shutdown_time} seconds, killing it forcefully"
                )
                self.process.kill()
            self.process = None
            self.logger.info("teardown complete")
        else:
            self.logger.info("no process to tear down")
