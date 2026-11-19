import math
from machine import Pin, SoftI2C
from utime import sleep

from buzzer import Buzzer
from stepper import Stepper
from hcsr04 import HCSR04
from mpu6050 import accel
import oled

# --- Pin map -------------------------------------------------------------
LED_PIN = 12
BUTTON_PIN = 27
BUZZER_PIN = 15

LEFT_STEP_PIN = 13
RIGHT_STEP_PIN = 19

TRIGGER_PIN = 5
ECHO_PIN = 18

I2C_SDA_PIN = 21
I2C_SCL_PIN = 22

# --- Robot geometry: convert a target distance into stepper motor steps --
STEPS_PER_REVOLUTION = 200
WHEEL_RADIUS_CM = 3
WHEEL_CIRCUMFERENCE_CM = 2 * math.pi * WHEEL_RADIUS_CM
STEPS_PER_CM = STEPS_PER_REVOLUTION / WHEEL_CIRCUMFERENCE_CM

# AcY readings beyond this magnitude mean the robot has tipped over.
TILT_THRESHOLD = 12000

# --- Components ------------------------------------------------------------
led = Pin(LED_PIN, Pin.OUT)
led.value(0)

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

buzzer = Buzzer(BUZZER_PIN)

left_stepper = Stepper(LEFT_STEP_PIN)
right_stepper = Stepper(RIGHT_STEP_PIN)

sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)

i2c = SoftI2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
display = oled.I2C(128, 64, i2c)
accelerometer = accel(i2c)


def show(lines):
    """Clears the OLED and prints each string in `lines` on its own row."""
    display.fill(0)
    for row, line in enumerate(lines):
        display.text(line, 0, row)
    display.show()


def wait_button_press():
    """Blocks until the button (active-low, pull-up) is pressed."""
    while button.value() == 1:
        sleep(0.01)


def get_steps_from_distance(distance_cm):
    """Converts a distance in centimeters into the number of stepper
    motor steps needed to travel it, based on the wheel's circumference."""
    return round(distance_cm * STEPS_PER_CM)


def is_tilted(values):
    return values["AcY"] > TILT_THRESHOLD or values["AcY"] < -TILT_THRESHOLD


while True:
    led.value(0)
    show(["Press button", "to start"])
    wait_button_press()

    buzzer.beep_once()

    distance = sensor.distance_cm()
    steps = get_steps_from_distance(distance)
    show(["Dist: {}cm".format(distance), "Steps: {}".format(steps)])

    reached = True
    for _ in range(steps):
        left_stepper.move_one_step()
        right_stepper.move_one_step()

        values = accelerometer.get_values()
        if is_tilted(values):
            reached = False
            break

    if reached:
        show(["REACHED"])
        buzzer.beep_once()
    else:
        led.value(1)
        show(["TILTED"])
        for _ in range(3):
            buzzer.beep_once()
            sleep(0.2)

    sleep(3)
