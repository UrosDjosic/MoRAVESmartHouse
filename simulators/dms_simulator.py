import time
import random

KEYPAD_LAYOUT = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

CORRECT_PIN_SEQUENCE = ['1', '2', '3', '4', '#']

def generate_dms_events():
    # First input correct PIN sequence
    for key in CORRECT_PIN_SEQUENCE:
        yield key

    # Then random keys forever
    while True:
        time.sleep(random.uniform(1, 2))
        row = random.randint(0, 3)
        col = random.randint(0, 2)
        key = KEYPAD_LAYOUT[row][col]
        yield key


def run_dms_simulator(delay, callback, stop_event, code):
    for key in generate_dms_events():
        if stop_event.is_set():
            break
        callback(code, key)
        time.sleep(delay)