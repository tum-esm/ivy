from typing import Any
import random
import signal
import time
import src


def run(config: src.types.Config) -> None:
    """Fetches the weather from a weather API. You can simply remove
    this in your own project and use it as an exaple for your own
    procedures."""

    logger = src.utils.Logger(config=config, origin="dummy-procedure")
    messaging_agent = src.utils.MessagingAgent()
    random.seed(time.time())
    current_positions: tuple[int, int] = (0, 0)

    # register a teardown procedure

    def teardown_handler(*args: Any) -> None:
        # TODO: add your own teardown logic
        logger.debug("nothing to tear down")

    signal.signal(signal.SIGTERM, teardown_handler)

    # start procedure loop

    exponential_backoff = src.utils.ExponentialBackoff(logger)
    while True:
        try:
            t = src.utils.functions.get_time_to_next_datapoint(
                seconds_between_datapoints=config.dummy_procedure.
                seconds_between_datapoints,
            )
            logger.debug(f"sleeping for {t} seconds")
            time.sleep(t)

            state = src.utils.StateInterface.load()
            assert (
                state.system.last_5_min_load or 0
            ) < 0.75, "can't perform this procedure while system load is above 75%"

            # do a random walk
            current_positions = (
                current_positions[0] + 1 if (random.random() < 0.5) else (-1),
                current_positions[1] + 1 if (random.random() < 0.5) else (-1),
            )

            # send out data
            messaging_agent.add_message(
                src.types.DataMessageBody(
                    message_body={
                        "random_walk_a_position": current_positions[0],
                        "random_walk_b_position": current_positions[1],
                    }
                )
            )

            exponential_backoff.reset()

        except Exception as e:
            logger.exception(e)
            exponential_backoff.sleep()
