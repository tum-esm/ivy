import pytest
import src


@pytest.mark.ci
def test_api_reference_state() -> None:

    # credits to https://stackoverflow.com/a/545413/8255842
    checksum_before = src.utils.functions.run_shell_command(
        "find docs/pages -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum",
        working_directory=src.constants.PROJECT_DIR,
    )

    src.utils.functions.run_shell_command(
        ".venv/bin/python docs/scripts/export_api_reference.py && " +
        ".venv/bin/python docs/scripts/export_config_schema.py",
        working_directory=src.constants.PROJECT_DIR,
    )

    checksum_after = src.utils.functions.run_shell_command(
        "find docs/pages -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum",
        working_directory=src.constants.PROJECT_DIR,
    )

    assert checksum_before == checksum_after, "API reference is out of sync"
