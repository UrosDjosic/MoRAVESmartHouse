from dataclasses import dataclass
from typing import Optional

@dataclass
class Device:
    code: str
    device_name : str
    freq: int
    simulated: bool
    pin: Optional[int] = None

@dataclass
class DoorPir(Device):
    dl: Optional[Device] = None
@dataclass
class DoorBuzzer(Device):
    pitch : Optional[int] = None
    duration : Optional[int] = None


@dataclass
class DoorUltrasonic(Device):
    trig_pin : Optional[int] = None
    echo_pin : Optional[int] = None

@dataclass
class DoorMembraneSwitch(Device):
    r_pins : Optional[list[int]] = None
    c_pins : Optional[list[int]] = None

@dataclass
class BRGB(Device):
    red_pin : Optional[int] = None
    green_pin : Optional[int] = None
    blue_pin : Optional[int] = None

@dataclass 
class IR(Device):
    brgb : Optional[BRGB] = None
    