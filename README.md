# torque2mqtt

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
