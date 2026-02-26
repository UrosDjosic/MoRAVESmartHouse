#!/usr/bin/env python3
import threading
import time
from shared.mqtt import batch_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
from simulators.gsg_simulator import run_gsg_simulator
import random

def gsg_callback(code, settings : Device, accel, gyro):
    payload = {
        "measurement": "gyroscope",
        "device_name": settings.device_name,
        "code": code,
        "accel": accel,
        "gyro": gyro,
        "simulated": settings['simulated'] 
    }
    batch_queue.put(payload) 
    print(f"[{settings.code}] Sent to buffer: Accel:{accel}, Gyro:{gyro}")


def gsg_loop(settings :Device, stop_event):
    from .MPU6050 import MPU6050
    mpu = MPU6050()
    mpu.dmp_initialize()
    code = settings.code
    
    while not stop_event.is_set():
        accel_raw = mpu.get_acceleration()
        gyro_raw = mpu.get_rotation()
        
        accel = [round(a / 16384.0, 3) for a in accel_raw]
        gyro = [round(g / 131.0, 3) for g in gyro_raw]
        
        gsg_callback(code, settings, accel, gyro)
        
        time.sleep(settings.get('delay', 0.5))


def run_gsg(settings : Device, threads, stop_event):
    if settings['simulated']:
        code = settings['code']
        print(f'Starting {code} simulator')
        dpir1_thread = threading.Thread(
            target=run_gsg_simulator, 
            args=(
                settings['delay'], 
                lambda c, a, g: gsg_callback(c, settings, a, g), 
                stop_event, 
                code
            )
        )
        dpir1_thread.start()
        threads.append(dpir1_thread)
        print(f"{code} simulator started")
    else:
        print(f"Starting {settings.code} real sensor")
        gsg_thread = threading.Thread(target=gsg_loop, args=(settings, stop_event))
        gsg_thread.start()
        threads.append(gsg_thread)
        print("GSG real sensor started")