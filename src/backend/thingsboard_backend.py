import os
import time
from typing import Optional
import paho.mqtt.client
import tb_device_mqtt
import src


def run_thingsboard_backend(
    config: src.types.Config,
    logger: src.utils.Logger,
) -> None:
    assert config.backend is not None
    assert config.backend.provider == "thingsboard"

    try:
        logger.info("Starting ThingsBoard backend")
        thingsboard_client = tb_device_mqtt.TBDeviceMqttClient(
            host=config.backend.mqtt_host,
            port=config.backend.mqtt_port,
            username=config.backend.mqtt_identifier,
            password=config.backend.mqtt_password,
        )
        thingsboard_client.connect(
            tls=True,
            timeout=15,
            ca_certs=os.path.join(
                src.constants.PROJECT_DIR, "config", "tb-cloud-root-ca.pem"
            ),
            # TODO: possibly add your TLS configuration here: we recommend
            #       including the TLS certificate files in your repository
            #       and only changing this with a software update
        )

        # TODO: add callback equivalent to the tenta backend
        thingsboard_client.subscribe_to_attribute("config", ...)
        logger.info("Thingsboard client has been set up")

        # active = in the process of sending
        messaging_agent = src.utils.MessagingAgent()
        active_messages: set[tuple[paho.mqtt.client.MQTTMessageInfo,
                                   src.types.MessageQueueItem]] = set()

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
                    result: Optional[tb_device_mqtt.TBPublishInfo] = None
                    if message.message_body.variant == "data":
                        result = thingsboard_client.send_telemetry(
                            message.message_body.data
                        )
                    if message.message_body.variant == "log":
                        result = thingsboard_client.send_telemetry({
                            "logging": {
                                "level": message.message_body.level,
                                "subject": message.message_body.subject,
                                "body": message.message_body.body,
                            }
                        })
                    if message.message_body.variant == "config":
                        result = thingsboard_client.send_telemetry({
                            "configuration": {
                                "status": message.message_body.status,
                                "config": message.message_body.model_dump(),
                            }
                        })
                    if result is not None:
                        active_messages.add((result.message_info, message))

            # determine which messages have been published
            published_message_identifiers: set[int] = set()
            for message_info, message in active_messages:
                if message_info.is_published():
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
