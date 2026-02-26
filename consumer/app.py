import os
import time
import json
import queue
import logging
from threading import Thread

from flask import Flask, send_from_directory, Response,request
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


mqtt_client = None

# ── Logging (must be first so everything below can use `log`) ──────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("mqtt-influx")

# ── ENV variables ──────────────────────────────────────────────────────────────
MQTT_BROKER  = os.environ.get("MQTT_BROKER")
MQTT_TOPIC   = os.environ.get("MQTT_TOPIC")
MQTT_SEND_TOPIC = os.environ.get("MQTT_SEND_TOPIC")
INFLUX_URL   = os.environ.get("INFLUX_URL")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN")
INFLUX_ORG   = os.environ.get("INFLUX_ORG")
INFLUX_BUCKET= os.environ.get("INFLUX_BUCKET")

# ── InfluxDB client ────────────────────────────────────────────────────────────
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api     = influx_client.write_api(write_options=SYNCHRONOUS)
query_api     = influx_client.query_api()

# ── SSE broadcast queue ────────────────────────────────────────────────────────
clients: list[queue.Queue] = []

def broadcast(data: dict):
    for q in clients:
        q.put(data)
def on_message(client, userdata, msg):
    payload_str = msg.payload.decode()
    try:
        batch = json.loads(payload_str)
    except json.JSONDecodeError:
        log.warning("Invalid JSON received: %s", payload_str)
        return

    updates = {}
    for item in batch:
        measurement = item.get("measurement", "unknown")
        code        = item.get("code", "unknown")
        device_name = item.get("device_name", "pi")
        simulated   = item.get("simulated", False)

        if measurement == "alarm":
            send_mqtt_message(MQTT_SEND_TOPIC, {
                "code": "db",
                "value": 1,
                "device": item.get("device_name")
            })
            log.info(f"Buzzer triggered by alarm from {item.get('device_name')}")

        point = Point(measurement).tag("code", code).tag("device_name", device_name).time(time.time_ns())
        fields_written = 0

        # ── GSG special case: unpack accel/gyro lists ──────────────────────
        if code == "gsg":
            accel = item.get("accel", [0, 0, 0])
            gyro  = item.get("gyro",  [0, 0, 0])
            axes  = ["x", "y", "z"]
            for i, ax in enumerate(axes):
                point.field(f"accel_{ax}", float(accel[i]))
                point.field(f"gyro_{ax}",  float(gyro[i]))
            point.field("simulated", 1 if simulated else 0)
            fields_written = 6
        else:
            for k, v in item.items():
                if k in ["measurement", "code", "device_name", "simulated"]:
                    continue
                if isinstance(v, list):
                    continue
                try:
                    if not code in ['ir','dms']:
                        point.field(k, float(v))
                    else:
                        if isinstance(v, str) and v.strip():
                            point.field(k, v) 

                except (ValueError, TypeError):
                    if isinstance(v, str) and v.strip():
                        point.field(k, v)  # ← stores "05:14" as string
                fields_written += 1  # ← outside try/except
            point.field("simulated", 1 if simulated else 0)
        # ──────────────────────────────────────────────────────────────────

        if fields_written > 0:
            try:
                write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)
                log.info(f"Wrote point: {item}")
                add_update(updates, code, measurement, device_name, item)
            except Exception:
                log.warning("Failed to write point", exc_info=True)

    if updates:
        broadcast(updates)
def add_update(updates, code, measurement, device_name, payload):
    if payload is None:
        payload = {}

    update = {
        "measurement": measurement,
        "device_name": device_name,
        "time": str(time.time()),
    }

    # ── GSG: unpack lists into named fields for JS ─────────────────────────
    if code == "gsg":
        accel = payload.get("accel", [0, 0, 0])
        gyro  = payload.get("gyro",  [0, 0, 0])
        update["accel_x"] = accel[0]
        update["accel_y"] = accel[1]
        update["accel_z"] = accel[2]
        update["gyro_x"]  = gyro[0]
        update["gyro_y"]  = gyro[1]
        update["gyro_z"]  = gyro[2]
    else:
        # All other sensors: pass through as-is
        for k, v in payload.items():
            if k not in ["measurement", "code", "device_name", "simulated"]:
                update[k] = v

    updates[code] = update
# ── MQTT thread ────────────────────────────────────────────────────────────────
def mqtt_thread():
    global mqtt_client
    mqtt_client = mqtt.Client("flask-mqtt")
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, 1883)
    mqtt_client.subscribe("pi1")
    mqtt_client.subscribe("pi2")
    mqtt_client.subscribe("pi3")
    mqtt_client.loop_forever()


Thread(target=mqtt_thread, daemon=True).start()


def send_mqtt_message(topic: str, payload: dict):
    if mqtt_client is None:
        log.warning("MQTT client not ready")
        return

    mqtt_client.publish(topic, json.dumps(payload))
    log.info(f"Published to {topic}: {payload}")


