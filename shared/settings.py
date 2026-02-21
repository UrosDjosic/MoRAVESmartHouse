import json
from typing import List, Dict
from shared.device import Device
from shared.pi_device import PiDevice
from dataclasses import dataclass
from shared.mqtt import MqttSettings
from shared.device_factory import device_factory
@dataclass
class Settings:
    pi: str
    device_name: str
    mqtt: MqttSettings
    devices: list[Device]

    @classmethod
    def from_json(cls, filepath: str) -> "Settings":
        import json

        with open(filepath) as f:
            data = json.load(f)

        pi = data['pi']
        device_name = data['device']
        mqtt = MqttSettings(**data['mqtt'])

        # Use factory to create correct subclasses
        devices = [device_factory(d) for d in data.get("devices", [])]

        return cls(pi=pi, device_name=device_name, mqtt=mqtt, devices=devices)