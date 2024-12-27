import pydantic
import pytest
import src


@pytest.mark.quick
def test_config_templates() -> None:
    """Test whether the config template is parseable using the
    config schema and the foreign config schema."""

    config = src.types.Config.load_template()
    assert (
        config.general.software_version == src.constants.VERSION
    ), "Version in config.template.json is not the same as in src/constants.py"

    src.types.ForeignConfig.model_validate_json(src.types.Config.load_template().model_dump_json())


@pytest.mark.quick
def test_config_validation() -> None:
    """Test whether the config validation fails as expected."""
    try:
        src.types.Config.model_validate({})
        raise AssertionError("Validation should have failed.")
    except pydantic.ValidationError:
        pass

    try:
        src.types.ForeignConfig.model_validate({})
        raise AssertionError("Validation should have failed.")
    except pydantic.ValidationError:
        pass
