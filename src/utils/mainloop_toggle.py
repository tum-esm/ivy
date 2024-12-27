"""Functions to start and terminate background processes."""

from __future__ import annotations
from typing import Annotated
import os
import sys
import time
import src
import tum_esm_utils

SCRIPT_PATH: Annotated[
    str,
    "Absolute path of the `run.py` file that starts an infinite mainloop",
] = os.path.join(src.constants.PROJECT_DIR, "run.py")


class MainloopToggle:
    """Used to start and stop the mainloop process in the background.

    All functionality borrowed from the [`tum-esm-utils` package](https://github.com/tum-esm/utils)
    """

    @staticmethod
    def start_mainloop() -> None:
        """Start the mainloop process in the background and print
        the process ID(s) of the new process(es)."""

        current_pids = tum_esm_utils.processes.get_process_pids(SCRIPT_PATH)
        if len(current_pids) > 0:
            print(f"Background processes already exists with PID(s) {current_pids}")
            exit(1)
        else:
            os.system(
                f"cd {os.path.dirname(SCRIPT_PATH)} && " + f"nohup {sys.executable} {SCRIPT_PATH} &"
            )
            time.sleep(0.5)
            new_pids = tum_esm_utils.processes.get_process_pids(SCRIPT_PATH)
            if len(new_pids) == 0:
                print(f"Could not start background process")
                exit(1)
            else:
                print(f"Started background process with PID(s) {new_pids}")

    @staticmethod
    def stop_mainloop() -> None:
        """Terminate the mainloop process in the background and print
        the process ID(s) of the terminated process(es)."""

        termination_pids = tum_esm_utils.processes.terminate_process(SCRIPT_PATH)
        if len(termination_pids) == 0:
            print("No active process to be terminated")
        else:
            print(
                f"Terminated {len(termination_pids)} automation background "
                + f"processe(s) with PID(s) {termination_pids}"
            )

    @staticmethod
    def get_mainloop_pids() -> list[int]:
        """Get the process ID(s) of the mainloop process(es).

        Should be used to check if the mainloop process is running.

        Returns:
            A list of process IDs. Might have more than one element if
            the mainloop process has spawned child process(es).
        """

        return tum_esm_utils.processes.get_process_pids(SCRIPT_PATH)
