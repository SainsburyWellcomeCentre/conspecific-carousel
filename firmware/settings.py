from machine import Pin, UART
from dynamixel.dynamixel import Dynamixel
from dynamixel.model import DynamixelModel
from debounce import DebouncedInput
# Configuration
USB_BAUD = 57600  # Baud rate for USB serial (usually UART0)
UART_BAUD = 57600  # Baud rate for hardware UART
UART_NUM = 0  # Use UART0
INDICATOR_PIN = 25  # GPIO for indicator LED
LIMITER_PIN = 28  # GPIO for limiter
BUFFER_SIZE = 256  # Power of 2 recommended


blink_state = False
class NosePoke:

    def __init__(self, beambreak_pin, valve_pin, led_pin):
        self.beambreak = Pin(beambreak_pin, Pin.IN)
        self.valve = Pin(valve_pin, Pin.OUT)
        self.led = Pin(led_pin, Pin.OUT)


portA = NosePoke(beambreak_pin=12, valve_pin=0, led_pin=3)
portB = NosePoke(beambreak_pin=13, valve_pin=1, led_pin=4)
portC = NosePoke(beambreak_pin=14, valve_pin=2, led_pin=5)
# Setup
indicator = Pin(INDICATOR_PIN, Pin.OUT)
indicator.value(0)

# limiter = DebouncedInput(LIMITER_PIN, 0)

limiter = Pin(LIMITER_PIN, Pin.IN, Pin.PULL_UP)


# UART for external device (e.g., UART1 on ESP32)
uart = UART(UART_NUM, baudrate=UART_BAUD, tx=Pin(16), rx=Pin(17))  # Adjust pins if needed
motor = Dynamixel(uart, model=DynamixelModel.XL430_W250, id=1, protocol_version=2)
motor2 = Dynamixel(uart, model=DynamixelModel.XM430_W350, id=2, protocol_version=2)

## 	Current-based Position Control Mode