import os
import time
from threading import Thread
from flask import Flask
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
import json
import logging

# ENV variables
MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC")

INFLUX_URL = os.environ.get("INFLUX_URL")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN")
INFLUX_ORG = os.environ.get("INFLUX_ORG")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET")

# Flask app (for health check)
app = Flask(__name__)

@app.route("/health")
def health():
    return "ok"

# Influx client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api()

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()  # string
    try:
        batch = json.loads(payload)  # now it's a list of dicts
    except json.JSONDecodeError:
        print("Invalid JSON received:", payload)
        return

    for item in batch:
        try:
            measurement = item.get("measurement", "unknown")
            code = item.get("code", "unknown")
            value = float(item.get("value", 0))
            simulated = item.get("simulated", False)

            point = (
                Point(measurement)
                .tag("topic", msg.topic)
                .tag("code", code)
                .field("value", value)
                .field("simulated", 1 if simulated else 0)  # <-- store as int
                .time(time.time_ns())
            )


            write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)
            log.info(f"Saved point: {item}")

        except Exception as e:
            log.warning("Failed to write point:", e)

def mqtt_thread():
    client = mqtt.Client("flask-mqtt")
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

# Start MQTT in background thread
Thread(target=mqtt_thread, daemon=True).start()

if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    )
    log = logging.getLogger("mqtt-influx")
    log.info("ENV CONFIG")
    log.info(f"MQTT_BROKER={MQTT_BROKER}")
    log.info(f"MQTT_TOPIC={MQTT_TOPIC}")
    log.info(f"INFLUX_URL={INFLUX_URL}")
    log.info(f"INFLUX_BUCKET={INFLUX_BUCKET}")
    app.run(host="0.0.0.0", port=5000)
