# torque2mqtt

With an Android Phone, the Torque App (I've only tested with Torque Pro, but I think it'll work with Torque Lite) and a OBD2 Bluetooth/Wifi Adapter, you can get data about your car (speed, location, coolant temperature, odometer reading, etc, etc) into MQTT.

It’s a simple Python Service that can be used as a Torque Web Endpoint. It publishes your Torque statistics to an MQTT topic.

I don’t think it REQUIRES Torque Pro, however, I’ve not tested at all with Torque Lite. So if you try it with Lite, please let me know if it works.

This is a first pass implementation. Some units can be converted to imperial, but more work is likely needed. By default, all units are metric (from Torque). Adding `imperial: True` to your config will attempt to convert to Imperial units.

This implementation has no security, authentication, or verification.

Pull Requests are VERY welcome!

# config.yaml example
```
server:
  ip: 0.0.0.0
  port: 5000

mqtt:
  host: 192.168.0.100
  port: 1883
  username: username
  password: password
  prefix: torque

imperial: True
```

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
