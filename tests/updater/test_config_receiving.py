import pytest


@pytest.mark.order(8)
@pytest.mark.updater
def test_connection_to_test_broker() -> None:
    # TODO: test whether connection to broker works
    pass


@pytest.mark.order(8)
@pytest.mark.updater
def test_tenta_config_receiving() -> None:
    # TODO: test whether messages sent to the broker are received by the backend and correctly put into the messaging queue
    # TODO: test this using a few invalid and a few valid messages
    pass


@pytest.mark.order(8)
@pytest.mark.updater
def test_thingsboard_config_receiving() -> None:
    # TODO: test whether messages sent to the broker are received by the backend and correctly put into the messaging queue
    # TODO: test this using a few invalid and a few valid messages
    pass
