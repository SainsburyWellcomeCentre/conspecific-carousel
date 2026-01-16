
import time
from machine import Pin, UART
from dynamixel.dynamixel import Dynamixel
from dynamixel.table import ControlTableItem
from dynamixel.model import DynamixelModel
from struct import pack_into, unpack_from
from dynamixel.packet import DynamixelTXPacket, DynamixelRXPacket
from dynamixel.crc import CRC_TABLE_V2

motor = Dynamixel(UART(0, baudrate=57600, tx=Pin(16), rx=Pin(17)), model=DynamixelModel.XL430_W250, id=1, protocol_version=2)


def calc_checksum(buffer):
    crc = 0x0000
    data = buffer[0:-2]
    for byte in data:
        i = ((crc >> 8) ^ byte) & 0xFF
        crc = CRC_TABLE_V2[i] ^ (crc << 8)
    return crc
