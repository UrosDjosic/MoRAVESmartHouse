from shared.device import Device, DoorPir, DoorBuzzer, DoorUltrasonic, DoorMembraneSwitch
from typing import Dict

def device_factory(d: Dict) -> Device:
    code = d.get("code", "")

    # DoorPir: has optional 'dl' nested device
    if code.startswith("dpir"):
        if "dl" in d:
            d["dl"] = Device(**d["dl"])
        return DoorPir(**d)

    # DoorBuzzer
    if code.startswith("db"):
        return DoorBuzzer(**d)

    # DoorUltrasonic
    if code.startswith("dus"):
        return DoorUltrasonic(**d)

    # DoorMembraneSwitch
    if code.startswith("dms"):
        return DoorMembraneSwitch(**d)

    # Default: generic Device
    return Device(**d)