import random
import time

BUTTON_CODES = [0x300ff22dd, 0x300ffc23d, 0x300ff629d, 0x300ffa857, 0x300ff9867, 0x300ffb04f, 0x300ff6897, 0x300ff02fd, 0x300ff30cf, 0x300ff18e7, 0x300ff7a85, 0x300ff10ef, 0x300ff38c7, 0x300ff5aa5, 0x300ff42bd, 0x300ff4ab5, 0x300ff52ad]
BUTTON_NAMES = ["LEFT",   "RIGHT",      "UP",       "DOWN",       "2",          "3",          "1",        "OK",        "4",         "5",         "6",         "7",         "8",          "9",        "*",         "0",        "#"]

def generate_ir_state():
    while True:
        if random.random() > 0.8:
            yield True
        else:
            yield False

def run_ir_simulator(delay, callback, stop_event, code, settings):
    for state in generate_ir_state():
        time.sleep(delay)
        if state:
            idx = random.randint(0, len(BUTTON_CODES) - 1)
            button_name = BUTTON_NAMES[idx]
            hex_code = hex(BUTTON_CODES[idx])
            callback(button_name, code, settings)
            
        if stop_event.is_set():
            break