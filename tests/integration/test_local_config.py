import pytest
import src


@pytest.mark.order(3)
@pytest.mark.integration
def test_config() -> None:
    config = src.types.Config.load()
    assert (
        config.general.software_version == src.constants.VERSION
    ), "Version in config.template.json is not the same as in src/constants.py"
