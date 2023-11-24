from typing import Callable
import os
import shutil
import sys
import pydantic
import src


class Updater:
    def __init__(
        self,
        config: src.types.Config,
        distribute_new_config: Callable[[src.types.Config], None],
    ) -> None:
        self.config = config
        self.distribute_new_config = distribute_new_config

    def perform_update(self, config_file_content: str) -> None:
        try:
            foreign_config = src.types.ForeignConfig.load_from_string(
                config_file_content
            )
        except pydantic.ValidationError as e:
            print(f"Could not parse config: {e}")

        if foreign_config.version == self.config.version:
            try:
                local_config = src.types.Config.load_from_string(
                    config_file_content
                )
            except pydantic.ValidationError as e:
                print(f"Could not parse config: {e}")

            if local_config == self.config:
                print("Received config is equal to the currently used config")
                return
            else:
                print(
                    "Received same config version number, only changing config"
                )
                self.config = local_config
                self.distribute_new_config(local_config)

    def download_source_code(self, version: str) -> None:
        assert self.config.updater is not None

        dst_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if os.path.isfile(dst_dir):
            raise FileExistsError(f"There should not be a file at {dst_dir}")
        if os.path.isdir(dst_dir):
            if self.config.updater.source_conflict_strategy == "overwrite":
                shutil.rmtree(dst_dir)

        if not os.path.isdir(dst_dir):
            tarball_name = f"{repository_name}-v{version}.tar.gz"
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
        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")

        venv_path = os.path.join(version_dir, ".venv")
        if os.path.isdir(venv_path):
            print(f"Removing existing virtual environment at {venv_path}")
            shutil.rmtree(venv_path)

        print(f"Creating virtual environment at {venv_path}")
        src.utils.functions.run_shell_command(
            f"python3.11 -m venv .venv",
            working_directory=version_dir,
        )

        print(f"Installing dependencies using poetry")
        src.utils.functions.run_shell_command(
            f"source .venv/bin/activate && poetry install --no-root",
            working_directory=version_dir,
        )

    def dump_config_file(self, version: str, config_file_content: str) -> None:
        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")

        with open(os.path.join(version_dir, "config", "config.json"), "w") as f:
            f.write(config_file_content)

    def run_pytests(self, version: str) -> None:
        version_dir = os.path.join(src.constants.IVY_ROOT_DIR, version)
        if not os.path.isdir(version_dir):
            raise RuntimeError(f"Directory {version_dir} does not exist")

        print(f"running all pytests")
        src.utils.functions.run_shell_command(
            f'.venv/bin/python -m pytest -m "version_change" tests/',
            working_directory=version_dir,
        )

    def remove_old_venvs(self) -> None:
        venvs_to_be_removed: list[str] = []
        for version in os.listdir(src.constants.IVY_ROOT_DIR):
            venv_path = os.path.join(
                src.constants.IVY_ROOT_DIR, version, ".venv"
            )
            if (
                src.utils.functions.string_is_valid_version(version) and
                os.path.isdir(venv_path) and
                (not (venv_path in sys.executable))
            ):
                venvs_to_be_removed.append(venv_path)

        print(f"found {len(venvs_to_be_removed)} old .venvs to be removed")

        for p in venvs_to_be_removed:
            print(f'removing old .venv at path "{p}"')
            shutil.rmtree(p)

        print(f"successfully removed all old .venvs")

    def _update_cli_pointer(self, version: str) -> None:
        """make the file pointing to the used cli to the new version's cli"""
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
