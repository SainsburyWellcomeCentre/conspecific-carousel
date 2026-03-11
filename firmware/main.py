from settings import portA, portB, portC, led, door, table, camA, camB, snsr_door, snsr_table, sync_out
import asyncio
from utility import WaitAny
from collections import deque
import sys

TX_LEN = 128
RX_LEN = 128


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
            if door.iserror:
                txMessages.append("Door error orcurred")
            elif door.status == 3:
                txMessages.append("Door paused")
            elif door.status == 2:
                txMessages.append("Door moving")
            elif door.status:
                txMessages.append("Door opened")
            else:
                txMessages.append("Door closed")
            door.isr.clear()
        elif evt is table.isr:
            if table.iserror:
                txMessages.append("Turn table error door.status")
            elif table.ismoving:
                txMessages.append("Table moving")
            else:
                txMessages.append("Table stopped")
            table.isr.clear()
        elif evt is portA.beambreak.isr:
            if portA.beambreak.value() == 0:
                txMessages.append("Port A beambreak cleared")
            else:
                txMessages.append("Port A beambreak triggered")
            portA.beambreak.isr.clear()
        elif evt is portB.beambreak.isr:
            if portB.beambreak.value() == 0:
                txMessages.append("Port B beambreak cleared")
            else:
                txMessages.append("Port B beambreak triggered")
            portB.beambreak.isr.clear()
        elif evt is portC.beambreak.isr:
            if portC.beambreak.value() == 0:
                txMessages.append("Port C beambreak cleared")
            else:
                txMessages.append("Port C beambreak triggered")
            portC.beambreak.isr.clear()
        elif evt is snsr_door.isr:
            if snsr_door.value() == 0:
                txMessages.append("Door sensor cleared")
                if door.interlock and door.target_pos == door._closed_pos:
                    await door._enable_torque()  # Enable torque to resume the operation if the sensor is cleared
            else:
                txMessages.append("Door sensor triggered")
                if door.interlock and door.target_pos == door._closed_pos:
                    await door._stop()  # Stop the door immediately if the sensor is triggered
            snsr_door.isr.clear()
        elif evt is snsr_table.isr:
            if snsr_table.value() == 0:
                txMessages.append("Table sensor cleared")
                if table.interlock:
                    await table._enable_torque()  # Enable torque to resume the operation if the sensor is cleared
            else:
                txMessages.append("Table sensor triggered")
                if table.interlock:
                    await table._stop()  # Stop the table immediately if the sensor is triggered
            snsr_table.isr.clear()
        elif evt is camA.isr:
            txMessages.append(f"Cam A state: {camA.value()}")
            camA.isr.clear()
        elif evt is camB.isr:
            txMessages.append(f"Cam B state: {camB.value()}")
            camB.isr.clear()


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
