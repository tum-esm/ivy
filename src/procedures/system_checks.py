import datetime
import signal
import time
import psutil
import src


def run(config: src.types.Config) -> None:
    """Logs the system load and last boot time."""

    logger = src.utils.Logger(config=config, origin="system-checks")

    # register a teardown procedure

    signal.signal(signal.SIGTERM, lambda: logger.debug("nothing to tear down"))

    # start procedure loop

    while True:
        t = src.utils.functions.get_time_to_next_datapoint(
            seconds_between_datapoints=config.system_checks.
            seconds_between_checks
        )
        logger.debug(f"sleeping for {t} seconds")
        time.sleep(t)

        loads = psutil.getloadavg()
        load_last_1_min = round(loads[0], 2)
        load_last_5_min = round(loads[1], 2)
        load_last_15_min = round(loads[2], 2)
        logger.debug(
            "Average system load (last 1/5/15 minutes) [%]:" +
            f" {load_last_1_min}/{load_last_5_min}/{load_last_15_min}"
        )

        if load_last_5_min > 70:
            logger.warning(
                "System load is very high (above 70% in the last 50 minutes)"
            )

        last_boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        logger.debug(f"Last boot time: {last_boot_time}")
