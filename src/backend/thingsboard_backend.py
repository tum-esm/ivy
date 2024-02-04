import json
import os
import ssl
import time
from typing import Any, Optional
import paho.mqtt.client
import pydantic
import src


def run_thingsboard_backend(
    config: src.types.Config,
    logger: src.utils.Logger,
) -> None:
    assert config.backend is not None
    assert config.backend.provider == "thingsboard"

    def on_config_message(
        c: paho.mqtt.client.Client,
        userdata: Any,
        message: paho.mqtt.client.MQTTMessage,
    ) -> None:
        try:
            data = json.loads(message.payload.decode())
            assert isinstance(data, dict)
            if "shared" in data.keys():
                data = data["shared"]
            assert isinstance(data, dict)
            if "configuration" not in data.keys():
                return
            foreign_config = src.types.ForeignConfig.model_validate_json(
                data["configuration"]
            )
            with src.utils.StateInterface.update() as state:
                state.pending_configs.append(foreign_config)
            logger.info(
                f"Config with revision {foreign_config.general.config_revision} was parsed"
            )
        except (AssertionError, json.JSONDecodeError) as e:
            logger.exception(e, f"Received config message in invalid format")
        except pydantic.ValidationError as e:
            logger.error(
                f"Received config message could not be parsed",
                details=e.json(indent=4),
            )

    try:
        logger.info("Setting up ThingsBoard backend")
        client = paho.mqtt.client.Client(
            client_id=config.backend.mqtt_client_id,
            protocol=4,
        )
        client.username_pw_set(
            username=config.backend.mqtt_username,
            password=config.backend.mqtt_password,
        )
        client.tls_set(
            ca_certs=os.path.join(
                src.constants.PROJECT_DIR,
                "config",
                "thingsboard-cloud-ca-root.pem",
            ),
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            # possibly add your own TLS configuration here
        )
        client.tls_insecure_set(False)
        client.on_message = on_config_message

        logger.info("Connecting to ThingsBoard")
        client.connect(
            host=config.backend.mqtt_host,
            port=config.backend.mqtt_port,
            keepalive=120,
        )
        client.subscribe(topic="v1/devices/me/attributes")
        client.loop_start()
        client.publish(
            f"v1/devices/me/attributes/request/{int(time.time()*1000)}",
            json.dumps({"sharedKeys": "configuration"})
        )
        time.sleep(0.5)

        assert client.is_connected()
        logger.info("Thingsboard client is connected")

        def send_telemetry(
            timestamp: float,
            data: dict[str, Any],
        ) -> paho.mqtt.client.MQTTMessageInfo:
            return client.publish(
                "v1/devices/me/telemetry",
                json.dumps({"ts": int(timestamp * 1000), "values": data}),
            )

        # active = in the process of sending
        messaging_agent = src.utils.MessagingAgent()
        active_messages: set[tuple[paho.mqtt.client.MQTTMessageInfo,
                                   src.types.MessageQueueItem]] = set()

        while True:
            # send new messages
            assert client.is_connected(
            ), "The Thingsboard client is not connected"

            open_message_slots = config.backend.max_parallel_messages - len(
                active_messages
            )
            if open_message_slots > 0:
                new_messages = messaging_agent.get_n_latest_messages(
                    open_message_slots,
                    excluded_message_ids={
                        m[1].identifier
                        for m in active_messages
                    },
                )
                for message in new_messages:
                    message_info: Optional[paho.mqtt.client.MQTTMessageInfo
                                          ] = None
                    if message.message_body.variant == "data":
                        message_info = send_telemetry(
                            message.timestamp, message.message_body.data
                        )
                    if message.message_body.variant == "log":
                        message_info = send_telemetry(
                            message.timestamp,
                            {
                                "logging": {
                                    "level": message.message_body.level,
                                    "subject": message.message_body.subject,
                                    "body": message.message_body.body,
                                }
                            },
                        )
                    if message.message_body.variant == "config":
                        message_info = send_telemetry(
                            message.timestamp,
                            {
                                "configuration": {
                                    "status": message.message_body.status,
                                    "config": message.message_body.model_dump(),
                                }
                            },
                        )
                    if message_info is not None:
                        active_messages.add((message_info, message))

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
                    published_message_identifiers,
                    active_messages,
                )
            )
            time.sleep(5)

    except Exception as e:
        logger.exception(e, "The Thingsboard backend encountered an exception")
        return
