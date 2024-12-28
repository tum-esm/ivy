import os
import pytest
import tum_esm_utils
import src
import random


@pytest.mark.order(4)
@pytest.mark.updater
def test_cli_pointer_switching() -> None:
    cli_path = os.path.join(src.constants.ROOT_DIR, f"{src.constants.NAME}-cli.sh")
    assert not os.path.exists(cli_path)

    local_cli_file = os.path.join(src.constants.PROJECT_DIR, "cli.py")
    assert os.path.exists(local_cli_file), f"CLI entrypoint not found at {local_cli_file}"

    for _ in range(5):
        version = tum_esm_utils.validators.Version(
            f"{random.randint(0, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
        )
        target_dir = os.path.join(src.constants.ROOT_DIR, version.as_identifier())

        src.utils.Updater.update_cli_pointer(version)

        assert os.path.exists(cli_path)
        cli_file_content = tum_esm_utils.files.load_file(cli_path)
        assert (
            f"{target_dir}/.venv/bin/python {target_dir}/cli.py" in cli_file_content
        ), f"Unexpected CLI file content: {cli_file_content}"

    os.remove(cli_path)
