from __future__ import annotations
from typing import Callable, Optional
import json
import os
import sys
import shutil
import pydantic
import tum_esm_utils
import src
from .logger import Logger
from .messaging_agent import MessagingAgent


class Updater:
    """Implementation of the update capabilities of ivy: checks whether
    a new config is in a valid format, downloads new source code, creates
    virtual environments, installs dependencies, runs pytests, removes
    old virtual environments, and updates the cli pointer to the currently
    used version of the automation software."""

    instance: Optional[Updater] = None

    def __init__(
        self,
        config: src.types.Config,
    ) -> None:
        """Initialize an Updater instance.

        Args:
            config: The current config object
        """

        assert Updater.instance is None, "There should only be one Updater instance"
        Updater.instance = self
        self.config = config
        self.processed_config_revisions: set[int] = set()
        self.logger = Logger(config=config, origin="updater")
        self.messaging_agent = MessagingAgent()

    def perform_update(
        self,
        foreign_config: src.types.ForeignConfig,
    ) -> None:
        """Perform an update for a received config file.

        See the [documentation](/core-concepts/over-the-air-updates) for a detailed
        explanation of the update process.

        Args:
            foreign_config: The received foreign config object
        """

        if foreign_config.general.config_revision <= self.config.general.config_revision:
            self.logger.info(
                f"Received config has "
                + (
                    "lower revision number than"
                    if (
                        foreign_config.general.config_revision < self.config.general.config_revision
                    )
                    else "same revision number as"
                )
                + f" current config ({foreign_config.general.config_revision}) -> not updating"
            )
            return

        if foreign_config.general.config_revision in self.processed_config_revisions:
            self.logger.debug(
                f"The config with revision {foreign_config.general.config_revision} "
                + "has already been processed"
            )
            return

        self.processed_config_revisions.add(foreign_config.general.config_revision)
        self.logger.info(
            f"Processing new config with revision {foreign_config.general.config_revision}",
            details=f"config = {foreign_config.model_dump_json(indent=4)}",
        )

        if foreign_config.general.software_version == self.config.general.software_version:
            self.logger.info("Received config has same version")
            try:
                local_config = src.types.Config.load_from_string(foreign_config.model_dump_json())
                self.logger.info(f"Successfully parsed local config")
            except pydantic.ValidationError as e:
                self.logger.exception(e, label="Could not parse local config")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            if local_config == self.config:
                self.logger.info("Received config is equal to the currently used config")
                return
            self.logger.info("Received config is not equal to the currently used config.")

            self.logger.debug("Dumping config file")
            try:
                local_config.dump()
                self.logger.debug("Successfully dumped config file")
            except Exception as e:
                self.logger.exception(e, "Could not dump config file")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=local_config)
                )
                return

            self.messaging_agent.add_message(
                src.types.ConfigMessageBody(status="accepted", config=local_config)
            )
            self.logger.debug("Exiting mainloop so that it can be restarted with the new config")
            exit(0)
        else:
            self.logger.info(
                f"Received config has different version ({foreign_config.general.software_version})"
            )
            updater_config = self.config.updater
            if updater_config is None:
                self.logger.error(
                    "Received config has different version but no updater config is present"
                )
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            # Download source code

            self.logger.debug(f"Downloading new source code")
            try:
                Updater.download_source_code(
                    updater_config, foreign_config.general.software_version
                )
                self.logger.debug(f"Successfully downloaded source code")
            except Exception as e:
                self.logger.exception(e, "Could not download source code")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            # Install dependencies

            self.logger.debug("Installing dependencies")
            try:
                Updater.install_dependencies(
                    foreign_config.general.software_version, self.logger.debug
                )
                self.logger.debug("Successfully installed dependencies")
            except Exception as e:
                self.logger.exception(e, "Could not install dependencies")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            # Write new config file to destination

            self.logger.debug("Dumping config file")
            try:
                foreign_config.dump()
                self.logger.debug("Successfully dumped config file")
            except Exception as e:
                self.logger.exception(e, "Could not dump config file")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            # Run tests on new version

            self.logger.debug("Running pytests")
            try:
                self.run_pytests(foreign_config.general.software_version)
                self.logger.debug("Successfully ran pytests")
            except Exception as e:
                self.logger.exception(e, "Running pytests failed")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            # Update cli pointer

            self.logger.debug("Updating cli pointer")
            try:
                self.update_cli_pointer(foreign_config.general.software_version)
                self.logger.debug("Successfully updated cli pointer")
            except Exception as e:
                self.logger.exception(e, "Could not update cli pointer")
                self.messaging_agent.add_message(
                    src.types.ConfigMessageBody(status="rejected", config=foreign_config)
                )
                return

            # Quit once update is successful

            self.messaging_agent.add_message(
                src.types.ConfigMessageBody(status="accepted", config=foreign_config)
            )
            self.logger.info(
                f"Successfully updated to version {foreign_config.general.software_version}, shutting down"
            )
            exit(0)

    @staticmethod
    def download_source_code(
        updater_config: src.types.UpdaterConfig,
        version: tum_esm_utils.validators.Version,
    ) -> None:
        """Download the source code of the new version to the version
        directory. This is currently only implemented for github and
        gitlab for private and public repositories. Feel free to request
        other providers in the issue tracker.

        This is a static method, so it can be tested independently.

        Args:
            updater_config: The updater config object
            version: The version of the source code to download
        """

        # TODO: support downloading arbitrary commit shas

        assert os.path.isdir(
            src.constants.IVY_ROOT_DIR
        ), f"IVY_ROOT_DIR ({src.constants.IVY_ROOT_DIR}) is not a directory"

        dst_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
        if os.path.isfile(dst_dir):
            raise FileExistsError(f"There should not be a file at {dst_dir}")
        if os.path.isdir(dst_dir):
            if updater_config.source_conflict_strategy == "overwrite":
                shutil.rmtree(dst_dir)

        if not os.path.isdir(dst_dir):
            repository_name = updater_config.repository.split("/")[-1]
            tarball_name = f"{repository_name}-{version.as_tag()}.tar.gz"
            dst_tar = os.path.join(src.constants.IVY_ROOT_DIR, tarball_name)

            if updater_config.provider == "github":
                header: str = '--header "Accept: application/vnd.github+json" --header "X-GitHub-Api-Version: 2022-11-28" '
                if updater_config.access_token is not None:
                    header += f'--header "Authorization: Bearer {updater_config.access_token}"'
                tum_esm_utils.shell.run_shell_command(
                    f"curl -L {header} https://api.{updater_config.provider_host}/repos/{updater_config.repository}/tarball/{version.as_tag()} --output {tarball_name}",
                    working_directory=src.constants.IVY_ROOT_DIR,
                )
            elif updater_config.provider == "gitlab":
                auth_param: str = ""
                if updater_config.access_token is not None:
                    auth_param = f"?private_token={updater_config.access_token}"
                repository_name = updater_config.repository.split("/")[-1]
                tum_esm_utils.shell.run_shell_command(
                    f"curl -L https://{updater_config.provider_host}/{updater_config.repository}/-/archive/{version.as_tag()}/{repository_name}-{version.as_tag()}.tar.gz{auth_param} --output {dst_tar}",
                    working_directory=src.constants.IVY_ROOT_DIR,
                )
            else:
                raise NotImplementedError(
                    f"Source code provider {updater_config.provider} not implemented"
                )

            name_of_directory_in_tarball = (
                tum_esm_utils.shell.run_shell_command(
                    f"tar -tf {tarball_name} | head -1",
                    working_directory=src.constants.IVY_ROOT_DIR,
                )
                .strip(" \n/")
                .replace("\n", " ")
            )
            if " " in name_of_directory_in_tarball:
                raise RuntimeError(
                    f"Found multiple directories/files in source code "
                    + f"tarball {name_of_directory_in_tarball.split(' ')}"
                )

            tum_esm_utils.shell.run_shell_command(
                f"tar -xf {tarball_name} && mv {name_of_directory_in_tarball} {version.as_identifier()}",
                working_directory=src.constants.IVY_ROOT_DIR,
            )
            os.remove(dst_tar)

    @staticmethod
    def install_dependencies(
        version: tum_esm_utils.validators.Version,
        log_progress: Callable[[str], None],
    ) -> None:
        """Create a virtual environment and install the dependencies in the
        version directory using PDM. It uses the `pdm sync` command to exactly
        create the desired environmont.

        Since the `pyproject.toml` file generated by PDM is complying with PEP
        standards, one could also use `pip install .`. However, we recommend
        using PDM for due to caching and dependency locking.

        This is a static method, so it can be tested independently.

        Args:
            version: The version of the source code to download
            log_progress: A function to log progress messages
        """

        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")

        venv_path = os.path.join(version_dir, ".venv")
        if os.path.isdir(venv_path):
            log_progress(f"Removing existing virtual environment at {venv_path}")
            shutil.rmtree(venv_path)

        log_progress(f"Creating virtual environment at {venv_path}")
        tum_esm_utils.shell.run_shell_command(
            f"python{sys.version_info.major}.{sys.version_info.minor} -m venv .venv",
            working_directory=version_dir,
        )

        log_progress(f"Installing dependencies using PDM")
        tum_esm_utils.shell.run_shell_command(
            f"source .venv/bin/activate && pdm sync --no-self",
            working_directory=version_dir,
        )

    def run_pytests(
        self,
        version: tum_esm_utils.validators.Version,
    ) -> None:
        """Run all pytests with the mark "version_change" in the version directory.

        Args:
            version: The version of the source code to be tested
        """

        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")
        tum_esm_utils.shell.run_shell_command(
            f'.venv/bin/python -m pytest -m "version_change" tests/',
            working_directory=version_dir,
        )

    def update_cli_pointer(
        self,
        to_version: tum_esm_utils.validators.Version,
    ) -> None:
        """Update the cli pointer to a new version.

        Args:
            to_version: The version to update the cli pointer to
        """

        venv_path = os.path.join(src.constants.IVY_ROOT_DIR, to_version.as_identifier(), ".venv")
        code_path = os.path.join(src.constants.IVY_ROOT_DIR, to_version.as_identifier(), "src")
        with open(f"{src.constants.IVY_ROOT_DIR}/{src.constants.NAME}-cli.sh", "w") as f:
            f.writelines(
                [
                    "#!/bin/bash",
                    "set -o errexit",
                    "",
                    f"{venv_path}/bin/python {code_path}/cli.py $*",
                ]
            )
        os.chmod(f"{src.constants.IVY_ROOT_DIR}/{src.constants.NAME}-cli.sh", 0o744)

    @staticmethod
    def remove_old_venvs(
        current_version: tum_esm_utils.validators.Version,
        log_progress: Callable[[str], None],
    ) -> None:
        """Remove all old virtual environments, besides the current one.

        Args:
            current_version: The current version of the software
            log_progress: A function to log progress
        """

        log_progress("Removing all unused .venvs")

        venvs_to_be_removed: list[str] = []
        for subdir in os.listdir(src.constants.IVY_ROOT_DIR):
            try:
                tum_esm_utils.validators.Version(subdir)
            except pydantic.ValidationError:
                continue
            if subdir == current_version.as_identifier():
                continue
            venv_path = os.path.join(src.constants.IVY_ROOT_DIR, subdir, ".venv")
            if os.path.isdir(venv_path):
                venvs_to_be_removed.append(venv_path)

        log_progress(
            f"found {len(venvs_to_be_removed)} old .venvs to be removed: {venvs_to_be_removed}"
        )
        for v in venvs_to_be_removed:
            shutil.rmtree(v)

        log_progress(f"successfully removed all old .venvs")
