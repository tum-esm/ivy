from typing import Any, Optional
import multiprocessing.synchronize
import signal
import time
import json
import pydantic
import tenta
import tum_esm_utils
import src


def run(
    config: src.types.Config,
    name: str,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
    """The main procedure for the Tenta backend.

    Args:
        config: The configuration object.
        name: The name of the backend procedure.
        teardown_indicator: The event that is set when the procedure should terminate.
    """

    assert config.backend is not None
    assert config.backend.provider == "tenta"
    logger = src.utils.Logger(config=config, origin=name)
    messaging_agent = src.utils.MessagingAgent()

    # parse incoming config messages

    def on_config_message(message: tenta.types.ConfigurationMessage) -> None:
        logger.info(
            f"Received config with revision {message.revision}",
            details=str(message.configuration),
        )
        try:
            assert isinstance(message.configuration, dict), "Configuration is not a dictionary"
            assert "general" in message.configuration, "General configuration is missing"
            assert isinstance(
                message.configuration["general"], dict
            ), "General configuration is not a dictionary"
            message.configuration["general"]["config_revision"] = message.revision
            foreign_config = src.types.ForeignConfig.model_validate(message.configuration)
            with src.utils.StateInterface.update() as state:
                state.pending_configs.append(foreign_config)
            logger.info(f"Config with revision {message.revision} was parsed successfully")
        except (pydantic.ValidationError, AssertionError) as e:
            logger.error(
                f"Config with revision {message.revision} is invalid",
                details=e.json(indent=4) if isinstance(e, pydantic.ValidationError) else str(e),
            )
            messaging_agent.add_message(
                src.types.ConfigMessageBody(
                    status="rejected",
                    config=src.types.ForeignConfig(
                        # using a dummy version here simplifies the rest of the codebase
                        general=src.types.config.ForeignGeneralConfig(
                            config_revision=message.revision,
                            software_version=tum_esm_utils.validators.Version("0.0.0"),
                        ),
                    ),
                )
            )

    # active = in the process of sending
    # the first element of the tuple is the mqtt message id
    active_messages: set[tuple[int, src.types.MessageQueueItem]] = set()
    tenta_client: Optional[tenta.TentaClient] = None
    exponential_backoff = tum_esm_utils.timing.ExponentialBackoff(
        log_info=logger.info, buckets=[120, 900, 3600]
    )
    teardown_receipt_time: Optional[float] = None

    try:
        logger.info("Setting up Tenta backend")
        logger.debug("Registering the teardown procedure")

        def teardown_handler(*args: Any) -> None:
            if tenta_client is not None:
                logger.debug("Tearing down the Tenta client")
                tenta_client.teardown()
            logger.debug("Finishing the teardown")

        signal.signal(signal.SIGINT, teardown_handler)
        signal.signal(signal.SIGTERM, teardown_handler)

        def connect() -> tuple[tenta.TentaClient, set[tuple[int, src.types.MessageQueueItem]]]:
            assert config.backend is not None
            logger.info("Connecting to Tenta backend")
            tenta_client = tenta.TentaClient(
                mqtt_client_id=config.backend.mqtt_connection.client_id,
                mqtt_host=config.backend.mqtt_connection.host,
                mqtt_port=config.backend.mqtt_connection.port,
                mqtt_identifier=config.backend.mqtt_connection.username,
                mqtt_password=config.backend.mqtt_connection.password,
                sensor_identifier=config.general.system_identifier,
                on_config_message=on_config_message,
                # possibly add your TLS configuration here
            )
            logger.info("Tenta connection has been set up")
            return tenta_client, set()

        tum_esm_utils.timing.set_alarm(20, "Could not connect to Tenta backend within 20 seconds")
        tenta_client, active_messages = connect()
        tum_esm_utils.timing.clear_alarm()

        # worst case is 8 seconds per messages (which is already very very slow)
        MAX_LOOP_TIME = config.backend.max_parallel_messages * 8 + 5
        tum_esm_utils.timing.set_alarm(
            MAX_LOOP_TIME,
            f"The Tenta backend did not finish one loop within {MAX_LOOP_TIME} seconds",
        )

        while True:
            signal.alarm(MAX_LOOP_TIME)
            try:
                if teardown_receipt_time is None:
                    if teardown_indicator.is_set():
                        logger.debug("Received a teardown indicator")
                        logger.debug(
                            f"Waiting max. {config.backend.max_drain_time} "
                            + "seconds to send remaining messages"
                        )
                        teardown_receipt_time = time.time()
                else:
                    if (time.time() - teardown_receipt_time) > config.backend.max_drain_time:
                        logger.debug("Max. drain time reached, stopping the Tenta backend")
                        return

                if not tenta_client.client.is_connected():
                    raise ConnectionError("MQTT client is not connected")
                else:
                    exponential_backoff.reset()

                # send new messages
                open_message_slots = config.backend.max_parallel_messages - len(active_messages)
                if open_message_slots > 0:
                    new_messages = messaging_agent.get_n_latest_messages(
                        open_message_slots,
                        excluded_message_ids={m[1].identifier for m in active_messages},
                    )
                    for message in new_messages:
                        mqtt_message_id: Optional[int] = None
                        if message.message_body.variant == "data":
                            numeric_data_only: dict[str, int | float] = {}
                            for key, value in message.message_body.data.items():
                                if isinstance(value, (int, float)):
                                    numeric_data_only[key] = value
                            mqtt_message_id = tenta_client.publish(
                                tenta.types.MeasurementMessage(
                                    value=numeric_data_only,
                                    revision=config.general.config_revision,
                                )
                            )
                        if message.message_body.variant == "log":
                            mqtt_message_id = tenta_client.publish(
                                tenta.types.LogMessage(
                                    severity={  # type: ignore
                                        "DEBUG": "info",
                                        "INFO": "info",
                                        "WARNING": "warning",
                                        "ERROR": "error",
                                        "EXCEPTION": "error",
                                    }[message.message_body.level],
                                    message=(
                                        message.message_body.subject
                                        + "\n\n"
                                        + message.message_body.body
                                    ),
                                    revision=config.general.config_revision,
                                )
                            )
                        if message.message_body.variant == "config":
                            if message.message_body.status in ["accepted", "rejected"]:
                                mqtt_message_id = tenta_client.publish(
                                    tenta.types.AcknowledgmentMessage(
                                        revision=message.message_body.config.general.config_revision,
                                        success=(message.message_body.status == "accepted"),
                                    )
                                )
                            # received and startup not implemented in Tenta yet
                        if mqtt_message_id is not None:
                            active_messages.add((mqtt_message_id, message))

                # determine which messages have been published
                published_message_identifiers: set[int] = set()
                for mqtt_message_id, message in active_messages:
                    if tenta_client.was_message_published(mqtt_message_id):
                        published_message_identifiers.add(message.identifier)

                # remove published messages from local message queue database
                messaging_agent.remove_messages(published_message_identifiers)

                # remove published messages from the active set
                active_messages = set(
                    filter(
                        lambda m: m[1].identifier not in published_message_identifiers,
                        active_messages,
                    )
                )

                # exit the procedure if teardown has been issued and all messages have been sent
                if (teardown_receipt_time is not None) and (len(active_messages) == 0):
                    logger.debug("Send out all messages, exiting the procedure")
                    return

                # sleep 5 seconds between message bursts
                time.sleep(5)

            except ConnectionError:
                logger.error("The Tenta backend is not connected")

                tum_esm_utils.timing.set_alarm(
                    20, "Could not tear down Tenta backend within 20 seconds"
                )
                teardown_handler()
                tum_esm_utils.timing.clear_alarm()

                if teardown_receipt_time is not None:
                    # the backoff procedure should not prevent remaining messages from being sent
                    logger.debug("Sleeping only 5 seconds because a teardown has been issued")
                    time.sleep(5)
                else:
                    sleep_seconds = exponential_backoff.sleep()
                    if sleep_seconds == exponential_backoff.buckets[-1]:
                        logger.debug("Fully tearing down the procedure")
                        return

                tum_esm_utils.timing.set_alarm(
                    20, "Could not reconnect to Tenta backend within 20 seconds"
                )
                tenta_client, active_messages = connect()
                tum_esm_utils.timing.clear_alarm()

    except Exception as e:
        logger.exception(e, "The Tenta backend encountered an exception")
        return
