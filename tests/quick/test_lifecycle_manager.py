import atexit
import signal
import time
from typing import Any
import pytest
import src
from ..fixtures import provide_test_config, restore_production_files


def pytest_dummy_procedure(config: src.types.Config, name: str) -> None:
    config.logging_verbosity.file_archive = "DEBUG"
    logger = src.utils.Logger(config, origin=name)
    logger.info("Pytest dummy procedure was started")

    def teardown_handler(*args: Any) -> None:
        # possibly add your own teardown logic
        logger.debug("nothing to tear down")
        exit(0)

    logger.info("Registering teardown handle")
    atexit.register(teardown_handler)
    signal.signal(signal.SIGINT, teardown_handler)
    signal.signal(signal.SIGTERM, teardown_handler)

    time.sleep(8)


def expected_log_entries(count: int) -> None:
    log_file_content = src.utils.Logger.read_current_log_file()
    if log_file_content is None:
        log_file_content = ""
    found = log_file_content.count("Pytest dummy procedure was started")
    assert (
        found == count
    ), f"Expected {count} log entries, found {found} log entries: {log_file_content}"


@pytest.mark.order(2)
@pytest.mark.quick
def test_lifecycle_manager(
    provide_test_config: src.types.Config,
    restore_production_files: None,
) -> None:
    lm = src.utils.LifecycleManager(
        config=provide_test_config,
        entrypoint=pytest_dummy_procedure,
        name="pytest-dummy-procedure",
        variant="procedure",
    )
    expected_log_entries(0)

    assert not lm.procedure_is_running()
    start_time = time.time()
    lm.start_procedure()
    time.sleep(0.5)
    assert lm.procedure_is_running()
    lm.check_procedure_status()
    expected_log_entries(1)

    lm.teardown()
    assert not lm.procedure_is_running()
    try:
        lm.check_procedure_status()
        raise Exception("Expected RuntimeError")
    except RuntimeError as e:
        pass
    stop_time = time.time()
    assert (
        stop_time - start_time
    ) < 7, "Expected teardown to happen before procedure finishes on its own"
    expected_log_entries(1)

    lm.start_procedure()
    time.sleep(0.5)
    lm.check_procedure_status()
    assert lm.procedure_is_running()
    expected_log_entries(2)

    lm.teardown()
    assert not lm.procedure_is_running()
    try:
        lm.check_procedure_status()
        raise Exception("Expected RuntimeError")
    except RuntimeError as e:
        pass
    expected_log_entries(2)
