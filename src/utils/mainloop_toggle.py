"""Functions to start and terminate background processes."""

from __future__ import annotations
from typing import Annotated, Optional
import os
import sys
import time
import click
import psutil
import src

SCRIPT_PATH: Annotated[
    str,
    "Absolute path of the `run.py` file that starts an infinite mainloop",
] = os.path.join(src.constants.PROJECT_DIR, "run.py")


# TODO: use `tum-esm-utils` for that
def _get_process_pids(script_path: str) -> list[int]:
    """Return a list of PIDs that have the given script as their entrypoint.
    
    Args:
        script_path: The absolute path of the python file entrypoint.
    """

    pids: list[int] = []
    for p in psutil.process_iter():
        try:
            if p.cmdline()[1] == script_path:
                pids.append(p.pid)
        except (
            psutil.AccessDenied,
            psutil.ZombieProcess,
            psutil.NoSuchProcess,
            IndexError,
        ):
            pass
    return pids


# TODO: use `tum-esm-utils` for that
def _terminate_process(
    script_path: str,
    termination_timeout: Optional[int] = None,
) -> list[int]:
    """Terminate all processes that have the given script as their
    entrypoint. Returns the list of terminated PIDs.
    
    If `termination_timeout` is not None, the processes will be
    terminated forcefully after the given timeout (in seconds).
    
    Args:
        script_path:         The absolute path of the python file entrypoint.
        termination_timeout: The timeout in seconds after which the
                             processes will be terminated forcefully.
    """

    processes_to_terminate: list[psutil.Process] = []

    # terminate the processes gracefully
    for p in psutil.process_iter():
        try:
            if p.cmdline()[1] == script_path:
                processes_to_terminate.append(p)
                p.terminate()
        except (
            psutil.AccessDenied,
            psutil.ZombieProcess,
            psutil.NoSuchProcess,
            IndexError,
        ):
            pass

    # kill the processes using SIGKILL after a timeout
    if termination_timeout is not None:
        t1 = time.time()
        while True:
            try:
                if (time.time() - t1) > termination_timeout:
                    for p in processes_to_terminate:
                        if p.is_running():
                            p.kill()
                if any([p.is_running() for p in processes_to_terminate]):
                    time.sleep(1)
                else:
                    # all processes have gracefully terminated
                    break
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass

    return [p.pid for p in processes_to_terminate]


class MainloopToggle:
    """Used to start and stop the mainloop process in the background.
    
    All functionality borrowed from the [`tum-esm-utils` package](https://github.com/tum-esm/utils)
    """
    @staticmethod
    def start_mainloop() -> None:
        """Start the mainloop process in the background and print
        the process ID(s) of the new process(es)."""

        current_pids = _get_process_pids(SCRIPT_PATH)
        if len(current_pids) > 0:
            click.echo(f"Background processes already exists with PID(s) {current_pids}")
            exit(1)
        else:
            os.system(
                f"cd {os.path.dirname(SCRIPT_PATH)} && " +
                f"nohup {sys.executable} {SCRIPT_PATH} &"
            )
            time.sleep(0.5)
            new_pids = _get_process_pids(SCRIPT_PATH)
            if len(new_pids) == 0:
                click.echo(f"Could not start background process")
                exit(1)
            else:
                click.echo(f"Started background process with PID(s) {new_pids}")

    @staticmethod
    def stop_mainloop() -> None:
        """Terminate the mainloop process in the background and print
        the process ID(s) of the terminated process(es)."""

        termination_pids = _terminate_process(SCRIPT_PATH)
        if len(termination_pids) == 0:
            click.echo("No active process to be terminated")
        else:
            click.echo(
                f"Terminated {len(termination_pids)} automation background " +
                f"processe(s) with PID(s) {termination_pids}"
            )

    @staticmethod
    def get_mainloop_pids() -> list[int]:
        """Get the process ID(s) of the mainloop process(es).
        
        Should be used to check if the mainloop process is running.
        
        Returns:
            A list of process IDs. Might have more than one element if
            the mainloop process has spawned child process(es).
        """

        return _get_process_pids(SCRIPT_PATH)
