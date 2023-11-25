import pytest
import src


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
