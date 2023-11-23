import os
import src
from src.constants import PROJECT_DIR, VERSION


def test_config_template() -> None:
    path = os.path.join(PROJECT_DIR, "config", "config.template.json")
    with open(path, "r") as f:
        config = src.types.Config.load_from_string(f.read())
    assert config.version == VERSION, "Version in config.template.json is not the same as in src/constants.py"
