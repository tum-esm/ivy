import pytest

import src


@pytest.mark.integration
def test_connection_to_repository() -> None:
    config = src.types.Config.load()
    if config.backend is None:
        return

    # TODO
