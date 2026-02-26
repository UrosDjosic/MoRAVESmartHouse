import time
import threading

buzzer_state = False
state_lock = threading.Lock()
def set_state(value : bool) :
    global buzzer_state
    with state_lock:
        buzzer_state = value


def get_buzzer_state():
    with state_lock:
        return buzzer_state


def run_db_simulator(freq,callback,stop_event,code,pitch,duration):
    while not stop_event.is_set():
        period = 1.0/pitch
        half_period = period/2
        cycles = int(duration*pitch)

        for _ in range(cycles):
            callback(True,code)
            time.sleep(half_period)
            callback(False,code)
            time.sleep(half_period)
        
        set_state(False)

        time.sleep(freq)