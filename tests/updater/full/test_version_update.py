from typing import Any
import pytest
from ...fixtures import provide_test_config

# TODO: Rename the two cases to "reconfiguration" and "version_change"


@pytest.mark.order(9)
@pytest.mark.updater
def test_updating_to_this_version() -> None:
    # TODO: test whether the update procedure correctly updates to a new version
    # only run this tests for a github
    # TODO: this test is now kind of redundant, because the previous test already covers, whether it can fully start up.

    # The success of this test is determined by where the ivy_cli.sh points to
    # and by the logs and whether the background process has stopped
    pass


@pytest.mark.order(9)
@pytest.mark.updater
def test_updating_from_this_version() -> None:
    # TODO: test whether the update procedure correctly updates to a new version
    # only run this tests for a github repo

    # The success of this test is determined by where the ivy_cli.sh points to
    # and by the logs and whether the background process has stopped
    pass
