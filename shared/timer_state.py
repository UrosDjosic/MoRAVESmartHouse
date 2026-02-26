import threading

_lock = threading.Lock()

timer_seconds = 180      # default 5 min
btn_add_seconds = 30     # default +30s per button press
timer_running = False
timer_expired = False
_timer_thread = None
_stop_event = None

def get_state():
    return {
        "seconds": timer_seconds,
        "running": timer_running,
        "expired": timer_expired,
        "btn_add": btn_add_seconds
    }

def set_timer(seconds):
    global timer_seconds, timer_expired
    with _lock:
        timer_seconds = seconds
        timer_expired = False

def set_btn_add(seconds):
    global btn_add_seconds
    with _lock:
        btn_add_seconds = seconds

def add_seconds(n):
    global timer_seconds, timer_expired
    with _lock:
        timer_seconds += n
        timer_expired = False
        print(f"[TIMER] +{n}s → {timer_seconds}s remaining")

def start():
    global timer_running
    with _lock:
        timer_running = True

def stop():
    global timer_running
    with _lock:
        timer_running = False

def tick():
    global timer_seconds, timer_running, timer_expired
    with _lock:
        if timer_running and timer_seconds > 0:
            timer_seconds -= 1
            if timer_seconds == 0:
                timer_expired = True
                timer_running = False
                print("[TIMER] ⏰ Timer expired!")