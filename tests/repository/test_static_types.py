import os
from src.constants import PROJECT_DIR


def _rm(path: str) -> None:
    os.system(f"rm -rf {os.path.join(PROJECT_DIR, path)}")


def test_static_types() -> None:
    _rm(".mypy_cache/3.*/src")
    _rm(".mypy_cache/3.*/tests")
    _rm(".mypy_cache/3.*/run.*")

    for path in ["src/", "tests/", "run.py"]:
        assert os.system(
            f"cd {PROJECT_DIR} && .venv/bin/python -m mypy {path}"
        ) == 0
