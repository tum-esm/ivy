from __future__ import annotations
import os
import pydantic
import src


class Config(pydantic.BaseModel):
    version: str = pydantic.Field(..., pattern=src.constants.VERSION_REGEX)

    @staticmethod
    def load() -> Config:
        path = os.path.join(src.constants.PROJECT_DIR, "config", "config.json")
        with open(path, "r") as f:
            return Config.model_validate_json(f.read())

    @staticmethod
    def load_from_string(c: str) -> Config:
        return Config.model_validate_json(c)
