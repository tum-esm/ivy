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
