import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
from shared.distance_update import update_persons
import random

def dpir2_callback(code, settings,value):
    payload = {
        "measurement": "door pir",
        "code": code,
        "value": value,
        "simulated": settings.simulated
    }
    batch_queue.put(payload) 
    update_persons(settings)


    
    print(f"[{code}] Sent to buffer: motion detected")

def run_dpir2(settings : Device, threads, stop_event):
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dpir1_thread = threading.Thread(
                 target = sensor_sim.run_simulator, 
                 args=(settings.freq, lambda c: dpir2_callback(c, settings,1), stop_event, code),
            )
            dpir1_thread.start()
            threads.append(dpir1_thread)
            print("DPIR1 simulator started")
        
        else:
            import RPi.GPIO as GPIO
            pin = settings.pin
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.IN)

            def gpio_callback(channel):
                value = GPIO.input(channel) 
                dpir2_callback(settings.code, settings, value=value)

            GPIO.add_event_detect(pin, GPIO.RISING, callback=gpio_callback)
            print("DPIR started")
        