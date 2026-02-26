import threading
import time
from shared.device import Device
from shared.mqtt import batch_queue
from simulators.ds_simulator import run_ds_simulator
from pi1.db import activate_buzzer,deactivate_buzzer

# Alarm state tracking per device
_alarm_timers = {}
_alarm_active = {}
_lock = threading.Lock()

def trigger_alarm(code, device_name, simulated):
    payload = {
        "measurement": "alarm",
        "device_name": device_name,
        "code": code,
        "value": 1,
        "simulated": simulated
    }
    batch_queue.put(payload)
    print(f"[{code}] ALARM ACTIVATED - door open too long!")
    activate_buzzer()

def clear_alarm(code, device_name, simulated):
    payload = {
        "measurement": "alarm",
        "device_name": device_name,
        "code": code,
        "value": 0,
        "simulated": simulated
    }
    batch_queue.put(payload)
    print(f"[{code}] Alarm cleared - door closed.")
    deactivate_buzzer()

def on_door_open(code, settings: Device):
    """Poziva se kada se vrata otvore (signal HIGH)."""
    with _lock:
        if code in _alarm_timers and _alarm_timers[code] is not None:
            return  # Timer već teče

        def alarm_trigger():
            with _lock:
                _alarm_active[code] = True
            trigger_alarm(code, settings.device_name, settings.simulated)

        timer = threading.Timer(5.0, alarm_trigger)
        _alarm_timers[code] = timer
        _alarm_active[code] = False
        timer.start()
        print(f"[{code}] Door opened - starting 5s timer.")


def on_door_closed(code, settings: Device):
    """Poziva se kada se vrata zatvore (signal LOW)."""
    with _lock:
        timer = _alarm_timers.pop(code, None)
        was_active = _alarm_active.pop(code, False)

    if timer is not None:
        timer.cancel()

    if was_active:
        clear_alarm(code, settings.device_name, settings.simulated)
    else:
        print(f"[{code}] Door closed before alarm triggered.")

def ds2_callback(code, settings:Device,state : int):
    payload = {
        "measurement": "door sensor",
        "device_name": settings.device_name,
        "code": code,
        "value": state,
        "simulated": settings.simulated # Tag da li je simulirano
    }
    batch_queue.put(payload) # Dodavanje u red (Thread-safe)
    print(f"[{code}] Sent to buffer: button pressed")

    if state == 1:
        on_door_open(code, settings)
    else:
        on_door_closed(code, settings)

def run_ds2(settings : Device, threads, stop_event):
        if settings.simulated:
            delay = settings.freq
            code = settings.code
            print("Starting {code} simulator")
            ds2_thread = threading.Thread(target = run_ds_simulator, args=(delay, lambda c, s,state: ds2_callback(c, s,state), stop_event, code, settings))
            ds2_thread.start()
            threads.append(ds2_thread)
            print(f"{code} sumilator started")
        else:
            """
            Docstring for run_ds1
            
            :param settings: Description
            :type settings: Device
            :param threads: Description
            :param stop_event: Description
            :param device_info: Description

            import RPi.GPIO as GPIO
            port_btn = settings.pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(port_btn, GPIO.BOTH, callback=lambda c: ds1_callback(settings['code'], settings), bouncetime = 100)
            """