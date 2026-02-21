import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
import random
from simulators.dms_simulator import run_dms_simulator

def dms_callback(code, key, settings : Device):
    payload = {
        "measurement": "door membrane switch",
        "device_name": settings.device_name,
        "code": code,
        "value" : 1,
        "simulated": settings.simulated
    }
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: {key} key pressed")


def run_dms(settings:Device, threads, stop_event):
    if settings.simulated:
        code = settings.code
        delay = settings.freq
        print(f"Starting {code} simulator")
        keypad_thread = threading.Thread(
            target=run_dms_simulator,
            args=(delay, lambda c, k: dms_callback(c, k, settings), stop_event, code),
            daemon=True
        )
        keypad_thread.start()
        threads.append(keypad_thread)
    else:
        """
        Docstring for run_dms
        
        :param settings: Description
        :type settings: Device
        :param threads: Description
        :param stop_event: Description

         '''
        def keypad_loop(settings, stop_event):
            import RPi.GPIO as GPIO
            
            R_PINS = settings.r_pins # Lista tipa [4,12,15,16]
            C_PINS = settings.c_pins # Takodje
            code = settings.code

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            for pin in R_PINS:
                GPIO.setup(pin, GPIO.OUT)
            for pin in C_PINS:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            def readLine(line_pin, characters):
                GPIO.output(line_pin, GPIO.HIGH)
                for idx, col_pin in enumerate(C_PINS):
                    if GPIO.input(col_pin) == 1:
                        key = characters[idx]
                        dms_callback(code, key, settings)
                        while GPIO.input(col_pin) == 1:
                            time.sleep(0.05)
                GPIO.output(line_pin, GPIO.LOW)

            try:
                while not stop_event.is_set():
                    readLine(R_PINS[0], ["1","2","3","A"])
                    readLine(R_PINS[1], ["4","5","6","B"])
                    readLine(R_PINS[2], ["7","8","9","C"])
                    readLine(R_PINS[3], ["*","0","#","D"])
                    time.sleep(0.1)
            finally:
                GPIO.cleanup()

        dms_thread = threading.Thread(target=keypad_loop, args=(settings, stop_event), daemon=True)
        dms_thread.start()
        threads.append(dms_thread)
        print(f"DMS real sensor started on code: {settings.code}")
        """