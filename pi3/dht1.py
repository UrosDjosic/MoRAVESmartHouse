import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
from shared.latest_dht import add_to_latest
import random
import threading
#from pi2.dht.DHT11 import DHT

def dht1_callback(code, device_info,temperature,humidity):
    payload = {
        "measurement": "DHT",
        "code": code,
        "temperature" : temperature,
        "humidity" : humidity,
        "simulated": device_info.simulated
    }
    batch_queue.put(payload) 
    add_to_latest(code,temperature,humidity)
    print(f"\n [{code}] Sent to buffer: temperature detected {temperature} C, humidity {humidity} % \n")


def dht_loop(settings : Device,stop_event):
     '''
     import RPi.GPIO as GPIO
     pin = settings.pin
     dht = DHT.DHT(pin)
     code = settings.code
     while not stop_event.is_set():
        chk = dht.readDHT11()
        if chk == dht.DHTLIB_OK:
            dht1_callback(code,settings,dht.temperature,dht.humidity)
        else:
             print(f"Nesto ne valja {chk}")
        time.sleep(settings.freq)
    '''
def run_dht1(settings : Device, threads, stop_event):
        
        def simulated_read(code):
            """
            Generate natural-looking DHT readings.
            """
            # Choose a realistic base temperature & humidity for the room
            base_temp = random.uniform(20.0, 25.0)  # e.g., room temp
            base_hum  = random.uniform(40.0, 60.0)  # e.g., indoor humidity

            while not stop_event.is_set():
                # Add small random fluctuations
                temp = round(base_temp + random.uniform(-0.5, 0.5), 1)
                hum  = round(base_hum + random.uniform(-2.0, 2.0), 0)

                dht1_callback(code, settings, temp, hum)
                time.sleep(settings.freq)
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dht1_thread = threading.Thread(
                target=simulated_read,
                args=(code,),
                daemon=True
            )
            dht1_thread.start()
            threads.append(dht1_thread)
            print(f"{code} simulator started")
        
        else:
            dht1_thread = threading.Thread( 
                target=dht_loop,args=(settings,stop_event),
            )
            dht1_thread.start()
            threads.append(dht1_thread)
            print(f"{settings.code} started")
        