# ── Flask app ──────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="/")


@app.route("/api/mqtt/send", methods=["POST"])
def api_mqtt_send():
    data = request.json

    topic = data.get("topic", MQTT_SEND_TOPIC)
    payload = data.get("payload", {})

    send_mqtt_message(topic, payload)

    return {"status": "sent"}

@app.route("/health")
def health():
    return "ok"

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)
@app.route("/api/sensors/<device>")
def get_sensors_by_device(device):
    device_codes = {
        "pi1": ["ds1", "dus1", "dpir1", "dl", "db", "dms"],
        "pi2": ["ds2", "dus2", "dpir2", "4sd", "btn", "dht3", "gsg"],
        "pi3": ["dht1", "dht2", "ir", "brgb", "lcd", "dpir3"],
    }

    if device not in device_codes:
        return {"error": "Unknown device"}, 400

    codes_filter = " or ".join([f'r.code == "{c}"' for c in device_codes[device]])

    # For most sensors filter by "value", for gsg/dht get all fields
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => {codes_filter})
        |> last()
    '''

    tables = query_api.query(query, org=INFLUX_ORG)
    result = {}
    for table in tables:
        for record in table.records:
            code  = record.values.get("code")
            field = record.get_field()
            if field == "simulated":
                continue
            if code not in result:
                result[code] = {"time": str(record.get_time()), "measurement": record.get_measurement()}
            result[code][field] = record.get_value()

    return result

@app.route("/api/grafana/panels/<device>")
def get_grafana_panels(device):
    base = "http://localhost:3000/d-solo/smarthome/smarthome-iot?orgId=1&refresh=5s&theme=dark&__feature.dashboardSceneSolo=true"
    
    panels = {
        "pi1": [
            { "label": "DS1 — Door",        "url": f"{base}&panelId=panel-1" },
            { "label": "DUS1 — Ultrasonic", "url": f"{base}&panelId=panel-2" },
            { "label": "DPIR1 — Motion",    "url": f"{base}&panelId=panel-3" },
            { "label": "DL — Light",        "url": f"{base}&panelId=panel-4" },
            { "label": "DB — Buzzer",       "url": f"{base}&panelId=panel-5" },
            { "label": "DMS — Switch",      "url": f"{base}&panelId=panel-6" },
            { "label": "DUS1 History",      "url": f"{base}&panelId=panel-7" },
            { "label": "DPIR1 History",     "url": f"{base}&panelId=panel-8" },
        ],
        "pi2": [
            { "label": "DS2 — Garage Door", "url": f"{base}&panelId=panel-9" },
            { "label": "DUS2 — Ultrasonic", "url": f"{base}&panelId=panel-10" },
            { "label": "DPIR2 — Motion",    "url": f"{base}&panelId=panel-11" },
            { "label": "DHT3 — Temp",       "url": f"{base}&panelId=panel-12" },
            { "label": "BTN — Button",      "url": f"{base}&panelId=panel-13" },
            { "label": "GSG — Gyroscope",   "url": f"{base}&panelId=panel-14" },
            { "label": "DHT3 History",      "url": f"{base}&panelId=panel-15" },
            { "label": "GSG History",       "url": f"{base}&panelId=panel-16" },
        ],
        "pi3": [
            { "label": "DHT1 — Bedroom",    "url": f"{base}&panelId=panel-17" },
            { "label": "DHT2 — Master Bed", "url": f"{base}&panelId=panel-18" },
            { "label": "DPIR3 — Motion",    "url": f"{base}&panelId=panel-19" },
            { "label": "IR — Infrared",     "url": f"{base}&panelId=panel-20" },
            { "label": "BRGB — RGB Light",  "url": f"{base}&panelId=panel-21" },
            { "label": "Temp Comparison",   "url": f"{base}&panelId=panel-22" },
            { "label": "Persons Now",       "url": f"{base}&panelId=panel-23" },
            { "label": "Persons History",   "url": f"{base}&panelId=panel-24" },
            { "label": "LCD",   "url": f"{base}&panelId=panel-25" },
        ],
    }

    if device not in panels:
        return {"error": "Unknown device"}, 400

    return panels[device]

@app.route("/api/stream")
def stream():
    def event_stream():
        q = queue.Queue()
        clients.append(q)
        try:
            while True:
                try:
                    data = q.get(timeout=30)
                    yield f"data: {json.dumps(data)}\n\n"
                except queue.Empty:
                    yield "data: {}\n\n"  # heartbeat
        finally:
            clients.remove(q)

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("ENV CONFIG")
    log.info(f"MQTT_BROKER={MQTT_BROKER}")
    log.info(f"MQTT_TOPIC={MQTT_TOPIC}")
    log.info(f"INFLUX_URL={INFLUX_URL}")
    log.info(f"INFLUX_BUCKET={INFLUX_BUCKET}")
    app.run(host="0.0.0.0", port=5000)