import random
import time

def generate_btn_state(min_duration=2):
    counter = 0

    while True:
        if counter >= min_duration and random.random() > 0.2:
            counter = 0
            yield True  
        else:
            yield False 

        counter += 1


def run_btn_simulator(delay, callback, stop_event, code, settings):
    for state in generate_btn_state():
        time.sleep(delay)
        if state:
            callback(code, settings)
        if stop_event.is_set():
            break