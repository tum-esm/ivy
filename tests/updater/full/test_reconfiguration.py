import re
import shutil
import time
import pytest
import tum_esm_utils
import src
import os
from ...fixtures import provide_test_config
from .utils import version_is_running, version_is_not_running
# TODO: Rename the two cases to "reconfiguration" and "version_change"


@pytest.mark.order(9)
@pytest.mark.updater
def test_reconfiguration(provide_test_config: src.types.Config) -> None:
    # The success of this test is determined by the logs and whether the
    # background process has stopped

    assert len(os.listdir(src.constants.ROOT_DIR)) == 0, "The ROOT_DIR is not empty"
    target_dir = os.path.join(src.constants.ROOT_DIR, src.constants.VERSION.as_identifier())
    os.mkdir(target_dir)
    os.system(f"git archive --format=tar HEAD | tar -x -C {target_dir}")
    assert not os.path.exists(os.path.join(target_dir, ".git"))
    assert not os.path.exists(os.path.join(target_dir, ".venv"))

    # set up test environment
    config = provide_test_config
    config.backend.mqtt_connection.client_id = config.general.system_identifier + "-reconfiguration"  # type: ignore
    with open(os.path.join(target_dir, "config", "config.json"), "w") as f:
        f.write(provide_test_config.model_dump_json(indent=4))
    src.utils.Updater.install_dependencies(src.constants.VERSION, print)
    src.utils.Updater.update_cli_pointer(src.constants.VERSION)
    out = tum_esm_utils.shell.run_shell_command(
        f"{src.constants.ROOT_DIR}/ivy-cli.sh info"
    ).replace("/private/tmp/", "/tmp/")
    assert f"Source code: {target_dir}" in out, f"CLI command had unexpected output: {out}"

    os.system(f"{src.constants.ROOT_DIR}/ivy-cli.sh start")
    time.sleep(10)

    assert version_is_running(src.constants.VERSION)
    current_logs = src.utils.Logger.read_current_log_file()
    assert current_logs is not None
    for procedure_name in ["system-checks", "dummy-procedure"]:
        matches = re.findall(
            r"\s" + procedure_name + r"\s+\- DEBUG\s+\- sleeping for \d+(.\d{2})? seconds",
            current_logs,
        )
        assert (
            len(matches) >= 2
        ), f"Expected at least 2 iterations of procedure {procedure_name}, got {len(matches)}"

    # send a new configuration
    new_config = provide_test_config.model_copy(deep=True)
    new_config.general.config_revision += 1
    new_config.dummy_procedure.seconds_between_datapoints -= 1
    src.utils.functions.publish_mqtt_message(
        topic=f"configurations/{new_config.general.system_identifier}",
        message={
            "revision": new_config.general.config_revision,
            "configuration": new_config.model_dump(),
        },
    )

    time.sleep(20)

    assert version_is_not_running(
        src.constants.VERSION,
        expected_log_lines=[
            "Exiting mainloop so that it can be restarted with the new config",
            "Finished teardown of the main loop",
        ],
    )

    shutil.rmtree(target_dir)
