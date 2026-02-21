import argparse
import threading
import time
import datetime
from shared.settings import Settings
from pi1.dpir1 import run_dpir1
from pi1.ds1 import run_ds1
from pi1.dus1 import run_dus1
from pi1.dms import run_dms
from pi1.dl import run_dl
from pi1.db import run_db

from pi3.dht1 import run_dht1

from threading import *
from shared.mqtt import start_batch_sender, batch_queue

#pi1
all_devices = {
    "dht1" : run_dht1
}

"""
pi2
all_devices = {
    "dpir1" : run_dpir1,
    "ds1" : run_ds1,
    "dus1" : run_dus1,
    "dms" : run_dms,
    "dl" : run_dl
}
"""
"""
pi3
all_devices = {
    "dpir1" : run_dpir1,
    "ds1" : run_ds1,
    "dus1" : run_dus1,
    "dms" : run_dms,
    "dl" : run_dl
}
"""
if __name__ == "__main__":
    settings = Settings.from_json('settings.json')

    threads = []
    stop_event = threading.Event()

    for device in settings.devices:
        if device.code not in all_devices.keys():
            continue
        all_devices[device.code](device, threads, stop_event)
    

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