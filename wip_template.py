#!/usr/bin/env python3
"""
BongoBoard controller that acts as a BLE HID keyboard to peer devices.
"""
import board  # type: ignore 
# import time
from digitalio import DigitalInOut, Direction
from digitalio import Pull
from analogio import AnalogIn

# import adafruit_ble
# from adafruit_ble.advertising import Advertisement
# from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
# from adafruit_ble.services.standard.hid import HIDService
# from adafruit_ble.services.standard.device_info import DeviceInfoService


# Set up hardware
class BongoButtons:
    def __init__(self):
        self.left_top = DigitalInOut(board.D10)
        self.left_bottom = DigitalInOut(board.D9)
        self.right_top = DigitalInOut(board.D6)
        self.right_bottom = DigitalInOut(board.D5)
        self.buttons = [self.left_top, self.left_bottom, self.right_top, self.right_bottom]

        # Set up buttons 
        for b in self.buttons:
            b.direction = Direction.INPUT 
            b.pull = Pull.UP

        # Set up button state
        self.last_polled_state = [not b.value for b in self.buttons]

    def __str__(self):
        return f"{[b.value for b in self.buttons]}"

    def get_current_button_status(self):
        updated_status = ["" for _ in self.buttons]
        current_state = [not b.value for b in self.buttons] 
        any_changed = False
        for i in range(len(self.buttons)):
            # print(i, self.last_polled_state, current_state)
            if current_state[i] == self.last_polled_state[i]:
                updated_status[i] = "pressed" if current_state[i] else "released"
            elif current_state[i] == True:
                updated_status[i] = "Newly pressed" 
                any_changed = True
            else:
                updated_status[i] = "Newly released" 
                any_changed = True
        self.last_polled_state = current_state 
        return any_changed, updated_status


BONGO_BUTTONS = BongoButtons()
print("Instantiated BongoBoard!", BONGO_BUTTONS)

MIC = AnalogIn(board.A1)
NUM_SMOOTHED_MIC_INPUTS = 1000
MIC_BUFFER = [0 for _ in range(NUM_SMOOTHED_MIC_INPUTS)]

# Set up bluetooth
# hid = HIDService()
# device_info = DeviceInfoService(
#     software_revision=adafruit_ble.__version__,
#     manufacturer="Adafruit Industries"
# )
# advertisement = ProvideServicesAdvertisement(hid)
# advertisement.appearance = 961
# scan_response = Advertisement()
# scan_response.complete_name = "BongoBoard"

# ble = adafruit_ble.BLERadio()
# ble.name = "BongoBoard"
# if not ble.connected:
#     print("advertising")
#     ble.start_advertising(advertisement, scan_response)
# else:
#     print("already connected")
#     print(ble.connections)


# Some development constants that can probably be removed soonish!
MONITOR_MIC = False  # Keep MIC buffer up to date?
VERBOSE = True  # Show assorted logging/debugging statements?


def main_event_loop():
    while True:
        # while not ble.connected:
        #     continue
        # print("Bluetooth connected!")

        if MONITOR_MIC:
            MIC_BUFFER.append(MIC.value)
            MIC_BUFFER.pop(0)
            if VERBOSE:
                abs_max = max([abs(x) for x in MIC_BUFFER])
                print(">mic_abs_max:", abs_max, ",neg_abs_max:", -abs_max, 
                      ",mic_raw:", MIC_BUFFER[NUM_SMOOTHED_MIC_INPUTS - 1], "\r\n")
        
        any_changed, button_state = BONGO_BUTTONS.get_current_button_status()
        if any_changed:
            print(button_state)


if __name__ == "__main__":
    main_event_loop()
