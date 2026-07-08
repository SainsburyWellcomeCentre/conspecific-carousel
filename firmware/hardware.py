from machine import Pin, UART
from utility import EventPin
from poke import Poke
from door import RatDoor, MiceDoor
from table import Table
from buzzer import BUZZER

UART_BAUD = 1_000_000  # Baud rate for hardware UART
UART_NUM = 0  # Use UART0
INDICATOR_PIN = 25  # GPIO for indicator LED

RAT_SETTING = True  # Set to True for rat configuration, False for mice configuration

portA = Poke(valve_pin=0, led_pin=3, beambreak_pin=12)
portB = Poke(valve_pin=1, led_pin=4, beambreak_pin=13)
portC = Poke(valve_pin=2, led_pin=5, beambreak_pin=14)

buzzer = BUZZER(pin=7)

camA = EventPin(8, Pin.IN, Pin.PULL_UP)
camB = EventPin(9, Pin.IN, Pin.PULL_UP)

snsr_door = EventPin(26, Pin.IN, Pin.PULL_DOWN)
snsr_table = EventPin(27, Pin.IN, Pin.PULL_DOWN)

sync_out = Pin(10, Pin.OUT, value=1)  # Sync output pin, default high

led = Pin(INDICATOR_PIN, Pin.OUT, value=0)  # Indicator LED

uart = UART(UART_NUM, baudrate=UART_BAUD, tx=Pin(16), rx=Pin(17))  # Adjust pins if needed

if RAT_SETTING:
    door = RatDoor(uart)  # Door configuration for rats
else:
    door = MiceDoor(uart)  # Door configuration for mice

table = Table(uart)
