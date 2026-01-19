from machine import Pin
from asyncio import Event


class Poke:

    def __init__(self, valve_pin, led_pin, beambreak_pin):

        self._valve = Pin(valve_pin, Pin.OUT)
        self._led = Pin(led_pin, Pin.OUT)
        self._beambreak = Pin(beambreak_pin, Pin.IN, Pin.PULL_UP)
        self.isr = Event()
        self._beambreak.irq(lambda pin: self.isr.set(), Pin.IRQ_FALLING | Pin.IRQ_RISING, hard=True)
        # self._beambreak.irq(lambda pin: print('s'), Pin.IRQ_FALLING | Pin.IRQ_RISING, hard=True)

    @property
    def beambreak(self) -> bool:
        return True if self._beambreak.value() == 1 else False

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
