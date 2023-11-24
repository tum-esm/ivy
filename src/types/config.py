from __future__ import annotations
import os
from typing import Literal, Optional
import pydantic
import src


class UpdaterConfig(pydantic.BaseModel):
    repository: str = pydantic.Field(
        ..., pattern=r"[a-zA-Z0-9-]+/[a-zA-Z0-9-]+"
    )
    provider: Literal["github", "gitlab"] = pydantic.Field(...)
    provider_host: str = pydantic.Field(..., min_length=3)
    access_token: Optional[str] = pydantic.Field(
        None, min_length=3, max_length=256
    )
    source_conflict_strategy: Literal["overwrite",
                                      "reuse"] = pydantic.Field("reuse")


class Config(pydantic.BaseModel):
    """Schema of the config file for this version of the software.
    
    A rendered API reference can be found in the documentation at TODO."""

    model_config = pydantic.ConfigDict(extra="forbid")
    version: str = pydantic.Field(..., pattern=src.constants.VERSION_REGEX)
    updater: Optional[UpdaterConfig] = pydantic.Field(None)

    @staticmethod
    def load() -> Config:
        """Load the config file from the path `project_dir/config/config.json`"""

        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.json")
        with open(path, "r") as f:
            return Config.model_validate_json(f.read())

    @staticmethod
    def load_from_string(c: str) -> Config:
        """Load the object from a string"""

        return Config.model_validate_json(c)


class ForeignConfig(pydantic.BaseModel):
    """Schema of a foreign config file for any other version of the software
    to update to.
    
    A rendered API reference can be found in the documentation at TODO."""

    model_config = pydantic.ConfigDict(extra="allow")
    version: str = pydantic.Field(..., pattern=src.constants.VERSION_REGEX)

    @staticmethod
    def load_from_string(c: str) -> ForeignConfig:
        """Load the object from a string"""

        return ForeignConfig.model_validate_json(c)
