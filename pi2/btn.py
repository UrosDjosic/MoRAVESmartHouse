import RPi.GPIO as GPIO
def button_pressed(event):
    print("BUTTON PRESS DETECTED")
PORT_BUTTON = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PORT_BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(PORT_BUTTON, GPIO.RISING, callback =
button_pressed, bouncetime = 100)