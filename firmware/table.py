from asyncio import Event
from dynamixel.dynamixel import Dynamixel
from micropython import const
import asyncio


tolerance = const(30)
timeout = const(20)
one_eighth = const(2048)
max_vel = const(40)


class Table:

    def __init__(self, motor: Dynamixel):

        self._motor = motor
        self._motor.torque_enabled = False  # Disable torque initially
        self._motor.operating_mode = 5  # Current-based Position Control Mode
        self._motor.current_limit = 500
        self._motor.profile_velocity = max_vel
        self.isr = Event()
        self.target_pos = self._motor.current_position
        self._task = None
        self.ismoving = False

    def turn(self, pos: int, dir=0):
        pos = pos * -1 if dir else pos
        self.target_pos = self._motor.current_position + pos
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None
            self._motor.torque_enabled = False
            self.ismoving = False
            self.isr.set()

    async def _run(self):
        await self._enable_torque()
        if self.target_pos > self._motor.current_position:
            while self._motor.current_position < self.target_pos - tolerance:
                await asyncio.sleep_ms(50)
        else:
            while self._motor.current_position > self.target_pos + tolerance:
                await asyncio.sleep_ms(50)
        await self._disable_torque()

    async def _disable_torque(self):
        self._motor.torque_enabled = False
        self.ismoving = False
        self.isr.set()

    async def _enable_torque(self):
        self._motor.torque_enabled = True
        self._motor.goal_extend_position = self.target_pos
        self.ismoving = True
        self.isr.set()
