#!/bin/python3

from typing import Callable, Generator, Optional
import contextlib
import json
import os
import re
import socket
import sys

BOLD_CODE = "\033[1m"
GREEN_CODE = "\033[32m"
YELLOW_CODE = "\033[33m"
RED_CODE = "\033[31m"
GRAY_CODE = "\033[90m"
RESET_CODE = "\033[0m"


@contextlib.contextmanager
def section(label: str) -> Generator[Callable[[str], None], None, None]:
    print(f"{BOLD_CODE}{label}: Starting{RESET_CODE}")
    print(GRAY_CODE)
    yield lambda message: print(f"{RESET_CODE}{message}{GRAY_CODE}")
    print(RESET_CODE)
    print(f"{GREEN_CODE}{label}: Finished{RESET_CODE}")


def error(message: str) -> None:
    print(f"{RED_CODE}ERROR: {message}{RESET_CODE}")
    sys.exit(1)


def format_warning(message: str) -> str:
    return f"{YELLOW_CODE}WARNING: {message}{RESET_CODE}"


def get_validated_input(
    prompt: str,
    conditions: list[tuple[Callable[[str], bool], str]],
) -> str:
    while True:
        output = input(f"{BOLD_CODE}{prompt}\n>{RESET_CODE} ").strip("\t\n ")
        valid_output: bool = True
        for condition, message in conditions:
            if not condition(output):
                print(f"{RED_CODE}Invalid input: {message}{RESET_CODE}")
                valid_output = False
                break
        if valid_output:
            return output


# GET USER INPUTS

PROJECT_NAME = get_validated_input(
    "What is the name of your DAS? (instead of `ivy`)",
    conditions=[
        (lambda s: len(s) > 0, "Project name cannot be empty"),
    ],
)

GIT_REPOSITORY = get_validated_input(
    "Where is your git repository hosted? (instead of `https://github.com/tum-esm/ivy`)",
    conditions=[
        (
            lambda s: s.startswith("https://") or s.startswith("git@"),
            "Git repository must start with 'https://' or 'git@'",
        ),
    ],
)

PACKAGE_MANAGER = get_validated_input(
    "How do you want to install your dependencies? (pip | pdm | uv)",
    conditions=[
        (lambda s: s in ["pip", "pdm", "uv"], "Must be one of 'pip', 'pdm', or 'uv'"),
    ],
)

HOSTNAME = socket.gethostname().replace("_", "-").replace(" ", "-").lower()
SYSTEM_IDENTIFIER = get_validated_input(
    f'How do you want to name this computer? (if empty, uses "{HOSTNAME}")',
    conditions=[
        (lambda s: len(s) <= 512, "System identifier cannot be empty"),
        (
            lambda s: re.match(r"^[a-z0-9-]+$", s),
            "Only lowercase letters, numbers, and hyphens are allowed",
        ),
    ],
)
if SYSTEM_IDENTIFIER == "":
    SYSTEM_IDENTIFIER = HOSTNAME

CONFIGURE_BACKEND = (
    get_validated_input(
        "Do you want to configure an MQTT broker? (yes | no)",
        conditions=[
            (
                lambda s: s.lower() in ["yes", "no", "y", "n"],
                "Must be 'yes'/'y' or 'no'/'n'",
            ),
        ],
    )
    .lower()
    .startswith("y")
)

# fmt: off
print(f"{BOLD_CODE}Setting up your DAS with the following configuration:{RESET_CODE}")
print(f"  Project name:            {PROJECT_NAME}")
print(f"  Git repository:          {GIT_REPOSITORY}")
print(f"  Package manager:         {PACKAGE_MANAGER}")
print(f"  System identifier:       {SYSTEM_IDENTIFIER}")
print(f"  Configure MQTT broker:   {'yes' if CONFIGURE_BACKEND else 'no'}\n")
print(f"  Python Interpreter:      {sys.executable}")
print(f"  Installation Location:   {os.path.join(os.path.expanduser('~'), 'Documents', PROJECT_NAME, 'dev')}\n")
# fmt: on

PROCEED = (
    get_validated_input(
        "Do you want to proceed? (yes | no)",
        conditions=[
            (
                lambda s: s.lower() in ["yes", "no", "y", "n"],
                "Must be 'yes'/'y' or 'no'/'n'",
            ),
        ],
    )
    .lower()
    .startswith("y")
)
if not PROCEED:
    print("Aborting setup.")
    sys.exit(0)

