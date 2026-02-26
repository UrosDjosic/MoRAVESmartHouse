import threading

# PIN system state
CORRECT_PIN = "1234"  # change as needed

_lock = threading.Lock()
_system_armed = False       # True = system is active/armed
_alarm_triggered = False    # True = alarm is going off
_arm_timer = None           # 10s timer before arming

def is_armed():
    return _system_armed

def is_alarm_triggered():
    return _alarm_triggered

def set_armed(val: bool):
    global _system_armed
    with _lock:
        _system_armed = val

def set_alarm_triggered(val: bool):
    global _alarm_triggered
    with _lock:
        _alarm_triggered = val