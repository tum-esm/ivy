from __future__ import annotations
from typing import Any, Callable, Optional
import signal
import multiprocessing
from .logger import Logger
import src


class ProcedureManager():
    def __init__(
        self,
        config: src.types.Config,
        procedure_entrypoint: Callable[[src.types.Config, Logger], None],
        procedure_name: str,
    ) -> None:
        self.config = config
        self.process: Optional[multiprocessing.Process] = None
        self.procedure_entrypoint = procedure_entrypoint
        self.procedure_name = procedure_name
        self.logger = Logger(
            config=config, origin=f"{self.procedure_name}-procedure-manager"
        )
        self.procedure_logger = Logger(
            config=config, origin=f"{self.procedure_name}"
        )

    def procedure_is_running(self) -> bool:
        return self.process is not None

    def start_procedure(self) -> None:
        assert not self.procedure_is_running()
        self.process = multiprocessing.Process(
            target=self.procedure_entrypoint,
            args=(self.config, self.procedure_logger),
            name=f"{src.constants.NAME}-procedure-{self.procedure_name}",
            daemon=True,
        )
        self.process.start()
        self.logger.info(
            "started process",
            details=f"pid = {self.process.pid}\nname={self.process.name}",
        )

    def check_procedure_status(self) -> None:
        assert self.process is not None

        if self.process.is_alive():
            self.logger.debug("process is alive")
        else:
            self.logger.error("process died unexpectedly")
            self.process = None

    def teardown(self) -> None:
        self.logger.info("starting teardown")
        if self.process is not None:
            # what to do if process does not tear down gracefully
            def kill_process(*args: Any) -> None:
                self.logger.error(
                    "process did not gracefully tear down in {} seconds, killing it forcefully"
                    .format(
                        src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN
                    )
                )
                if self.process is not None:
                    self.process.kill()

            # give process some time to tear down gracefully
            # if it does not stop, kill it forcefully
            self.process.terminate()
            signal.signal(signal.SIGALRM, kill_process)
            signal.alarm(src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN)
            self.process.join()
            signal.alarm(0)

            self.process = None
            self.logger.info("teardown complete")
        else:
            self.logger.info("no process to tear down")
