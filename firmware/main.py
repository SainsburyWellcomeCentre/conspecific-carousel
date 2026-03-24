from settings import portA, portB, portC, led, door, table, camA, camB, snsr_door, snsr_table, sync_out
import asyncio
from utility import WaitAny
from collections import deque
from micropython import const
from table import one_eighth
import sys

TX_LEN = 128
RX_LEN = 128

HEADER = const(0xCC)
MSG_WRITE = const(0x01)
MSG_READ = const(0x02)
MSG_ACK = const(0x02)
MSG_EVENT = const(0x03)

# Register addresses
REG_LED_SYNC = const(0x01)
REG_DOOR_SENSOR = const(0x02)
REG_TABLE_SENSOR = const(0x03)
REG_CAM_A = const(0x04)
REG_CAM_B = const(0x05)
REG_DOOR_STATUS = const(0x10)
REG_DOOR_CMD = const(0x11)
REG_TABLE_STATUS = const(0x18)
REG_TABLE_CMD = const(0x19)
REG_PA_LED = const(0x21)
REG_PA_VALVE = const(0x22)
REG_PA_IR = const(0x23)
REG_PB_LED = const(0x24)
REG_PB_VALVE = const(0x25)
REG_PB_IR = const(0x26)
REG_PC_LED = const(0x27)
REG_PC_VALVE = const(0x28)
REG_PC_IR = const(0x29)


def _tx_packet(register, msg_type, value):
    return bytes((HEADER, register, msg_type, value))


def _read_register(register):
    if register == REG_LED_SYNC:
        return led.value()
    elif register == REG_DOOR_STATUS:
        return door.status
    elif register == REG_TABLE_STATUS:
        return 0x01 if table.ismoving else 0x00
    elif register == REG_DOOR_SENSOR:
        return snsr_door.value()
    elif register == REG_TABLE_SENSOR:
        return snsr_table.value()
    elif register == REG_CAM_A:
        return camA.value()
    elif register == REG_CAM_B:
        return camB.value()
    elif register == REG_PA_LED:
        return int(portA.led)
    elif register == REG_PA_VALVE:
        return int(portA.valve)
    elif register == REG_PA_IR:
        return portA.beambreak.value()
    elif register == REG_PB_LED:
        return int(portB.led)
    elif register == REG_PB_VALVE:
        return int(portB.valve)
    elif register == REG_PB_IR:
        return portB.beambreak.value()
    elif register == REG_PC_LED:
        return int(portC.led)
    elif register == REG_PC_VALVE:
        return int(portC.valve)
    elif register == REG_PC_IR:
        return portC.beambreak.value()
    return 0x00


def _write_register(register, value):
    if register == REG_LED_SYNC:
        sync_out.value(0 if value else 1)
        led.value(value)
    elif register == REG_DOOR_CMD:
        if value == 0x00:
            door.open()
        elif value == 0x01:
            door.close()
        elif value == 0x02:
            door.stop()
    elif register == REG_TABLE_CMD:
        direction = (value >> 7) & 1
        position = value & 0x7F
        table.turn(position * one_eighth, dir=direction)
    elif register == REG_PA_LED:
        portA.led = bool(value)
    elif register == REG_PA_VALVE:
        portA.valve = bool(value)
    elif register == REG_PB_LED:
        portB.led = bool(value)
    elif register == REG_PB_VALVE:
        portB.valve = bool(value)
    elif register == REG_PC_LED:
        portC.led = bool(value)
    elif register == REG_PC_VALVE:
        portC.valve = bool(value)


async def event_monitor(txMessages: deque):
    while True:

        evt = await WaitAny(
            (
                door.isr,
                table.isr,
                portA.beambreak.isr,
                portB.beambreak.isr,
                portC.beambreak.isr,
                camA.isr,
                camB.isr,
                snsr_door.isr,
                snsr_table.isr,
            )
        ).wait()

        if evt is door.isr:
            txMessages.append(_tx_packet(REG_DOOR_STATUS, MSG_EVENT, door.status))
        elif evt is table.isr:
            txMessages.append(_tx_packet(REG_TABLE_STATUS, MSG_EVENT, 0x01 if table.ismoving else 0x00))
        elif evt is portA.beambreak.isr:
            txMessages.append(_tx_packet(REG_PA_IR, MSG_EVENT, portA.beambreak.value()))
        elif evt is portB.beambreak.isr:
            txMessages.append(_tx_packet(REG_PB_IR, MSG_EVENT, portB.beambreak.value()))
        elif evt is portC.beambreak.isr:
            txMessages.append(_tx_packet(REG_PC_IR, MSG_EVENT, portC.beambreak.value()))
        elif evt is snsr_door.isr:
            txMessages.append(_tx_packet(REG_DOOR_SENSOR, MSG_EVENT, snsr_door.value()))
        elif evt is snsr_table.isr:
            txMessages.append(_tx_packet(REG_TABLE_SENSOR, MSG_EVENT, snsr_table.value()))
        elif evt is camA.isr:
            txMessages.append(_tx_packet(REG_CAM_A, MSG_EVENT, camA.value()))
        elif evt is camB.isr:
            txMessages.append(_tx_packet(REG_CAM_B, MSG_EVENT, camB.value()))
        if evt:
            evt.clear()


async def transceiver(txMessages: deque, rxMessages: deque):
    import uselect

    stream = uselect.poll()
    stream.register(sys.stdin, uselect.POLLIN)
    while True:
        # Receive 4-byte packets
        while stream.poll(0):
            data = sys.stdin.buffer.read(4)
            if data and len(data) == 4 and data[0] == HEADER:
                rxMessages.append(data)

        # Send messages
        while txMessages:
            message = txMessages.popleft()
            sys.stdout.buffer.write(message)

        await asyncio.sleep(0)


async def processor(rxMessages: deque, txMessages: deque):
    while True:
        while rxMessages:
            packet = rxMessages.popleft()
            register = packet[1]
            msg_type = packet[2]
            value = packet[3]

            if msg_type == MSG_WRITE:
                _write_register(register, value)
                txMessages.append(_tx_packet(register, MSG_ACK, _read_register(register)))
            elif msg_type == MSG_READ:
                txMessages.append(_tx_packet(register, MSG_ACK, _read_register(register)))

        await asyncio.sleep(0)


async def main():

    txMessages = deque(bytearray(), TX_LEN)
    rxMessages = deque(bytearray(), RX_LEN)

    monitor_task = asyncio.create_task(event_monitor(txMessages))
    processor_task = asyncio.create_task(processor(rxMessages, txMessages))
    transceiver_task = asyncio.create_task(transceiver(txMessages, rxMessages))

    await asyncio.gather(monitor_task, processor_task, transceiver_task)


asyncio.run(main())
