import os
import shutil
import pytest
import tum_esm_utils
import src


def _run(
    updater_config: src.types.UpdaterConfig,
    version: tum_esm_utils.validators.Version,
) -> None:
    target_dir = os.path.join(src.constants.IVY_ROOT_DIR, version.as_identifier())
    assert os.path.isdir(
        src.constants.IVY_ROOT_DIR
    ), f"IVY_ROOT_DIR ({src.constants.IVY_ROOT_DIR}) does not exist"
    assert not os.path.exists(target_dir), f"Target directory ({target_dir}) already exists"

    # download source code
    src.utils.Updater.download_source_code(updater_config, version)

    assert os.path.isdir(target_dir), f"Target directory ({target_dir}) does not exist"
    files = os.listdir(src.constants.IVY_ROOT_DIR)
    assert len(files) == 1, f"Unexpected files: {files}"
    shutil.rmtree(target_dir)


@pytest.mark.order(5)
@pytest.mark.updater
def test_github_code_download() -> None:
    _run(
        src.types.UpdaterConfig(
            repository="tum-esm/utils",
            provider="github",
            provider_host="github.com",
            access_token=None,
            source_conflict_strategy="reuse",
        ),
        tum_esm_utils.validators.Version("2.5.3"),
    )


@pytest.mark.order(5)
@pytest.mark.updater
def test_gitlab_code_download() -> None:
    _run(
        src.types.UpdaterConfig(
            repository="coccon-kit/proffastpylot",
            provider="gitlab",
            provider_host="gitlab.eudat.eu",
            access_token=None,
            source_conflict_strategy="reuse",
        ),
        tum_esm_utils.validators.Version("1.3.2"),
    )
