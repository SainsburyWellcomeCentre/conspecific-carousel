from machine import Pin, PWM
from micropython import const

DEFAULT_FREQ = const(1000)  # Default frequency in Hz
class BUZZER:
    def __init__(self, pin: int):
        self._out = PWM(Pin(pin), freq=DEFAULT_FREQ, duty_u16=0)  # Initialize PWM with default frequency and 0% duty cycle
        self._out.freq(DEFAULT_FREQ)  # Set the frequency to the default value
        self._enabled = False

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if value:
            self._out.duty_u16(32768)  # 50% duty cycle
            self._enabled = True
        else:
            self._out.duty_u16(0)  # 0% duty cycle
            self._enabled = False

    @property
    def freq(self):
        freq = self._out.freq()
        return int(freq // 20)  # Convert to Hz

    @freq.setter
    def freq(self, freq: int):
        freq = freq * 20
        self._out.freq(freq)
