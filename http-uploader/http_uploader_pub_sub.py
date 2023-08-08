"""This file contains the HTTPUploaderPubSub class which is a child class of BaseMQTTPubSub. The
HTTP UploaderPubSub writes data published to on the telemetry topic and posts that to an
HTTP endpoint. 
"""
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
    """This class reads MQTT topic data and posts it to an HTTP webhook.

    Args:
        BaseMQTTPubSub (BaseMQTTPubSub): parent class written in the EdgeTech Core module.
    """

    def __init__(
        self: Any,
        telemetry_json_topic: str,
        webhook_url: str,
        webhook_token: str,
        debug: bool = False,
        **kwargs: Any,
    ):
        """The HTTPUploaderPubSub takes a topic and webhook/webhook validation information to craft
        a payload to POST to an HTTP endpoint, currently directed at Tag.IO.

        Args:
            telemetry_json_topic (str): topic to read data from, currently only telemetry is posted.
            webhook_url (str): the URL of the webhook to POST to.
            webhook_token (str): the token to validate POST.
            debug (bool, optional):If the debug mode is turned on, log statements print to stdout.
            Defaults to False.
        """
        # Pass environment variables as parameters (include **kwargs) in super().__init__()
        super().__init__(**kwargs)

        # assign class attributes
        self.telemetry_json_topic = telemetry_json_topic
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
        """Callback to trigger HTTP POST of message when topic data is received.

        Args:
           _client (mqtt.Client): the MQTT client that was instantiated in the constructor.
           _userdata (Dict[Any,Any]): data passed to the callback through the MQTT paho Client
           class constructor or set later through user_data_set().
           msg (Any): the received message over the subscribed channel that includes
           the topic name and payload after decoding.
        """
        # decode message
        payload = json.loads(str(msg.payload.decode("utf-8")))
        if self.debug:
            print(f"payload: {payload}")

        # POST header for validation (this if for Tag.IO)
        headers = {"Device-Token": self.webhook_token}
        try:
            # execute POST
            result = httpx.post(
                self.webhook_url, headers=headers, json=payload, timeout=5.0
            )
            if self.debug:
                print(f"POST status: {result.status_code}")
        except httpx.RequestError as exception:
            print(f"HTTP POST failed because: {exception}")

    def main(self: Any) -> None:
        """Main loop and function that setup the heartbeat to keep the TCP/IP
        connection alive and publishes the data to the MQTT broker and keeps the
        main thread alive.
        """
        # schedule heartbeat
        schedule.every(10).seconds.do(
            self.publish_heartbeat, payload="HTTP Uploader Heartbeat"
        )

        # subscript to telemetry topic
        self.add_subscribe_topic(self.telemetry_json_topic, self._http_upload_callback)

        while True:
            try:
                # run heartbeat and anything else scheduled if clock is up
                schedule.run_pending()
                # include a sleep so loop does not run at CPU time
                sleep(0.001)

            except KeyboardInterrupt as exception:
                if self.debug:
                    print(exception)


if __name__ == "__main__":
    uploader = HTTPUploaderPubSub(
        telemetry_json_topic=str(os.environ.get("TELEMETRY_JSON_TOPIC")),
        webhook_url=str(os.environ.get("WEBHOOK_URL")),
        webhook_token=str(os.environ.get("WEBHOOK_TOKEN")),
        mqtt_ip=os.environ.get("MQTT_IP"),
    )
    uploader.main()
