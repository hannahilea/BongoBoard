#!/usr/bin/env python3
"""
BongoBoard controller that acts as a BLE HID keyboard to peer devices.
"""
import board # type: ignore 
import time
from digitalio import DigitalInOut, Direction
from digitalio import Pull

button_1 = DigitalInOut(board.D10)
button_1.direction = Direction.INPUT
button_1.pull = Pull.UP

button_2 = DigitalInOut(board.D9)
button_2.direction = Direction.INPUT
button_2.pull = Pull.UP

button_3 = DigitalInOut(board.D6)
button_3.direction = Direction.INPUT
button_3.pull = Pull.UP

button_4 = DigitalInOut(board.D5)
button_4.direction = Direction.INPUT
button_4.pull = Pull.UP


def main_event_loop():
    i = 0
    while True:
        print("Buttons pushed (", i, ")? ", not button_1.value, not button_2.value, 
              not button_3.value, not button_4.value)
        time.sleep(.2)
        i += 1

if __name__ == "__main__":
    main_event_loop()
