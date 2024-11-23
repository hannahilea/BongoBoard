#!/usr/bin/env python3
"""
BongoBoard controller that acts as a BLE HID keyboard to peer devices.
"""
import board
from digitalio import DigitalInOut, Direction

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService

# Initialize the onboard controls
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
scan_response.complete_name = "BongoBoard"

ble = adafruit_ble.BLERadio()
ble.name = "BongoBoard"
if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)

def main_event_loop():
    while True:
        while not ble.connected:
            pass
        print("Bluetooth connected!")

        is_onboard_button_pushed = False
        while ble.connected:

            # Update button state
            _is_onboard_button_pushed = not onboard_button.value
            if is_onboard_button_pushed != _is_onboard_button_pushed:
                is_onboard_button_pushed = _is_onboard_button_pushed
                if is_onboard_button_pushed:
                    print("On-board button pressed!")
                else:
                    print("On-board button released")

        ble.start_advertising(advertisement)


if __name__ == "__main__":
    main_event_loop()
