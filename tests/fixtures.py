import datetime
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
    today's message archive file.
    
    It also acquires a mainlock so that the automation cannot run while
    the test is running and vice versa."""

    with src.utils.functions.with_automation_lock():
        utcnow = datetime.datetime.utcnow()
        assert not (
            utcnow.hour == 23 and utcnow.minute == 59
        ), "this test can fail at midnight"
        assert not (
            utcnow.hour == 0 and utcnow.minute == 0
        ), "this test can fail at midnight"

        config_file = os.path.join(
            src.constants.PROJECT_DIR, "config", "config.json"
        )
        log_file = os.path.join(
            src.utils.logger.LOGS_ARCHIVE_DIR, utcnow.strftime("%Y-%m-%d.log")
        )
        message_archive_file = src.utils.MessagingAgent.get_message_archive_file(
        )
        message_database_file = src.utils.messaging_agent.ACTIVE_QUEUE_FILE

        tmp_config_file = config_file + ".tmp"
        tmp_log_file = log_file + ".tmp"
        tmp_message_archive_file = message_archive_file + ".tmp"
        tmp_message_database_file = message_database_file + ".tmp"

        assert not os.path.isfile(tmp_config_file)
        assert not os.path.isfile(tmp_log_file)
        assert not os.path.isfile(tmp_message_archive_file)
        assert not os.path.isfile(tmp_message_database_file)

        if os.path.isfile(config_file):
            os.rename(config_file, tmp_config_file)
        if os.path.isfile(log_file):
            os.rename(log_file, tmp_log_file)
        if os.path.isfile(message_archive_file):
            os.rename(message_archive_file, tmp_message_archive_file)
        if os.path.isfile(message_database_file):
            os.rename(message_database_file, tmp_message_database_file)

        yield

        if os.path.isfile(tmp_config_file):
            os.rename(tmp_config_file, config_file)
        if os.path.isfile(tmp_log_file):
            os.rename(tmp_log_file, log_file)
        if os.path.isfile(tmp_message_archive_file):
            os.rename(tmp_message_archive_file, message_archive_file)
        if os.path.isfile(tmp_message_database_file):
            os.rename(tmp_message_database_file, message_database_file)
