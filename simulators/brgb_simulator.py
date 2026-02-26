import random
import time

def generate_brgb_state():
    """Infinite generator for random BRGB colors including 'off'."""
    colors = ["off", "red", "green", "blue", "white", "yellow", "purple", "cyan", "pink"]
    while True:
        yield random.choice(colors)

def run_brgb_simulator(delay: float, callback, stop_event, code: str):
    """
    Simulate BRGB LED changes.

    :param delay: seconds between color changes
    :param callback: function to call for each new color, signature callback(state: bool, color: str, code: str)
    :param stop_event: threading.Event to stop the simulator
    :param code: device code for logging
    """
    for color in generate_brgb_state():
        if stop_event.is_set():
            break

        # Treat 'off' as state=False, others as state=True
        state = color.lower() != "off"
        callback(state, color.lower())
        time.sleep(delay)