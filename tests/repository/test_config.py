import json
import pytest
import src


@pytest.mark.ci
def test_config_template() -> None:
    """Test whether the config template is parseable"""
    config = src.types.Config.load_template()
    assert config.version == src.constants.VERSION, "Version in config.template.json is not the same as in src/constants.py"


@pytest.mark.ci
def test_foreign_config() -> None:
    """Test wether the config template which is a valid config can be parsed
    by the foreign config schema. I.e. all valid configs should also be valid
    foreign configs."""
    src.types.ForeignConfig.model_validate_json(
        src.types.Config.load_template().model_dump_json()
    )
