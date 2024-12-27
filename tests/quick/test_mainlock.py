import pytest
import src


@pytest.mark.order(2)
@pytest.mark.quick
def test_mainlock() -> None:
    with src.utils.functions.with_automation_lock():
        try:
            with src.utils.functions.with_automation_lock():
                raise Exception("mainlock could be acquired twice")
        except TimeoutError:
            pass
        return
    assert False, "mainlock could not be acquired at all"
