import os
import pytest
import src


def _rm(path: str) -> None:
    os.system(f"rm -rf {os.path.join(src.constants.PROJECT_DIR, path)}")


@pytest.mark.ci
def test_static_types() -> None:
    _rm(".mypy_cache/3.*/src")
    _rm(".mypy_cache/3.*/tests")
    _rm(".mypy_cache/3.*/run.*")
    _rm(".mypy_cache/3.*/docs/scripts")

    for path in ["src/", "tests/", "run.py", "docs/scripts/"]:
        assert os.system(
            f"cd {src.constants.PROJECT_DIR} && .venv/bin/python -m mypy {path}"
        ) == 0
