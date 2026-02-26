import threading
import time
import platform
import random
from shared.mqtt import batch_queue
from shared.latest_dht import get_latest_by_code
from simulators.lcd_simulator import run_lcd_simulator, set_lcd_state

def lcd_callback(line1, line2, code, settings):
    payload = {
        "measurement": "lcd",
        "device_name": settings.device_name,
        "code": code,
        "line1": line1,
        "line2": line2,
        "simulated": settings.simulated
    }
    batch_queue.put(payload)
    print(f"[{code}] LCD Update: L1: '{line1}' | L2: '{line2}'")

def get_cpu_temp():
    if platform.system() == "Windows":
        return '{:.2f}'.format(random.uniform(40.0, 60.0)) + ' C'
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as tmp:
            cpu = tmp.read()
        return '{:.2f}'.format(float(cpu)/1000) + ' C'
    except:
        return "0.00 C"

def run_lcd_real(callback, stop_event, code, settings):
    from .PCF8574 import PCF8574_GPIO
    from .Adafruit_LCD1602 import Adafruit_CharLCD
    from datetime import datetime

    address = 0x27
    try:
        mcp = PCF8574_GPIO(address)
    except:
        mcp = PCF8574_GPIO(0x3F)

    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
    mcp.output(3,1)
    lcd.begin(16,2)

    
    while not stop_event.is_set():
        latest_record = get_latest_by_code()
        if latest_record:
            temp = latest_record['temp']
            hum = latest_record['hum']

            line1 = f"Temp: {temp}C"
            line2 = f"Hum : {hum}%"

            lcd.setCursor(0, 0)
            lcd.message(line1.ljust(16) + '\n')
            lcd.message(line2.ljust(16))

            set_lcd_state(line1, line2)
            callback(line1, line2, code, settings)

        time.sleep(5)
    
    lcd.clear()

def run_lcd(settings, threads, stop_event):
    code = settings.code
    
    if settings.simulated:
        delay = settings.freq
        def simulated_logic():
            from datetime import datetime
            while not stop_event.is_set():
                l1 = f"CPU: {get_cpu_temp()} (S)"
                l2 = datetime.now().strftime('    %H:%M:%S')
                set_lcd_state(l1, l2)
                time.sleep(1)

        logic_thread = threading.Thread(target=simulated_logic)
        logic_thread.start()
        threads.append(logic_thread)

        lcd_thread = threading.Thread(
            target=run_lcd_simulator, 
            args=(delay, lambda l1, l2, c: lcd_callback(l1, l2, c, settings), stop_event, code)
        )
    else:
        lcd_thread = threading.Thread(
            target=run_lcd_real, 
            args=(lcd_callback, stop_event, code, settings)
        )

        print("LCD RUN!")

    lcd_thread.start()
    threads.append(lcd_thread)