from machine import Pin, UART
from dynamixel import Dynamixel, DynamixelModel
from poke import Poke
from door import Door
from table import Table

UART_BAUD = 57600  # Baud rate for hardware UART
UART_NUM = 0  # Use UART0
INDICATOR_PIN = 25  # GPIO for indicator LED
LIMITER_PIN = 28  # GPIO for limiter


portA = Poke(valve_pin=0, led_pin=3, beambreak_pin=12)
portB = Poke(valve_pin=1, led_pin=4, beambreak_pin=13)
portC = Poke(valve_pin=2, led_pin=5, beambreak_pin=14)


uart = UART(UART_NUM, baudrate=UART_BAUD, tx=Pin(16), rx=Pin(17))  # Adjust pins if needed

door = Door(motor=Dynamixel(uart, model=DynamixelModel.XL430_W250, id=1, protocol_version=2), limiter_pin=LIMITER_PIN)

table = Table(motor=Dynamixel(uart, model=DynamixelModel.XM430_W350, id=2, protocol_version=2))
