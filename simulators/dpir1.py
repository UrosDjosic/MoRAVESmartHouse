import threading
import time

def run_simulator(freq: float, callback, stop_event: threading.Event, code: str):
    """
    Simulate a device triggering periodically.

    :param freq: frequency in seconds between events
    :param callback: function to call for each simulated event
    :param stop_event: threading.Event to allow clean shutdown
    :param code: device code or name to pass to callback
    """
    while not stop_event.is_set():
        callback(code)
        time.sleep(freq)