from __future__ import annotations
from typing import Callable, Optional
import signal
import multiprocessing
import src


class ProcedureManager():
    def __init__(
        self,
        config: src.types.Config,
        procedure_entrypoint: Callable[[src.types.Config], None],
        procedure_name: str,
    ) -> None:
        self.config = config
        self.process: Optional[multiprocessing.Process] = None
        self.procedure_entrypoint = procedure_entrypoint
        self.procedure_name = procedure_name
        self.logger = src.utils.Logger(
            f"{self.procedure_name}-procedure-manager"
        )

    def start_process_if_not_running(self) -> bool:
        if self.process is None:
            self.process = multiprocessing.Process(
                target=self.run_procedure,
                args=(self.config, ),
                name=f"{src.constants.NAME}-procedure-{self.procedure_name}",
                daemon=True,
            )
            self.process.start()
            self.logger.info(
                "started process",
                details=f"pid = {self.process.pid}\nname={self.process.name}",
            )
            return True
        else:
            self.logger("process is already running")
            return False

    def check_process_status(self) -> None:
        if self.process is not None:
            if self.process.is_alive():
                self.logger("process is alive")
            else:
                self.logger("process died unexpectedly")
                self.process = None
        else:
            self.logger("process has not been started yet")

    def teardown(self) -> None:
        if self.process is not None:
            # what to do if process does not tear down gracefully
            def kill_process() -> None:
                self.logger(
                    "process did not gracefully tear down in {} seconds, killing it forcefully"
                    .format(
                        src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN
                    )
                )
                self.process.kill()

            # give process some time to tear down gracefully
            # if it does not stop, kill it forcefully
            self.process.terminate()
            signal.signal(signal.SIGALRM, kill_process)
            signal.alarm(src.constants.SECONDS_PER_GRACEFUL_PROCEDURE_TEARDOWN)
            self.process.join()
            signal.alarm(0)

            self.process = None
            self.logger("teardown complete")
        else:
            self.logger("no process to tear down")
