from machine import Pin
from utility import EventPin

class Poke:

    def __init__(self, valve_pin, led_pin, beambreak_pin):

        self._valve = Pin(valve_pin, Pin.OUT)
        self._led = Pin(led_pin, Pin.OUT)
        self.beambreak = EventPin(beambreak_pin, Pin.IN, Pin.PULL_UP)

    @property
    def led(self) -> bool:
        return True if self._led.value() == 1 else False

    @led.setter
    def led(self, value: bool):
        self._led.value(1 if value else 0)

    @property
    def valve(self) -> bool:
        return True if self._valve.value() == 1 else False

    @valve.setter
    def valve(self, value: bool):
        self._valve.value(1 if value else 0)
