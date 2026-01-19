from settings import portA, portB, portC, led, door, table
import asyncio
from utility import WaitAny
from collections import deque
import sys

TX_LEN = 128
RX_LEN = 128

async def event_monitor(txMessages: deque):

    while True:

        evt = await WaitAny((door.isr, table.isr, portA.isr, portB.isr, portC.isr)).wait()

        if evt is door.isr:
            if door.iserror:
                txMessages.append(f"Door error!!")
            else:
                txMessages.append(f"Door event: {door.status}")
            door.isr.clear()
        elif evt is table.isr:
            txMessages.append(f"Table event: {table.ismoving}")
            table.isr.clear()
        elif evt is portA.isr:
            txMessages.append(f"Port A event: {portA.beambreak}")
            portA.isr.clear()
        elif evt is portB.isr:
            txMessages.append(f"Port B event: {portB.beambreak}")
            portB.isr.clear()
        elif evt is portC.isr:
            txMessages.append(f"Port C event: {portC.beambreak}")
            portC.isr.clear()

async def sender(txMessages: deque):
    while True:
        while txMessages:
            message = txMessages.popleft()
            sys.stdout.write(message + '\n')
        await asyncio.sleep(0)

async def receiver(rxMessages: deque):
    import uselect
    stream = uselect.poll()
    stream.register(sys.stdin, uselect.POLLIN)
    while True:
        if stream.poll(0):
            rxMessages.append(sys.stdin.buffer.read(1))
        await asyncio.sleep(0)

async def blink(rxMessages: deque):
    while True:
        while rxMessages:
            message = rxMessages.popleft()
            msg = message[0]
            if msg == 0x01:
                led.toggle()
            elif msg == b'\n':
                pass
            elif msg == 0x11:
                door.open()
            elif msg == 0x10:
                door.close()
            elif msg == 0x21:
                portA.led=True
            elif msg == 0x22:
                portA.led=False
            elif msg == 0x23:
                table.turn(4096, dir=0)
            elif msg == 0x24:
                table.turn(4096, dir=1)
            # sys.stdout.write(message)
        await asyncio.sleep(0)

async def main():

    txMessages = deque(bytearray(), TX_LEN)
    rxMessages = deque(bytearray(), RX_LEN)

    monitor_task = asyncio.create_task(event_monitor(txMessages))
    sender_task = asyncio.create_task(sender(txMessages))
    receiver_task = asyncio.create_task(receiver(rxMessages))
    blinker = asyncio.create_task(blink(rxMessages))
    
    await monitor_task

asyncio.run(main())
