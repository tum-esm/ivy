import datetime
import os
import re
import subprocess
import time
import psutil
import pytest
import tum_esm_utils

import src
from ...fixtures import provide_test_config


def _version_is_running(version: tum_esm_utils.validators.Version) -> bool:
    current_logs = tum_esm_utils.files.load_file(
        os.path.join(
            src.constants.ROOT_DIR,
            version.as_identifier(),
            "data",
            "logs",
            datetime.datetime.now().strftime("%Y-%m-%d.log"),
        )
    )
    assert current_logs is not None
    print(f"--- current logs ---\n{current_logs}")
    pids = [
        int(p[1])
        for p in re.findall(r"- Starting (process|automation) with PID (\d+)\n", current_logs)
    ]
    print(pids)
    assert len(pids) == 4, f"there is not exactly 4 pids, got {len(pids)}"
    return all([psutil.pid_exists(pid) for pid in pids])


def _replace_file_content(filepath: str, old: str, new: str) -> None:
    with open(filepath, "r") as f:
        content = f.read()
    assert (
        content.count(old) == 1
    ), f"Expected exactly one occurence of {old} in {filepath}, got {content.count(old)}"
    with open(filepath, "w") as f:
        f.write(content.replace(old, new))


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
    from_config.backend.mqtt_connection.client_id = from_config.general.system_identifier

    to_config = provide_test_config.model_copy(deep=True)
    to_config.general.software_version = to_v
    to_config.general.config_revision = from_config.general.config_revision + 2
    to_config.general.system_identifier += "-version-update"
    to_config.backend.mqtt_connection.client_id = to_config.general.system_identifier

    # make 1.2.3 fully operational

    with open(os.path.join(from_dir, "config", "config.json"), "w") as f:
        f.write(from_config.model_dump_json(indent=4))
    src.utils.Updater.install_dependencies(from_v, print)
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
    assert _version_is_running(from_v), "The 1.2.3 version is not running correctly"
    time.sleep(10)
    assert _version_is_running(from_v), "The 1.2.3 version is not running correctly"

    # publish the same config -> no update

    src.utils.functions.publish_mqtt_message(
        topic=f"configurations/{from_config.general.system_identifier}",
        message={
            "config": from_config.model_dump(),
            "revision": from_config.general.config_revision,
        },
    )

    # TODO: check whether logs contain "same revision, no update"

    # publish the new config -> update

    src.utils.functions.publish_mqtt_message(
        topic=f"configurations/{from_config.general.system_identifier}",
        message={
            "config": to_config.model_dump(),
            "revision": to_config.general.config_revision,
        },
    )

    # check whether the update was successful

    # TODO: check whether logs contain "updating now"
    # TODO: check whether logs contain "download skipped"
    # TODO: check whether logs contain "install"
    # TODO: check whether logs contain "pytest"
    # TODO: check whether logs contain "switch cli pointer"
    # TODO: check whether logs contain "update successful exiting"
    # TODO: check whether logs contain "finished mainloop teardown"
    # TODO: check whether 1.2.3 has stopped
    # TODO: check whether cli points to 4.5.6

    # start the 4.5.6 version

    subprocess.run(f"nohup {src.constants.ROOT_DIR}/ivy-cli.sh start &", shell=True, env=env)
    time.sleep(5)
    assert _version_is_running(to_v), "The 4.5.6 version is not running correctly"
    time.sleep(10)
    assert _version_is_running(to_v), "The 4.5.6 version is not running correctly"
