import datetime
import os
import sys
from typing import Generator
import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_DIR)
import src

if not os.path.isdir(src.constants.IVY_ROOT_DIR):
    raise FileNotFoundError(f"The directory {src.constants.IVY_ROOT_DIR} does not exist")


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
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        assert not (
            (utcnow.hour == 23 and utcnow.minute == 59) or (utcnow.hour == 0 and utcnow.minute == 0)
        ), "this test is blocked at midnight (UTC) because it is writing to dated files, wait until 00:01"

        paths = [
            os.path.join(
                src.constants.PROJECT_DIR,
                "config",
                "config.json",
            ),
            os.path.join(src.utils.logger.LOGS_ARCHIVE_DIR, utcnow.strftime("%Y-%m-%d.log")),
            src.utils.MessagingAgent.get_message_archive_file(),
            src.utils.messaging_agent.ACTIVE_QUEUE_FILE,
        ]

        # move production files to temporary files
        for path in paths:
            tmp_path = path + ".tmp"
            assert not os.path.isfile(tmp_path), (
                f"the temporary file {tmp_path} already exists, " + "please delete it manually"
            )
            if os.path.isfile(path):
                os.rename(path, tmp_path)

        yield

        # restore production files
        for path in paths:
            tmp_path = path + ".tmp"
            if os.path.isfile(path):
                os.remove(path)
            if os.path.isfile(tmp_path):
                os.rename(tmp_path, path)
