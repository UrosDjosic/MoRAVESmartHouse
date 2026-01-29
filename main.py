"""
PI1 controller script

Usage examples:
  python pi1.py --simulate-all -> simulate all devices, interactive
  python pi1.py --simulate-all --run-duration 5 -> run 5 seconds then exit (used for smoke tests)

Controls: via console commands: 'led on', 'led off', 'buzzer on', 'buzzer off', 'status', 'exit'

This script prints sensor readings to console periodically.
"""
import argparse
import threading
import time
import datetime
from shared.settings import Settings
from components.dpir1 import run_dpir1
from threading import *
from shared.mqtt import start_batch_sender, batch_queue

all_devices = {
    "dpir1" : run_dpir1
}


if __name__ == "__main__":
    settings = Settings.from_json('settings.json')

    threads = []
    stop_event = threading.Event()

    for device in settings.devices:
        if device.code not in all_devices.keys():
            continue
        all_devices[device.code](device, threads, stop_event,settings.pi_device)

    start_batch_sender(stop_event=stop_event,batch_queue=batch_queue,mqtt_settings=settings.mqtt)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all devices...")
        stop_event.set()
        for t in threads:
            t.join()
        print("All devices stopped")