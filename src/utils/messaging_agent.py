import json
from typing import Union
import datetime
import os
import sqlite3
import filelock
import src

ACTIVE_QUEUE_FILE = os.path.join(
    src.constants.PROJECT_DIR,
    "data",
    "active-message-queue.sqlite3",
)
MESSAGE_ARCHIVE_DIR = os.path.join(
    src.constants.PROJECT_DIR,
    "data",
    "messages",
)
MESSAGE_ARCHIVE_DIR_LOCK = os.path.join(
    src.constants.PROJECT_DIR,
    "data",
    "messages.lock",
)


class MessagingAgent():
    def __init__(self) -> None:
        self.connection = sqlite3.connect(
            ACTIVE_QUEUE_FILE, check_same_thread=True
        )
        self.message_archive_lock = filelock.FileLock(
            MESSAGE_ARCHIVE_DIR_LOCK,
            timeout=5,
        )
        with self.connection:
            self.connection.execute(
                """
                    CREATE TABLE IF NOT EXISTS QUEUE (
                        internal_id INTEGER PRIMARY KEY,
                        timestamp DOUBLE NOT NULL,
                        message_body TEXT NOT NULL
                    );
                """
            )

    def add_message(
        self,
        message_body: Union[
            src.types.DataMessageBody,
            src.types.LogMessageBody,
            src.types.ConfigMessageBody,
        ],
    ) -> None:
        timestamp = datetime.datetime.utcnow().timestamp()
        message_body_string = message_body.model_dump_json()

        # write message to archive
        archive_file = MessagingAgent.get_message_archive_file()
        with self.message_archive_lock:
            if not os.path.isfile(archive_file):
                with open(archive_file, "w") as f:
                    f.write("timestamp,message_body\n")
            with open(archive_file, "a") as f:
                f.write(f'{timestamp},"{message_body_string}"\n')

        # add message to active message queue
        with self.connection:
            self.connection.execute(
                """
                    INSERT INTO QUEUE (timestamp, message_body)
                    VALUES (?, ?);
                """,
                (timestamp, message_body_string),
            )

    def get_n_latest_messages(
        self,
        n: int,
        excluded_message_ids: set[int] | list[int] = set(),
    ) -> list[src.types.MessageQueueItem]:
        with self.connection:
            mids_placeholder = ",".join(["?"] * len(excluded_message_ids))
            results = list(
                self.connection.execute(
                    f"""
                        SELECT internal_id, timestamp, message_body
                        FROM QUEUE
                        WHERE internal_id NOT IN ({mids_placeholder})
                        ORDER BY timestamp DESC
                        LIMIT ?;
                    """,
                    (*excluded_message_ids, n),
                ).fetchall()
            )
        return [
            src.types.MessageQueueItem(
                identifier=result[0],
                timestamp=result[1],
                message_body=json.loads(result[2]),
            ) for result in results
        ]

    def remove_messages(self, message_ids: set[int] | list[int]) -> None:
        with self.connection:
            mids_placeholder = ",".join(["?"] * len(message_ids))
            self.connection.execute(
                f"""
                    DELETE FROM QUEUE
                    WHERE internal_id IN ({mids_placeholder});
                """,
                (*message_ids, ),
            )

    @staticmethod
    def get_message_archive_file() -> str:
        return os.path.join(
            MESSAGE_ARCHIVE_DIR,
            datetime.datetime.utcnow().strftime("%Y-%m-%d.csv")
        )

    def teardown(self) -> None:
        self.connection.close()
