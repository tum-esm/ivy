import pytest
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
    # 2.1.0


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
    # v1.3.2
