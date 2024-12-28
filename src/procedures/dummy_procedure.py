import atexit
import sys
from typing import Any
import random
import signal
import time

import tum_esm_utils
import src


def run(config: src.types.Config, name: str) -> None:
    """Performs a random walk and sends out the current position.

    You can use this as an example for your own procedures and
    remove this in your own project

    Args:
        config: The configuration object.
        name: The name of the procedure.
    """

    logger = src.utils.Logger(config=config, origin=name)
    messaging_agent = src.utils.MessagingAgent()
    random.seed(time.time())
    current_positions: tuple[int, int] = (0, 0)

    # register a teardown procedure

    def teardown_handler(*args: Any) -> None:
        # possibly add your own teardown logic
        logger.debug("nothing to tear down")
        sys.exit(0)

    signal.signal(signal.SIGTERM, teardown_handler)

    # start procedure loop

    exponential_backoff = tum_esm_utils.timing.ExponentialBackoff(log_info=logger.info)
    while True:
        try:
            t = src.utils.functions.get_time_to_next_datapoint(
                seconds_between_datapoints=config.dummy_procedure.seconds_between_datapoints,
            )
            logger.debug(f"Sleeping for {t:.2f} seconds")
            time.sleep(t)

            state = src.utils.StateInterface.load()
            assert (
                state.system.last_5_min_load or 0
            ) < 75, "can't perform this procedure while system load is above 75%"

            # do a random walk
            current_positions = (
                current_positions[0] + 1 if (random.random() < 0.5) else (-1),
                current_positions[1] + 1 if (random.random() < 0.5) else (-1),
            )

            # send out data
            messaging_agent.add_message(
                src.types.DataMessageBody(
                    data={
                        "random_walk_a_position": current_positions[0],
                        "random_walk_b_position": current_positions[1],
                    }
                )
            )

            exponential_backoff.reset()

        except Exception as e:
            logger.exception(e)
            exponential_backoff.sleep()
