import time
import random

KEYPAD_LAYOUT = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

def generate_dms_events():
    while True:
        time.sleep(random.uniform(1, 2))

        row = random.randint(0, 2)
        col = random.randint(0, 2)
        key = KEYPAD_LAYOUT[row][col]

        yield key


def run_dms_simulator(delay, callback, stop_event, code):
    for key in generate_dms_events():
        if stop_event.is_set():
            break

        callback(code, key)
        time.sleep(delay)