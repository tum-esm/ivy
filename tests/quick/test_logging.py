import datetime
import os
import pytest
from ..fixtures import restore_production_files
import src


@pytest.mark.quick
def test_logging_to_files(restore_production_files: None) -> None:
    config = src.types.Config.load_template()

    config.logging_verbosity.console_prints = None
    config.logging_verbosity.file_archive = "DEBUG"
    config.logging_verbosity.message_sending = None
    logger = src.utils.Logger(config=config, origin="some-origin")

    logging_file = os.path.join(
        src.utils.logger.LOGS_ARCHIVE_DIR,
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d.log"),
    )
    assert not os.path.isfile(logging_file)

    def check_last_line(snippets: list[str]) -> None:
        with open(logging_file, "r") as f:
            last_line = [l for l in f.readlines() if l[0] == "2"][-1].strip("\n")
        for snippet in snippets:
            assert (
                snippet in last_line
            ), f"last line should contain '{snippet}', but it is '{last_line}'"

    logger.debug("debug message")
    check_last_line(["some-origin", "DEBUG", "debug message"])

    logger.info("info message")
    check_last_line(["some-origin", "INFO", "info message"])

    logger.warning("warning message")
    check_last_line(["some-origin", "WARNING", "warning message"])

    logger.error("error message")
    check_last_line(["some-origin", "ERROR", "error message"])

    try:
        4 / 0
    except Exception as e:
        logger.exception(e)
    check_last_line(["some-origin", "EXCEPTION", "ZeroDivisionError: division by zero"])


@pytest.mark.quick
def test_logging_to_messages(restore_production_files: None) -> None:
    config = src.types.Config.load_template()

    config.logging_verbosity.console_prints = None
    config.logging_verbosity.file_archive = None
    config.logging_verbosity.message_sending = "DEBUG"
    logger = src.utils.Logger(config=config, origin="some-origin")

    messaging_agent = src.utils.MessagingAgent()
    assert len(messaging_agent.get_n_latest_messages(10)) == 0

    logger.debug("debug message")
    assert len(messaging_agent.get_n_latest_messages(10)) == 1

    logger.info("info message")
    assert len(messaging_agent.get_n_latest_messages(10)) == 2

    logger.warning("warning message")
    assert len(messaging_agent.get_n_latest_messages(10)) == 3

    logger.error("error message")
    assert len(messaging_agent.get_n_latest_messages(10)) == 4

    try:
        4 / 0
    except Exception as e:
        logger.exception(e)
    assert len(messaging_agent.get_n_latest_messages(10)) == 5

    mids = [m.identifier for m in messaging_agent.get_n_latest_messages(10)]
    messaging_agent.remove_messages(mids)
    assert len(messaging_agent.get_n_latest_messages(10)) == 0


@pytest.mark.quick
def test_log_level_visibiliy() -> None:
    # min_log_level=None
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]:
        assert not src.utils.functions.log_level_is_visible(
            min_log_level=None,
            log_level=level,  # type: ignore
        )

    # min_log_level="DEBUG"
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]:
        assert src.utils.functions.log_level_is_visible(
            min_log_level="DEBUG",
            log_level=level,  # type: ignore
        )

    # min_log_level="INFO"
    for level in ["DEBUG"]:
        assert not src.utils.functions.log_level_is_visible(
            min_log_level="INFO",
            log_level=level,  # type: ignore
        )
    for level in ["INFO", "WARNING", "ERROR", "EXCEPTION"]:
        assert src.utils.functions.log_level_is_visible(
            min_log_level="INFO",
            log_level=level,  # type: ignore
        )

    # min_log_level="WARNING"
    for level in ["DEBUG", "INFO"]:
        assert not src.utils.functions.log_level_is_visible(
            min_log_level="WARNING",
            log_level=level,  # type: ignore
        )
    for level in ["WARNING", "ERROR", "EXCEPTION"]:
        assert src.utils.functions.log_level_is_visible(
            min_log_level="WARNING",
            log_level=level,  # type: ignore
        )

    # min_log_level="ERROR"
    for level in ["DEBUG", "INFO", "WARNING"]:
        assert not src.utils.functions.log_level_is_visible(
            min_log_level="ERROR",
            log_level=level,  # type: ignore
        )
    for level in ["ERROR", "EXCEPTION"]:
        assert src.utils.functions.log_level_is_visible(
            min_log_level="ERROR",
            log_level=level,  # type: ignore
        )

    # min_log_level="EXCEPTION"
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        assert not src.utils.functions.log_level_is_visible(
            min_log_level="EXCEPTION",
            log_level=level,  # type: ignore
        )
    for level in ["EXCEPTION"]:
        assert src.utils.functions.log_level_is_visible(
            min_log_level="EXCEPTION",
            log_level=level,  # type: ignore
        )
