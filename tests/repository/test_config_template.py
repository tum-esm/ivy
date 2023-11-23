import os
import src


def test_config_template() -> None:
    path = os.path.join(
        src.constants.PROJECT_DIR,
        "config",
        "config.template.json",
    )
    with open(path, "r") as f:
        config = src.types.Config.load_from_string(f.read())
    assert (
        config.version == src.constants.VERSION,
        "Version in config.template.json is not the same as in src/constants.py"
    )
