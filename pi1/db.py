import threading
import time
from shared.mqtt import batch_queue
from shared.device import DoorBuzzer

_buzzer_lock = threading.Lock()
_buzzer_active_event = threading.Event()  # Set = active, clear = inactive

def activate_buzzer():
    _buzzer_active_event.set()
    print("[BUZZER] Activated")

def deactivate_buzzer():
    _buzzer_active_event.clear()
    print("[BUZZER] Deactivated")

def db_callback(code, settings: DoorBuzzer, value):
    payload = {
        "measurement": "door buzzer",
        "device_name": settings.device_name,
        "code": code,
        "value": value,
        "simulated": settings.simulated
    }
    batch_queue.put(payload)
    print(f"[{code}] Sent to buffer: buzzer state={value}")

def _buzzer_loop(settings: DoorBuzzer, stop_event):
    code = settings.code
    while not stop_event.is_set():
        # Block until buzzer should be active (or stop_event fires)
        active = _buzzer_active_event.wait(timeout=0.1)
        if active and not stop_event.is_set():
            db_callback(code, settings, 1)
            time.sleep(0.5)
            # Check again before sending OFF — might have been deactivated
            if not stop_event.is_set():
                db_callback(code, settings, 0)
                time.sleep(0.5)

def run_db(settings: DoorBuzzer, threads, stop_event):
    if settings.simulated:
        code = settings.code
        print(f'Starting {code} simulator')
        db_thread = threading.Thread(
            target=_buzzer_loop,
            args=(settings, stop_event),
            daemon=True
        )
        db_thread.start()
        threads.append(db_thread)
        print(f"{code} simulator started")
    else:
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