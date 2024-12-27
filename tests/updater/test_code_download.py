import os
import shutil
import pytest
import tum_esm_utils
import src


@pytest.mark.order(4)
@pytest.mark.updater
def test_code_github_download() -> None:
    updater_config = src.types.UpdaterConfig(
        repository="tum-esm/utils",
        provider="github",
        provider_host="github.com",
        access_token=None,
        source_conflict_strategy="reuse",
    )
    version = tum_esm_utils.validators.Version("2.1.0")
    target_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
    assert os.path.isdir(
        src.constants.IVY_ROOT_DIR
    ), f"IVY_ROOT_DIR ({src.constants.IVY_ROOT_DIR}) does not exist"
    assert not os.path.exists(target_dir), f"Target directory ({target_dir}) already exists"
    if "1.3.2" in os.listdir(src.constants.IVY_ROOT_DIR):
        shutil.rmtree(os.path.join(src.constants.IVY_ROOT_DIR, "1.3.2"))

    # download source code
    src.utils.Updater.download_source_code(updater_config, version)

    assert os.path.isdir(target_dir), f"Target directory ({target_dir}) does not exist"
    files = os.listdir(src.constants.IVY_ROOT_DIR)
    assert len(files) == 1, f"Unexpected files: {files}"


@pytest.mark.order(4)
@pytest.mark.updater
def test_code_gitlab_download() -> None:
    updater_config = src.types.UpdaterConfig(
        repository="coccon-kit/proffastpylot",
        provider="gitlab",
        provider_host="gitlab.eudat.eu",
        access_token=None,
        source_conflict_strategy="reuse",
    )
    version = tum_esm_utils.validators.Version("1.3.2")
    target_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
    assert os.path.isdir(
        src.constants.IVY_ROOT_DIR
    ), f"IVY_ROOT_DIR ({src.constants.IVY_ROOT_DIR}) does not exist"
    if "2.1.0" in os.listdir(src.constants.IVY_ROOT_DIR):
        shutil.rmtree(os.path.join(src.constants.IVY_ROOT_DIR, "2.1.0"))

    assert not os.path.exists(target_dir), f"Target directory ({target_dir}) already exists"

    # download source code
    src.utils.Updater.download_source_code(updater_config, version)

    assert os.path.isdir(target_dir), f"Target directory ({target_dir}) does not exist"
    files = os.listdir(src.constants.IVY_ROOT_DIR)
    assert len(files) == 1, f"Unexpected files: {files}"
