import threading
import time
from shared.mqtt import batch_queue
from simulators import dpir1
from shared.device import Device
from shared.pi_device import PiDevice
import random

def dpir1_callback(code,value, device_info : PiDevice, settings):
    payload = {
        "measurement": "door pir 1",
        "device_name": device_info.name,
        "code": code,
        "value": value,
        "simulated": settings.simulated
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: motion detected")

def run_dpir1(settings : Device, threads, stop_event, device_info):
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(
                 target = dpir1.run_simulator, 
                 args=(settings.freq, lambda c: dpir1_callback(c,random.choice([0,1]), device_info, settings), stop_event, code),
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
    