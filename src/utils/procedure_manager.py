from __future__ import annotations
from typing import Any, Literal, Union, Callable, Optional
import signal
import multiprocessing
import multiprocessing.synchronize
import pydantic
from .logger import Logger
import src


class ProcedureManager():
    """Manages the lifecycle of a procedure. A procedure is a long-running
    process that is started in a separate process. The procedure manager
    is responsible for starting, stopping and checking the status of the
    procedure."""
    def __init__(
        self,
        config: src.types.Config,
        entrypoint: Union[
            Callable[[src.types.Config, Logger], None],
            Callable[[src.types.Config, Logger, multiprocessing.synchronize.Event], None],
        ],
        procedure_name: str,
        variant: Literal["procedure", "backend"],
    ) -> None:
        self.config = config
        self.process: Optional[multiprocessing.Process] = None

        self.entrypoint: Union[
            Callable[[src.types.Config, Logger], None],
            Callable[[src.types.Config, Logger, multiprocessing.synchronize.Event], None],
        ]
        self.variant = variant
        self.teardown_indicator = multiprocessing.synchronize.Event()
        if variant == "procedure":
            self.entrypoint = pydantic.RootModel[Callable[
                [src.types.Config, Logger],
                None,
            ]].model_validate(entrypoint).root
        else:
            self.procedure_entrypoint = pydantic.RootModel[Callable[
                [src.types.Config, Logger, multiprocessing.synchronize.Event],
                None,
            ]].model_validate(entrypoint).root

        self.procedure_name = procedure_name
        self.logger = Logger(
            config=config, origin=f"{self.procedure_name}-procedure-manager"
        )
        self.procedure_logger = Logger(config=config, origin=f"{self.procedure_name}")

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
            target=self.procedure_entrypoint,
            args=((self.config, self.procedure_logger) if
                  (self.variant == "procedure") else
                  (self.config, self.procedure_logger, self.teardown_indicator)),
            name=f"{src.constants.NAME}-procedure-{self.procedure_name}",
            daemon=True,
        )
        self.process.start()
        self.logger.info(
            "started process",
            details=f"pid = {self.process.pid}\nname={self.process.name}",
        )

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
        """Tears down the procedures."""

        self.logger.info(f"starting teardown of {self.variant}")
        if self.process is not None:
            graceful_shutdown_time = (
                src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN if
                (self.variant == "procedure") else
                (self.config.backend.max_drain_time + 120)
            )

            # what to do if process does not tear down gracefully
            def kill_process(*args: Any) -> None:
                self.logger.error(
                    f"process did not gracefully tear down in " +
                    f"{graceful_shutdown_time} seconds, killing it forcefully"
                )
                if self.process is not None:
                    self.process.kill()

            # give process some time to tear down gracefully
            # if it does not stop, kill it forcefully
            signal.signal(signal.SIGALRM, kill_process)
            signal.alarm(graceful_shutdown_time)

            if self.variant == "procedure":
                self.process.terminate()
            else:
                self.teardown_indicator.set()
            self.process.join()
            signal.alarm(0)

            self.process = None
            self.logger.info("teardown complete")
        else:
            self.logger.info("no process to tear down")
