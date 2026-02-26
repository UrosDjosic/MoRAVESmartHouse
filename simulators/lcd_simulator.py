# simulators/lcd_simulator.py

import threading
import time

# Shared LCD state between simulated_logic and run_lcd_simulator
_lcd_lock = threading.Lock()
_lcd_state = {"line1": "", "line2": ""}

def set_lcd_state(line1, line2):
    with _lcd_lock:
        _lcd_state["line1"] = line1
        _lcd_state["line2"] = line2

def get_lcd_state():
    with _lcd_lock:
        return _lcd_state["line1"], _lcd_state["line2"]

def run_lcd_simulator(delay, callback, stop_event, code):
    """
    Periodically reads the current LCD state and fires the callback.
    Mimics what run_lcd_real does — but without hardware.
    
    Args:
        delay:      seconds between each simulated LCD "refresh"
        callback:   callable(line1, line2, code)
        stop_event: threading.Event to signal shutdown
        code:       device code string (e.g. "lcd")
    """
    while not stop_event.is_set():
        line1, line2 = get_lcd_state()
        
        if line1 or line2:  # only fire once we have actual data
            callback(line1, line2, code)
        
        stop_event.wait(delay)  # interruptible sleep