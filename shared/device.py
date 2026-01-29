from dataclasses import dataclass
from typing import Optional

@dataclass
class Device:
    code: str
    freq: int
    simulated: bool
    pin: Optional[int] = None