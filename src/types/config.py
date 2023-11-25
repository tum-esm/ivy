from __future__ import annotations
import os
from typing import Literal, Optional
import pydantic
import src


class LoggingVerbosityConfig(pydantic.BaseModel):
    """How verbose to log to the different data streams.
    
    For example, If the level is set to "WARNING", only warnings, errors
    and exceptions will be written to the respective data stream. If the
    level is set to "DEBUG", all logs will be written to the respective
    data stream.
    
    Importance: DEBUG > INFO > WARNING > ERROR > EXCEPTION
    
    If the level is set to None, no logs will be written to the respective
    data stream."""

    file_archive: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", None
    ] = pydantic.Field(
        default=...,
        description="The minimum log level for the file archive in `data/logs`"
    )
    console_prints: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION",
        None] = pydantic.Field(
            default=...,
            description="The minimum log level for the console prints"
        )
    message_sending: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION",
        None] = pydantic.Field(
            default=...,
            description="The minimum log level for the message sending"
        )


class UpdaterConfig(pydantic.BaseModel):
    repository: str = pydantic.Field(
        ...,
        pattern=r"[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
        description=
        "The repository in which this source code is hosted, i.e. 'orgname/reponame'"
    )
    provider: Literal["github", "gitlab"] = pydantic.Field(
        ..., description="You can suggest more providers in the issue tracker"
    )
    provider_host: str = pydantic.Field(
        ...,
        min_length=3,
        examples=["github.com", "gitlab.com", "gitlab.yourcompany.com"]
    )
    access_token: Optional[str] = pydantic.Field(
        None,
        min_length=3,
        max_length=256,
        description=
        "The access token to use for the provider. If the repository is public, this can be left empty.",
    )
    source_conflict_strategy: Literal["overwrite", "reuse"] = pydantic.Field(
        "reuse",
        description=
        "The strategy to follow, when upgrading to a new version and the source code already exists. 'reuse' will keep the existing source code but create a new venv. 'overwrite' will remove the existing code directory and create a new one. You can keep this at 'reuse' by default and if a version upgrade fails during the download phase, temporarily change this to 'overwrite' to force a redownload of the source code."
    )


class Config(pydantic.BaseModel):
    """Schema of the config file for this version of the software.
    
    A rendered API reference can be found in the documentation at TODO."""

    model_config = pydantic.ConfigDict(extra="forbid")
    version: str = pydantic.Field(
        ...,
        pattern=src.constants.VERSION_REGEX,
        description="The version of the software this config file is for",
        examples=[
            "0.1.0", "1.2.3", "0.4.0-alpha.1", "0.5.0-beta.12", "0.6.0-rc.123"
        ]
    )
    logging_verbosity: LoggingVerbosityConfig = pydantic.Field(default=...)
    updater: Optional[UpdaterConfig] = pydantic.Field(
        default=None,
        description="If this is not set, the updater will not be used."
    )

    @staticmethod
    def load() -> Config:
        """Load the config file from the path `project_dir/config/config.json`"""
        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.json")
        with open(path, "r") as f:
            return Config.model_validate_json(f.read())

    @staticmethod
    def load_template() -> Config:
        """Load the config file from the path `project_dir/config/config.template.json`"""
        path = os.path.join(
            src.constants.PROJECT_DIR, "config", "config.template.json"
        )
        with open(path, "r") as f:
            return Config.model_validate_json(f.read())

    def dump(self) -> None:
        """Dump the config file to the path `<ivy_root>/<version>/config/config.json`"""

        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.json")
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))

    @staticmethod
    def load_from_string(c: str) -> Config:
        """Load the object from a string"""

        return Config.model_validate_json(c)


class ForeignConfig(pydantic.BaseModel):
    """Schema of a foreign config file for any other version of the software
    to update to.
    
    A rendered API reference can be found in the documentation at TODO."""

    model_config = pydantic.ConfigDict(extra="allow")
    version: str = pydantic.Field(
        ...,
        pattern=src.constants.VERSION_REGEX,
        description="The version of the software this config file is for",
        examples=["0.1.0", "0.2.0"]
    )

    @staticmethod
    def load_from_string(c: str) -> ForeignConfig:
        """Load the object from a string"""

        return ForeignConfig.model_validate_json(c)

    def dump(self) -> None:
        """Dump the config file to the path `<ivy_root>/<version>/config/config.json`"""

        path = os.path.join(
            src.constants.IVY_ROOT_DIR, self.version, "config", "config.json"
        )
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))
