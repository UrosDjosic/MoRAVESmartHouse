import threading
import time
from shared.mqtt import batch_queue
from shared.device import Device
from simulators.dms_simulator import run_dms_simulator
import shared.mqtt as mqtt_state

CORRECT_PIN = "1234"

_current_input = []
_pin_lock = threading.Lock()

# ── System state ───────────────────────────────────────────────────────────
system_armed = False      # True = system is active/armed
alarm_active = False      # True = alarm is currently ringing
_arm_timer = None         # 10s arming delay timer

def is_armed():
    return system_armed

def is_alarm_active():
    return alarm_active

def arm_system(code, settings):
    global system_armed
    system_armed = True
    mqtt_state.alarm_enabled = True  # ← enable alarms when armed
    print("[DMS] ✅ System ARMED")

def disarm_system(code, settings):
    global system_armed, alarm_active
    system_armed = False
    alarm_active = False
    mqtt_state.alarm_enabled = False  # ← disable alarms when disarmed
    print("[DMS] 🔓 System DISARMED")
    _send_alarm(code, settings, 0)
    from pi1.db import deactivate_buzzer
    deactivate_buzzer()

def trigger_alarm(code, settings):
    global alarm_active
    if not system_armed:
        return
    alarm_active = True
    print("[DMS] 🚨 ALARM TRIGGERED")
    _send_alarm(code, settings, 1)
    from pi1.db import activate_buzzer
    activate_buzzer()

def _send_alarm(code, settings, value):
    batch_queue.put({
        "measurement": "alarm",
        "device_name": settings.device_name,
        "code": code,
        "value": value,
        "simulated": settings.simulated
    })

def _send_system_state(code, settings, state):
    batch_queue.put({
        "measurement": "system_state",
        "device_name": settings.device_name,
        "code": code,
        "state": state,
        "simulated": settings.simulated
    })

def dms_callback(code, key, settings: Device):
    batch_queue.put({
        "measurement": "door membrane switch",
        "device_name": settings.device_name,
        "code": code,
        "key": key,
        "simulated": settings.simulated
    })
    print(f"[{code}] Key pressed: {key}")
    _handle_pin_input(key, code, settings)

def _handle_pin_input(key, code, settings):
    global _current_input, _arm_timer

    with _pin_lock:
        if key == '*':
            _current_input = []
            print("[DMS] Input reset")
            return

        if key == '#':
            entered = ''.join(_current_input)
            _current_input = []
            print(f"[DMS] PIN entered: {entered}")

            if entered == CORRECT_PIN:
                if not system_armed and not alarm_active:
                    # ── Arm after 10s delay ────────────────────────────
                    print("[DMS] ✅ Correct PIN — arming in 10s...")
                    if _arm_timer:
                        _arm_timer.cancel()
                    _arm_timer = threading.Timer(10.0, arm_system, args=(code, settings))
                    _arm_timer.start()
                else:
                    # ── Disarm / clear alarm ───────────────────────────
                    print("[DMS] ✅ Correct PIN — disarming system")
                    if _arm_timer:
                        _arm_timer.cancel()
                    disarm_system(code, settings)
            else:
                print("[DMS] ❌ Wrong PIN")
            return

        _current_input.append(key)
        print(f"[DMS] Input so far: {''.join(_current_input)}")

def run_dms(settings: Device, threads, stop_event):
    if settings.simulated:
        code = settings.code
        delay = settings.freq
        print(f"Starting {code} simulator")
        t = threading.Thread(
            target=run_dms_simulator,
            args=(delay, lambda c, k: dms_callback(c, k, settings), stop_event, code),
            daemon=True
        )
        t.start()
        threads.append(t)
    else:
        def keypad_loop(settings, stop_event):
            import RPi.GPIO as GPIO
            R_PINS = settings.r_pins
            C_PINS = settings.c_pins
            code = settings.code
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            for pin in R_PINS:
                GPIO.setup(pin, GPIO.OUT)
            for pin in C_PINS:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            def readLine(line_pin, characters):
                GPIO.output(line_pin, GPIO.HIGH)
                for idx, col_pin in enumerate(C_PINS):
                    if GPIO.input(col_pin) == 1:
                        key = characters[idx]
                        dms_callback(code, key, settings)
                        while GPIO.input(col_pin) == 1:
                            time.sleep(0.05)
                GPIO.output(line_pin, GPIO.LOW)

            try:
                while not stop_event.is_set():
                    readLine(R_PINS[0], ["1","2","3","A"])
                    readLine(R_PINS[1], ["4","5","6","B"])
                    readLine(R_PINS[2], ["7","8","9","C"])
                    readLine(R_PINS[3], ["*","0","#","D"])
                    time.sleep(0.1)
            finally:
                GPIO.cleanup()

        t = threading.Thread(target=keypad_loop, args=(settings, stop_event), daemon=True)
        t.start()
        threads.append(t)
        print(f"DMS real sensor started on code: {settings.code}")