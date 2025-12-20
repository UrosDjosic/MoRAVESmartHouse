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
from devices import make_default_pi1_devices


class PI1Controller:
    def __init__(self, devices, poll_interval=10.0):
        self.devices = devices
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._threads = []

    def _sensor_loop(self, name, sensor):
        while not self._stop.is_set():
            try:
                val = sensor.read()
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{ts}] SENSOR {name}: {val}")
            except Exception as e:
                print(f"Error reading {name}: {e}")
            time.sleep(self.poll_interval)

    def start(self):
        #start sensor threads
        for name, dev in self.devices.items():
            if hasattr(dev, 'read'):
                t = threading.Thread(target=self._sensor_loop, args=(name, dev), daemon=True)
                t.start()
                self._threads.append(t)

    def stop(self):
        self._stop.set()
        for t in self._threads:
            t.join(timeout=0.2)

    def status(self):
        s = {}
        for name, dev in self.devices.items():
            if hasattr(dev, '_on'):
                s[name] = getattr(dev, '_on')
            elif hasattr(dev, '_color'):
                s[name] = getattr(dev, '_color')
            else:
                s[name] = 'N/A'
        return s


def interactive_loop(ctrl, devices, run_duration=0):
    start = time.time()
    if run_duration > 0:
        #non-interactive: just run sensors for run_duration seconds
        try:
            while time.time() - start < run_duration:
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass
        return

    print("Entering interactive control loop. Type 'help' for commands.")
    while True:
        try:
            cmd = input('> ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting...')
            break
        if not cmd:
            continue
        if cmd in ('exit', 'quit'):
            break
        if cmd == 'help':
            print("Commands: led on|off, buzzer on|off, status, help, exit")
            continue
        if cmd.startswith('led '):
            if 'DL' in devices:
                if cmd.endswith('on'):
                    devices['DL'].on()
                else:
                    devices['DL'].off()
            else:
                print('LED device DL not present')
            continue
        if cmd.startswith('buzzer '):
            if 'db' in {k.lower(): v for k, v in devices.items()}:
                db = devices.get('DB') or devices.get('db')
                if cmd.endswith('on'):
                    db.on()
                else:
                    db.off()
            else:
                if 'DB' in devices:
                    if cmd.endswith('on'):
                        devices['DB'].on()
                    else:
                        devices['DB'].off()
                else:
                    print('Buzzer DB not present')
            continue
        if cmd == 'status':
            s = ctrl.status()
            for k, v in s.items():
                print(f"{k}: {v}")
            continue
        print('Unknown command, type help')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--simulate-all', action='store_true', help='simulate all PI1 devices')
    p.add_argument('--run-duration', type=int, default=0, help='if >0 run for that many seconds then exit')
    return p.parse_args()


def main():
    args = parse_args()
    simulated = args.simulate_all
    devices = make_default_pi1_devices(simulated=simulated)
    ctrl = PI1Controller(devices)
    ctrl.start()
    try:
        interactive_loop(ctrl, devices, run_duration=args.run_duration)
    finally:
        ctrl.stop()


if __name__ == '__main__':
    main()
