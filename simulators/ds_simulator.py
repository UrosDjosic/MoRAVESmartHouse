import random
import time

def generate_ds_state(min_duration=2):
    counter = 0

    while True:
        if counter >= min_duration and random.random() > 0.2:
            counter = 0
            yield True  
        else:
            yield False 

        counter += 1


def run_ds_simulator(delay, callback, stop_event, code, settings):
    for state in generate_ds_state():
        time.sleep(delay)
        if state:
            callback(code, settings, 1)  # vrata otvorena
        else:
            callback(code, settings, 0)  # vrata zatvorena
        if stop_event.is_set():
            break