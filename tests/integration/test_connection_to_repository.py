import pytest
import tum_esm_utils
import src


@pytest.mark.integration
def test_connection_to_repository() -> None:
    config = src.types.Config.load()
    if config.updater is None:
        return

    headers: str

    if config.updater.provider == "github":
        headers = '--header "Accept: application/vnd.github+json" --header "X-GitHub-Api-Version: 2022-11-28"'
        if config.updater.access_token is not None:
            headers += f' --header "Authorization: Bearer {config.updater.access_token}"'
        try:
            tum_esm_utils.shell.run_shell_command(
                f"curl --fail -L {headers} https://api.{config.updater.provider_host}/repos/{config.updater.repository}/readme"
            )
        except Exception as e:
            raise Exception(f"Could not connect to repository: {e}")

    if config.updater.provider == "gitlab":
        headers = ""
        if config.updater.access_token is not None:
            headers += f'--header "PRIVATE-TOKEN: {config.updater.access_token}"'
        try:
            tum_esm_utils.shell.run_shell_command(
                f'curl -L --fail {headers} https://{config.updater.provider_host}/api/v4/projects/{config.updater.repository.replace("/", "%2F")}/repository/tags?search=v0.0.0'
            )
        except Exception as e:
            raise Exception(f"Could not connect to repository: {e}")
