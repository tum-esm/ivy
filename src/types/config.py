from __future__ import annotations
import os
import pydantic
import src


class Config(pydantic.BaseModel):
    version: str = pydantic.Field(..., pattern=src.constants.VERSION_REGEX)

    @staticmethod
    def load() -> Config:
        with open(
                os.path.join(src.constants.PROJECT_DIR, "config",
                             "config.json"), "r") as f:
            return Config.model_validate_json(f.read())

    @staticmethod
    def load_from_string(c: str) -> Config:
        return Config.model_validate_json(c)
