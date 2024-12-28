import os
import shutil
import pytest
import tum_esm_utils
import src


@pytest.mark.order(7)
@pytest.mark.updater
def test_pytest_verification() -> None:
    updater_config = src.types.UpdaterConfig(
        repository="tum-esm/utils",
        provider="github",
        provider_host="github.com",
        access_token=None,
        source_conflict_strategy="reuse",
    )
    version = tum_esm_utils.validators.Version("2.5.3")
    target_dir = os.path.join(src.constants.ROOT_DIR, version.as_identifier())

    src.utils.Updater.download_source_code(updater_config, version)
    src.utils.Updater.install_dependencies(
        version,
        installation_command="pdm sync --with=dev,all --no-self",
    )
    src.utils.Updater.run_pytests(version, pytest_marker="quick")

    shutil.rmtree(target_dir)
