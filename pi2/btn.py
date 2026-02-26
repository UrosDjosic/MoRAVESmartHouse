import threading
import time
from shared.mqtt import batch_queue
from shared import timer_state
from simulators.btn_simulator import run_btn_simulator
from shared.device import Device

def btn_callback(code, settings):
    payload = {
        "measurement": "kitchen button",
        "device_name": settings.device_name,
        "code": code,
        "value": 1,
        "simulated": settings.simulated
    }
    batch_queue.put(payload)
    print(f"[{code}] Sent to buffer: kitchen button pressed")

    # ── Add seconds or stop blinking ──────────────────────────────────
    if timer_state.timer_expired:
        timer_state.timer_expired = False 
        print("[BTN] Blinking stopped")
    else:
        timer_state.add_seconds(timer_state.btn_add_seconds)

def run_btn(settings: Device, threads, stop_event):
    if settings.simulated:
        delay = settings.freq
        code = settings.code
        print(f"Starting {code} simulator")
        t = threading.Thread(
            target=run_btn_simulator,
            args=(delay, lambda c, s: btn_callback(c, s), stop_event, code, settings)
        )
        t.start()
        threads.append(t)
        print("BTN simulator started")
    else:
        import RPi.GPIO as GPIO
        port_btn = settings.pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            port_btn, GPIO.RISING,
            callback=lambda c: btn_callback(settings.code, settings),
            bouncetime=200
        )