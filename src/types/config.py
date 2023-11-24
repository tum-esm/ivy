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
    model_config = pydantic.ConfigDict(extra="forbid")
    version: str = pydantic.Field(..., pattern=src.constants.VERSION_REGEX)
    updater: Optional[UpdaterConfig] = pydantic.Field(None)

    @staticmethod
    def load() -> Config:
        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.json")
        with open(path, "r") as f:
            return Config.model_validate_json(f.read())

    @staticmethod
    def load_from_string(c: str) -> Config:
        return Config.model_validate_json(c)
