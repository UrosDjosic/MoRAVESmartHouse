import json
from typing import List, Dict
from shared.device import Device
from shared.pi_device import PiDevice
from dataclasses import dataclass
from shared.mqtt import MqttSettings

@dataclass
class Settings:
    pi: str
    device_name : str
    mqtt : MqttSettings
    devices: List[Device]


    @classmethod
    def from_json(cls, filepath: str) -> "Settings":
        with open(filepath) as f:
            data = json.load(f)

        pi = data['pi']
        device = data['device']

        mqtt = MqttSettings(**data['mqtt'])

        devices = [Device(**d) for d in data.get("devices", [])]

        return cls(pi = pi, device_name = device , devices=devices,mqtt = mqtt)