# common/mqtt_sender.py
import threading
import time
import json
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
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
    # Do NOT pass callback_api_version
    client = mqtt.Client(client_id="pi1_batch_sender")
    client.connect(mqtt_settings.broker, mqtt_settings.port)
    client.loop_start()

    def sender():
        buffer = []
        while not stop_event.is_set():
            try:
                while len(buffer) < 10:
                    try:
                        msg = batch_queue.get(timeout=2)
                        buffer.append(msg)
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