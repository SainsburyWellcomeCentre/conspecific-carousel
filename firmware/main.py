from settings import portA, portB, portC, led, door, table, camA, camB, snsr_door, snsr_table, sync_out

import asyncio
from utility import WaitAny
from collections import deque
from micropython import const
from table import ONE_EIGHTH
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
        return table.status
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
        table.turn(position * ONE_EIGHTH, dir=direction)
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
            if door.status == 3:
                txMessages.append("Door paused")
            elif door.status == 2:
                txMessages.append("Door moving")
            elif door.status:
                txMessages.append("Door opened")
            else:
                txMessages.append("Door closed")
        elif evt is table.isr:
            if table.ismoving:
                txMessages.append("Table moving")
            else:
                txMessages.append("Table stopped")
        elif evt is portA.beambreak.isr:
            if portA.beambreak.value() == 0:
                txMessages.append("Port A beambreak cleared")
            else:
                txMessages.append("Port A beambreak triggered")
        elif evt is portB.beambreak.isr:
            if portB.beambreak.value() == 0:
                txMessages.append("Port B beambreak cleared")
            else:
                txMessages.append("Port B beambreak triggered")
        elif evt is portC.beambreak.isr:
            if portC.beambreak.value() == 0:
                txMessages.append("Port C beambreak cleared")
            else:
                txMessages.append("Port C beambreak triggered")
        elif evt is snsr_door.isr:
            if snsr_door.value() == 0:
                txMessages.append("Door sensor cleared")
                if door.interlock and door.target_pos == door._closed_pos:
                    door.close()  # Enable torque to resume the operation if the sensor is cleared
            else:
                txMessages.append("Door sensor triggered")
                if door.interlock and door.target_pos == door._closed_pos:
                    door.stop()  # Stop the door immediately if the sensor is triggered
        elif evt is snsr_table.isr:
            if snsr_table.value() == 0:
                txMessages.append("Table sensor cleared")
                if table.interlock and door.target_pos == door._closed_pos:
                    door.close()  # Enable torque to resume the operation if the sensor is cleared
            else:
                txMessages.append("Table sensor triggered")
                if table.interlock and door.target_pos == door._closed_pos:
                    door.stop()  # Stop the door immediately if the sensor is triggered
        elif evt is camA.isr:
            txMessages.append(f"Cam A state: {camA.value()}")

        elif evt is camB.isr:
            txMessages.append(f"Cam B state: {camB.value()}")
        if evt:
            evt.clear()

async def transceiver(txMessages: deque, rxMessages: deque):
    import uselect

    stream = uselect.poll()
    stream.register(sys.stdin, uselect.POLLIN)
    while True:
        # Receive messages
        while stream.poll(0):
            rxMessages.append(sys.stdin.buffer.read(1))

        # Send messages
        while txMessages:
            message = txMessages.popleft()
            sys.stdout.write(message + "\n")

        await asyncio.sleep(0)


async def processor(rxMessages: deque):
    while True:
        while rxMessages:
            message = rxMessages.popleft()
            msg = message[0]
            if msg == 0x01:
                sync_out.value(0)
                led.value(1)
            elif msg == 0x02:
                sync_out.value(1)
                led.value(0)
            elif msg == 0x08:
                table.turn(2048, dir=0)
            elif msg == 0x09:
                table.turn(2048, dir=1)
            elif msg == 0x10:
                door.open()
            elif msg == 0x11:
                door.close()
            elif msg == 0x21:
                portA.led = True
            elif msg == 0x22:
                portA.led = False
            elif msg == 0x23:
                portA.valve = True
            elif msg == 0x24:
                portA.valve = False
            elif msg == 0x25:
                portB.led = True
            elif msg == 0x26:
                portB.led = False
            elif msg == 0x27:
                portB.valve = True
            elif msg == 0x28:
                portB.valve = False
            elif msg == 0x29:
                portC.led = True
            elif msg == 0x2A:
                portC.led = False
            elif msg == 0x2B:
                portC.valve = True
            elif msg == 0x2C:
                portC.valve = False
            elif msg == 0x2D:
                table.turn(4096, dir=0)
            elif msg == 0x2E:
                table.turn(4096, dir=1)
            elif msg == 0x2F:
                table.turn(8192, dir=0)
            elif msg == 0x30:
                table.turn(8192, dir=1)
            elif msg == 0x31:
                table.turn(12288, dir=0)
            elif msg == 0x32:
                table.turn(12288, dir=1)
            elif msg == 0x33:
                door.interlock = True
            elif msg == 0x34:
                door.interlock = False
            elif msg == 0x35:
                table.interlock = True
            elif msg == 0x36:
                table.interlock = False
        await asyncio.sleep(0)


async def main():

    txMessages = deque(bytearray(), TX_LEN)
    rxMessages = deque(bytearray(), RX_LEN)

    monitor_task = asyncio.create_task(event_monitor(txMessages))
    processor_task = asyncio.create_task(processor(rxMessages))
    transceiver_task = asyncio.create_task(transceiver(txMessages, rxMessages))

    await asyncio.gather(monitor_task, processor_task, transceiver_task)


asyncio.run(main())
