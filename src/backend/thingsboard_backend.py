import os
from typing import Optional
import time
import json
import pydantic
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
        thingsboard_client.max_inflight_messages_set(
            config.backend.max_parallel_messages
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
        # the first element of the tuple is the mqtt message id
        messaging_agent = src.utils.MessagingAgent()
        active_messages: set[tuple[int, src.types.MessageQueueItem]] = set()

    except Exception as e:
        logger.exception(e, "The Tenta backend encountered an exception")
        return
