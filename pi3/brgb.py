import threading
import time
from simulators.brgb_simulator import run_brgb_simulator
from shared.device import Device, BRGB
from shared.mqtt import batch_queue
#from shared.colours import * 


# --- BRGB callback ---
def brgb_callback(state: bool, color: str, settings: BRGB):

    """Turn LED ON/OFF with given color and send MQTT batch."""
    # Send to MQTT batch
    payload = {
        "measurement": "light_state",
        "device_name": settings.device_name,
        "code": settings.code,
        "value": 1 if state else 0,
        "simulated": settings.simulated,
        "color": color
    }
    batch_queue.put(payload)
    print(f"[{settings.code}] Sent to buffer: {'ON' if state else 'OFF'}, color={color}")

    # Apply color if turning ON
    if state:
        if settings.simulated:
            print(f"[{settings.code}] Simulated {color} ON")

        else:
            #func = colors.get(color.lower(), turnOff) NOT SIMULATED
            #func(settings) NOT SIMULATED
            time.sleep(3)
            print(f"Turning on color {color}!")
    '''
    elif not settings.simulated:
        turnOff(settings)
    '''
    
    
            

# --- Run BRGB (simulator or real) ---
def run_brgb(settings: BRGB, threads: list, stop_event: threading.Event):
    if settings.simulated:
        delay = settings.freq
        code = settings.code
        print(f"Starting {code} simulator")

        t = threading.Thread(
            target=run_brgb_simulator, 
            args=(delay, lambda s, c: brgb_callback(s, c, settings), stop_event, code)
        )
        t.start()
        threads.append(t)
        print(f"{code} simulator started")
    else:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        # setmode should be global in main, but just in case:
        try:
            GPIO.setmode(GPIO.BCM)
        except:
            pass
        GPIO.setup(settings.red_pin, GPIO.OUT)
        GPIO.setup(settings.green_pin, GPIO.OUT)
        GPIO.setup(settings.blue_pin, GPIO.OUT)
        turnOff(settings)  # start OFF
        print(f"{settings.code} ready for real BRGB control")
