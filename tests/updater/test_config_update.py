import pytest

# TODO: Rename the two cases to "reconfiguration" and "version_change"


@pytest.mark.order(9)
@pytest.mark.updater
def test_reconfiguration() -> None:
    # TODO: test whether the update procedure correctly processes the received messages

    # The success of this test is determined by the logs and whether the
    # background process has stopped
    pass


@pytest.mark.order(9)
@pytest.mark.updater
def test_version_update() -> None:
    # TODO: test whether the update procedure correctly updates to a new version
    # only run this tests for a github repo

    # The success of this test is determined by where the ivy_cli.sh points to
    # and by the logs and whether the background process has stopped
    pass
