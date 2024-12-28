import os
import subprocess
import time
import pytest
import tum_esm_utils

import src
from ...fixtures import provide_test_config
from .utils import version_is_running, version_is_not_running


def _replace_file_content(filepath: str, old: str, new: str) -> None:
    with open(filepath, "r") as f:
        content = f.read()
    assert (
        content.count(old) == 1
    ), f"Expected exactly one occurence of {old} in {filepath}, got {content.count(old)}"
    with open(filepath, "w") as f:
        f.write(content.replace(old, new))


@pytest.mark.skip
@pytest.mark.order(9)
@pytest.mark.updater
def test_version_update(provide_test_config: src.types.Config) -> None:
    assert len(os.listdir(src.constants.ROOT_DIR)) == 0, "The ROOT_DIR is not empty"

    current_v = src.constants.VERSION
    from_v = tum_esm_utils.validators.Version("1.2.3")
    to_v = tum_esm_utils.validators.Version("4.5.6")

    from_dir = os.path.join(src.constants.ROOT_DIR, from_v.as_identifier())
    to_dir = os.path.join(src.constants.ROOT_DIR, to_v.as_identifier())

    # set up this codebase once under 1.2.3 and once under 4.5.6
    # the 1.2.3 version will be fully set up and running, and we
    # try to successfully update to 4.5.6. Then this proves that
    # the current codebase can update to a new version and that
    # the current codebase can be updated to.

    for v in [from_v, to_v]:
        target_dir = os.path.join(src.constants.ROOT_DIR, v.as_identifier())
        os.mkdir(target_dir)
        os.system(f"git archive --format=tar HEAD | tar -x -C {target_dir}")
        assert not os.path.exists(os.path.join(target_dir, ".git"))
        assert not os.path.exists(os.path.join(target_dir, ".venv"))
        _replace_file_content(
            os.path.join(target_dir, "pyproject.toml"),
            f'version = "{current_v.as_identifier()}"',
            f'version = "{v.as_identifier()}"',
        )
        _replace_file_content(
            os.path.join(target_dir, "src/constants.py"),
            f'tum_esm_utils.validators.Version("{current_v.as_identifier()}")',
            f'tum_esm_utils.validators.Version("{v.as_identifier()}")',
        )
        _replace_file_content(
            os.path.join(target_dir, "config/config.template.json"),
            f'"software_version": "{current_v.as_identifier()}"',
            f'"software_version": "{v.as_identifier()}"',
        )

    # besides version and revision number, the configs are identical
    # when the new version is already downloaded, it skips the download
    # if set to "reuse". Since the download functionality is already
    # tested in a separate unit test, we can always test this exact
    # codebase without having to tag or push commits to be tested.

    from_config = provide_test_config.model_copy(deep=True)
    from_config.general.software_version = from_v
    from_config.general.config_revision = provide_test_config.general.config_revision + 1
    from_config.general.system_identifier += "-version-update"
    assert from_config.backend is not None
    from_config.backend.mqtt_connection.client_id = from_config.general.system_identifier

    to_config = provide_test_config.model_copy(deep=True)
    to_config.general.software_version = to_v
    to_config.general.config_revision = from_config.general.config_revision + 2
    to_config.general.system_identifier += "-version-update"
    assert to_config.backend is not None
    to_config.backend.mqtt_connection.client_id = to_config.general.system_identifier

    # make 1.2.3 fully operational

    with open(os.path.join(from_dir, "config", "config.json"), "w") as f:
        f.write(from_config.model_dump_json(indent=4))
    src.utils.Updater.install_dependencies(from_v)
    src.utils.Updater.update_cli_pointer(from_v)
    out = tum_esm_utils.shell.run_shell_command(
        f"{src.constants.ROOT_DIR}/ivy-cli.sh info"
    ).replace("/private/tmp/", "/tmp/")
    assert f"Source code: {from_dir}" in out, f"CLI command had unexpected output: {out}"

    # start the 1.2.3 version

    env = {**os.environ.copy()}
    del env["IVY_DATA_DIR"]

    subprocess.run(f"nohup {src.constants.ROOT_DIR}/ivy-cli.sh start &", shell=True, env=env)
    time.sleep(5)
    assert version_is_running(from_v), "The 1.2.3 version is not running correctly"
    time.sleep(10)
    assert version_is_running(from_v), "The 1.2.3 version is not running correctly"

    # publish the same config -> no update

    src.utils.functions.publish_mqtt_message(
        topic=f"configurations/{from_config.general.system_identifier}",
        message={
            "config": from_config.model_dump(),
            "revision": from_config.general.config_revision,
        },
    )

    time.sleep(15)
    assert version_is_running(
        from_v,
        expected_log_lines=[
            f"Received config has same revision number as current config ({from_config.general.config_revision}) -> not updating"
        ],
    ), "The 1.2.3 version is not running correctly"

    # publish the new config -> update

    src.utils.functions.publish_mqtt_message(
        topic=f"configurations/{from_config.general.system_identifier}",
        message={
            "config": to_config.model_dump(),
            "revision": to_config.general.config_revision,
        },
    )
    tum_esm_utils.timing.wait_for_condition(
        is_successful=lambda: version_is_not_running(from_v),
        timeout_message="The 1.2.3 version did not stop within 180 seconds",
        timeout_seconds=180,
        check_interval_seconds=5,
    )

    # check whether the update was successful

    assert version_is_not_running(
        from_v,
        expected_log_lines=[
            f"Processing new config with revision {to_config.general.config_revision}",
            f"Received config has different version ({to_config.general.software_version.as_identifier()})",
            "Downloading new source code",
            "Successfully downloaded source code",
            f"Directory {to_dir} already exists, skipping download",
            "Installing dependencies",
            "Successfully installed dependencies",
            "Dumping config file",
            "Successfully dumped config file",
            "Running pytests",
            "Successfully ran pytests",
            "Updating cli pointer",
            "Successfully updated cli pointer",
            f"Successfully updated to version {to_v.as_identifier()}, shutting down",
            "finished teardown of the main loop",
        ],
    )

    # check whether CLI points to new version

    out = tum_esm_utils.shell.run_shell_command(
        f"{src.constants.ROOT_DIR}/ivy-cli.sh info"
    ).replace("/private/tmp/", "/tmp/")
    assert f"Source code: {to_dir}" in out, f"CLI command had unexpected output: {out}"

    # start the 4.5.6 version

    subprocess.run(f"nohup {src.constants.ROOT_DIR}/ivy-cli.sh start &", shell=True, env=env)
    time.sleep(5)
    assert version_is_running(to_v), "The 4.5.6 version is not running correctly"
    time.sleep(10)
    assert version_is_running(to_v), "The 4.5.6 version is not running correctly"
