"""Entrypoint of the automation

1. Load environment variables from `../.env` and `config/.env` (the latter has priority)
2. Lock the automation with a file lock so that only one instance can run at a time
3. Run the automation if the lock could be acquired"""

import dotenv
import os
import filelock
from src import main, utils

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(PROJECT_DIR)

if __name__ == "__main__":
    # local `config/.env` takes priority over `../.env`
    dotenv.load_dotenv(os.path.join(PARENT_DIR, ".env"))
    dotenv.load_dotenv(os.path.join(PROJECT_DIR, "config", ".env"))

    if utils.functions.string_is_valid_version(os.path.basename(PROJECT_DIR)):
        lock_path = os.path.join(PARENT_DIR, "run.lock")
    else:
        lock_path = os.path.join(PROJECT_DIR, "run.lock")

    lock = filelock.FileLock(lock_path, timeout=2)

    try:
        with lock:
            main.run()
    except filelock.Timeout:
        print(f'locked by another process via file at path "{lock_path}"')
        raise TimeoutError("automation is already running")
