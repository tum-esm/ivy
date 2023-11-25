import pytest
import src


@pytest.mark.ci
def test_mainlock() -> None:
    with src.utils.functions.with_automation_lock():
        try:
            with src.utils.functions.with_automation_lock():
                raise Exception("mainlock could be acquired twice")
        except TimeoutError:
            pass
