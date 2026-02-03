import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
import random

def ds1_callback(code, settings):
    payload = {
        "measurement": "door sensor (button)",
        "code": code,
        "value": 1,
        "simulated": settings.simulated
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: motion detected")

def run_ds1(settings : Device, threads, stop_event):
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(
                 target = sensor_sim.run_simulator, 
                 args=(settings.freq, lambda c: ds1_callback(c, settings), stop_event, code),
                 daemon=True
            )
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR1 simulator started")
        '''
        else:
            import RPi.GPIO as GPIO
            port_btn = settings['pin']
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(port_btn, GPIO.IN)
            GPIO.add_event_detect(port_btn, GPIO.RISING, callback=lambda c: dpir1_callback(settings['code'], device_info, settings))
        '''