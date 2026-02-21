import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
import random
import threading
from ..pi2.dht.DHT11 import DHT

def dht2_callback(code, device_info,temperature,humidity):
    payload = {
        "measurement": "DHT",
        "code": code,
        "temperature" : temperature,
        "humidity" : humidity,
        "simulated": device_info.simulated
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: motion detected")


def dht_loop(settings : Device,stop_event):
     import RPi.GPIO as GPIO

     pin = settings.pin
     dht = DHT(pin)
     code = settings.code
     while not stop_event.is_set():
        chk = dht.readDHT11()
        if chk == dht.DHTLIB_OK:
            dht2_callback(code,settings,dht.temperature,dht.humidity)
        time.sleep(settings.get('delay',4))

def run_dht2(settings : Device, threads, stop_event):
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dht2_thread = threading.Thread(
                 target = sensor_sim.run_simulator, 
                 args=(settings.freq, lambda c: dht2_callback(c, settings, random.randint(0,40),random.randint(0,100)), stop_event, code),
            )
            dht2_thread.start()
            threads.append(dht2_thread)
            print(f"{code} simulator started")
        
        else:
            dht2_thread = threading.Thread( 
                target=dht_loop,args=(settings,stop_event),
            )
            dht2_thread.start()
            threads.append(dht2_thread)
            print(f"{settings.code} started")
        