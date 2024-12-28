import os
import ssl
import time
import pytest
import tenta
import paho.mqtt.client
import src


@pytest.mark.version_change
@pytest.mark.order(3)
@pytest.mark.integration
def test_connection_to_backend() -> None:
    config = src.types.Config.load()
    if config.backend is None:
        return

    if config.backend.provider == "tenta":
        tenta_client = tenta.TentaClient(
            mqtt_client_id=config.backend.mqtt_connection.client_id,
            mqtt_host=config.backend.mqtt_connection.host,
            mqtt_port=config.backend.mqtt_connection.port,
            mqtt_identifier=config.backend.mqtt_connection.username,
            mqtt_password=config.backend.mqtt_connection.password,
            sensor_identifier=config.general.system_identifier,
            # possibly add your TLS configuration here
        )
        assert tenta_client.client.is_connected(), "Client is not connected"
        tenta_client.teardown()

    if config.backend.provider == "thingsboard":
        thingsboard_client = paho.mqtt.client.Client(
            callback_api_version=paho.mqtt.client.CallbackAPIVersion.VERSION2,
            client_id=config.backend.mqtt_connection.client_id,
        )
        thingsboard_client.username_pw_set(
            username=config.backend.mqtt_connection.username,
            password=config.backend.mqtt_connection.password,
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
        thingsboard_client.connect(
            host=config.backend.mqtt_connection.host,
            port=config.backend.mqtt_connection.port,
            keepalive=120,
        )
        thingsboard_client.loop_start()
        assert thingsboard_client.is_connected(), "Client is not connected"
        time.sleep(1)
        assert thingsboard_client.is_connected(), "Client is not connected"
        thingsboard_client.loop_stop()
        thingsboard_client.disconnect()
