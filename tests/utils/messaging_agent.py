import datetime
import os
import time
from typing import Generator
import pytest
import itertools
import src
from src.utils.messaging_agent import MessagingAgent, ACTIVE_QUEUE_FILE
from src.types import DataMessageBody, LogMessageBody, ConfigMessageBody


def assert_not_midnight() -> None:
    now = datetime.datetime.utcnow()
    assert not (
        now.hour == 23 and now.minute == 59
    ), "this test can fail at midnight"
    assert not (
        now.hour == 0 and now.minute == 0
    ), "this test can fail at midnight"


@pytest.fixture(scope="function")
def _provide_config_template() -> Generator[src.types.Config, None, None]:
    path = os.path.join(
        src.constants.PROJECT_DIR,
        "config",
        "config.template.json",
    )
    with open(path, "r") as f:
        yield src.types.Config.load_from_string(f.read())


@pytest.fixture(scope="function")
def _remove_active_messages() -> Generator[None, None, None]:
    archive_file = MessagingAgent.get_message_archive_file()

    def clean() -> None:
        if os.path.isfile(archive_file):
            os.remove(archive_file)
        if os.path.isfile(ACTIVE_QUEUE_FILE):
            os.remove(ACTIVE_QUEUE_FILE)

    clean()
    yield
    clean()


@pytest.mark.ci
def test_simple_addition_and_deletion(_remove_active_messages: None) -> None:
    assert_not_midnight()
    archive_file = MessagingAgent.get_message_archive_file()

    agent = MessagingAgent()
    assert os.path.isfile(ACTIVE_QUEUE_FILE)
    assert not os.path.isfile(archive_file)
    assert len(agent.get_n_latest_messages(1)) == 0

    agent.add_message(DataMessageBody(message_body={"test": "test"}))
    assert os.path.isfile(archive_file)
    with open(archive_file, "r") as f:
        assert len(f.readlines()) == 2

    time.sleep(0.1)
    agent.add_message(DataMessageBody(message_body={"test": "test2"}))
    with open(archive_file, "r") as f:
        assert len(f.readlines()) == 3

    time.sleep(0.1)
    agent.add_message(DataMessageBody(message_body={"test": "test3"}))
    with open(archive_file, "r") as f:
        assert len(f.readlines()) == 4

    assert len(agent.get_n_latest_messages(1)) == 1
    assert len(agent.get_n_latest_messages(2)) == 2
    assert len(agent.get_n_latest_messages(3)) == 3
    assert len(agent.get_n_latest_messages(5)) == 3

    # remove one messages
    mids = [message.identifier for message in agent.get_n_latest_messages(3)]
    agent.remove_messages([mids[1]])
    new_mids = [
        message.identifier for message in agent.get_n_latest_messages(3)
    ]
    assert len(new_mids) == 2
    assert mids[1] not in new_mids

    # remove all messages
    agent.remove_messages(mids)
    assert len(agent.get_n_latest_messages(3)) == 0

    # close SQLite connection
    agent.teardown()


@pytest.mark.ci
def test_all_message_types(
    _remove_active_messages: None,
    _provide_config_template: src.types.Config,
) -> None:
    assert_not_midnight()
    agent = MessagingAgent()
    assert len(
        agent.get_n_latest_messages(20)
    ) == 0, "message queue is not empty"

    # add data message
    agent.add_message(DataMessageBody(message_body={"test": "test"}))
    time.sleep(0.01)
    assert len(agent.get_n_latest_messages(20)) == 1, "message was not added"

    # add log messages
    for i, level in enumerate([
        "DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"
    ]):
        agent.add_message(
            # type: ignore
            LogMessageBody(level=level, subject="test", body="test")
        )
        time.sleep(0.01)
        assert len(
            agent.get_n_latest_messages(20)
        ) == i + 2, "message was not added"

    # add config messages
    for i, status in enumerate(["received", "accepted", "rejected", "startup"]):
        agent.add_message(
            # type: ignore
            ConfigMessageBody(status=status, config=_provide_config_template)
        )
        time.sleep(0.01)
        assert len(
            agent.get_n_latest_messages(20)
        ) == i + 7, "message was not added"

    # check message queue
    mids = set([
        message.identifier for message in agent.get_n_latest_messages(20)
    ])
    assert len(mids) == 10, "message queue is not correct"

    # check filtering by message id
    for i in range(len(mids) + 1):
        for mids_subset in itertools.combinations(mids, i):
            messages = agent.get_n_latest_messages(
                20, excluded_message_ids=set(mids_subset)
            )
            filtered_mids = set([message.identifier for message in messages])
            assert set(mids_subset).isdisjoint(
                filtered_mids
            ), "filtering by message id is not correct"
            assert set(mids_subset).union(
                filtered_mids
            ) == mids, "filtering by message id is not correct"
            timestamps = [message.timestamp for message in messages]
            assert timestamps == list(
                sorted(timestamps)
            ), "messages are not sorted by timestamp"

    # check correctness of message types
    messages = agent.get_n_latest_messages(20)
    assert isinstance(messages[0].message_body, DataMessageBody)
    for i in range(1, 6):
        assert isinstance(messages[i].message_body, LogMessageBody)
    for i in range(6, 10):
        assert isinstance(messages[i].message_body, ConfigMessageBody)


@pytest.mark.ci
def test_message_archive_integrity(
    _remove_active_messages: None,
    _provide_config_template: src.types.Config,
) -> None:
    assert_not_midnight()
    agent = MessagingAgent()

    config1 = _provide_config_template
    config2 = config1.model_copy()
    config2.version = "0.0.0"

    message_bodies: list[
        DataMessageBody | LogMessageBody | ConfigMessageBody] = [
            DataMessageBody(message_body={"test": "test"}),
            LogMessageBody(level="INFO", subject="test", body="test"),
            ConfigMessageBody(status="received", config=config1),
            DataMessageBody(message_body={"test2": "test2"}),
            LogMessageBody(level="INFO", subject="test2", body="test2"),
            ConfigMessageBody(status="rejected", config=config2),
        ]

    # add messages
    for message_body in message_bodies:
        agent.add_message(message_body)
        time.sleep(0.01)
    assert len(agent.get_n_latest_messages(20)) == 6, "message queue is wrong"

    # check message archive
    archive_messages = MessagingAgent.load_message_archive(
        datetime.date.today()
    )
    assert len(archive_messages) == 6, "message archive is wrong"

    # check message archive integrity
    timestamps = [message.timestamp for message in archive_messages]
    assert timestamps == list(
        sorted(timestamps)
    ), "messages are not sorted by timestamp"
    for i in range(len(message_bodies)):
        assert message_bodies[i] == archive_messages[i].message_body
