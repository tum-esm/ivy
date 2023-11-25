import pytest
import src


@pytest.mark.ci
def test_config_template() -> None:
    config = src.types.Config.load_template()
    assert config.version == src.constants.VERSION, "Version in config.template.json is not the same as in src/constants.py"
