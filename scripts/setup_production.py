#!/bin/python3

from typing import Generator
import contextlib
import json
import os
import re
import shutil
import sys
import tarfile
import urllib.request

BOLD_CODE = "\033[1m"
GREEN_CODE = "\033[32m"
YELLOW_CODE = "\033[33m"
RED_CODE = "\033[31m"
GRAY_CODE = "\033[90m"
RESET_CODE = "\033[0m"


@contextlib.contextmanager
def section(label: str) -> Generator[None, None, None]:
    print(f"{BOLD_CODE}{label}: Starting{RESET_CODE}")
    print(GRAY_CODE)
    yield
    print(RESET_CODE)
    print(f"{GREEN_CODE}{label}: Finished{RESET_CODE}")


def error(message: str) -> None:
    print(f"{RED_CODE}ERROR: {message}{RESET_CODE}")
    sys.exit(1)


def get_required_env_var(var_name: str) -> str:
    """Get required environment variable or exit with error."""
    value = os.getenv(var_name)
    if value is None:
        error(f"Required environment variable {var_name} is not set")
    assert value is not None
    return value.strip()


def load_env_vars() -> dict[str, str]:
    with section("Loading environment variables"):
        env_vars = {
            "project_name": get_required_env_var("IVY_PROJECT_NAME"),
            "git_repository": get_required_env_var("IVY_GIT_REPOSITORY"),
            "git_provider": get_required_env_var("IVY_GIT_PROVIDER"),
            "version": get_required_env_var("IVY_VERSION"),
            "system_identifier": get_required_env_var("IVY_SYSTEM_IDENTIFIER"),
            "config_filepath": get_required_env_var("IVY_CONFIG_FILEPATH"),
            "package_manager": get_required_env_var("IVY_PACKAGE_MANAGER"),
        }

        if not env_vars["project_name"]:
            error("Project name cannot be empty")

        if not env_vars["git_repository"].startswith("https://"):
            error("Git repository must start with 'https://'")

        if not env_vars["git_provider"] in ["github", "gitlab"]:
            error("Git repository must be from either 'github' or 'gitlab'")

        if not env_vars["version"].startswith("v"):
            env_vars["version"] = f"v{env_vars['version']}"

        if not re.match(r"^[a-z0-9-]+$", env_vars["system_identifier"]):
            error("System identifier can only contain lowercase letters, numbers, and hyphens")

        if not os.path.exists(env_vars["config_filepath"]):
            error(f"Config source file not found: {env_vars['config_filepath']}")

        if not os.path.isfile(env_vars["config_filepath"]):
            error(f"Config source must be a file, not a directory: {env_vars['config_filepath']}")

        if env_vars["package_manager"] not in ["pip", "pdm", "uv"]:
            error("Package manager must be one of: pip, pdm, uv")

        if sys.version_info.major != 3 or sys.version_info.minor < 10:
            error("Python version must be 3.10 or higher")

        print(json.dumps(env_vars, indent=4))

    return env_vars


def setup_directories(config: dict[str, str]) -> tuple[str, str, str]:
    with section("Setting up directories"):
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        project_dir = os.path.join(documents_dir, config["project_name"])
        version_dir = os.path.join(project_dir, config["version"].lstrip("v"))
        for path in [documents_dir, project_dir, version_dir]:
            if os.path.isfile(path):
                error(f"{path} is a file, not a directory. Please remove it.")
        if os.path.isdir(version_dir):
            error(
                f"{version_dir} already exists. Cannot setup again. Remove it if you want to run the setup again."
            )
        os.makedirs(project_dir, exist_ok=True)
        return documents_dir, project_dir, version_dir


def download_and_codebase(config: dict[str, str], version_dir: str) -> None:
    with section(f"Downloading version {config['version']}"):
        git_repo = config["git_repository"]
        if git_repo.endswith(".git"):
            git_repo = git_repo[:-4]

        archive_path = f"/tmp/{config['project_name']}-{config['version']}.tar.gz"
        download_url: str
        extracted_name: str
        if config["git_provider"] == "github":
            download_url = f"{git_repo}/archive/refs/tags/{config['version']}.tar.gz"
            extracted_name = f"{config['project_name']}-{config['version'].lstrip('v')}"
        else:
            download_url = f"{git_repo}/-/archive/{config['version']}/{config['project_name']}-{config['version']}.tar.gz"
            extracted_name = f"{config['project_name']}-{config['version']}"

        if os.path.exists(archive_path):
            os.remove(archive_path)
        if os.path.exists(f"/tmp/{extracted_name}"):
            shutil.rmtree(f"/tmp/{extracted_name}")

        try:
            urllib.request.urlretrieve(download_url, archive_path)
        except Exception as e:
            error(f"Failed to download {download_url}: {e}")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall("/tmp")
        os.rename(f"/tmp/{extracted_name}", version_dir)
        os.remove(archive_path)


def setup_virtual_environment(config: dict[str, str], version_dir: str) -> None:
    with section("Setting up virtual environment"):
        assert os.system(f"cd {version_dir} && {sys.executable} -m venv .venv") == 0

        if config["package_manager"] == "pip":
            assert os.system(f"cd {version_dir} && source .venv/bin/activate && pip install .") == 0

        elif config["package_manager"] == "pdm":
            assert os.system(f"cd {version_dir} && source .venv/bin/activate && pdm sync") == 0

        elif config["package_manager"] == "uv":
            assert os.system(f"cd {version_dir} && source .venv/bin/activate && uv sync") == 0


def setup_configuration(config: dict[str, str], version_dir: str) -> None:
    with section("Copying configuration"):
        shutil.copyfile(
            config["config_filepath"], os.path.join(version_dir, "config", "config.json")
        )


def setup_cli_pointer(config: dict[str, str], project_dir: str, version_dir: str) -> None:
    with section("Setting up CLI pointer"):
        cli_script_path = os.path.join(project_dir, f"{config['project_name']}-cli.sh")
        python_path = os.path.join(version_dir, ".venv", "bin", "python")
        cli_path = os.path.join(version_dir, "cli.py")
        with open(cli_script_path, "w") as f:
            f.write(f"#!/bin/bash\n\nset -o errexit\n\n{python_path} {cli_path} $*")
        os.chmod(cli_script_path, 0o755)


if __name__ == "__main__":
    print("🚀 Starting Ivy Production Setup")

    env_vars = load_env_vars()
    documents_dir, project_dir, version_dir = setup_directories(env_vars)
    cli_pointer = os.path.join(project_dir, f"{env_vars['project_name']}-cli.sh")
    download_and_codebase(env_vars, version_dir)
    setup_virtual_environment(env_vars, version_dir)
    setup_configuration(env_vars, version_dir)
    setup_cli_pointer(env_vars, project_dir, version_dir)

    print("🎉 Production setup complete! 🎉")
    print(f"\nYour DAS has been set up at: {version_dir}")
    print(f"CLI pointer: {cli_pointer}")

    cli_script_path = os.path.join(project_dir, f"{env_vars['project_name']}-cli.sh")
    cron_line = f"* * * * * {cli_script_path} start"

    print(f"IMPORTANT: Please Add the following line to your crontab (run 'crontab -e'):")
    print(cron_line)
