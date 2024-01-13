import sys
import pytest
import src


def get_checksum() -> str:
    # credits to https://stackoverflow.com/a/545413/8255842
    return src.utils.functions.run_shell_command(
        "find docs/pages docs/components -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum",
        working_directory=src.constants.PROJECT_DIR,
    )


@pytest.mark.ci
def test_api_reference_state() -> None:
    checksum_before = get_checksum()
    src.utils.functions.run_shell_command(
        f"{sys.executable} docs/scripts/export_api_reference.py",
        working_directory=src.constants.PROJECT_DIR,
    )
    checksum_after = get_checksum()
    assert checksum_before == checksum_after, "API reference is out of sync"
