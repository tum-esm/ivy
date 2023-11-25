import os
import sqlite3
import time
from typing import Union
import src

ACTIVE_QUEUE_FILE = os.path.join(
    src.constants.PROJECT_DIR,
    "data",
    "active-message-queue.sqlite3",
)


class MessagingAgent():
    def __init__(self) -> None:
        self.connection = sqlite3.connect(
            ACTIVE_QUEUE_FILE, check_same_thread=True
        )
        with self.connection:
            self.connection.execute(
                """
                    CREATE TABLE IF NOT EXISTS QUEUE (
                        internal_id INTEGER PRIMARY KEY,
                        timestamp INTEGER NOT NULL,
                        message_body INTEGER NOT NULL,
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
        with self.connection:
            self.connection.execute(
                """
                    INSERT INTO QUEUE (timestamp, message_body)
                    VALUES (?);
                """,
                (int(time.time()), message_body.model_dump_json()),
            )

    def get_n_latest_messages(
        self,
        n: int,
        excluded_message_ids: list[int] = []
    ) -> list[src.types.MessageQueueItem]:
        with self.connection:
            results = list(
                self.connection.execute(
                    """
                        SELECT internal_id, timestamp, message_body
                        FROM QUEUE
                        WHERE internal_id NOT IN (?)
                        ORDER BY timestamp DESC
                        LIMIT ?;
                    """,
                    (excluded_message_ids, n),
                ).fetchall()
            )
        assert len(results) <= n
        for result in results:
            assert len(result) == 3
            assert isinstance(result[0], int)
            assert isinstance(result[1], int)
            assert isinstance(result[2], str)
        return [
            src.types.MessageQueueItem(
                internal_id=result[0],
                timestamp=result[1],
                message_body=result[2],
            ) for result in results
        ]

    def remove_messages(self, message_ids: list[int]) -> None:
        with self.connection:
            self.connection.execute(
                """
                    DELETE FROM QUEUE
                    WHERE internal_id IN (?);
                """,
                (message_ids, ),
            )
