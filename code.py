#!/usr/bin/env python3
"""
Controller for Trombone Champ by acting as a BLE HID keyboard to peer devices.
  Attach one button with a pullup resistor and one potentiometer to Feather nRF52840
  The button will send a configurable keycode to mobile device or computer;
  the slider will send a mouse movement in the y-axis direction.
"""
import board
import math
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.mouse import Mouse

# Global constants
MAX_SLIDER_Y_VALUE = 300  # roughly corresponds to pixel height of screen
MOUSE_Y_CHANGE_TOLERANCE = 12    # "pixel" change threshold; above this tolerance triggers mouse movement
NUM_SMOOTHED_SLIDER_INPUTS = 60  # Buffer for running average of slider values

# Initialize the onboard controls
clicky_button = DigitalInOut(board.A2)
clicky_button.direction = Direction.INPUT
slide_potentiometer = AnalogIn(board.A1)
onboard_button = DigitalInOut(board.SWITCH)
onboard_button.direction = Direction.INPUT

# Set up bluetooth connection
hid = HIDService()
device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries"
)
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "CircuitPython HID"

ble = adafruit_ble.BLERadio()
ble.name = "Hannex Trombone Champ"
if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)

# Set up mouse
mouse = Mouse(hid.devices)

# Helper functions for slider mapping
def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def map_pot_percent(voltage, v_min, v_max):
    f = (voltage - v_min) / (v_max - v_min)
    return math.trunc(f * 100)

def main_event_loop():
    while True:
        while not ble.connected:
            pass
        print("Bluetooth connected!")

        is_clicky_button_pushed = False
        is_onboard_button_pushed = False
        send_commands_enabled = True

        slider_buffer = [0 for _ in range(NUM_SMOOTHED_SLIDER_INPUTS)]
        mouse_y_previous = 0.0
        while ble.connected:

            # Update whether mouse commands should be sent
            _is_onboard_button_pushed = not onboard_button.value
            if is_onboard_button_pushed != _is_onboard_button_pushed:
                is_onboard_button_pushed = _is_onboard_button_pushed
                if is_onboard_button_pushed:
                    print("On-board button pressed!")

                    # Update sending state
                    send_commands_enabled = not send_commands_enabled

                    # If sending is newly disabled, release the clicky button!
                    if not send_commands_enabled and is_clicky_button_pushed:
                        is_clicky_button_pushed = False
                        mouse.release(Mouse.LEFT_BUTTON)

                else:
                    print("On-board button released")
                    pass

            if not send_commands_enabled:
                continue

            # Store current raw slider position from voltage
            slider_voltage = get_voltage(slide_potentiometer)
            slider_value_raw = MAX_SLIDER_Y_VALUE * map_pot_percent(slider_voltage, 1.62, 2.13) / 100
            slider_buffer.append(slider_value_raw)
            slider_buffer.pop(0)

            slider_buffer_avg = sum(slider_buffer) / NUM_SMOOTHED_SLIDER_INPUTS
            mouse_y_diff = math.trunc(mouse_y_previous - slider_buffer_avg)

            # Check/update button state
            _is_clicky_button_pushed = clicky_button.value
            if is_clicky_button_pushed != _is_clicky_button_pushed:
                is_clicky_button_pushed = _is_clicky_button_pushed
                # print("Value changed!")  # debug
                if is_clicky_button_pushed:
                    mouse.press(Mouse.LEFT_BUTTON)
                else:
                    mouse.release(Mouse.LEFT_BUTTON)

            # Update mouse position
            elif abs(mouse_y_diff) >= MOUSE_Y_CHANGE_TOLERANCE:
                # print("UPDATING: ", mouse_y_previous, slider_buffer_avg, mouse_y_diff)
                mouse.move(y=mouse_y_diff)
                mouse_y_previous = slider_buffer_avg

        ble.start_advertising(advertisement)


if __name__ == "__main__":
    main_event_loop()
