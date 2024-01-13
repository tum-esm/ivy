import time
from typing import Optional
import tenta
import src


def run_tenta_backend(config: src.types.Config) -> None:
    assert config.backend is not None
    assert config.backend.provider == "tenta"

    tenta_client = tenta.TentaClient(
        mqtt_host=config.backend.mqtt_host,
        mqtt_port=config.backend.mqtt_port,
        mqtt_identifier=config.backend.mqtt_identifier,
        mqtt_password=config.backend.mqtt_password,
        sensor_identifier=config.system_identifier,
        on_config_message=lambda x: ...,
    )
    messaging_agent = src.utils.MessagingAgent()

    # TODO: subscribe to configs
    # TODO: write new configs to state file when they arrive

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
                excluded_message_ids={m[1].identifier
                                      for m in active_messages}
            )
            for message in new_messages:
                mqtt_message_id: Optional[int] = None
                if message.message_body.variant == "data":
                    mqtt_message_id = tenta_client.publish(
                        tenta.types.MeasurementMessage(
                            value=message.message_body.data,
                            revision=config.config_revision,
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
                            revision=config.config_revision,
                        )
                    )
                if message.message_body.variant == "config":
                    if message.message_body.status in ["accepted", "rejected"]:
                        mqtt_message_id = tenta_client.publish(
                            tenta.types.ConfigurationMessage(
                                revision=message.message_body.config.revision,
                                status=message.message_body.status,
                            )
                        )
                    # received and startup not implemented in Tenta yet
                if mqtt_message_id is not None:
                    active_messages.add((mqtt_message_id, message))

        published_messages: set[int] = set()
        for message in active_messages:
            if tenta_client.was_message_published(message[0]):
                published_messages.append(message)
                messaging_agent.remove_messages([message[1].identifier])

        active_messages = active_messages.difference(published_messages)

        time.sleep(2)
