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

from pi2.ds2 import run_ds2
from pi2.dus2 import run_dus2
from pi2.dpir2 import run_dpir2
from pi2._4sd import run_4sd
from pi2.btn import run_btn
from pi2.dht3 import run_dht3
from pi2.gsg.gsg import run_gsg

from pi3.dht1 import run_dht1
from pi3.dht2 import run_dht2
from pi3.ir import run_ir
from pi3.brgb import run_brgb
from pi3.lcd.lcd import run_lcd
from pi3.dpir3 import run_dpir3

from threading import *
from shared.mqtt import start_batch_sender, batch_queue
from shared.listener import MqttListener


#pi1
pi1 = {
    "ds1" : run_ds1,
    "dus1" : run_dus1,
    "dpir1" : run_dpir1,
    "dms" : run_dms,
    "dl" : run_dl,
    "db" : run_db
}


#pi2
pi2 = {
    "ds2" : run_ds2,
    "dus2" : run_dus2,
    "dpir2" : run_dpir2,
    "4sd" : run_4sd,
    "btn" : run_btn,
    "dht3" : run_dht3,
    "gsg" : run_gsg,
}


#pi3
pi3 = {
    "dht1" : run_dht1,
    "dht2" : run_dht2,
    "ir" : run_ir,
    "brgb" : run_brgb,
    "dpir3" : run_dpir3,
    "lcd" : run_lcd
}


'''
# export http_proxy="http://proxy.uns.ac.rs:8080"
# export https_proxy="http://proxy.uns.ac.rs:8080"
# mjpg_streamer -i "input_uvc.so" -o "output_http.so -p 8080 -w /usr/local/share/mjpg-streamer/www"
# http://<raspberry_pi_ip>:8080/?action=stream
'''
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--settings', default='settings.json')  # ← add this
    args = parser.parse_args()

    settings = Settings.from_json(args.settings) 

    threads = []
    stop_event = threading.Event()

    all_devices = []
    if (settings.pi == 1):
        all_devices = pi1
    elif (settings.pi == 2):
        all_devices = pi2
    elif (settings.pi == 3):
        all_devices = pi3
    else: 
        RuntimeError("No pi device set!")


    for device in settings.devices:
        if device.code not in all_devices.keys():
            continue
        all_devices[device.code](device, threads, stop_event)
    

    start_batch_sender(stop_event=stop_event,batch_queue=batch_queue,mqtt_settings=settings.mqtt)

    listener = MqttListener(
        broker=settings.mqtt.broker,
        port=settings.mqtt.port,
        topic="actuator",
        settings = settings,
        client_id=f"{settings.device_name}_listener",
    )

    listener.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all devices...")
        stop_event.set()
        listener.stop()
        for t in threads:
            t.join()
        print("All devices stopped")