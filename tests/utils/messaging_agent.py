import os
from typing import Generator
import pytest
from src.utils.messaging_agent import MessagingAgent, ACTIVE_QUEUE_FILE, MESSAGE_ARCHIVE_DIR


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
