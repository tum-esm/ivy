import datetime
import os
import pytest
from fixtures import restore_production_files
import src


@pytest.mark.ci
def test_logging(restore_production_files: None) -> None:
    config = src.types.Config.load_template()
    logger = src.utils.Logger(config=config, origin="some-origin")
    logging_file = os.path.join(
        src.utils.logger.LOGS_ARCHIVE_DIR,
        datetime.datetime.utcnow().strftime("%Y-%m-%d.log")
    )
    assert not os.path.isfile(logging_file)

    def get_lines() -> list[str]:
        with open(logging_file, "r") as f:
            return f.readlines()

    logger.debug("debug message")
    lines = get_lines()
    assert len(lines) == 1
    assert "some-origin" in lines[0]
    assert "DEBUG" in lines[0]
    assert "debug message" in lines[0]

    logger.info("info message")
    lines = get_lines()
    assert len(lines) == 2
    assert "some-origin" in lines[1]
    assert "INFO" in lines[1]
    assert "info message" in lines[1]

    logger.warning("warning message")
    lines = get_lines()
    assert len(lines) == 3
    assert "some-origin" in lines[2]
    assert "WARNING" in lines[2]
    assert "warning message" in lines[2]

    logger.error("error message")
    lines = get_lines()
    assert len(lines) == 4
    assert "some-origin" in lines[3]
    assert "ERROR" in lines[3]
    assert "error message" in lines[3]

    try:
        4 / 0
    except Exception as e:
        logger.exception(e)
    lines = get_lines()
    assert len(lines) > 5
    assert "some-origin" in lines[4]
    assert "EXCEPTION" in lines[4]
    assert "ZeroDivisionError" in lines[4]
    assert "division by zero" in lines[4]
    assert "traceback" in lines[5]


@pytest.mark.ci
def test_log_level_order() -> None:
    # min_log_level=None
    # min_log_level="DEBUG"
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"]:
        assert src.utils.logger.log_level_should_be_forwarded(
            min_log_level=None,
            log_level=level  # type: ignore
        )
        assert src.utils.logger.log_level_should_be_forwarded(
            min_log_level="DEBUG",
            log_level=level  # type: ignore
        )

    # min_log_level="INFO"
    for level in ["DEBUG"]:
        assert not src.utils.logger.log_level_should_be_forwarded(
            min_log_level="INFO",
            log_level=level  # type: ignore
        )
    for level in ["INFO", "WARNING", "ERROR", "EXCEPTION"]:
        assert src.utils.logger.log_level_should_be_forwarded(
            min_log_level="INFO",
            log_level=level  # type: ignore
        )

    # min_log_level="WARNING"
    for level in ["DEBUG", "INFO"]:
        assert not src.utils.logger.log_level_should_be_forwarded(
            min_log_level="WARNING",
            log_level=level  # type: ignore
        )
    for level in ["WARNING", "ERROR", "EXCEPTION"]:
        assert src.utils.logger.log_level_should_be_forwarded(
            min_log_level="WARNING",
            log_level=level  # type: ignore
        )

    # min_log_level="ERROR"
    for level in ["DEBUG", "INFO", "WARNING"]:
        assert not src.utils.logger.log_level_should_be_forwarded(
            min_log_level="ERROR",
            log_level=level  # type: ignore
        )
    for level in ["ERROR", "EXCEPTION"]:
        assert src.utils.logger.log_level_should_be_forwarded(
            min_log_level="ERROR",
            log_level=level  # type: ignore
        )

    # min_log_level="EXCEPTION"
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        assert not src.utils.logger.log_level_should_be_forwarded(
            min_log_level="EXCEPTION",
            log_level=level  # type: ignore
        )
    for level in ["EXCEPTION"]:
        assert src.utils.logger.log_level_should_be_forwarded(
            min_log_level="EXCEPTION",
            log_level=level  # type: ignore
        )
