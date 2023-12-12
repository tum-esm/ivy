from typing import Any
import signal
import time
import src


def run(config: src.types.Config) -> None:
    """Fetches the weather from a weather API. You can simply remove
    this in your own project and use it as an exaple for your own
    procedures."""

    logger = src.utils.Logger(config=config, origin="dummy-procedure")

    # register a teardown procedure

    def teardown_handler(*args: Any) -> None:
        logger.debug("nothing to tear down")

    signal.signal(signal.SIGTERM, teardown_handler)

    # start procedure loop

    # TODO: add exponential backoff
    while True:
        t = src.utils.functions.get_time_to_next_datapoint(
            seconds_between_datapoints=config.dummy_procedure.
            seconds_between_datapoints,
        )
        logger.debug(f"sleeping for {t} seconds")
        time.sleep(t)

        state = src.utils.StateInterface.load()
        if (state.system.last_5_min_load or 0) > 0.75:
            logger.debug("system load is above 75%, skipping this procedure")
            continue

        # TODO: fetch weather from API
        # TODO: log progress
        # TODO: send out data
