# edgetech-http-uploader

EdgeTech http upload utility for [edgetech-core](https://github.com/IQTLabs/edgetech-core/tree/main/examples).

Subscribe to a specified topic and save data passed over it as a file. 

## Parameters

The key environment variables specified in `docker-compose.yml`:
- `TELEMETRY_TOPIC` is a **string** value specifying which MQTT topic the filesaver should listen for data on
- `MQTT_IP` is a **string** value specifying the MQTT broker host

The key environment variables specified in `.env`:
- `WEBHOOK_URL` is a **string** value specifying the HTTP endpoint URL
- `WEBHOOK_TOKEN` is a **string** value specifying the HTTP header token for authenticating with the endpoint