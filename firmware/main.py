from settings import door, table, portA, portB, portC
import asyncio
from utility import WaitAny


# async def sender():
#     swriter = asyncio.StreamWriter(uart, {})
#     while True:
#         swriter.write("Hello uart\n")
#         await swriter.drain()  # Transmission starts now.
#         await asyncio.sleep(2)


# async def receiver():
#     sreader = asyncio.StreamReader(uart)
#     while True:
#         res = await sreader.readline()
#         print("Received", res)


async def event_monitor():
    while True:
        evt = await WaitAny((door.isr, table.isr, portA.isr, portB.isr, portC.isr)).wait()

        if evt is door.isr:
            print("Door event", door.status)
            door.isr.clear()
        elif evt is table.isr:
            print("Table event", table.ismoving)
            table.isr.clear()
        elif evt is portA.isr:
            print("Port A event", portA.beambreak)
            portA.isr.clear()
        elif evt is portB.isr:
            print("Port B event", portB.beambreak)
            portB.isr.clear()
        elif evt is portC.isr:
            print("Port C event", portC.beambreak)
            portC.isr.clear()


async def main():
    # rx = asyncio.create_task(receiver())
    # tx = asyncio.create_task(sender())
    monitor = asyncio.create_task(event_monitor())

    await monitor


asyncio.run(main())
