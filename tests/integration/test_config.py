import pytest
import src


@pytest.mark.integration
def test_config() -> None:
    config = src.types.Config.load()
    assert config.version == src.constants.VERSION, "Version in config.template.json is not the same as in src/constants.py"
