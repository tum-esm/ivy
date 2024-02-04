from typing import Optional
import time
import json
import pydantic
import tenta
import src


def run_tenta_backend(
    config: src.types.Config,
    logger: src.utils.Logger,
) -> None:
    assert config.backend is not None
    assert config.backend.provider == "tenta"
    messaging_agent = src.utils.MessagingAgent()

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

    try:

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

        # active = in the process of sending
        # the first element of the tuple is the mqtt message id
        active_messages: set[tuple[int, src.types.MessageQueueItem]] = set()

        # TODO: add graceful teardown to send the remaining messages
        # TODO: add parameter `skip_remaining_messages_on_update`

        while True:
            # send new messages
            open_message_slots = config.backend.max_parallel_messages - len(
                active_messages
            )
            if open_message_slots > 0:
                new_messages = messaging_agent.get_n_latest_messages(
                    open_message_slots,
                    excluded_message_ids={
                        m[1].identifier
                        for m in active_messages
                    }
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
                        if message.message_body.status in [
                            "accepted", "rejected"
                        ]:
                            mqtt_message_id = tenta_client.publish(
                                tenta.types.AcknowledgmentMessage(
                                    revision=message.message_body.config.
                                    general.config_revision,
                                    success=(
                                        message.message_body.status ==
                                        "accepted"
                                    ),
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
                    lambda m: m[1].identifier not in
                    published_message_identifiers, active_messages
                )
            )
            time.sleep(5)

    except Exception as e:
        logger.exception(e, "The Tenta backend encountered an exception")
        return
