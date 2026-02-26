import threading
import time
from shared.mqtt import priority_queue
from shared.device import DoorBuzzer

_buzzer_active_event = threading.Event()

def activate_buzzer():
    print(f"[BUZZER] Activated, event id: {id(_buzzer_active_event)}")
    _buzzer_active_event.set()

def deactivate_buzzer():
    print("[BUZZER] Deactivated")
    _buzzer_active_event.clear()

def db_callback(code, settings: DoorBuzzer, value):
    payload = {
        "measurement": "door buzzer",
        "device_name": settings.device_name,
        "code": code,
        "value": value,
        "simulated": settings.simulated
    }
    priority_queue.put(payload)
    print(f"[{code}] Sent to buffer: buzzer state={value}")

def _buzzer_loop(settings: DoorBuzzer, stop_event):
    code = settings.code
    last_state = 0
    print(f"[BUZZER LOOP] Started, event id: {id(_buzzer_active_event)}")

    while not stop_event.is_set():
        active = _buzzer_active_event.wait(timeout=0.1)

        if active and last_state != 1:
            print("[BUZZER] Sending ON")
            db_callback(code, settings, 1)
            last_state = 1
        elif not active and last_state != 0:
            print("[BUZZER] Sending OFF")
            db_callback(code, settings, 0)
            last_state = 0

        time.sleep(0.1)

def run_db(settings: DoorBuzzer, threads, stop_event):
    if settings.simulated:
        print(f'Starting {settings.code} simulator')
        db_thread = threading.Thread(
            target=_buzzer_loop,
            args=(settings, stop_event),
            daemon=True
        )
        db_thread.start()
        threads.append(db_thread)
        print(f"{settings.code} simulator started, alive: {db_thread.is_alive()}")
    else:
        '''
        import RPi.GPIO as GPIO
        
        GPIO.setmode(GPIO.BCM)
        buzzer_pin = settings.pin
        GPIO.setup(buzzer_pin, GPIO.OUT)
        GPIO.output(buzzer_pin, GPIO.LOW)  # Ensure starts LOW

        def buzz_loop():
            active = _buzzer_active_event.wait(timeout=0.1)
            if active:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(buzzer_pin,GPIO.OUT)
                GPIO.output(buzzer_pin,GPIO.HIGH)
                time.sleep(1)
                GPIO.output(buzzer_pin,GPIO.LOW)
            else:
                GPIO.output(buzzer_pin, GPIO.LOW)

        db_thread = threading.Thread(target=buzz_loop, daemon=True)
        db_thread.start()
        threads.append(db_thread)
        '''
        