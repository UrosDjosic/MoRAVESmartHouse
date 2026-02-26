import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import DoorPir
from shared.pi_device import PiDevice
from pi1.dl import dl_callback
from shared.distance_update import update_persons
import random

def dpir1_callback(code, settings:DoorPir, value):
    payload = {
        "measurement": "door pir",
        "device_name" : settings.device_name,
        "code": code,
        "value": value,
        "simulated": settings.simulated
    }
    batch_queue.put(payload) 
    update_persons(settings)
    if not settings.simulated:
         dl_callback(1,settings.dl)
    
    print(f"[{code}] Sent to buffer: motion detected")

def run_dpir1(settings : DoorPir, threads, stop_event):
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(
                 target = sensor_sim.run_simulator, 
                 args=(settings.freq, lambda c: dpir1_callback(c, settings,value = 1), stop_event, code),
            )
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR1 simulator started")
        
        else:
            """
            Docstring for run_dpir1
            
            :param settings: Description
            :type settings: DoorPir
            :param threads: Description
            :param stop_event: Description

            import RPi.GPIO as GPIO
            pin = settings.pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.IN)

            def gpio_callback(channel):
                value = GPIO.input(channel) 
                dpir1_callback(settings.code, settings, value=value)

            GPIO.add_event_detect(pin, GPIO.RISING, callback=gpio_callback)
            print("DPIR started")
            """
            
        