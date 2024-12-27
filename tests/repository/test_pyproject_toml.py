import os
import pydantic
import pytest
import tum_esm_utils
import src

# credits to https://hellocoding.de/blog/coding-language/python/tomllib-toml-lesen#fallback-fr-alte-versionen-von-python3
try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

path = os.path.join(src.constants.PROJECT_DIR, "pyproject.toml")


@pytest.mark.ci
def test_pyproject_toml() -> None:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    try:
        assert (
            data["project"]["name"] == src.constants.NAME
        ), "NAME in pyproject.toml should be the same as in src/constants.py"
        assert (
            tum_esm_utils.validators.Version(data["project"]["version"]) == src.constants.VERSION
        ), "VERSION in pyproject.toml should be the same as in src/constants.py"

        try:
            tum_esm_utils.validators.Version(src.constants.NAME)
            raise ValueError("should not be a valid version")
        except pydantic.ValidationError:
            pass

    except KeyError:
        raise KeyError(f"could not read {path}")
