from typing import Literal, Optional
import os
import traceback
import filelock
import datetime

import src
from .functions import CommandLineException, log_level_is_visible
from .messaging_agent import MessagingAgent

LOGS_ARCHIVE_DIR = os.path.join(src.constants.PROJECT_DIR, "data", "logs")
FILELOCK_PATH = os.path.join(src.constants.PROJECT_DIR, "data", "logs.lock")


def _pad_str_right(
    text: str, min_width: int, fill_char: Literal["0", " ", "-"] = " "
) -> str:
    if len(text) >= min_width:
        return text
    else:
        return text + (fill_char * (min_width - len(text)))


class Logger:
    """A custom logger class that optionally sends out the logs via
    MQTT and writes them to a file. One can add details to log messages
    of all levels which will be logged on a separate line for better
    readability.

    You can give each instance a custom origin to distinguish between
    the sources of the log messages.

    A simple log message will look like this:

    ```
    2021-08-22 16:00:00.000 UTC+2 - origin - INFO - test message
    ```

    A log message with details will look like this:

    ```
    2021-08-22 16:00:00.000 UTC+2 - origin - INFO - test message
    --- details ----------------------------
    test details
    ----------------------------------------
    ```

    An exception will be formatted like this:

    ```
    2021-08-22 16:00:00.000 UTC+2 - origin - EXCEPTION - ZeroDivisionError: division by zero
    --- exception details ------------------
    test details
    --- traceback --------------------------
    Traceback (most recent call last):
        File "src/utils/logger.py", line 123, in _write_log_line
            raise Exception("test exception")
    Exception: test exception
    ----------------------------------------
    ```"""
    def __init__(
        self,
        config: src.types.Config,
        origin: str = "insert-name-here",
    ) -> None:
        """Initializes the logger.

        Args:
            config:  The config object
            origin:  The origin of the log messages, will be displayed
                     in the log lines."""

        self.origin: str = origin
        self.config = config
        self.filelock = filelock.FileLock(FILELOCK_PATH, timeout=3)
        self.messaging_agent = MessagingAgent()

    def horizontal_line(
        self,
        fill_char: Literal["-", "=", ".", "_"] = "=",
    ) -> None:
        """Writes a horizontal line."""

        self._write_log_line("INFO", fill_char * 40)

    def debug(
        self,
        message: str,
        details: Optional[str] = None,
    ) -> None:
        """Writes a INFO log line.
        
        Args:
            message:  The message to log
            details:  Additional details to log, useful for verbose output."""

        self._write_log_line("DEBUG", message, details=[("details", details)])

    def info(
        self,
        message: str,
        details: Optional[str] = None,
    ) -> None:
        """Writes a INFO log line.
        
        Args:
            message:  The message to log
            details:  Additional details to log, useful for verbose output."""

        self._write_log_line("INFO", message, details=[("details", details)])

    def warning(
        self,
        message: str,
        details: Optional[str] = None,
    ) -> None:
        """Writes a WARNING log line.
        
        Args:
            message:  The message to log
            details:  Additional details to log, useful for verbose output."""

        self._write_log_line("WARNING", message, details=[("details", details)])

    def error(self, message: str, details: Optional[str] = None) -> None:
        """Writes an error log line.

        Args:
            message:  The message to log
            details:  Additional details to log, useful for verbose output."""

        self._write_log_line("ERROR", message, details=[("details", details)])

    def exception(
        self,
        e: Exception,
        label: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """logs the traceback of an exception, sends the message via
        MQTT when config is passed (required for revision number).

        The subject will be formatted like this:
        `(label, )ZeroDivisionError: division by zero`
        
        Args:
            e:      The exception to log
            label:  A label to prepend to the exception name."""

        exception_name = traceback.format_exception_only(type(e), e)[0].strip()
        exception_traceback = "\n".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        ).strip()
        exception_details = None
        if isinstance(e, CommandLineException) and (e.details is not None):
            exception_details = e.details.strip()

        if label is None:
            subject = f"{exception_name}"
        else:
            subject = f"{label}, {exception_name}"
        self._write_log_line(
            "EXCEPTION",
            subject,
            details=[
                ("exception details", exception_details),
                ("traceback", exception_traceback),
                ("details", details),
            ]
        )

    def _write_log_line(
        self,
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"],
        subject: str,
        details: list[tuple[str, Optional[str]]] = [],
    ) -> None:
        """formats the log line string and writes it to
        `logs/current-logs.log`"""

        now = datetime.datetime.now()
        utcnow = datetime.datetime.utcnow()
        utc_offset = round((now - utcnow).total_seconds() / 3600, 1)
        if round(utc_offset) == utc_offset:
            utc_offset = round(utc_offset)

        log_string = (
            f"{str(now)[:-3]} UTC{'' if utc_offset < 0 else '+'}{utc_offset} " +
            f"- {_pad_str_right(self.origin, min_width=16)} " +
            f"- {_pad_str_right(level, min_width=9)} " + f"- {subject}\n"
        )
        filtered_detals = [(k, v) for k, v in details if v is not None]
        body: str = ""
        for key, value in filtered_detals:
            body += (
                _pad_str_right(f"--- {key} ", min_width=40, fill_char="-") +
                f"\n{value}\n"
            )
        if len(filtered_detals) > 0:
            body += "-" * 40 + "\n"

        # optionally write logs to console
        if log_level_is_visible(
            min_visible_log_level=self.config.logging_verbosity.console_prints,
            log_level=level
        ):
            print(log_string + body, end="")

        # optionally write logs to archive
        if log_level_is_visible(
            min_visible_log_level=self.config.logging_verbosity.file_archive,
            log_level=level
        ):
            path = os.path.join(
                LOGS_ARCHIVE_DIR, utcnow.strftime("%Y-%m-%d.log")
            )
            with self.filelock:
                with open(path, "a") as f1:
                    f1.write(log_string + body)

        # optionally send logs via MessagingAgent
        if log_level_is_visible(
            min_visible_log_level=self.config.logging_verbosity.message_sending,
            log_level=level
        ):
            self.messaging_agent.add_message(
                src.types.LogMessageBody(
                    level=level,
                    subject=f"{self.origin} - {level} - {subject}",
                    body=body.strip("\n"),
                )
            )
