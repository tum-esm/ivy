import pytest

# TODO: Rename the two cases to "reconfiguration" and "version_change"
# TODO: Before the test, set this up inside a Docker container
# TODO: Maybe set up a local MQTT broker for this test
# TODO: During this test, point src.constants.IVY_ROOT_DIR to a directory inside /tmp


@pytest.mark.order(8)
@pytest.mark.updater
def test_remote_config_receiving() -> None:
    # TODO: test whether messages sent to the broker are received by the backend and correctly put into the messaging queue
    # TODO: test this using a few invalid and a few valid messages
    pass


@pytest.mark.order(8)
@pytest.mark.updater
def test_reconfiguration() -> None:
    # TODO: test whether the update procedure correctly processes the received messages

    # The success of this test is determined by the logs and whether the
    # background process has stopped
    pass


@pytest.mark.order(8)
@pytest.mark.updater
def test_version_update() -> None:
    # TODO: test whether the update procedure correctly updates to a new version
    # only run this tests for a github repo

    # The success of this test is determined by where the ivy_cli.sh points to
    # and by the logs and whether the background process has stopped
    pass
