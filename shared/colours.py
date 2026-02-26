
import RPi.GPIO as GPIO
from shared.device import BRGB

# --- Color functions using device pins ---
def turnOff(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.LOW)
    GPIO.output(settings.green_pin, GPIO.LOW)
    GPIO.output(settings.blue_pin, GPIO.LOW)

def white(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.HIGH)
    GPIO.output(settings.green_pin, GPIO.HIGH)
    GPIO.output(settings.blue_pin, GPIO.HIGH)

def red(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.HIGH)
    GPIO.output(settings.green_pin, GPIO.LOW)
    GPIO.output(settings.blue_pin, GPIO.LOW)

def green(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.LOW)
    GPIO.output(settings.green_pin, GPIO.HIGH)
    GPIO.output(settings.blue_pin, GPIO.LOW)

def blue(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.LOW)
    GPIO.output(settings.green_pin, GPIO.LOW)
    GPIO.output(settings.blue_pin, GPIO.HIGH)

def yellow(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.HIGH)
    GPIO.output(settings.green_pin, GPIO.HIGH)
    GPIO.output(settings.blue_pin, GPIO.LOW)

def purple(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.HIGH)
    GPIO.output(settings.green_pin, GPIO.LOW)
    GPIO.output(settings.blue_pin, GPIO.HIGH)

def cyan(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.LOW)
    GPIO.output(settings.green_pin, GPIO.HIGH)
    GPIO.output(settings.blue_pin, GPIO.HIGH)

def pink(settings: BRGB):
    GPIO.output(settings.red_pin, GPIO.HIGH)
    GPIO.output(settings.green_pin, GPIO.LOW)
    GPIO.output(settings.blue_pin, GPIO.HIGH)

# --- Map color names to functions ---
colors = {
    "red": red,
    "orange": yellow,   # approximate orange
    "yellow": yellow,
    "green": green,
    "cyan": cyan,
    "blue": blue,
    "lightBlue": cyan,  # approximate
    "purple": purple,
    "pink": pink,
    "white": white,
    "off": turnOff
}
BUTTON_TO_COLOR = {
    "1": "red",
    "2": "green",
    "3": "blue",
    "4": "yellow",
    "5": "cyan",
    "6": "purple",
    "7": "white",
    "8": "pink",
    "9": "orange",
    "0": "off",
    "OK": "white"
}
def handle_brgb_from_ir(button, brgb_settings):
    if button in BUTTON_TO_COLOR:
        color = BUTTON_TO_COLOR[button]
        colors[color](brgb_settings)
        print(f"💡 Set color {color}")

