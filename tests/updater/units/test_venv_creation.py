import os
import shutil
import pytest
import tum_esm_utils
import src


@pytest.mark.skip
@pytest.mark.order(6)
@pytest.mark.updater
def test_venv_creation_and_destruction() -> None:
    updater_config = src.types.UpdaterConfig(
        repository="tum-esm/utils",
        provider="github",
        provider_host="github.com",
        access_token=None,
        source_conflict_strategy="reuse",
    )
    other_version = tum_esm_utils.validators.Version("2.5.0")
    version = tum_esm_utils.validators.Version("2.5.3")
    target_dir = os.path.join(src.constants.ROOT_DIR, version.as_identifier())
    venv_dir = os.path.join(target_dir, ".venv")

    src.utils.Updater.download_source_code(updater_config, version)

    assert os.path.isdir(target_dir), f"Target directory ({target_dir}) does not exist"
    assert not os.path.exists(venv_dir), f"venv directory ({venv_dir}) already exists"

    src.utils.Updater.install_dependencies(version)
    assert os.path.isdir(venv_dir), f"venv directory ({venv_dir}) does not exist"
    some_lib_dir = os.path.join(venv_dir, "lib/python3.10/site-packages/mypy")
    assert os.path.isdir(some_lib_dir), f"Library directory ({some_lib_dir}) does not exist"
    activate_script = os.path.join(venv_dir, "bin/activate")
    assert os.path.isfile(activate_script), f"Activate script ({activate_script}) does not exist"

    py_version = tum_esm_utils.shell.run_shell_command(f"{venv_dir}/bin/python --version")
    assert py_version.startswith("Python 3."), f"Unexpected Python version: {py_version}"

    logs: list[str] = []
    log = lambda msg: logs.append(msg)

    # test removing venvs but not the current one
    src.utils.Updater.remove_old_venvs(version, log)
    assert os.path.isdir(venv_dir), f"venv directory ({venv_dir}) does not exist"
    assert f"found 0 old .venvs to be removed" in "\n".join(logs), f"Unexpected logs: {logs}"
    logs.clear()

    # test removing venvs including the current one
    src.utils.Updater.remove_old_venvs(other_version, log)
    assert not os.path.isdir(venv_dir), f"venv directory ({venv_dir}) still exists"
    assert f"found 1 old .venvs to be removed" in "\n".join(logs), f"Unexpected logs: {logs}"
    logs.clear()

    shutil.rmtree(target_dir)
