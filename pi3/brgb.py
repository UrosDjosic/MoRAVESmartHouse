import RPi.GPIO as GPIO
from time import sleep

#disable warnings (optional)
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

RED_PIN = 12
GREEN_PIN = 13
BLUE_PIN = 19

#set pins as outputs
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

def turnOff():
    GPIO.output(RED_PIN, GPIO.LOW)
    GPIO.output(GREEN_PIN, GPIO.LOW)
    GPIO.output(BLUE_PIN, GPIO.LOW)
    
def white():
    GPIO.output(RED_PIN, GPIO.HIGH)
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    GPIO.output(BLUE_PIN, GPIO.HIGH)
    
def red():
    GPIO.output(RED_PIN, GPIO.HIGH)
    GPIO.output(GREEN_PIN, GPIO.LOW)
    GPIO.output(BLUE_PIN, GPIO.LOW)

def green():
    GPIO.output(RED_PIN, GPIO.LOW)
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    GPIO.output(BLUE_PIN, GPIO.LOW)
    
def blue():
    GPIO.output(RED_PIN, GPIO.LOW)
    GPIO.output(GREEN_PIN, GPIO.LOW)
    GPIO.output(BLUE_PIN, GPIO.HIGH)
    
def yellow():
    GPIO.output(RED_PIN, GPIO.HIGH)
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    GPIO.output(BLUE_PIN, GPIO.LOW)
    
def purple():
    GPIO.output(RED_PIN, GPIO.HIGH)
    GPIO.output(GREEN_PIN, GPIO.LOW)
    GPIO.output(BLUE_PIN, GPIO.HIGH)
    
def lightBlue():
    GPIO.output(RED_PIN, GPIO.LOW)
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    GPIO.output(BLUE_PIN, GPIO.HIGH)

import threading
import time
from simulators.led_simulator import run_dl_simulator
from shared.device import Device
from shared.mqtt import batch_queue

'''
def led_on(pin):
    import RPi.GPIO as GPIO
    import time
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(10)
    GPIO.output(pin,GPIO.LOW)
'''



def dl_callback(state,code, settings : Device):
    payload = {
        "measurement": "light_state",
        "device_name": settings.device_name,
        "code": settings.code,
        "value": 1 if state else 0,
        "simulated": settings.simulated
    }
    batch_queue.put(payload)
    '''
    if not settings.simulated and state == 1:
        led_on(settings.pin)
    '''

    
    print(f"[{settings.code}] Sent to buffer: {'ON' if state else 'OFF'}")


def run_dl(settings : Device, threads, stop_event):
        if settings.simulated:
            delay = settings.freq
            code = settings.code
            print("Starting {code} simulator")

            dl_thread = threading.Thread(
                target=run_dl_simulator, 
                args=(delay, lambda s, c: dl_callback(s, c, settings), stop_event, code)
            )
            dl_thread.start()
            threads.append(dl_thread)
            print("Dl simulator started")

