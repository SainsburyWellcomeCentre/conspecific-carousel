import asyncio
from machine import Pin
from asyncio import Event


class EventPin(Pin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.isr = Event()
        self.irq(lambda pin: self.isr.set(), Pin.IRQ_FALLING | Pin.IRQ_RISING, hard=True)


# An Event-like class that can wait on an iterable of Event-like instances.
# .wait pauses until any passed event is set.
class WaitAny:
    def __init__(self, events):
        self.events = events
        self.trig_event = None
        self.evt = asyncio.Event()

    async def wait(self):
        tasks = [asyncio.create_task(self.wt(event)) for event in self.events]
        try:
            await self.evt.wait()
        finally:
            self.evt.clear()
            for task in tasks:
                task.cancel()
        return self.trig_event

    async def wt(self, event):
        await event.wait()
        self.evt.set()
        self.trig_event = event

    def event(self):
        return self.trig_event

    def clear(self):
        for evt in (x for x in self.events if hasattr(x, "clear")):
            evt.clear()
