from aiohttp import web

import yaml
import paho.mqtt.client as mqtt
import json
import argparse
import time


assumedUnits = {
    "04": "%",
    "05": "°C",
    "0c": "rpm",
    "0d": "km/h",
    "0f": "°C",
    "11": "%",
    "1f": "km",
    "21": "km",
    "2f": "%",
    "31": "km",
}

assumedShortName = {
    "04": "engine_load",
    "05": "coolant_temp",
    "0c": "engine_rpm",
    "0d": "speed",
    "0f": "intake_temp",
    "11": "throttle_pos",
    "1f": "run_since_start",
    "21": "dis_mil_on",
    "2f": "fuel",
    "31": "dis_mil_off",
}

assumedFullName = {
    "04": "Engine Load",
    "05": "Coolant Temperature",
    "0c": "Engine RPM",
    "0d": "Vehicle Speed",
    "0f": "Intake Air Temperature",
    "11": "Throttle Position",
    "1f": "Distance Since Engine Start",
    "21": "Distance with MIL on",
    "2f": "Fuel Level",
    "31": "Distance with MIL off",
}

data = {}


async def process_torque(request):
    session = parse_fields(request.query)
    publish_data(session)
    return web.Response(text="OK!")


def parse_fields(qdata):  # noqa
    session = qdata.get("session")
    if session is None:
        raise Exception("No Session")

    if session not in data:
        data[session] = {
            "profile": {},
            "unit": {},
            "defaultUnit": {},
            "fullName": {},
            "shortName": {},
            "value": {},
            "unknown": [],
            "time": 0,
        }

    for key, value in qdata.items():
        if key.startswith("userUnit"):
            item = key[8:]
            data[session]["unit"][item] = value
            continue
        if key.startswith("userShortName"):
            item = key[13:]
            data[session]["shortName"][item] = value
            continue
        if key.startswith("userFullName"):
            item = key[12:]
            data[session]["fullName"][item] = value
            continue
        if key.startswith("defaultUnit"):
            item = key[11:]
            data[session]["defaultUnit"][item] = value
            continue
        if key.startswith("k"):
            item = key[1:]
            if len(item) == 1:
                item = "0" + item
            data[session]["value"][item] = value
            continue
        if key.startswith("profile"):
            item = key[7:]
            data[session]["profile"][item] = value
            continue
        if key == "eml":
            data[session]["profile"]["email"] = value
            continue
        if key == "time":
            data[session]["time"] = value
            continue
        if key == "v":
            data[session]["profile"]["version"] = value
            continue
        if key == "session":
            continue
        if key == "id":
            data[session]["profile"]["id"] = value
            continue

        data[session]["unknown"].append({"key": key, "value": value})

    return session


def slugify(name):
    return (
        name.lower()
        .replace("(", " ")
        .replace(")", " ")
        .strip()
        .replace(" ", "_")
    )


def get_field(session, key):
    name = data[session]["fullName"].get(key, assumedFullName.get(key, key))
    short_name = data[session]["shortName"].get(
        key, assumedShortName.get(key, key)
    )
    unit = data[session]["defaultUnit"].get(
        key, data[session]["unit"].get(key, assumedUnits.get(key, ""))
    )
    value = data[session]["value"].get(key)
    short_name = slugify(short_name)
    return {
        "name": name,
        "short_name": short_name,
        "unit": unit,
        "value": value,
    }


def get_profile(session):
    return data[session]["profile"]


def get_topic_prefix(session):
    topic = data[session]["profile"].get("Name")
    if topic is None:
        topic = data[session]["profile"].get("email")
    if topic is None:
        topic = session

    topic = slugify(topic)

    return config["mqtt"]["prefix"] + "/" + topic


def get_data(session):
    retdata = {}
    retdata["profile"] = get_profile(session)
    retdata["time"] = data[session]["time"]
    meta = {}

    for key, value in data[session]["value"].items():
        row_data = get_field(session, key)
        retdata[row_data["short_name"]] = row_data["value"]
        meta[row_data["short_name"]] = {
            "name": row_data["name"],
            "unit": row_data["unit"],
        }

    retdata["meta"] = meta

    return retdata


def publish_data(session):
    session_data = get_data(session)
    mqttc.publish(get_topic_prefix(session), json.dumps(session_data))


mqttc = None
mqttc_time = time.time()


def mqtt_on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("MQTT Connection Issue")
        exit()


def mqtt_on_disconnect(client, userdata, rc):
    print("MQTT Disconnected")
    if time.time() > mqttc_time + 10:
        mqttc_create()
    else:
        exit()


def mqttc_create():
    global mqttc
    global mqttc_time
    mqttc = mqtt.Client(client_id="torque", clean_session=True)
    mqttc.username_pw_set(
        username=config["mqtt"].get("username"),
        password=config["mqtt"].get("password"),
    )
    print("CALLING MQTT CONNECT")
    mqttc.connect(
        config["mqtt"]["host"], config["mqtt"].get("port", 1883), keepalive=60
    )
    mqttc.on_connect = mqtt_on_connect
    mqttc.mqtt_on_disconnect = mqtt_on_disconnect
    mqttc.loop_start()
    mqttc_time = time.time()


mqttc_create()

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "-c",
    "--config",
    required=True,
    help="Directory holding config.yaml and application storage",
)
args = argparser.parse_args()

configdir = args.config
if not configdir.endswith("/"):
    configdir = configdir + "/"

with open(configdir + "config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

if __name__ == "__main__":
    host = config.get("server", {}).get("ip", "0.0.0.0")
    port = config.get("server", {}).get("port", 5000)

    app = web.Application()
    app.router.add_get("/", process_torque)
    web.run_app(app, host=host, port=port)
