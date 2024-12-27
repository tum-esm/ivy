import os
import shutil
import pytest
import tum_esm_utils
import src


@pytest.mark.order(4)
@pytest.mark.updater
def test_venv_creation() -> None:
    updater_config = src.types.UpdaterConfig(
        repository="tum-esm/utils",
        provider="github",
        provider_host="github.com",
        access_token=None,
        source_conflict_strategy="reuse",
    )
    version = tum_esm_utils.validators.Version("2.1.0")
    target_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
    venv_dir = os.path.join(target_dir, ".venv")

    src.utils.Updater.download_source_code(updater_config, version)

    assert os.path.isdir(target_dir), f"Target directory ({target_dir}) does not exist"
    assert not os.path.exists(venv_dir), f"venv directory ({venv_dir}) already exists"

    src.utils.Updater.install_dependencies(version, print)
    assert os.path.isdir(venv_dir), f"venv directory ({venv_dir}) does not exist"
    some_lib_dir = os.path.join(venv_dir, "lib/python3.10/site-packages/mypy")
    assert os.path.isdir(some_lib_dir), f"Library directory ({some_lib_dir}) does not exist"
    activate_script = os.path.join(venv_dir, "bin/activate")
    assert os.path.isfile(activate_script), f"Activate script ({activate_script}) does not exist"

    shutil.rmtree(target_dir)
