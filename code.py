#!/usr/bin/env python3
"""
BongoBoard controller that acts as a BLE HID keyboard to peer devices.
"""
import board # type: ignore 
import time
from digitalio import DigitalInOut, Direction
from digitalio import Pull
from analogio import AnalogIn

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

mic = AnalogIn(board.A1)
NUM_SMOOTHED_MIC_INPUTS = 100
mic_buffer = [0 for _ in range(NUM_SMOOTHED_MIC_INPUTS)]

def main_event_loop():
    i = 0
    while True:
        mic_buffer.append(mic.value)
        mic_buffer.pop(0)

        i += 1
        if i % 1000 == 0:
            print("Buttons pushed? ", not button_1.value, not button_2.value, 
                not button_3.value, not button_4.value)
            print("Mic: ", max(mic_buffer))
        

if __name__ == "__main__":
    main_event_loop()
