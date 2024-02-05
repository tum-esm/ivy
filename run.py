"""Entrypoint of the automation

1. Load environment variables from `../.env` and `config/.env` (the latter has priority)
2. Lock the automation with a file lock so that only one instance can run at a time
3. Run the automation if the lock could be acquired
"""

import dotenv
import os
import src

PARENT_DIR = os.path.dirname(src.constants.PROJECT_DIR)

if __name__ == "__main__":
    dotenv.load_dotenv(os.path.join(PARENT_DIR, ".env"))
    dotenv.load_dotenv(os.path.join(src.constants.PROJECT_DIR, "config", ".env"))

    with src.utils.functions.with_automation_lock():
        src.main.run()
