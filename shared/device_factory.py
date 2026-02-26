from shared.device import Device, DoorPir, DoorBuzzer, DoorUltrasonic, DoorMembraneSwitch, BRGB, IR
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
    if code.startswith("brgb") :
        return BRGB(**d)
    
    if code.startswith("ir"):
        if "brgb" in d and isinstance(d["brgb"], dict):
            d["brgb"] = BRGB(**d["brgb"])
        return IR(**d)
    # Default: generic Device
    return Device(**d)