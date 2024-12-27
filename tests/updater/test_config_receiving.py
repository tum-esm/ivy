import time
import pytest
import paho.mqtt.client


@pytest.mark.order(8)
@pytest.mark.updater
def test_connection_to_test_broker() -> None:
    client = paho.mqtt.client.Client(
        callback_api_version=paho.mqtt.client.CallbackAPIVersion.VERSION2,
        clean_session=True,
    )
    client.username_pw_set(username="test_username", password="test_password")
    r = client.connect(host="localhost", port=1883)
    assert r == 0, f"Connection to test broker failed: {r}"
    client.subscribe(topic="v1/devices/me/attributes")
    client.loop_start()
    time.sleep(0.4)
    assert client.is_connected(), "Client is not connected"
    time.sleep(0.4)
    assert client.is_connected(), "Client is not connected"
    message_info = client.publish(topic="somerandomtopic", payload="somerandompayload")
    time.sleep(0.4)
    assert message_info.is_published(), "Message was not published"
    client.loop_stop()
    client.disconnect()
    assert not client.is_connected(), "Client is still connected"


@pytest.mark.order(8)
@pytest.mark.updater
def test_tenta_config_receiving() -> None:
    # TODO: test whether messages sent to the broker are received by the backend and correctly put into the messaging queue
    # TODO: test this using a few invalid and a few valid messages
    pass


@pytest.mark.order(8)
@pytest.mark.updater
def test_thingsboard_config_receiving() -> None:
    # TODO: test whether messages sent to the broker are received by the backend and correctly put into the messaging queue
    # TODO: test this using a few invalid and a few valid messages
    pass
