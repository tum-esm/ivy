import atexit
import sys
from typing import Any
import datetime
import signal
import time
import psutil
import tum_esm_utils
import src


def run(config: src.types.Config, name: str) -> None:
    """Logs the system load and last boot time.

    Args:
        config: The configuration object.
        name: The name of the procedure.
    """

    logger = src.utils.Logger(config=config, origin=name)
    messaging_agent = src.utils.MessagingAgent()

    # register a teardown procedure

    def teardown_handler(*args: Any) -> None:
        logger.debug("nothing to tear down")
        sys.exit(0)

    signal.signal(signal.SIGTERM, teardown_handler)

    # start procedure loop

    exponential_backoff = tum_esm_utils.timing.ExponentialBackoff(log_info=logger.info)
    while True:
        try:
            t = src.utils.functions.get_time_to_next_datapoint(
                seconds_between_datapoints=config.system_checks.seconds_between_checks
            )
            logger.debug(f"Sleeping for {t:.2f} seconds")
            time.sleep(t)

            # get and log CPU load
            loads = psutil.getloadavg()
            load_last_1_min = round(loads[0], 2)
            load_last_5_min = round(loads[1], 2)
            load_last_15_min = round(loads[2], 2)
            logger.debug(
                "Average CPU load (last 1/5/15 minutes) [%]:"
                + f" {load_last_1_min}/{load_last_5_min}/{load_last_15_min}"
            )
            if load_last_5_min > 75:
                logger.warning(
                    "CPU load is very high",
                    details=f"CPU load was at {load_last_5_min} % in the last 5 minutes",
                )

            # get and log last boot time
            seconds_since_last_boot = psutil.boot_time()
            last_boot_time = datetime.datetime.fromtimestamp(seconds_since_last_boot)
            logger.debug(f"Last boot time: {last_boot_time}")

            # On Linux system you could use `psutil.sensors_temperatures()`
            # and `psutil.sensors_fans()` If you know your disk partitions
            # you can use `psutil.disk_usage()`

            # write system data into state
            with src.utils.StateInterface.update() as state:
                state.system.last_boot_time = last_boot_time
                state.system.last_5_min_load = load_last_5_min

            # send out system data
            messaging_agent.add_message(
                src.types.DataMessageBody(
                    data={
                        "last_boot_time": last_boot_time.timestamp(),
                        "last_5_min_load": load_last_5_min,
                    }
                )
            )

            exponential_backoff.reset()

        except Exception as e:
            logger.exception(e)
            exponential_backoff.sleep()
