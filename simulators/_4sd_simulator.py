import time
import threading

current_value = "    "
display_lock = threading.Lock()

def set_4sd_state(value):
    with display_lock:
        global current_value
        current_value = str(value).rjust(4)[:4]

def get_4sd_state():
    with display_lock:
        return current_value

def run_4sd_simulator(delay, callback, stop_event, code):
    last_value = ""
    while not stop_event.is_set():
        current = get_4sd_state()
        if current != last_value:
            callback(current, code)
            last_value = current
        time.sleep(delay)