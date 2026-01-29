import json
from typing import List, Dict
from shared.device import Device
from shared.pi_device import PiDevice
from dataclasses import dataclass
from shared.mqtt import MqttSettings

@dataclass
class Settings:
    pi_device: PiDevice
    mqtt : MqttSettings
    devices: List[Device]


    @classmethod
    def from_json(cls, filepath: str) -> "Settings":
        with open(filepath) as f:
            data = json.load(f)

        pi_device = PiDevice(**data["pi_device"])

        mqtt = MqttSettings(**data['mqtt'])

        devices = [Device(**d) for d in data.get("devices", [])]

        return cls(pi_device=pi_device, devices=devices,mqtt = mqtt)