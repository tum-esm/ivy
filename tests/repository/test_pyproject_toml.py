import os
import tomllib
import src

path = os.path.join(src.constants.PROJECT_DIR, "pyproject.toml")


def test_pyproject_toml() -> None:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    try:
        assert data["tool"]["poetry"]["name"] == src.constants.NAME
        assert data["tool"]["poetry"]["version"] == src.constants.VERSION
    except KeyError:
        raise KeyError(f"could not read {path}")
