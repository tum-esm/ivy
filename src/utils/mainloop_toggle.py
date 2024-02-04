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


def _get_process_pids(script_path: str) -> list[int]:
    """Return a list of PIDs that have the given script as their entrypoint"""

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


def _start_background_process(interpreter_path: str, script_path: str) -> int:
    """Start a new background process with nohup with a given python
    interpreter and script path. The script paths parent directory
    will be used as the working directory for the process."""

    existing_pids = _get_process_pids(script_path)
    assert len(existing_pids) == 0, "process is already running"

    cwd = os.path.dirname(script_path)
    os.system(f"cd {cwd} && nohup {interpreter_path} {script_path} &")
    time.sleep(0.5)

    new_pids = _get_process_pids(script_path)
    assert (
        len(new_pids) == 1
    ), f"multiple processes found ({new_pids}), when there should only be one"

    return new_pids[0]


def _terminate_process(
    script_path: str,
    termination_timeout: Optional[int] = None,
) -> list[int]:
    """Terminate all processes that have the given script as their
    entrypoint. Returns the list of terminated PIDs.
    
    If `termination_timeout` is not None, the processes will be
    terminated forcefully after the given timeout (in seconds)."""

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
            os.system(f"nohup {sys.executable} {SCRIPT_PATH} &")
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
        """Return the process ID(s) of the mainloop process(es).
        
        Should be used to check if the mainloop process is running."""

        return _get_process_pids(SCRIPT_PATH)
