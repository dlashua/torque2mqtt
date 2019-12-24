# torque2mqtt

With an Android Phone, the Torque App (I've only tested with Torque Pro, but I think it'll work with Torque Lite) and a OBD2 Bluetooth/Wifi Adapter, you can get data about your car (speed, location, coolant temperature, odometer reading, etc, etc) into MQTT.

It’s a simple Python Service that can be used as a Torque Web Endpoint. It publishes your Torque statistics to an MQTT topic.

I don’t think it REQUIRES Torque Pro, however, I’ve not tested at all with Torque Lite. So if you try it with Lite, please let me know if it works.

This is a first pass implementation, so unit conversion and other such "nice things" need to be handled externally (conversion code in the consumer, Home Assistant Template Sensors, AppDaemon code, whatever). By default, all Torque units are metric and, therefore, all the metrics published will be in metric units.

This implementation has no security, authentication, verification, or conversion. Pull Requests are quite welcome, however.

# Running From Source Tree

run with `python3 server.py -c /directory/containing/config.yaml`

See config.yaml.example for configuration elements.

# Running From Docker

Docker Builds are available here:
https://hub.docker.com/r/dlashua/torque2mqtt

`docker run -d -v /path/to/config:/config -p 5000:5000 dlashua/torque2mqtt`

# Running with docker-compose

```
version: "3.4"

services:
  torque2mqtt:
    image: dlashua/torque2mqtt
    restart: unless-stopped
    container_name: torque2mqtt
    ports:
      - 5000:5000
    volumes:
      - ./config:/config
```
