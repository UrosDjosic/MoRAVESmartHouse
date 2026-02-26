import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import DoorUltrasonic
from shared.pi_device import PiDevice
from shared.distance_update import add_distance
import random

def dus2_callback(distance,code, settings: DoorUltrasonic):
    payload = {
        "measurement": "door ultrasonic",
        "device_name" : settings.device_name,
        "code": settings.code,
        "value": distance,
        "simulated": settings.simulated
    }
    add_distance(distance,code)
    batch_queue.put(payload) 
    print(f"[{code}] Sent to buffer: motion detected")

def run_dus2(settings : DoorUltrasonic, threads, stop_event):
        if settings.simulated:
            code = settings.code
            print(f'Starting {code} simulator')
            dus1_thread = threading.Thread(
                 target = sensor_sim.run_simulator, 
                 args=(settings.freq, lambda c: dus2_callback(random.randint(0,100),c, settings), stop_event, code),
                 daemon=True
            )
            dus1_thread.start()
            threads.append(dus1_thread)
            print(f"{code} simulator started")
        else:
            '''
            Docstring for run_dus1
            
            :param settings: Description
            :type settings: DoorUltrasonic
            :param threads: Description
            :param stop_event: Description


            def loop(settings : DoorUltrasonic,stop_event):
                import RPi.GPIO as GPIO
                TRIG_PIN = settings.trig_pin
                ECHO_PIN = settings.echo_pin

                GPIO.setup(TRIG_PIN, GPIO.OUT)
                GPIO.setup(ECHO_PIN, GPIO.IN)

                try:
                    while not stop_event.is_set():
                        GPIO.output(TRIG_PIN, False)
                        time.sleep(0.2)
                        GPIO.output(TRIG_PIN, True)
                        time.sleep(0.00001)
                        GPIO.output(TRIG_PIN, False)
                        pulse_start_time = time.time()
                        pulse_end_time = time.time()

                        max_iter = 100

                        iter = 0
                        while GPIO.input(ECHO_PIN) == 0:
                            if iter > max_iter:
                                return None
                            pulse_start_time = time.time()
                            iter += 1

                        iter = 0
                        while GPIO.input(ECHO_PIN) == 1:
                            if iter > max_iter:
                                return None
                            pulse_end_time = time.time()
                            iter += 1

                        if iter <= max_iter:
                            pulse_duration = pulse_end_time - pulse_start_time
                            distance = (pulse_duration * 34300) / 2
                            
                            dus1_callback(distance, code, settings)
                        

                finally:
                    GPIO.cleanup()

            dus1_thread = threading.Thread(target=loop,
            args = (settings,stop_event))
            dus1_thread.start()
            threads.append(dus1_thread)
            '''