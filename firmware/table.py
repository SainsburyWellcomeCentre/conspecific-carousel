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
        self._motor.current_limit = 500
        self._motor.profile_velocity = 40
        self.isr = Event()
        self.iserror = False
        self._ismoving = False
        self._op_flag = Event()
        self._pos = 0
        self._task = asyncio.create_task(self._run())

    @property
    def ismoving(self) -> bool:
        return self._ismoving

    @ismoving.setter
    def ismoving(self, value: bool):
        self._ismoving = value
        self.isr.set()

    def turn(self, pos: int, dir=0):
        self._pos = pos * -1 if dir else pos
        self._op_flag.set()

    async def _run(self):
        while True:
            await self._op_flag.wait()
            try:
                await asyncio.wait_for(self._turn(self._pos), timeout)
            except asyncio.TimeoutError:
                self.iserror = True
                self.isr.set()
            finally:
                self._op_flag.clear()

    async def _turn(self, pos):
        goal = self._motor.current_position + pos
        self._motor.torque_enabled = True
        self._motor.goal_extend_position = goal
        self.ismoving = True

        if goal > self._motor.current_position:
            while self._motor.current_position < goal - tolerance:
                await asyncio.sleep_ms(50)
        else:
            while self._motor.current_position > goal + tolerance:
                await asyncio.sleep_ms(50)
        await self._stop()

    async def _stop(self):
        self._motor.torque_enabled = False
        self.ismoving = False
