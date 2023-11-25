import os
import time
from typing import Generator
import pytest
import itertools
import src
from src.utils.messaging_agent import MessagingAgent, ACTIVE_QUEUE_FILE
from src.types import DataMessageBody, LogMessageBody, ConfigMessageBody


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
    def clean() -> None:
        archive_file = MessagingAgent.get_message_archive_file()
        if os.path.isfile(archive_file):
            os.remove(archive_file)
        if os.path.isfile(ACTIVE_QUEUE_FILE):
            os.remove(ACTIVE_QUEUE_FILE)

    clean()
    yield
    clean()


@pytest.mark.ci
def test_messaging_agent(_remove_active_messages: None) -> None:
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
    assert len(agent.get_n_latest_messages(5)) == 3

    messages = agent.get_n_latest_messages(3)
    assert all(
        isinstance(message.message_body, DataMessageBody)
        for message in messages
    )
    assert len(messages) == 3
    timesamps = [message.timestamp for message in messages]
    assert timesamps[0] > timesamps[1] > timesamps[2]

    # remove one messages
    mid1 = messages[1].identifier
    agent.remove_messages([mid1])
    messages = agent.get_n_latest_messages(3)
    assert len(messages) == 2
    assert mid1 not in [message.identifier for message in messages]

    # remove all messages
    agent.remove_messages([message.identifier for message in messages])
    assert len(agent.get_n_latest_messages(3)) == 0

    # close SQLite connection
    agent.teardown()


@pytest.mark.ci
def test_different_message_types(
    _remove_active_messages: None,
    _provide_config_template: src.types.Config,
) -> None:
    agent = MessagingAgent()
    assert len(
        agent.get_n_latest_messages(20)
    ) == 0, "message queue is not empty"

    agent.add_message(DataMessageBody(message_body={"test": "test"}))
    time.sleep(0.01)
    assert len(agent.get_n_latest_messages(20)) == 1, "message was not added"

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

    for i, status in enumerate(["received", "accepted", "rejected", "startup"]):
        agent.add_message(
            # type: ignore
            ConfigMessageBody(status=status, config=_provide_config_template)
        )
        time.sleep(0.01)
        assert len(
            agent.get_n_latest_messages(20)
        ) == i + 7, "message was not added"

    mids = set([
        message.identifier for message in agent.get_n_latest_messages(20)
    ])
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
                sorted(timestamps, reverse=True)
            ), "messages are not sorted by timestamp"