# CREATE DIRECTORIES

with section("Setting up directories") as localprint:
    documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
    project_dir = os.path.join(documents_dir, PROJECT_NAME)
    version_dir = os.path.join(project_dir, "dev")

    for d in [documents_dir, project_dir, version_dir]:
        if os.path.isfile(d):
            error(f"{d} is a file, not a directory. Please remove it.")

    if os.path.isdir(version_dir):
        error(f"{version_dir} already exists. Remove it if you want to run the setup again.")

    if not os.path.isdir(project_dir):
        os.makedirs(project_dir, exist_ok=True)
        localprint(f"Created directory {project_dir}")

# CLONE REPOSITORY

with section("Cloning repository") as localprint:
    assert os.system(f"git clone {GIT_REPOSITORY} {version_dir}") == 0
    localprint(f"Cloned repository to {version_dir}")

# SET UP VENV

with section("Setting up virtual environment") as localprint:
    venv_path = os.path.join(version_dir, ".venv")
    assert os.system(f"{sys.executable} -m venv {venv_path}") == 0
    localprint(f"Created virtual environment at {venv_path}")

# INSTALL DEPENDENCIES

with section(f"Installing dependencies using {PACKAGE_MANAGER}"):
    common = f"cd {version_dir} && source .venv/bin/activate"
    if PACKAGE_MANAGER == "pip":
        assert os.system(f'{common} && pip install ".[dev]"') == 0
    elif PACKAGE_MANAGER == "pdm":
        assert os.system(f"{common} && pdm sync --with dev") == 0
    elif PACKAGE_MANAGER == "uv":
        assert os.system(f"{common} && uv sync --extra dev") == 0

# SET UP CONFIG FILE

with section("Setting up configuration file") as localprint:
    with open(os.path.join(version_dir, "config", "config.template.json"), "r") as f:
        config = json.load(f)

    config["general"]["system_identifier"] = SYSTEM_IDENTIFIER
    config["general"]["software_version"] = "0.0.0"

    GIT_PROVIDER: Optional[str] = None
    if "github" in GIT_REPOSITORY:
        GIT_PROVIDER = "github"
    elif "gitlab" in GIT_REPOSITORY:
        GIT_PROVIDER = "gitlab"
    else:
        localprint(
            format_warning(
                "Could not determine git provider from repository URL. "
                + "Not configuring updater."
            )
        )
        config["updater"] = None

    if GIT_PROVIDER is not None:
        clean_repo = GIT_REPOSITORY.replace("git@", "").replace("https://", "").replace(":", "/")
        if clean_repo.endswith(".git"):
            clean_repo = clean_repo[:-4]
        if clean_repo.count("/") != 2:
            localprint(
                format_warning(
                    f"Repository URL is not in a valid format (gitlab suburls "
                    + "some.gitlab.domain/org/user/repo are not supported, "
                    + "please only use some.gitlab.domain/user/repo)."
                )
            )
            GIT_PROVIDER = None
            config["updater"] = None
        else:
            config["updater"]["repository"] = "/".join(clean_repo.split("/")[1:])
            config["updater"]["provider"] = GIT_PROVIDER
            config["updater"]["provider_host"] = clean_repo.split("/")[0]

    if not CONFIGURE_BACKEND:
        localprint("Disabling backend configuration as per user request.")
        config["backend"] = None
    else:
        localprint(
            "Adding default backend configuration (for local mosquitto broker). "
            + "Update `config.backend` if you want to use a different broker."
        )

    config_path = os.path.join(version_dir, "config", "config.json")
    with open(os.path.join(version_dir, "config", "config.json"), "w") as f:
        json.dump(config, f, indent=4)
    localprint(f"Wrote configuration to {config_path}")


# RUNNING THE QUICK PYTESTS

with section("Running quick tests to verify the installation"):
    assert os.system(f"cd {version_dir} && source .venv/bin/activate && pytest tests -m quick") == 0

# DONE

# fmt: off
print(f"\n{BOLD_CODE}🎉 Setup complete! 🎉\n\nNext steps:{RESET_CODE}")
print(f'  > Navigate to "{version_dir}"" where the local dev environment has been set up.')
print(f'  > Continue with steps 6 of the "Getting Started" guide (https://tum-esm-ivy.netlify.app/getting-started)')
# fmt: on
