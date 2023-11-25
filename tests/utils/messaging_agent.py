import os
import time
from typing import Generator
import pytest
from src.utils.messaging_agent import MessagingAgent, ACTIVE_QUEUE_FILE, MESSAGE_ARCHIVE_DIR
from src.types import DataMessageBody, LogMessageBody, ConfigMessageBody


@pytest.fixture(scope="function")
def _remove_active_message_queue() -> Generator[None, None, None]:
    if os.path.isfile(ACTIVE_QUEUE_FILE):
        os.remove(ACTIVE_QUEUE_FILE)
    yield
    if os.path.isfile(ACTIVE_QUEUE_FILE):
        os.remove(ACTIVE_QUEUE_FILE)


@pytest.mark.ci
def test_messaging_agent(_remove_active_message_queue: None) -> None:
    agent = MessagingAgent()
    assert os.path.isfile(ACTIVE_QUEUE_FILE)
    assert len(agent.get_n_latest_messages(2)) == 0

    agent.add_message(DataMessageBody(message_body={"test": "test"}))
    time.sleep(0.1)
    agent.add_message(DataMessageBody(message_body={"test": "test2"}))
    time.sleep(0.1)
    agent.add_message(DataMessageBody(message_body={"test": "test3"}))

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

    # check whether filtering works
    mids = [message.identifier for message in messages]
    for excluded_mids in [
        [mids[0]],
        [mids[1]],
        [mids[2]],
        [mids[0], mids[1]],
        [mids[0], mids[2]],
        [mids[1], mids[2]],
        [mids[0], mids[1], mids[2]],
    ]:
        filtered_messages = agent.get_n_latest_messages(3, excluded_mids)
        # correct number of messages
        assert len(filtered_messages) == 3 - len(excluded_mids)
        # no excluded message ids
        assert all(
            message.identifier not in excluded_mids
            for message in filtered_messages
        )
        # unique message ids
        assert len(set(message.identifier for message in filtered_messages)
                  ) == len(filtered_messages)

    # check whether removing messages works
    agent.remove_messages([mids[1]])
    messages = agent.get_n_latest_messages(3)
    assert len(messages) == 2
    assert mids[1] not in [message.identifier for message in messages]

    agent.remove_messages(mids)
    assert len(agent.get_n_latest_messages(3)) == 0
