from typing import Optional
import time
import json
import pydantic
import tenta
import src


def run_tenta_backend(config: src.types.Config) -> None:
    assert config.backend is not None
    assert config.backend.provider == "tenta"

    logger = src.utils.Logger(config=config, origin="tenta-backend")

    def on_config_message(message: tenta.types.ConfigurationMessage) -> None:
        logger.info(
            f"Received config with revision {message.revision}",
            details=json.dumps(message.configuration, indent=4),
        )
        try:
            foreign_config = src.types.ForeignConfig(
                **message.config,
                revision=message.revision,
            )
            with src.utils.StateInterface.update() as state:
                state.pending_configs.append(foreign_config)
            logger.info(f"Config with revision {message.revision} was parsed")
        except pydantic.ValidationError as e:
            logger.error(
                f"Config with revision {message.revision} was invalid",
                details=e.json(indent=4),
            )
            pass

    try:

        logger.info("Starting Tenta backend")
        tenta_client = tenta.TentaClient(
            mqtt_host=config.backend.mqtt_host,
            mqtt_port=config.backend.mqtt_port,
            mqtt_identifier=config.backend.mqtt_identifier,
            mqtt_password=config.backend.mqtt_password,
            sensor_identifier=config.system_identifier,
            on_config_message=on_config_message,
        )
        messaging_agent = src.utils.MessagingAgent()
        logger.info("Tenta client has been set up")

        # active = in the process of sending
        # the first element of the tuple is the mqtt message id
        active_messages: set[tuple[int, src.types.MessageQueueItem]] = set()

        while True:
            open_message_slots = config.backend.max_parallel_messages - len(
                active_messages
            )
            new_messages: list[src.types.MessageQueueItem] = []
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
                                revision=config.revision,
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
                                revision=config.revision,
                            )
                        )
                    if message.message_body.variant == "config":
                        if message.message_body.status in [
                            "accepted", "rejected"
                        ]:
                            mqtt_message_id = tenta_client.publish(
                                tenta.types.AcknowledgmentMessage(
                                    revision=message.message_body.config.
                                    revision,
                                    success=(
                                        message.message_body.status ==
                                        "accepted"
                                    ),
                                )
                            )
                        # received and startup not implemented in Tenta yet
                    if mqtt_message_id is not None:
                        active_messages.add((mqtt_message_id, message))

            published_message_ids: set[int] = set()
            for message_id, message in active_messages:
                if tenta_client.was_message_published(message_id):
                    published_message_ids.add(message_id)
                    messaging_agent.remove_messages([message.identifier])

            active_messages = set(
                filter(
                    lambda m: m[0] not in published_message_ids, active_messages
                )
            )
            time.sleep(5)

    except Exception as e:
        logger.exception(e, "The Tenta backend encountered an exception")
        return
