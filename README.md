# Sensor Robot (ESP32 + MicroPython + Wokwi)

By Abdulhakeem Omotolani Yaqoob

A two-wheel robot that waits for a button press, measures how far away an
obstacle is with an ultrasonic sensor, drives that exact distance using two
stepper motors, and aborts with an alarm if an accelerometer detects it has
tipped over mid-drive.

## Block diagram

See `block_diagram.png` / `block_diagram.pdf` (generated for this submission)
for the full visual diagram. Summary:

```
LED(D12) Button(D27) Buzzer(D15) HC-SR04(TRIG=D5,ECHO=D18) OLED(I2C) MPU6050(I2C)
   \         |           |              |                     |          /
    \________|___________|______________|_____________________|_________/
                                  |
                              ESP32 (MicroPython, main.py)
                                  |
                 ________________|________________
                /                                  \
     A4988 (left, STEP=D13)              A4988 (right, STEP=D19)
                |                                    |
       Stepper Motor (left wheel)          Stepper Motor (right wheel)
```

OLED and MPU6050 share the same I2C bus: SDA = GPIO21, SCL = GPIO22.

## Pin map

| Signal                         | ESP32 pin |
|---------------------------------|-----------|
| LED                              | GPIO12 |
| Button (pull-up)                 | GPIO27 |
| Buzzer                            | GPIO15 |
| Left stepper driver (A4988) STEP  | GPIO13 |
| Right stepper driver (A4988) STEP | GPIO19 |
| HC-SR04 TRIG                      | GPIO5 |
| HC-SR04 ECHO                      | GPIO18 |
| I2C SDA (OLED + MPU6050)          | GPIO21 |
| I2C SCL (OLED + MPU6050)          | GPIO22 |

Both A4988 drivers: `VDD`→3V3, `GND`→GND, `DIR` tied permanently low (the
`Stepper` class only ever calls `move_one_step()`, so direction is fixed in
hardware rather than software), and `RESET` wired to that same driver's
`SLEEP` pin (per Wokwi's A4988 docs, `RESET` must be high and `SLEEP` is
already pulled high by default). `ENABLE`/`MS1`/`MS2`/`MS3` are left
unconnected (Wokwi defaults them to enabled/full-step). Each driver's
`1A`/`1B`/`2A`/`2B` go to its stepper motor's `B+`/`B-`/`A+`/`A-`.

## Files

- `buzzer.py`, `hcsr04.py`, `stepper.py`, `mpu6050.py`, `oled.py` — the
  official starter libraries, copied in unmodified (all five were already
  fully implemented in the starter repo, not templates needing code added).
- `main.py` — the application:
  - `wait_button_press()` blocks until the button (active-low, pull-up) is
    pressed.
  - `get_steps_from_distance(distance_cm)` converts a distance into stepper
    steps using the wheel's circumference (`200` steps/revolution, `3cm`
    wheel radius → `10.6103` steps/cm — see `distance_vs_steps.txt`).
  - `show(lines)` clears the OLED and prints each string on its own line.
  - `is_tilted(values)` checks the MPU6050's `AcY` reading against a
    `±12000` threshold.
  - The main loop: shows "Press button to start" with the LED off, blocks on
    the button, beeps once, measures distance, shows distance+steps on the
    OLED, then steps both motors one step at a time (checking for a tilt
    after every single step) until either the target step count is reached
    or a tilt is detected — showing "REACHED" (+1 beep) or turning the LED
    on and showing "TILTED" (+3 beeps) accordingly, then pausing 3 seconds
    before returning to IDLE.
- `diagram.json` — Wokwi wiring diagram with the LED, button, buzzer,
  HC-SR04, OLED, MPU6050, and both A4988+stepper motor pairs already wired
  per the pin map above.
- `distance_vs_steps.txt` — the required distance→steps table for 10/20/30/
  50/100cm.
- `block_diagram.png` / `.pdf` — the required block diagram image.

## Setting it up in Wokwi

1. Create a **new Wokwi project** using the **MicroPython ESP32** template
   (not the Arduino/C++ template — that fails to build since there's no
   `setup()`/`loop()`).
2. Replace the generated `diagram.json` with this folder's `diagram.json`.
3. Replace `main.py` with this folder's `main.py`.
4. Add `buzzer.py`, `hcsr04.py`, `stepper.py`, `mpu6050.py`, and `oled.py` as
   new files with the contents from this folder.
5. Add this `README.md` itself as a new file in the Wokwi project too, so it
   is included when the project is exported/submitted as a ZIP.
6. Run it, open the serial monitor to watch prints, and watch the OLED panel
   in the diagram.

## Testing checklist (per the project's Part 1-5 instructions)

- Button value prints `0` when pressed (pull-up wiring).
- LED turns on only while the button is held, if testing standalone; in the
  final app the LED is only on during a `TILTED` abort.
- Buzzer beeps once (`beep_once()`) when the button is pressed.
- `wait_button_press()` blocks until pressed, then returns.
- Holding the button moves both steppers continuously if tested standalone
  (final app instead steps a calculated number of times per button press).
- `distance_cm()` prints a sane value when you move the HC-SR04 "obstacle"
  slider/object in the simulator.
- OLED shows the distance and calculated step count after a button press.
- Clicking the MPU6050 in the simulator and dragging its Y slider changes
  the printed `AcY` value; dragging it past ±12000 while the robot is
  driving should trigger the TILTED path (LED on, 3 beeps, OLED message,
  motors stop immediately).
- Full behavior: IDLE → press button → beep → measure+display → drive →
  REACHED (beep once) or TILTED (LED + 3 beeps) → 3s pause → back to IDLE.

## Distance → steps calculation

```
wheel radius        = 3 cm
wheel circumference = 2 * pi * 3 = 18.8496 cm   (one 200-step revolution)
steps per cm        = 200 / 18.8496 = 10.6103
steps(distance_cm)  = round(distance_cm * steps_per_cm)
```

| Distance (cm) | Steps |
|---------------|-------|
| 10            | 106   |
| 20            | 212   |
| 30            | 318   |
| 50            | 531   |
| 100           | 1061  |

## Submission

Per the rubric, submit:
1. The Wokwi project ZIP (Save → blue dropdown arrow → Download project ZIP).
2. `block_diagram.png` or `block_diagram.pdf`.
3. `distance_vs_steps.txt`.
