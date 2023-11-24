import os
import re
import subprocess
from typing import Optional
import src

version_regex = re.compile(src.constants.VERSION_REGEX)


def string_is_valid_version(version_string: str) -> bool:
    """Check if the version string is valid. Valid version name examples `v1.2.3`,
    `v4.5.6-alpha.78`, `v7.8.9-beta.10`, `v11.12.13-rc.14`.
    
    Args:
        version_string: version string to check.
    
    Returns:
        True if the version string is valid, False otherwise."""

    return version_regex.match(version_string) is not None


class CommandLineException(Exception):
    def __init__(self, value: str, details: Optional[str] = None) -> None:
        self.value = value
        self.details = details
        Exception.__init__(self)

    def __str__(self) -> str:
        return repr(self.value)


def run_shell_command(
    command: str,
    working_directory: Optional[str] = None,
    executable: str = "/bin/bash",
) -> str:
    """runs a shell command and raises a `CommandLineException`
    if the return code is not zero, returns the stdout. Uses
    `/bin/bash` by default."""

    p = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_directory,
        env=os.environ.copy(),
        executable=executable,
    )
    stdout = p.stdout.decode("utf-8", errors="replace").strip()
    stderr = p.stderr.decode("utf-8", errors="replace").strip()

    if p.returncode != 0:
        raise CommandLineException(
            f"command '{command}' failed with exit code {p.returncode}",
            details=f"\nstderr:\n{stderr}\nstout:\n{stdout}",
        )

    return stdout
