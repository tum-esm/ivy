#!/bin/python3

from typing import Callable, Generator
import contextlib
import json
import os
import re
import shutil
import sys
import urllib.request

BOLD_CODE = "\033[1m"
GREEN_CODE = "\033[32m"
YELLOW_CODE = "\033[33m"
RED_CODE = "\033[31m"
GRAY_CODE = "\033[90m"
RESET_CODE = "\033[0m"


@contextlib.contextmanager
def section(label: str) -> Generator[Callable[[str], None], None, None]:
    print(f"{BOLD_CODE}{label}: Starting{RESET_CODE}{GRAY_CODE}")
    yield lambda message: print(f"{RESET_CODE}{message}{GRAY_CODE}")
    print(f"{RESET_CODE}{GREEN_CODE}{label}: Finished{RESET_CODE}")


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


if __name__ == "__main__":
    print("🚀 Starting Ivy Production Setup")

    with section("Loading environment variables") as localprint:
        config = {
            "project_name": get_required_env_var("IVY_PROJECT_NAME"),
            "git_repository": get_required_env_var("IVY_GIT_REPOSITORY"),
            "git_provider": get_required_env_var("IVY_GIT_PROVIDER"),
            "version": get_required_env_var("IVY_VERSION"),
            "system_identifier": get_required_env_var("IVY_SYSTEM_IDENTIFIER"),
            "config_filepath": get_required_env_var("IVY_CONFIG_FILEPATH"),
            "package_manager": get_required_env_var("IVY_PACKAGE_MANAGER"),
        }

        if not config["project_name"]:
            error("Project name cannot be empty")

        if not config["git_repository"].startswith("https://"):
            error("Git repository must start with 'https://'")

        if not config["git_provider"] in ["github", "gitlab"]:
            error("Git repository must be from either 'github' or 'gitlab'")

        if not (re.match(r"^\d+\.", config["version"]) or config["version"].startswith("/")):
            error("Version must either start with a number (e.g. '1.0.0') or be a an absolute path")

        if not re.match(r"^[a-z0-9-]+$", config["system_identifier"]):
            error("System identifier can only contain lowercase letters, numbers, and hyphens")

        if not os.path.exists(config["config_filepath"]):
            error(f"Config source file not found: {config['config_filepath']}")

        if not os.path.isfile(config["config_filepath"]):
            error(f"Config source must be a file, not a directory: {config['config_filepath']}")

        if config["package_manager"] not in ["pip", "pdm", "uv"]:
            error("Package manager must be one of: pip, pdm, uv")

        if sys.version_info.major != 3 or sys.version_info.minor < 10:
            error("Python version must be 3.10 or higher")

        localprint(f"config = {json.dumps(config, indent=4)}")

    with section("Setting up directories") as localprint:
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        project_dir = os.path.join(documents_dir, config["project_name"])
        version_dir: str
        if config["version"].startswith("/"):
            version_dir = "/tmp/thisdoesdefinitelyhopefullynotexist"
        else:
            version_dir = os.path.join(project_dir, config["version"])

        localprint(f"documents_dir = {documents_dir}")
        localprint(f"project_dir = {project_dir}")
        localprint(f"version_dir = {version_dir}")

        for path in [documents_dir, project_dir, version_dir]:
            if os.path.isfile(path):
                error(f"{path} is a file, not a directory. Please remove it.")
        if os.path.isdir(version_dir):
            error(
                f"{version_dir} already exists. Cannot setup again. Remove it if you want to run the setup again."
            )
        os.makedirs(project_dir, exist_ok=True)

    with section(f"Downloading code version {config['version']}") as localprint:
        if config["version"].startswith("/"):
            localprint(f"Skipping download of codebase in CI (code path is given at IVY_VERSION)")
            assert os.path.isdir(config["version"])
            with open(os.path.join(config["version"], "config", "config.template.json"), "r") as f:
                version = str(json.load(f)["general"]["software_version"])
            version_dir = os.path.join(project_dir, version)
            os.rename(config["version"], version_dir)
            config["version"] = version
        else:
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
            os.system(f"cd /tmp && tar -xzf {archive_path.split('/')[-1]}")
            os.rename(f"/tmp/{extracted_name}", version_dir)
            os.remove(archive_path)

    with section("Setting up virtual environment"):
        assert os.system(f"cd {version_dir} && {sys.executable} -m venv .venv") == 0

    with section(f"Installing dependencies with {config['package_manager']}"):
        common = f"cd {version_dir} && . .venv/bin/activate"
        if config["package_manager"] == "pip":
            assert os.system(f"{common} && pip install .") == 0
        elif config["package_manager"] == "pdm":
            assert os.system(f"{common} && pdm sync") == 0
        elif config["package_manager"] == "uv":
            assert os.system(f"{common} && uv sync") == 0

    with section("Copying configuration"):
        with open(config["config_filepath"], "r") as f:
            config_file = json.load(f)
        config_file["general"]["system_identifier"] = config["system_identifier"]
        with open(os.path.join(version_dir, "config", "config.json"), "w") as f:
            json.dump(config_file, f, indent=4)

    with section("Setting up CLI pointer"):
        cli_pointer_path = os.path.join(project_dir, f"{config['project_name']}-cli.sh")
        python_path = os.path.join(version_dir, ".venv", "bin", "python")
        cli_path = os.path.join(version_dir, "cli.py")
        with open(cli_pointer_path, "w") as f:
            f.write(f"#!/bin/bash\n\nset -o errexit\n\n{python_path} {cli_path} $*")
        os.chmod(cli_pointer_path, 0o755)

    print("🎉 Production setup complete! 🎉")
    print(f"\nYour DAS has been set up at: {version_dir}")
    print(f"CLI pointer: {cli_pointer_path}\n")

    cli_script_path = os.path.join(project_dir, f"{config['project_name']}-cli.sh")
    cron_line = f"* * * * * {cli_script_path} start"
    print(f"IMPORTANT: Please Add the following line to your crontab (run 'crontab -e'):")
    print(cron_line)
