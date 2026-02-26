import threading
import time
from shared.mqtt import batch_queue
from simulators._4sd_simulator import *
from shared.device import Device
import shared.timer_state as timer_state

def _4sd_callback(value, code, settings: Device):
    payload = {
        "measurement": "7-Segment Display",
        "device_name": settings.device_name,
        "code": code,
        "timer": value,
        "simulated": settings.simulated
    }
    batch_queue.put(payload)
    print(f"[{code}] Display updated: {value}")

def _format_time(seconds):
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

def _timer_loop(settings, stop_event):
    code = settings.code
    blink_on = True

    while not stop_event.is_set():
        if timer_state.timer_expired:
            display = "00:00" if blink_on else "     "
            blink_on = not blink_on
            _4sd_callback(display, code, settings)
            time.sleep(0.5)
        else:
            if timer_state.timer_seconds > 0:
                timer_state.timer_seconds -= 1
            if timer_state.timer_seconds == 0:
                timer_state.timer_expired = True
            display = _format_time(timer_state.timer_seconds)
            _4sd_callback(display, code, settings)
            time.sleep(1.0)

def run_4sd_real(callback, stop_event, code, settings):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    segments = settings.segment_pins
    digits = settings.digit_pins

    for segment in segments:
        GPIO.setup(segment, GPIO.OUT)
        GPIO.output(segment, 0)
    for digit in digits:
        GPIO.setup(digit, GPIO.OUT)
        GPIO.output(digit, 1)

    num = {
        ' ':(0,0,0,0,0,0,0), '0':(1,1,1,1,1,1,0), '1':(0,1,1,0,0,0,0),
        '2':(1,1,0,1,1,0,1), '3':(1,1,1,1,0,0,1), '4':(0,1,1,0,0,1,1),
        '5':(1,0,1,1,0,1,1), '6':(1,0,1,1,1,1,1), '7':(1,1,1,0,0,0,0),
        '8':(1,1,1,1,1,1,1), '9':(1,1,1,1,0,1,1)
    }

    try:
        while not stop_event.is_set():
            s = _format_time(timer_state.timer_seconds).replace(":", "")
            s = s.rjust(4)
            callback(s, code, settings)

            for digit in range(4):
                if stop_event.is_set():
                    break
                for loop in range(7):
                    GPIO.output(segments[loop], num[s[digit]][loop])
                if (int(time.ctime()[18:19]) % 2 == 0) and (digit == 1):
                    GPIO.output(segments[7], 1)
                else:
                    GPIO.output(segments[7], 0)
                GPIO.output(digits[digit], 0)
                time.sleep(0.001)
                GPIO.output(digits[digit], 1)
    finally:
        GPIO.cleanup()


def run_4sd(settings: Device, threads, stop_event):
    code = settings.code

    if settings.simulated:
        # ── Timer logic thread ─────────────────────────────────────────
        timer_thread = threading.Thread(
            target=_timer_loop,
            args=(settings, stop_event),
            daemon=True
        )
        timer_thread.start()
        threads.append(timer_thread)

        # ── Simulator display thread ───────────────────────────────────
        seg_thread = threading.Thread(
            target=run_4sd_simulator,
            args=(settings.freq, lambda v, c: _4sd_callback(v, c, settings), stop_event, code)
        )
        seg_thread.start()
        threads.append(seg_thread)

    else:
        seg_thread = threading.Thread(
            target=run_4sd_real,
            args=(_4sd_callback, stop_event, code, settings)
        )
        seg_thread.start()
        threads.append(seg_thread)

    print(f"{code} simulator started")