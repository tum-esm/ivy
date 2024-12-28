import json
import os
import time
from typing import Any
import pytest
import paho.mqtt.client
from ...fixtures import provide_test_config
import src


@pytest.mark.order(8)
@pytest.mark.updater
def test_connection_to_test_broker() -> None:
    client = paho.mqtt.client.Client(
        callback_api_version=paho.mqtt.client.CallbackAPIVersion.VERSION2,
        client_id="test_connection_to_test_broker",
    )
    client.username_pw_set(username="test_username", password="test_password")
    r = client.connect(host="localhost", port=1883)
    assert r == 0, f"Connection to test broker failed: {r}"
    client.subscribe(topic="v1/devices/me/attributes")
    client.loop_start()
    time.sleep(0.4)
    assert client.is_connected(), "Client is not connected"
    message_info = client.publish(topic="somerandomtopic", payload="somerandompayload")
    time.sleep(0.4)
    assert message_info.is_published(), "Message was not published"
    client.loop_stop()
    client.disconnect()
    assert not client.is_connected(), "Client is still connected"


def _pub(topic: str, message: Any) -> None:
    exit_code = os.system(
        f"""mosquitto_pub -h localhost -p 1883 \\
        -u 'test_username' -P 'test_password' \\
        -t '{topic}' -m '{json.dumps(message)}'"""
    )
    assert exit_code == 0, f"Failed to publish message to topic {topic}"
    time.sleep(0.2)


@pytest.mark.order(8)
@pytest.mark.updater
def test_tenta_config_receiving(provide_test_config: src.types.Config) -> None:
    with src.utils.StateInterface.update() as state:
        state.pending_configs = []

    config = provide_test_config
    config.backend = src.types.config.BackendConfig(
        provider="tenta",
        mqtt_connection=src.types.config.MQTTBrokerConfig(
            host="localhost",
            port=1883,
            client_id=config.general.system_identifier + "-tenta-config-receiving",
            username="test_username",
            password="test_password",
        ),
    )
    backend_lm = src.utils.LifecycleManager(
        config=config,
        entrypoint=src.backend.tenta_backend.run,
        name="tenta-backend",
        variant="backend",
    )
    backend_lm.start_procedure()
    time.sleep(0.5)
    assert backend_lm.procedure_is_running(), "Backend is not running"
    time.sleep(0.5)

    current_state = src.utils.StateInterface.load()
    assert (
        len(current_state.pending_configs) == 0
    ), f"There are pending configs in the state: {current_state.pending_configs}"

    def c(rev: int) -> dict[Any, Any]:
        return {
            "configuration": {"general": {"software_version": f"0.0.{rev}"}},
            "revision": rev,
        }

    try:
        # 1. send valid config to wrong topic
        _pub(topic=f"config/{config.general.system_identifier}", message=c(1))

        # 2. send valid config to correct topic but wrong client_id
        _pub(topic=f"configurations/{config.general.system_identifier}wrong", message=c(2))

        # 3. send valid config to correct topic
        _pub(topic=f"configurations/{config.general.system_identifier}", message=c(3))

        # 4. send invalid config to correct topic
        _pub(topic=f"configurations/{config.general.system_identifier}", message={"other": {}})

        # 5. send invalid config to wrong topic
        _pub(topic=f"config/{config.general.system_identifier}", message={"other": {}})

        # 6. send valid config to correct topic
        _pub(topic=f"configurations/{config.general.system_identifier}", message=c(4))

        start_time = time.time()
        while True:
            current_state = src.utils.StateInterface.load()
            if len(current_state.pending_configs) > 0:
                assert current_state.pending_configs[0].general.config_revision == 3
            if len(current_state.pending_configs) > 1:
                assert current_state.pending_configs[1].general.config_revision == 4
                break
            if (time.time() - start_time) > 15:
                raise Exception("Timeout")
            time.sleep(2)
    finally:
        backend_lm.teardown()


@pytest.mark.order(8)
@pytest.mark.updater
def test_thingsboard_config_receiving(provide_test_config: src.types.Config) -> None:
    with src.utils.StateInterface.update() as state:
        state.pending_configs = []

    config = provide_test_config
    config.backend = src.types.config.BackendConfig(
        provider="thingsboard",
        mqtt_connection=src.types.config.MQTTBrokerConfig(
            host="localhost",
            port=1883,
            client_id=config.general.system_identifier + "-thingsboard-config-receiving",
            username="test_username",
            password="test_password",
        ),
    )
    backend_lm = src.utils.LifecycleManager(
        config=config,
        entrypoint=src.backend.thingsboard_backend.run,
        name="thingsboard-backend",
        variant="backend",
    )
    backend_lm.start_procedure()
    time.sleep(0.5)
    assert backend_lm.procedure_is_running(), "Backend is not running"
    time.sleep(0.5)

    current_state = src.utils.StateInterface.load()
    assert (
        len(current_state.pending_configs) == 0
    ), f"There are pending configs in the state: {current_state.pending_configs}"

    def c(rev: int) -> dict[Any, Any]:
        return {
            "shared": {
                "configuration": {
                    "general": {
                        "software_version": f"0.0.{rev}",
                        "config_revision": rev,
                    }
                }
            },
        }

    try:
        # 1. send valid config to wrong topic
        _pub(topic="v1/devices/me/attributeseee", message=c(5))

        # 2. send valid config to wrong topic
        _pub(topic="v1/devices/me", message=c(6))

        # 3. send valid config to correct topic
        _pub(topic="v1/devices/me/attributes", message=c(7))

        # 4. send invalid config to correct topic
        _pub(topic="v1/devices/me/attributes", message={"other": {}})

        # 5. send invalid config to wrong topic
        _pub(topic="v1/devices/me/attributes", message={"other": {}})

        # 6. send valid config to correct topic
        _pub(topic="v1/devices/me/attributes", message=c(8))

        start_time = time.time()
        while True:
            current_state = src.utils.StateInterface.load()
            if len(current_state.pending_configs) > 0:
                assert current_state.pending_configs[0].general.config_revision == 7
            if len(current_state.pending_configs) > 1:
                assert current_state.pending_configs[1].general.config_revision == 8
                break
            if (time.time() - start_time) > 15:
                raise Exception("Timeout")
            time.sleep(2)
    finally:
        backend_lm.teardown()
