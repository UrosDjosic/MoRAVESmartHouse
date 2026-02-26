import threading
import time
from shared.mqtt import batch_queue
#from shared.colours import handle_brgb_from_ir
from simulators.ir_simulator import run_ir_simulator, BUTTON_CODES, BUTTON_NAMES
from shared.device import IR

def ir_callback(button, code, settings:IR):
    payload = {
        "measurement": "Bedroom_Infrared",
        "device_name": settings.device_name,
        "code": code,
        "value": button,
        "simulated": settings.simulated
    }
    batch_queue.put(payload) 
    if not settings.simulated:
        #handle_brgb_from_ir(button, settings.brgb)
        time.sleep(settings.freq)
    print(f"[{code}] Sent to buffer: IR Button {button} detected")


def get_binary(pin, stop_event):
    import RPi.GPIO as GPIO
    from datetime import datetime
    
    num1s = 0
    binary = 1
    command = []
    previousValue = 0
    
    while GPIO.input(pin):
        if stop_event.is_set(): return None
        time.sleep(0.0001)
        
    startTime = datetime.now()
    while not stop_event.is_set():
        value = GPIO.input(pin)
        if previousValue != value:
            now = datetime.now()
            pulseTime = now - startTime
            startTime = now
            command.append((previousValue, pulseTime.microseconds))
        
        if value: num1s += 1
        else: num1s = 0
        
        if num1s > 10000: break
        previousValue = value
        
    for (typ, tme) in command:
        if typ == 1:
            if tme > 1000: binary = binary * 10 + 1
            else: binary *= 10
            
    if len(str(binary)) > 34:
        binary = int(str(binary)[:34])
    return binary

def run_ir_real(pin, callback, stop_event, settings):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN)
    
    print(f"Real IR sensor started on pin {pin}")

    while not stop_event.is_set():
        binary_val = get_binary(pin, stop_event)
        if binary_val is None or binary_val == 1:
            continue
        
        try:
            inData = hex(int(str(binary_val), 2))
            
            found = False
            for i in range(len(BUTTON_CODES)):
                if hex(BUTTON_CODES[i]) == inData:
                    callback(BUTTON_NAMES[i], settings.code, settings)
                    found = True
                    break
            
            if not found:
                print(f"Unknown IR code: {inData}")
                    
        except Exception as e:
            print(f"IR Error: {e}")

def run_ir(settings : IR, threads, stop_event):
    if settings.simulated:
        delay = settings.freq
        code = settings.code
        print(f'Starting {code} simulator')
        ir_thread = threading.Thread(
            target=run_ir_simulator, 
            args=(delay, ir_callback, stop_event, code, settings)
        )        
    else:
        import RPi.GPIO as GPIO

        pin = settings.pin
        code = settings.code
        print(f'Starting {code} real sensor')
        ir_thread = threading.Thread(
            target=run_ir_real, 
            args=(pin, ir_callback, stop_event, settings)
        )

        GPIO.setwarnings(False)
        # setmode should be global in main, but just in case:
        try:
            GPIO.setmode(GPIO.BCM)
        except:
            pass
        GPIO.setup(settings.brgb.red_pin, GPIO.OUT)
        GPIO.setup(settings.brgb.green_pin, GPIO.OUT)
        GPIO.setup(settings.brgb.blue_pin, GPIO.OUT)

    ir_thread.start()
    threads.append(ir_thread)