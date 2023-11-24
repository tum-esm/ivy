
# run

Entrypoint of the automation

1. Load environment variables from `../.env` and `config/.env` (the latter has priority)
2. Lock the automation with a file lock so that only one instance can run at a time
3. Run the automation if the lock could be acquired