#!/usr/bin/env python3
import threading
import time
from shared.mqtt import batch_queue,priority_queue
from shared import sensor_sim
from shared.device import Device
from shared.pi_device import PiDevice
from simulators.gsg_simulator import run_gsg_simulator
import random


ALARM_ACCEL_THRESHOLD = 0.25
ALARM_GYRO_THRESHOLD = 10

last_accel = None

def gsg_callback(code, settings: Device, accel, gyro):
    global last_accel

    alarm = False

    #Acceleration delta check
    if last_accel is not None:
        delta = [abs(accel[i] - last_accel[i]) for i in range(3)]
        if any(d > ALARM_ACCEL_THRESHOLD for d in delta):
            alarm = True

    #Gyro check
    if any(abs(g) > ALARM_GYRO_THRESHOLD for g in gyro):
        alarm = True

    #Update last accel
    last_accel = accel

    payload = {
        "measurement": "gyroscope",
        "device_name": settings.device_name,
        "code": code,
        "accel": accel,
        "gyro": gyro,
        "alarm": alarm,
        "simulated": settings.simulated
    }

    batch_queue.put(payload)

    if alarm:
        print(f"🚨 [{code}] ALARM — Significant movement detected on GSG!")
        send_alarm(settings)
    else:
        print(f"[{settings.code}] Accel:{accel}, Gyro:{gyro}")

def send_alarm(settings:Device):
    payload = {
        "measurement": "alarm",
        "device_name": settings.device_name,
        "code": settings.code,
        "simulated": settings.simulated
    }
    priority_queue.put(payload)


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
        
        time.sleep(settings.freq)


def run_gsg(settings : Device, threads, stop_event):
    if settings.simulated:
        code = settings.code
        print(f'Starting {code} simulator')
        gsg_thread = threading.Thread(
            target=run_gsg_simulator, 
            args=(
                settings.freq, 
                lambda c, a, g: gsg_callback(c, settings, a, g), 
                stop_event, 
                code
            )
        )
        gsg_thread.start()
        threads.append(gsg_thread)
        print(f"{code} simulator started")
    else:
        print(f"Starting {settings.code} real sensor")
        gsg_thread = threading.Thread(target=gsg_loop, args=(settings, stop_event))
        gsg_thread.start()
        threads.append(gsg_thread)
        print("GSG real sensor started")