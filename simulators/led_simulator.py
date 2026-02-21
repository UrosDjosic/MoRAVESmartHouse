import time
import threading

led_state = False
state_lock = threading.Lock()

def set_led_state(value: bool):
    with state_lock:
        global led_state
        led_state = value

def get_led_state():
    with state_lock:
        return led_state


def run_dl_simulator(delay, callback, stop_event, code):
    while not stop_event.is_set():
        state = get_led_state()
        callback(state, code)
        time.sleep(delay)