import signal
from typing import Any, Optional
import json
import multiprocessing.synchronize
import os
import ssl
import time
import paho.mqtt.client
import pydantic
import tum_esm_utils
import src


def run(
    config: src.types.Config,
    logger: src.utils.Logger,
    teardown_indicator: multiprocessing.synchronize.Event,
) -> None:
    """The main procedure for the ThingsBoard backend.

    Args:
        config: The configuration object.
        logger: The logger object.
        teardown_indicator: The event that is set when the procedure should terminate.
    """
    assert config.backend is not None
    assert config.backend.provider == "thingsboard"
    messaging_agent = src.utils.MessagingAgent()

    # parse incoming config messages

    def on_config_message(
        client: paho.mqtt.client.Client,
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
            # cannot send a rejection because we dont know a revision
            # the rejection still shows up in the logs

    # active = in the process of sending
    active_messages: set[tuple[paho.mqtt.client.MQTTMessageInfo,
                               src.types.MessageQueueItem]] = set()
    thingsboard_client: Optional[paho.mqtt.client.Client] = None
    exponential_backoff = src.utils.ExponentialBackoff(logger, buckets=[120, 900, 3600])
    teardown_receipt_time: Optional[float] = None

    try:
        logger.info("Setting up ThingsBoard backend")
        logger.debug("Registering the teardown procedure")

        def teardown_handler(*args: Any) -> None:
            if thingsboard_client is not None:
                logger.debug("Tearing down the ThingsBoard client")
                thingsboard_client.loop_stop()
                thingsboard_client.disconnect()
            logger.debug("Finishing the teardown")

        signal.signal(signal.SIGINT, teardown_handler)
        signal.signal(signal.SIGTERM, teardown_handler)

        def connect(
        ) -> tuple[paho.mqtt.client.Client, set[tuple[int, src.types.MessageQueueItem]]]:
            assert config.backend is not None
            logger.info("Connecting to ThingsBoard backend")
            thingsboard_client = paho.mqtt.client.Client(
                client_id=config.backend.mqtt_client_id,
                protocol=4,
            )
            thingsboard_client.username_pw_set(
                username=config.backend.mqtt_username,
                password=config.backend.mqtt_password,
            )
            thingsboard_client.tls_set(
                ca_certs=os.path.join(
                    src.constants.PROJECT_DIR,
                    "config",
                    "thingsboard-cloud-ca-root.pem",
                ),
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                # possibly add your own TLS configuration here
            )
            thingsboard_client.tls_insecure_set(False)
            thingsboard_client.on_message = on_config_message
            thingsboard_client.connect(
                host=config.backend.mqtt_host,
                port=config.backend.mqtt_port,
                keepalive=120,
            )
            thingsboard_client.subscribe(topic="v1/devices/me/attributes")
            thingsboard_client.loop_start()
            thingsboard_client.publish(
                f"v1/devices/me/attributes/request/{int(time.time()*1000)}",
                json.dumps({"sharedKeys": "configuration"})
            )
            logger.info("ThingsBoard connection has been set up")
            return thingsboard_client, set()

        tum_esm_utils.timing.set_alarm(
            20, "Could not connect to ThingsBoard backend within 20 seconds"
        )
        thingsboard_client, active_messages = connect()
        tum_esm_utils.timing.clear_alarm()

        # worst case is 8 seconds per messages (which is already very very slow)
        MAX_LOOP_TIME = config.backend.max_parallel_messages * 8 + 5
        tum_esm_utils.timing.set_alarm(
            MAX_LOOP_TIME,
            f"The ThingsBoard backend did not finish one loop within {MAX_LOOP_TIME} seconds"
        )

        def send_data(
            timestamp: float,
            data: dict[str, Any],
        ) -> paho.mqtt.client.MQTTMessageInfo:
            return thingsboard_client.publish(
                "v1/devices/me/telemetry",
                json.dumps({"ts": int(timestamp * 1000), "values": data}),
            )

        while True:
            signal.alarm(MAX_LOOP_TIME)
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
                        logger.debug(
                            "Max. drain time reached, stopping the Tenta backend"
                        )
                        return

                if not thingsboard_client.is_connected():
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
                                              for m in active_messages},
                    )
                    for message in new_messages:
                        message_info: Optional[paho.mqtt.client.MQTTMessageInfo] = None
                        if message.message_body.variant == "data":
                            message_info = send_data(
                                message.timestamp, message.message_body.data
                            )
                        if message.message_body.variant == "log":
                            message_info = send_data(
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
                            message_info = send_data(
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
                logger.error("The ThingsBoard backend is not connected")

                tum_esm_utils.timing.set_alarm(
                    20, "Could not tear down ThingsBoard backend within 20 seconds"
                )
                teardown_handler()
                tum_esm_utils.timing.clear_alarm()

                if teardown_receipt_time is not None:
                    # the backoff procedure should not prevent remaining messages from being sent
                    logger.debug(
                        "Sleeping only 5 seconds because a teardown has been issued"
                    )
                    time.sleep(5)
                else:
                    sleep_seconds = exponential_backoff.sleep()
                    if sleep_seconds == exponential_backoff.buckets[-1]:
                        logger.debug("Fully tearing down the procedure")
                        return

                tum_esm_utils.timing.set_alarm(
                    20, "Could not reconnect to ThingsBoard backend within 20 seconds"
                )
                thingsboard_client, active_messages = connect()
                tum_esm_utils.timing.clear_alarm()

    except Exception as e:
        logger.exception(e, "The Thingsboard backend encountered an exception")
        return
