from __future__ import annotations
from typing import Literal, Optional
import tum_esm_utils
import os
import pydantic
import src


class _GeneralConfig(pydantic.BaseModel):
    config_revision: int = pydantic.Field(
        ...,
        ge=0,
        description=
        "The revision of this config file. This should be incremented when the config file is changed. It is used to tag messages with the settings that were active at the time of sending.",
    )
    software_version: tum_esm_utils.validators.Version = pydantic.Field(
        ...,
        description="The version of the software this config file is for.",
    )
    system_identifier: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=512,
        description=
        "The identifier of this system. If possible, it is convenient to use the hostname of the system.",
    )


class _LoggingVerbosityConfig(pydantic.BaseModel):
    """How verbose to log to the different data streams.
    
    For example, If the level is set to "WARNING", only warnings, errors
    and exceptions will be written to the respective data stream. If the
    level is set to "DEBUG", all logs will be written to the respective
    data stream.
    
    Importance: DEBUG > INFO > WARNING > ERROR > EXCEPTION
    
    If the level is set to None, no logs will be written to the respective
    data stream."""

    file_archive: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", None] = pydantic.Field(
            default=...,
            description="The minimum log level for the file archive in `data/logs`"
        )
    console_prints: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", None] = pydantic.Field(
            default=...,
            description="The minimum log level for the console prints",
        )
    message_sending: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", None] = pydantic.Field(
            default=..., description="The minimum log level for the message sending"
        )


class _UpdaterConfig(pydantic.BaseModel):
    repository: str = pydantic.Field(
        ...,
        pattern=r"[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
        description=
        "The repository in which this source code is hosted, i.e. `orgname/reponame`"
    )
    provider: Literal["github", "gitlab"] = pydantic.Field(
        ..., description="You can suggest more providers in the issue tracker"
    )
    provider_host: str = pydantic.Field(
        ...,
        min_length=3,
        examples=["github.com", "gitlab.com", "gitlab.yourcompany.com"],
        description="The host of the code provider."
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


class MQTTBrokerConfig(pydantic.BaseModel):
    host: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=512,
        description="The host to use for the MQTT connection"
    )
    port: int = pydantic.Field(
        ..., ge=1, le=65535, description="The port to use for the MQTT connection"
    )
    client_id: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=512,
        description=
        "The client ID to use for the MQTT connection. Not necessarily the same as the username."
    )
    username: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=512,
        description="The username to use for the MQTT connection."
    )
    password: str = pydantic.Field(
        ...,
        min_length=1,
        max_length=512,
        description="The password to use for the MQTT connection."
    )


class _BackendConfig(pydantic.BaseModel):
    provider: Literal["tenta", "thingsboard"] = pydantic.Field(
        ...,
        description=
        "The provider to use for the backend. The template ships with these two providers but is easily extendable to support other backends."
    )
    mqtt_connection: MQTTBrokerConfig = pydantic.Field(
        ...,
        description=
        "The MQTT broker to use for the backend. In future versions, one could add support for other protocols like `https_connection` or `lorawan_connection`."
    )
    max_parallel_messages: int = pydantic.Field(
        ...,
        ge=1,
        le=10000,
        description=
        "How many messages that are not published yet should be passed to the backend at once"
    )
    max_drain_time: int = pydantic.Field(
        ...,
        ge=10,
        le=7200,
        description=
        "When the mainloop wants to shut down (after a config change, or an update), how many seconds should the backend be allowed to continue sending out unsent messages."
    )


class _DummyProcedureConfig(pydantic.BaseModel):
    seconds_between_datapoints: int = pydantic.Field(
        ...,
        ge=1,
        le=7200,
        description=
        "How many seconds should be between each datapoint in the dummy procedure",
    )


class _SystemChecksConfig(pydantic.BaseModel):
    seconds_between_checks: int = pydantic.Field(
        ...,
        ge=1,
        le=7200,
        description="How many seconds should be between each run of the system checks",
    )


class Config(pydantic.BaseModel):
    """Schema of the config file for this version of the software.
    
    A rendered API reference can be found in the documentation."""

    model_config = pydantic.ConfigDict(extra="forbid")
    general: _GeneralConfig = pydantic.Field(...)
    logging_verbosity: _LoggingVerbosityConfig = pydantic.Field(...)
    updater: Optional[_UpdaterConfig] = pydantic.Field(
        default=None,
        description="If this is not set, the updater will not be used.",
    )
    backend: Optional[_BackendConfig] = pydantic.Field(
        default=None,
        description="If this is not set, the backend will not be used.",
    )
    dummy_procedure: _DummyProcedureConfig = pydantic.Field(
        default=...,
        description="Settings for the dummy procedure.",
    )
    system_checks: _SystemChecksConfig = pydantic.Field(
        default=...,
        description="Settings for the system checks procedure.",
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
        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.template.json")
        with open(path, "r") as f:
            return Config.model_validate_json(f.read())

    def dump(self) -> None:
        """Dump the config file to the path `<ivy_root>/<version>/config/config.json`"""

        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.json")
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))

    @staticmethod
    def load_from_string(c: str) -> Config:
        """Load the object from a string.
        
        Args:
            c: The string to load the object from.
        """

        return Config.model_validate_json(c)

    def to_foreign_config(self) -> ForeignConfig:
        """Convert the config to a `src.types.ForeignConfig` object."""

        return ForeignConfig.model_validate(self.model_dump())


class ForeignGeneralConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    config_revision: int = pydantic.Field(
        ...,
        ge=0,
        description=
        "The revision of this config file. This should be incremented when the config file is changed. It is used to tag messages with the settings that were active at the time of sending.",
    )
    software_version: tum_esm_utils.validators.Version = pydantic.Field(
        ...,
        description=
        "The version of the software this config file is for. The updater only works if this is set.",
        examples=[
            tum_esm_utils.validators.Version("0.1.0"),
            tum_esm_utils.validators.Version("0.2.0"),
        ]
    )


class ForeignConfig(pydantic.BaseModel):
    """Schema of a foreign config file for any other version of the software
    to update to. It probably has more fields than listed in the schema. This
    schema only includes the fields that are required in any new config to be
    accepted by the updater in this version of the software.
    
    A rendered API reference can be found in the documentation."""

    model_config = pydantic.ConfigDict(extra="allow")
    general: ForeignGeneralConfig = pydantic.Field(...)

    @staticmethod
    def load_from_string(c: str) -> ForeignConfig:
        """Load the object from a string.
        
        Args:
            c: The string to load the object from.
        """

        return ForeignConfig.model_validate_json(c)

    def dump(self) -> None:
        """Dump the config file to the path `<ivy_root>/<version>/config/config.json`"""

        path = os.path.join(
            src.constants.IVY_ROOT_DIR,
            self.general.software_version.as_identifier(),
            "config",
            "config.json",
        )
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))
