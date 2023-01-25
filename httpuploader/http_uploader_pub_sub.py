import os
from time import sleep
import json
from typing import Any, Dict
import schedule
import paho.mqtt.client as mqtt
import httpx

from base_mqtt_pub_sub import BaseMQTTPubSub

# inherit functionality from BaseMQTTPubSub
class HTTPUploaderPubSub(BaseMQTTPubSub):
    def __init__(
        self: Any,
        telemetry_topic: str,
        webhook_url: str,
        webhook_token: str,
        debug: bool = True,
        **kwargs: Any,
    ):
        # Pass enviornment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)
        self.telemetry_topic = telemetry_topic
        self.webhook_url = webhook_url
        self.webhook_token = webhook_token
        self.debug = debug

        # Connect client in constructor
        self.connect_client()
        sleep(1)
        self.publish_registration("HTTP Uploader Module Registration")

    def _http_upload_callback(
        self: Any, _client: mqtt.Client, _userdata: Dict[Any, Any], msg: Any
    ) -> None:
        payload = json.loads(str(msg.payload.decode("utf-8")))
        if self.debug:
            print(f"payload: {payload}")

        headers = {"Device-Token": self.webhook_token}
        try:
            result = httpx.post(
                self.webhook_url, headers=headers, json=payload, timeout=5.0
            )
            if self.debug:
                print(f"POST status: {result.status_code}")
        except Exception as e:
            print(f"HTTP POST failed because: {e}")

    def main(self: Any) -> None:
        # schedule heartbeat
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="HTTP Uploader Heartbeat"
        )

        # subscript to telemetry topic
        self.add_subscribe_topic(self.telemetry_topic, self._http_upload_callback)

        while True:
            try:
                # run heartbeat and anything else scheduled if clock is up
                schedule.run_pending()
                # include a sleep so loop does not run at CPU time
                sleep(0.001)

            except Exception as e:
                if self.debug:
                    print(e)


if __name__ == "__main__":
    uploader = HTTPUploaderPubSub(
        telemetry_topic=str(os.environ.get("TELEMETRY_TOPIC")),
        webhook_url=str(os.environ.get("WEBHOOK_URL")),
        webhook_token=str(os.environ.get("WEBHOOK_TOKEN")),
        mqtt_ip=os.environ.get("MQTT_IP"),
    )
    uploader.main()
