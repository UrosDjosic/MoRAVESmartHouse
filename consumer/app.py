import os
import time
from threading import Thread
from flask import Flask, send_from_directory
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import logging

# ENV variables
MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC")

INFLUX_URL = os.environ.get("INFLUX_URL")
INFLUX_TOKEN = os.environ.get("INFLUX_TOKEN")
INFLUX_ORG = os.environ.get("INFLUX_ORG")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET")

app = Flask(__name__,static_folder = "static", static_url_path = "/")

@app.route("/health")
def health():
    return "ok"

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/path:path")
def static_files(path):
    return send_from_directory("static",path)

# Influx client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)
query_api = influx_client.query_api()

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode() 
    try:
        batch = json.loads(payload) 
    except json.JSONDecodeError:
        print("Invalid JSON received:", payload)
        return

    for item in batch:
        try:
            measurement = item.get("measurement", "unknown")
            code = item.get("code", "unknown")
            value_raw = item.get("value", 0)
        
            if code in ['dpir1','dpir2']:
                dus_code = 'dus1' if code == 'dpir1' else 'dus2'
                update_num_persons(dus_code)

            try:
                value = float(value_raw)
            except (ValueError, TypeError):
                value = 1 
            simulated = item.get("simulated", False)

            point = (
                Point(measurement)
                .tag("code", code)
                .field("value", value)
                .field("simulated", 1 if simulated else 0)
                .time(time.time_ns())
            )

            write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)
            log.info(f"Saved point: {item}")

        except Exception:
            log.warning("Failed to write point", exc_info=True)

def update_num_persons(code: str):
    """
    Queries the last 5 seconds of ultrasonic distance readings for the given
    sensor code (dus1 or dus2), determines direction of movement by comparing
    the first half vs second half of readings (increasing = leaving, 
    decreasing = entering), then increments or decrements the 'persons' measurement.
    """
    try:
        flux_query = f'''
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -5s)
              |> filter(fn: (r) => r._measurement == "door ultrasonic")
              |> filter(fn: (r) => r.code == "{code}")
              |> filter(fn: (r) => r._field == "value")
              |> sort(columns: ["_time"], desc: false)
        '''

        tables = query_api.query(flux_query, org=INFLUX_ORG)
        records = [record for table in tables for record in table.records]

        if len(records) < 3:
            log.info(f"[{code}] Not enough data points to determine direction ({len(records)} points), skipping.")
            return

        values = [r.get_value() for r in records]

        # Compare average of first half vs second half
        mid = len(values) // 2
        avg_first = sum(values[:mid]) / mid
        avg_second = sum(values[mid:]) / (len(values) - mid)

        THRESHOLD = 5.0  # cm — ignore noise below this delta

        delta = avg_second - avg_first
        if abs(delta) < THRESHOLD:
            log.info(f"[{code}] Movement delta {delta:.2f} below threshold, ignoring.")
            return

        if delta > 0:
            # Distance increasing → person moving away → leaving
            direction = "leaving"
            person_delta = -1
        else:
            # Distance decreasing → person approaching → entering
            direction = "entering"
            person_delta = 1

        log.info(f"[{code}] Person detected {direction} (avg_first={avg_first:.1f}, avg_second={avg_second:.1f})")

        # Query current persons count
        count_query = f'''
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -30d)
              |> filter(fn: (r) => r._measurement == "persons")
              |> filter(fn: (r) => r._field == "count")
              |> last()
        '''
        count_tables = query_api.query(count_query, org=INFLUX_ORG)
        count_records = [r for table in count_tables for r in table.records]

        current_count = count_records[-1].get_value() if count_records else 0
        new_count = max(0, int(current_count) + person_delta)  # floor at 0

        point = (
            Point("persons")
            .field("count", new_count)
            .tag("triggered_by", code)
            .time(time.time_ns())
        )
        write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)
        log.info(f"[{code}] Persons count updated: {current_count} → {new_count}")

    except Exception:
        log.warning(f"[{code}] Failed to update persons count", exc_info=True)

def mqtt_thread():
    client = mqtt.Client("flask-mqtt")
    client.on_message = on_message
    
    client.connect(MQTT_BROKER, 1883)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

# Startujemo mqtt daemon nit
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
