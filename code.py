#!/usr/bin/env python3
"""
BongoBoard controller that acts as a BLE HID keyboard to peer devices.
"""
import board  # type: ignore
# import time
from digitalio import DigitalInOut, Direction
from digitalio import Pull

import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


# Set up bluetooth
hid = HIDService()
device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__,
    manufacturer="Adafruit Industries"
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

k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)

# Set up hardware
class BongoButton:
    def __init__(self, name, button_pin, button_pushed_key):
        self.button = DigitalInOut(button_pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP
        self.last_polled_state = not self.button.value
        self.button_pushed_key = button_pushed_key
        self.name = name

    def __str__(self):
        return f"{self.button.value}"

    def handle(self):
        current_state = not self.button.value
        if (current_state != self.last_polled_state):
            if current_state:
                # print(self.name, " pushed! Triggering ", self.button_pushed_key)
                k.send(self.button_pushed_key)
            self.last_polled_state = current_state


BONGO_BUTTONS = [BongoButton("left_top", board.D10, Keycode.DOWN_ARROW),
                 BongoButton("left_bottom", board.D9, Keycode.UP_ARROW),
                 BongoButton("right_top", board.D6, Keycode.RIGHT_ARROW),
                 BongoButton("right_bottom", board.D5, Keycode.LEFT_ARROW)]
print("Instantiated BongoBoard!", BONGO_BUTTONS)


def main_event_loop():
    bt_connected = False
    while True:
        while not ble.connected:
            continue
        if not bt_connected:
            print("Bluetooth connected!")
            bt_connected = True

        for button in BONGO_BUTTONS:
            button.handle()

if __name__ == "__main__":
    main_event_loop()
