import random


class BaseDevice:
    def __init__(self, name, simulated=True):
        self.name = name
        self.simulated = simulated


class BaseSensor(BaseDevice):
    def read(self):
        raise NotImplementedError()


class ButtonSensor(BaseSensor):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)
        self._state = False

    def read(self):
        if self.simulated:
            #random press occasionally
            self._state = random.random() < 0.05
        return self._state


class UltrasonicSensor(BaseSensor):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)

    def read(self):
        if self.simulated:
            #distance in cm
            return round(10 + random.random() * 200, 1)
        return None


class MotionSensor(BaseSensor):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)
        self._motion = False

    def read(self):
        if self.simulated:
            self._motion = random.random() < 0.02
        return self._motion


class MembraneSwitch(BaseSensor):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)
        self._pressed = False

    def read(self):
        if self.simulated:
            self._pressed = random.random() < 0.03
        return self._pressed


class Buzzer(BaseDevice):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)
        self._on = False

    def on(self):
        self._on = True
        if self.simulated:
            print(f"[SIM] {self.name} BUZZER ON")

    def off(self):
        self._on = False
        if self.simulated:
            print(f"[SIM] {self.name} BUZZER OFF")


class LED(BaseDevice):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)
        self._on = False

    def on(self):
        self._on = True
        if self.simulated:
            print(f"[SIM] {self.name} LED ON")

    def off(self):
        self._on = False
        if self.simulated:
            print(f"[SIM] {self.name} LED OFF")


class RGBLED(BaseDevice):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)
        self._color = (0, 0, 0)

    def set_color(self, r, g, b):
        self._color = (r, g, b)
        if self.simulated:
            print(f"[SIM] {self.name} RGB set to {self._color}")


class DHTSensor(BaseSensor):
    def __init__(self, name, simulated=True):
        super().__init__(name, simulated)

    def read(self):
        if self.simulated:
            temp = round(18 + random.random() * 10, 1)
            hum = round(30 + random.random() * 40, 1)
            return {"temperature": temp, "humidity": hum}
        return None


def make_default_pi1_devices(simulated=True):
    #devices for PI1
    return {
        'DS1': ButtonSensor('DS1', simulated=simulated),
        'DL': LED('DL', simulated=simulated),
        'DUS1': UltrasonicSensor('DUS1', simulated=simulated),
        'DB': Buzzer('DB', simulated=simulated),
        'DPIR1': MotionSensor('DPIR1', simulated=simulated),
        'DMS': MembraneSwitch('DMS', simulated=simulated),
        #WEBC not for K1
    }
