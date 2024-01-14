from __future__ import annotations
from typing import Optional
import json
import os
import sys
import shutil
import pydantic
import src
from .logger import Logger
from .messaging_agent import MessagingAgent


class Updater:
    """Implementation of the update capabilities of the ivy seed: checks
    whether a new config is in a valid format, downloads new source code,
    creates virtual environments, installs dependencies, runs pytests,
    removes old virtual environments, and updates the cli pointer to the
    currently used version of the automation software."""

    instance: Optional[Updater] = None

    def __init__(self, config: src.types.Config) -> None:
        """Initialize an Updater instance.
        
        Args:
            config: The current config."""

        assert Updater.instance is None, "There should only be one Updater instance"
        Updater.instance = self
        self.config = config
        self.processed_config_revisions: set[int] = set()
        self.logger = Logger(config=config, origin="updater")
        self.messaging_agent = MessagingAgent()

    def perform_update(self, foreign_config: src.types.ForeignConfig) -> None:
        """Perform an update for a received config file.

        1. Check whether this config revision has already been processed.
        2. If version is equal to the current version:
            * Parse the received config file string using
                `types.Config.load_from_string`
            * If the received config is equal to the current
                config, do nothing
            * Otherwise, dump the received config to the config
                file path and exit with status code 0
        3. Otherwise:
            * Download the source code of the new version
            * Create a virtual environment
            * Install dependencies
            * Dump the received config to the config file path
            * Run the integration pytests
            * Update the cli pointer
            * Exit with status code 0
        
        If any of the steps above fails, log the error and return. The
        automation will continue with the current config. If the pytests
        of the software version to be updated make sure, that the software
        runs correctly, it is not possible to update to a new version, that
        does not work. 
        
        Args:
            config_file_string: The content of the config file to be processed.
                                 This is a string, which will be parsed using
                                 `types.ForeignConfig.load_from_string`. It should
                                 be a JSON object with at least the `version` field,
                                 everything else is optional."""

        if foreign_config.revision <= self.config.revision:
            self.logger.info(
                f"Received config has " + (
                    "lower revision number than" if
                    (foreign_config.revision < self.config.revision
                    ) else "same revision number as"
                ) +
                f" current config ({foreign_config.revision}) -> not updating"
            )
            return

        if foreign_config.revision in self.processed_config_revisions:
            self.logger.debug(
                f"The config with revision {foreign_config.revision} " +
                "has already been processed"
            )
            return
        else:
            self.processed_config_revisions.add(foreign_config.revision)
            self.logger.info(
                f"Processing new config with revision {foreign_config.revision}",
                details=f"config = {foreign_config.model_dump_json(indent=4)}"
            )

        if foreign_config.version == self.config.version:
            self.logger.info("Received config has same version number")
            try:
                local_config = src.types.Config.load_from_string(
                    foreign_config.model_dump_json()
                )
                self.logger.info(f"Successfully parsed local config")
            except pydantic.ValidationError as e:
                self.logger.exception(e, label="Could not parse local config")

            if local_config == self.config:
                self.logger.info(
                    "Received config is equal to the currently used config"
                )
                return
            self.logger.info(
                "Received config is not equal to the currently used config."
            )

            self.logger.debug("Dumping config file")
            try:
                local_config.dump()
                self.logger.debug("Successfully dumped config file")
            except Exception as e:
                self.logger.exception(e, "Could not dump config file")
                return

            self.logger.debug(
                "Exiting mainloop so that it can " +
                "be restarted with the new config"
            )
            exit(0)
        else:
            self.logger.info(
                f"Received config has different version number ({foreign_config.version})"
            )

            # Download source code

            self.logger.debug(f"Downloading new source code")
            try:
                self.download_source_code(foreign_config.version)
                self.logger.debug(f"Successfully downloaded source code")
            except Exception as e:
                self.logger.exception(e, "Could not download source code")
                return

            # Install dependencies

            self.logger.debug("Installing dependencies")
            try:
                self.install_dependencies(foreign_config.version)
                self.logger.debug("Successfully installed dependencies")
            except Exception as e:
                self.logger.exception(e, "Could not install dependencies")
                return

            # Write new config file to destination

            self.logger.debug("Dumping config file")
            try:
                foreign_config.dump()
                self.logger.debug("Successfully dumped config file")
            except Exception as e:
                self.logger.exception(e, "Could not dump config file")
                return

            # Run tests on new version

            self.logger.debug("Running pytests")
            try:
                self.run_pytests(foreign_config.version)
                self.logger.debug("Successfully ran pytests")
            except Exception as e:
                self.logger.exception(e, "Running pytests failed")
                return

            # Update cli pointer

            self.logger.debug("Updating cli pointer")
            try:
                self.update_cli_pointer(foreign_config.version)
                self.logger.debug("Successfully updated cli pointer")
            except Exception as e:
                self.logger.exception(e, "Could not update cli pointer")
                return

            # Quit once update is successful

            self.logger.info(
                f"Successfully updated to version {foreign_config.version}, shutting down"
            )
            exit(0)

    def download_source_code(self, version: str) -> None:
        """Download the source code of the new version to the version
        directory. This is currently only implemented for github and
        gitlab for private and public repositories. Feel free to request
        other providers in the issue tracker."""

        assert self.config.updater is not None

        dst_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if os.path.isfile(dst_dir):
            raise FileExistsError(f"There should not be a file at {dst_dir}")
        if os.path.isdir(dst_dir):
            if self.config.updater.source_conflict_strategy == "overwrite":
                shutil.rmtree(dst_dir)

        if not os.path.isdir(dst_dir):
            repository_name = self.config.updater.repository.split("/")[-1]
            tarball_name = f"{self.config.updater.repository}-v{version}.tar.gz"
            dst_tar = os.path.join(src.constants.IVY_ROOT_DIR, tarball_name)

            if self.config.updater.provider == "github":
                header: str = '--header "Accept: application/vnd.github+json" --header "X-GitHub-Api-Version: 2022-11-28" '
                if self.config.updater.access_token is not None:
                    header += f'--header "Authorization: Bearer {self.config.updater.access_token}"'
                src.utils.functions.run_shell_command(
                    f'curl -L {header} https://api.{self.config.updater.provider_host}/repos/{self.config.updater.repository}/tarball/v{version} --output {tarball_name}',
                    working_directory=src.constants.IVY_ROOT_DIR,
                )
            elif self.config.updater.provider == "gitlab":
                auth_param: str = ""
                if self.config.updater.access_token is not None:
                    auth_param = f"?private_token={self.config.updater.access_token}"
                repository_name = self.config.updater.repository.split("/")[-1]
                src.utils.functions.run_shell_command(
                    f"curl -L https://{self.config.updater.provider_host}/{self.config.updater.repository}/-/archive/example-tag/{repository_name}-v{version}.tar.gz{auth_param} --output {dst_tar}",
                    working_directory=src.constants.IVY_ROOT_DIR,
                )
            else:
                raise NotImplementedError(
                    f"Source code provider {self.config.updater.provider} not implemented"
                )

            name_of_directory_in_tarball = src.utils.functions.run_shell_command(
                f"tar -tf {tarball_name} | head -1",
                working_directory=src.constants.IVY_ROOT_DIR,
            ).strip(" \n/").replace("\n", " ")
            if " " not in name_of_directory_in_tarball:
                raise RuntimeError(
                    f"Found multiple directories/files in source code " +
                    f"tarball {name_of_directory_in_tarball.split(' ')}"
                )

            src.utils.functions.run_shell_command(
                f"tar -xf {tarball_name} && mv {name_of_directory_in_tarball} {version}",
                working_directory=src.constants.IVY_ROOT_DIR,
            )

    def install_dependencies(self, version: str) -> None:
        """Create a virtual environment and install the dependencies in
        the version directory using poetry."""

        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")

        venv_path = os.path.join(version_dir, ".venv")
        if os.path.isdir(venv_path):
            self.logger.debug(
                f"Removing existing virtual environment at {venv_path}"
            )
            shutil.rmtree(venv_path)

        self.logger.debug(f"Creating virtual environment at {venv_path}")
        src.utils.functions.run_shell_command(
            f"python{sys.version_info.major}.{sys.version_info.minor} -m venv .venv",
            working_directory=version_dir,
        )

        self.logger.debug(f"Installing dependencies using poetry")
        src.utils.functions.run_shell_command(
            f"source .venv/bin/activate && poetry install --no-root",
            working_directory=version_dir,
        )

    def run_pytests(self, version: str) -> None:
        """Run all pytests with the mark "version_change" in the version directory."""

        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")
        src.utils.functions.run_shell_command(
            f'.venv/bin/python -m pytest -m "version_change" tests/',
            working_directory=version_dir,
        )

    def update_cli_pointer(self, version: str) -> None:
        """Update the cli pointer to a new version"""

        venv_path = os.path.join(src.constants.IVY_ROOT_DIR, version, ".venv")
        code_path = os.path.join(src.constants.IVY_ROOT_DIR, version, "src")
        with open(
            f"{src.constants.IVY_ROOT_DIR}/{src.constants.NAME}-cli.sh", "w"
        ) as f:
            f.writelines([
                "#!/bin/bash",
                "set -o errexit",
                "",
                f"{venv_path}/bin/python {code_path}/cli/main.py $*",
            ])

    def remove_old_venvs(self) -> None:
        """Remove all old virtual environments, that are not currently in use."""

        self.logger.info("Removing all unused .venvs")

        venvs_to_be_removed: list[str] = []
        for version in os.listdir(src.constants.IVY_ROOT_DIR):
            if version == self.config.version:
                continue
            venv_path = os.path.join(
                src.constants.IVY_ROOT_DIR, version, ".venv"
            )
            if (
                src.utils.functions.string_is_valid_version(version) and
                os.path.isdir(venv_path)
            ):
                venvs_to_be_removed.append(venv_path)

        self.logger.debug(
            f"found {len(venvs_to_be_removed)} old .venvs to be removed",
            details=f"paths = {json.dumps(venvs_to_be_removed, indent=4)}",
        )
        for p in venvs_to_be_removed:
            shutil.rmtree(p)

        self.logger.debug(f"successfully removed all old .venvs")
