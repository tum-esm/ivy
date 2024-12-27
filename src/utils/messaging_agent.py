import json
from typing import Union, Annotated
import datetime
import os
import sqlite3
import filelock
import src

ACTIVE_QUEUE_FILE: Annotated[
    str,
    "The absolute path of the SQLite database that stores the active message queue "
    + "(`data/active-message-queue.sqlite3`)",
] = os.path.join(
    src.constants.DATA_DIR,
    "active-message-queue.sqlite3",
)

MESSAGE_ARCHIVE_DIR: Annotated[
    str,
    "The absolute path of the directory that stores the message archive " + "(`data/messages/`)",
] = os.path.join(
    src.constants.DATA_DIR,
    "messages",
)

MESSAGE_ARCHIVE_DIR_LOCK: Annotated[
    str,
    "The absolute path of the lock file that is used to lock the message archive "
    + "directory (`data/messages.lock`). This is used to make sure that only one "
    + "process can write to the message archive at a time.",
] = os.path.join(
    src.constants.DATA_DIR,
    "messages.lock",
)


class MessagingAgent:
    def __init__(self) -> None:
        """Create a new messaging agent.

        Sets up a connection to the SQLite database that stores the active
        message queue. Creates the SQL tables if they don't exist yet.
        """

        self.connection = sqlite3.connect(ACTIVE_QUEUE_FILE, check_same_thread=True)
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
        """Add a message to the active message queue and the message archive.
        Messages are written to the archive right away so they don't get lost
        if the backend process fails to send them out.

        Args:
            message_body: The message body.
        """

        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        message_body_string = message_body.model_dump_json()

        # write message to archive
        archive_file = MessagingAgent.get_message_archive_file()
        with self.message_archive_lock:
            if not os.path.isfile(archive_file):
                with open(archive_file, "w") as f:
                    f.write("timestamp,message_body\n")
            with open(archive_file, "a") as f:
                csv_message_body_string = message_body_string.replace('"', '""')
                f.write(f'{timestamp},"{csv_message_body_string}"\n')

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
        """Get the `n` latest messages from the active message queue.

        Args:
            n:                    The number of messages to get.
            excluded_message_ids: The message IDs to exclude from the result. Can be
                                  used to exclude messages that are already being processed
                                  but are still in the active message queue.

        Returns:
            A list of messages from the active queue.
        """

        with self.connection:
            mids_placeholder = ",".join(["?"] * len(excluded_message_ids))
            results = list(
                self.connection.execute(
                    f"""
                        SELECT internal_id, timestamp, message_body
                        FROM QUEUE
                        WHERE internal_id NOT IN ({mids_placeholder})
                        ORDER BY timestamp ASC
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
            )
            for result in results
        ]

    def remove_messages(self, message_ids: set[int] | list[int]) -> None:
        """Remove messages from the active message queue.

        Args:
            message_ids: The message IDs to be removed.
        """

        with self.connection:
            mids_placeholder = ",".join(["?"] * len(message_ids))
            self.connection.execute(
                f"""
                    DELETE FROM QUEUE
                    WHERE internal_id IN ({mids_placeholder});
                """,
                (*message_ids,),
            )

    @staticmethod
    def get_message_archive_file() -> str:
        """Get the file path of the message archive file for the current date."""

        return os.path.join(
            MESSAGE_ARCHIVE_DIR,
            datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d.csv"),
        )

    def teardown(self) -> None:
        """Close the connection to the active message queue database."""

        self.connection.close()

    @staticmethod
    def load_message_archive(date: datetime.date) -> list[src.types.MessageArchiveItem]:
        """Load the message archive for a specific date.

        Args:
            date: The date for which to load the message archive.

        Returns:
            A list of messages from the message archive.
        """

        path = os.path.join(MESSAGE_ARCHIVE_DIR, date.strftime("%Y-%m-%d.csv"))
        results: list[src.types.MessageArchiveItem] = []
        if os.path.isfile(path):
            with open(path, "r") as f:
                lines = f.read().strip(" \n").split("\n")[1:]

            for line in lines:
                line_parts = line.split(",")
                assert len(line_parts) >= 2
                timestamp = line_parts[0]
                message_body = ",".join(line_parts[1:]).replace('""', '"')[1:-1]
                results.append(
                    src.types.MessageArchiveItem(
                        timestamp=float(timestamp),
                        message_body=json.loads(message_body),
                    )
                )

        return results
