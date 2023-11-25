import os
import sys
from typing import Generator
import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_DIR)
import src


@pytest.fixture(scope="function")
def restore_production_files() -> Generator[None, None, None]:
    """This function will store all production files into temporary files
    so that they are not modified by any tests. After the test is done,
    the files will be restored to their original state.
    
    I.e., the file `config/config.json` will be temporarily saved in
    `config/config.json.tmp`, so is the active message queue file and
    today's message archive file."""

    config_file = os.path.join(
        src.constants.PROJECT_DIR, "config", "config.json"
    )
    message_archive_file = src.utils.MessagingAgent.get_message_archive_file()
    message_database_file = src.utils.messaging_agent.ACTIVE_QUEUE_FILE

    tmp_config_file = config_file + ".tmp"
    tmp_message_archive_file = message_archive_file + ".tmp"
    tmp_message_database_file = message_database_file + ".tmp"

    assert not os.path.isfile(tmp_config_file)
    assert not os.path.isfile(tmp_message_archive_file)
    assert not os.path.isfile(tmp_message_database_file)

    if os.path.isfile(config_file):
        os.rename(config_file, tmp_config_file)
    if os.path.isfile(message_archive_file):
        os.rename(message_archive_file, tmp_message_archive_file)
    if os.path.isfile(message_database_file):
        os.rename(message_database_file, tmp_message_database_file)

    yield

    if os.path.isfile(tmp_config_file):
        os.rename(tmp_config_file, config_file)
    if os.path.isfile(tmp_message_archive_file):
        os.rename(tmp_message_archive_file, message_archive_file)
    if os.path.isfile(tmp_message_database_file):
        os.rename(tmp_message_database_file, message_database_file)
