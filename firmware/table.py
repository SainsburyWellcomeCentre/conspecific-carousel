from asyncio import Event
from dynamixel.dynamixel import Dynamixel
from micropython import const
import asyncio


tolerance = const(50)
timeout = const(5000)
one_eighth = const(2048)


class Table:

    def __init__(self, motor: Dynamixel):

        self._motor = motor
        self._motor.torque_enabled = False  # Disable torque initially
        self._motor.operating_mode = 5  # Current-based Position Control Mode
        self.isr = Event()
        self.iserror = False
        self._ismoving = False

    @property
    def ismoving(self) -> bool:
        return self._ismoving

    @ismoving.setter
    def ismoving(self, value: bool):
        self._ismoving = value
        self.isr.set()

    async def turn(self, pos: int, dir=0):
        pos = pos * -1 if dir else pos
        task = asyncio.create_task(self._run(pos))
        await asyncio.sleep_ms(timeout)
        if task.done() is False:
            task.cancel()
            self.iserror = True
            self.isr.set()

    async def _run(self, pos):
        goal = self._motor.current_position + pos
        self._motor.torque_enabled = True
        self._motor.goal_extend_position = goal
        self.ismoving = True

        if pos > self._motor.current_position:
            while self._motor.current_position < pos - tolerance:
                await asyncio.sleep_ms(0)
        else:
            while self._motor.current_position > pos + tolerance:
                await asyncio.sleep_ms(0)
        await self._stop()

    async def _stop(self):
        self._motor.torque_enabled = False
        self.ismoving = False
