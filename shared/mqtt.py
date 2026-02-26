# common/mqtt_sender.py
import threading
import time
import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass
import queue

@dataclass
class MqttSettings:
    client_id : str
    broker: str
    port: int
    topic: str
    batch_size : int
    batch_interval : int

    @classmethod
    def from_dict(cls, data: dict) -> "MqttSettings":
        return cls(
            broker=data["broker"],
            port=int(data.get("port", 1883)),
            topic=data["topic"],
            batch_size = data['batch_size'],
            batch_interval = data['batch_interval'],
            client_id = data['client_id']
         )

batch_queue = queue.Queue()

def start_batch_sender(batch_queue, stop_event, mqtt_settings : MqttSettings):
    client = mqtt.Client(client_id="pi1_batch_sender")
    connected = threading.Event()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            connected.set()
        else:
            print("Failed to connect, rc=", rc)

    client.on_connect = on_connect
    client.connect(mqtt_settings.broker, mqtt_settings.port)
    client.loop_start()

    if not connected.wait(timeout=5):
        print("MQTT connection failed, batch sender exiting")
        return

    def sender():
        buffer = []
        while not stop_event.is_set():
            print("Batch sender waiting for messages...")
            try:
                while len(buffer) < mqtt_settings.batch_size:
                    try:
                        msg = batch_queue.get(timeout=mqtt_settings.batch_interval)
                        buffer.append(msg)
                        print("Got message for batch:", msg)
                    except queue.Empty:
                        break

                if buffer:
                    client.publish(mqtt_settings.topic, json.dumps(buffer))
                    print(f"Sent batch of {len(buffer)} messages")
                    buffer.clear()
            except Exception as e:
                print("Error in batch sender:", e)

    t = threading.Thread(target=sender, daemon=True)
    t.start()
    return t