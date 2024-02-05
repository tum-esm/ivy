from typing import Any, Optional
import multiprocessing.synchronize
import signal
import time
import json
import pydantic
import tenta
import src


def run(
    config: src.types.Config,
    logger: src.utils.Logger,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
    """The main procedure for the Tenta backend.
    
    Args:
        config: The configuration object.
        logger: The logger object.
        teardown_indicator: The event that is set when the procedure should terminate.
    """

    assert config.backend is not None
    assert config.backend.provider == "tenta"
    messaging_agent = src.utils.MessagingAgent()

    # parse incoming config messages

    def on_config_message(message: tenta.types.ConfigurationMessage) -> None:
        logger.info(
            f"Received config with revision {message.revision}",
            details=json.dumps(message, indent=4),
        )
        try:
            foreign_config = src.types.ForeignConfig.model_validate_json(
                message.configuration
            )
            foreign_config.general.config_revision = message.revision
            with src.utils.StateInterface.update() as state:
                state.pending_configs.append(foreign_config)
            logger.info(f"Config with revision {message.revision} was parsed")
        except pydantic.ValidationError as e:
            logger.error(
                f"Config with revision {message.revision} is invalid",
                details=e.json(indent=4),
            )
            messaging_agent.add_message(
                src.types.ConfigMessageBody(
                    status="rejected",
                    config=src.types.ForeignConfig(
                        # using a dummy version here simplifies the rest of the codebase
                        general=src.types.config.ForeignGeneralConfig(
                            config_revision=message.revision,
                            software_version="0.0.0",
                        ),
                    ),
                )
            )

    # active = in the process of sending
    # the first element of the tuple is the mqtt message id
    active_messages: set[tuple[int, src.types.MessageQueueItem]] = set()
    tenta_client: Optional[tenta.TentaClient] = None
    exponential_backoff = src.utils.ExponentialBackoff(logger, buckets=[120, 900, 3600])
    teardown_receipt_time: Optional[float] = None

    try:

        # register a teardown procedure

        def teardown_handler(*args: Any) -> None:
            if tenta_client is not None:
                logger.debug("Tearing down the Tenta Client")
                tenta_client.teardown()
            logger.debug("Finishing the teardown")

        signal.signal(signal.SIGINT, teardown_handler)
        signal.signal(signal.SIGTERM, teardown_handler)

        # TODO: add timeout alarms

        def connect(
        ) -> tuple[tenta.TentaClient, set[tuple[int, src.types.MessageQueueItem]]]:
            logger.info("Starting Tenta backend")
            tenta_client = tenta.TentaClient(
                mqtt_client_id=config.backend.mqtt_client_id,
                mqtt_host=config.backend.mqtt_host,
                mqtt_port=config.backend.mqtt_port,
                mqtt_identifier=config.backend.mqtt_username,
                mqtt_password=config.backend.mqtt_password,
                sensor_identifier=config.general.system_identifier,
                on_config_message=on_config_message,
                # possibly add your TLS configuration here
            )
            logger.info("Tenta client has been set up")
            return tenta_client, set()

        tenta_client, active_messages = connect()

        while True:
            try:
                if teardown_receipt_time is None:
                    if teardown_indicator.is_set():
                        logger.debug("Received a teardown indicator")
                        logger.debug(
                            f"Waiting max. {config.backend.max_drain_time} " +
                            "seconds to send remaining messages"
                        )
                        teardown_receipt_time = time.time()
                else:
                    if (
                        time.time() - teardown_receipt_time
                    ) > config.backend.max_drain_time:
                        logger.debug("Max. drain time reached")
                        exit(0)

                if not tenta_client.client.is_connected():
                    raise ConnectionError("MQTT client is not connected")
                else:
                    exponential_backoff.reset()

                # send new messages
                open_message_slots = config.backend.max_parallel_messages - len(
                    active_messages
                )
                if open_message_slots > 0:
                    new_messages = messaging_agent.get_n_latest_messages(
                        open_message_slots,
                        excluded_message_ids={m[1].identifier
                                              for m in active_messages}
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
                                    severity={ # type: ignore
                                        "DEBUG": "info",
                                        "INFO": "info",
                                        "WARNING": "warning",
                                        "ERROR": "error",
                                        "EXCEPTION": "error",
                                    }[message.message_body.level],
                                    message=(
                                        message.message_body.subject + "\n\n" +
                                        message.message_body.body
                                    ),
                                    revision=config.general.config_revision,
                                )
                            )
                        if message.message_body.variant == "config":
                            if message.message_body.status in ["accepted", "rejected"]:
                                mqtt_message_id = tenta_client.publish(
                                    tenta.types.AcknowledgmentMessage(
                                        revision=message.message_body.config.general.
                                        config_revision,
                                        success=(
                                            message.message_body.status == "accepted"
                                        ),
                                    )
                                )
                            # received and startup not implemented in Tenta yet
                        if mqtt_message_id is not None:
                            active_messages.add((mqtt_message_id, message))

                if (teardown_receipt_time is not None) and (len(active_messages) == 0):
                    logger.debug("Send out all messages, exiting the procedure")
                    exit(0)

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
                        active_messages
                    )
                )
                time.sleep(5)

            except ConnectionError:
                logger.error("The Tenta backend is not connected")
                logger.debug("Tearing down the Tenta Client")
                tenta_client.teardown()
                if teardown_receipt_time is not None:
                    logger.debug(
                        "Sleeping only 10 seconds because a teardown has been issued"
                    )
                    time.sleep(10)
                else:
                    sleep_seconds = exponential_backoff.sleep()
                    if sleep_seconds == exponential_backoff.buckets[-1]:
                        logger.debug("Fully tearing down the procedure")
                        exit(0)
                tenta_client, active_messages = connect()

    except Exception as e:
        logger.exception(e, "The Tenta backend encountered an exception")
        return
