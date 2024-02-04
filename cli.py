"""Provides a command-line interface to interact with the automation"""

import sys
import time
import click
import src


@click.group()
def cli() -> None:
    pass


@cli.command(
    name="info",
    help="Information about which CLI version and path is used.",
)
def info() -> None:
    click.echo(f"CLI version: {src.constants.VERSION}")
    click.echo(f"Python interpreter: {sys.executable}")
    click.echo(f"Source code: {src.constants.PROJECT_DIR}")


@cli.command(
    name="start",
    help="Start the automation as a background process. " +
    "Prevents spawning multiple processes.",
)
def start() -> None:
    src.utils.MainloopToggle.start_mainloop()


@cli.command(
    name="is-running",
    help="Checks whether the background processes are running.",
)
def is_running() -> None:
    pids = src.utils.MainloopToggle.get_mainloop_pids()
    if len(pids) > 0:
        click.echo(f"background process is running with PID(s) {pids}")
    else:
        click.echo("background processes are not running")


@cli.command(
    name="stop",
    help="Stop the automation's background process.",
)
def stop() -> None:
    src.utils.MainloopToggle.stop_mainloop()


@cli.command(
    name="restart",
    help="Stop and start the automation as a background process."
)
def restart() -> None:
    click.echo("Restarting background process")
    src.utils.MainloopToggle.stop_mainloop()
    time.sleep(0.5)
    src.utils.MainloopToggle.start_mainloop()


if __name__ == "__main__":
    cli.main(prog_name=f"{src.constants.NAME}-cli")
