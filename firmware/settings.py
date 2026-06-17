from machine import Pin, UART
from utility import EventPin
from poke import Poke
from door import Door, RAT_SETTING, MICE_SETTING
from table import Table


UART_BAUD = 1_000_000  # Baud rate for hardware UART
UART_NUM = 0  # Use UART0
INDICATOR_PIN = 25  # GPIO for indicator LED

portA = Poke(valve_pin=0, led_pin=3, beambreak_pin=12)
portB = Poke(valve_pin=1, led_pin=4, beambreak_pin=13)
portC = Poke(valve_pin=2, led_pin=5, beambreak_pin=14)

camA = EventPin(8, Pin.IN, Pin.PULL_UP)
camB = EventPin(9, Pin.IN, Pin.PULL_UP)

snsr_door = EventPin(26, Pin.IN, Pin.PULL_DOWN)
snsr_table = EventPin(27, Pin.IN, Pin.PULL_DOWN)

sync_out = Pin(10, Pin.OUT, value=1)  # Sync output pin, default high

led = Pin(INDICATOR_PIN, Pin.OUT, value=0)  # Indicator LED

uart = UART(UART_NUM, baudrate=UART_BAUD, tx=Pin(16), rx=Pin(17))  # Adjust pins if needed

door = Door(uart, setting=RAT_SETTING)  # Door configuration, change setting to MICE_SETTING if needed

table = Table(uart)
