import random
import time

def run_gsg_simulator(delay, callback, stop_event, code):
    """
    Simulates MPU6050 gyroscope/accelerometer readings.
    
    Accel: ±2g range → values roughly in [-2.0, 2.0] (g-force)
    Gyro:  ±250°/s range → values roughly in [-250.0, 250.0] (°/s)
    """
    # Simulate a slowly drifting baseline to make it feel realistic
    base_accel = [0.0, 0.0, 1.0]  # Z-axis at 1g (gravity)
    base_gyro  = [0.0, 0.0, 0.0]

    while not stop_event.is_set():
        # Add small drift to baseline over time
        base_accel = [round(b + random.uniform(-0.005, 0.005), 3) for b in base_accel]
        base_gyro  = [round(b + random.uniform(-0.1,   0.1),   3) for b in base_gyro]

        # Add noise on top of baseline
        accel = [round(b + random.gauss(0, 0.02), 3) for b in base_accel]
        gyro  = [round(b + random.gauss(0, 0.5),  3) for b in base_gyro]

        # Clamp to realistic sensor ranges
        accel = [max(-2.0,   min(2.0,   v)) for v in accel]
        gyro  = [max(-250.0, min(250.0, v)) for v in gyro]

        callback(code, accel, gyro)

        time.sleep(delay)