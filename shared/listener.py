import json
import paho.mqtt.client as mqtt
from pi1.dl import dl_callback
from pi1.db import activate_buzzer,deactivate_buzzer
from pi3.brgb import brgb_callback
from pi2.btn import btn_callback
from shared.settings import Settings
from shared.device import Device

class MqttListener:

    def __init__(self, broker: str, port: int, topic: str, settings: Settings, client_id: str = "pi_listener"):
        self.broker = broker
        self.port = port
        self.topic = topic

        self.settings= settings

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        print("Connecting to MQTT...")
        self.client.connect(self.broker, self.port)
        self.client.loop_start()  # ← not loop_forever()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to broker")
            client.subscribe(self.topic)
            print(f"📡 Subscribed to {self.topic}")
        else:
            print("❌ Connection failed:", rc)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            print("📩 Received:", payload)

            # Process commands
            self.handle_message(payload)

        except Exception as e:
            print("⚠️ Failed to parse message:", e)

    def handle_message(self, data):
        """
        Expected payload examples:

        { "code": "dl", "value": 1 }
        OR batch
        [{...}, {...}]
        """

        if isinstance(data, list):
            for item in data:
                self.process_command(item)
        else:
            self.process_command(data)

    def process_command(self, cmd):
        code = cmd.get("code")
        value = cmd.get("value")

        setting = self.get_device_by_code(self.settings.devices,code)


        print(f"➡️ Command for {code}: {value}")

        if code == "dl" and self.settings.pi== 1:
            print("Toggle light:", value)
            dl_callback(value,code,setting)
        elif code == "db" and self.settings.pi == 1:
            print("Toggle buzzer:", value)
            if value == 1:
                activate_buzzer()
            else:
                deactivate_buzzer()
        elif code == 'btn' and self.settings.pi == 2:
            btn_callback(setting.code,setting)
        elif code == 'brgb' and self.settings.pi == 3:
            color = cmd.get('color')
            brgb_callback(value,color,setting)
        
    def get_device_by_code(self,devices: list[Device], code):
        for d in devices:
            if d.code == code:
                return d
        return None