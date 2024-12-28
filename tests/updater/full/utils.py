import datetime
import os
import re
import psutil
import tum_esm_utils

import src


def _thread_logs(version: tum_esm_utils.validators.Version) -> str:
    current_logs = tum_esm_utils.files.load_file(
        os.path.join(
            src.constants.ROOT_DIR,
            version.as_identifier(),
            "data",
            "logs",
            datetime.datetime.now().strftime("%Y-%m-%d.log"),
        )
    )
    assert current_logs is not None
    print(f"--- current logs ---\n{current_logs}")
    return current_logs


def _thread_pids(current_logs: str) -> list[int]:
    pids = [
        int(p[1])
        for p in re.findall(r"- Starting (process|automation) with PID (\d+)\n", current_logs)
    ]
    print(f"pids: {pids}")
    assert len(pids) == 4, f"there is not exactly 4 pids, got {len(pids)}"
    return pids


def version_is_running(
    version: tum_esm_utils.validators.Version,
    expected_log_lines: list[str] = [],
) -> bool:
    current_logs = _thread_logs(version)
    pids = _thread_pids(current_logs)
    for line in expected_log_lines:
        assert line in current_logs, f"Expected log line not found: {line}"
    return all([psutil.pid_exists(pid) for pid in pids])


def version_is_not_running(
    version: tum_esm_utils.validators.Version,
    expected_log_lines: list[str] = [],
) -> bool:
    current_logs = _thread_logs(version)
    pids = _thread_pids(current_logs)
    for line in expected_log_lines:
        assert line in current_logs, f"Expected log line not found: {line}"
    return not any([psutil.pid_exists(pid) for pid in pids])
