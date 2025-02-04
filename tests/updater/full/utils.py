import datetime
import os
import re
import shutil
import psutil
import tum_esm_utils

import src


def read_current_logs(version: tum_esm_utils.validators.Version) -> str:
    logspath = os.path.join(
        src.constants.ROOT_DIR,
        version.as_identifier(),
        "data",
        "logs",
        datetime.datetime.now().strftime("%Y-%m-%d.log"),
    )
    print(f"reading logs from {logspath}")
    current_logs = tum_esm_utils.files.load_file(logspath)
    assert current_logs is not None
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
    print_logs: bool = False,
) -> bool:
    current_logs = read_current_logs(version)
    pids = _thread_pids(current_logs)
    if print_logs:
        print(f"--- current logs ---\n{current_logs}")
    for line in expected_log_lines:
        assert line in current_logs, f"Expected log line not found: {line}"
    return all([psutil.pid_exists(pid) for pid in pids])


def version_is_not_running(
    version: tum_esm_utils.validators.Version,
    expected_log_lines: list[str] = [],
    print_logs: bool = False,
) -> bool:
    current_logs = read_current_logs(version)
    pids = _thread_pids(current_logs)
    if print_logs:
        print(f"--- current logs ---\n{current_logs}")
    for line in expected_log_lines:
        assert line in current_logs, f"Expected log line not found: {line}"
    return not any([psutil.pid_exists(pid) for pid in pids])


def replace_file_content(filepath: str, old: str, new: str) -> None:
    with open(filepath, "r") as f:
        content = f.read()
    assert (
        content.count(old) == 1
    ), f"Expected exactly one occurence of {old} in {filepath}, got {content.count(old)}"
    with open(filepath, "w") as f:
        f.write(content.replace(old, new))


def clean_root_dir() -> None:
    for item in os.listdir(src.constants.ROOT_DIR):
        item_path = os.path.join(src.constants.ROOT_DIR, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
