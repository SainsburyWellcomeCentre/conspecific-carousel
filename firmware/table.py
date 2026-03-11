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
        self.iserror = False
        self._ismoving = False
        self._op_flag = Event()
        self._pos = 0
        self._motor.profile_velocity = max_vel
        self._task = asyncio.create_task(self._run())
        self.target_pos = self._motor.current_position
        self.running = False
        self.interlock = True

    @property
    def ismoving(self) -> bool:
        return self._ismoving

    @ismoving.setter
    def ismoving(self, value: bool):
        self._ismoving = value
        self.isr.set()

    def turn(self, pos: int, dir=0):
        pos = pos * -1 if dir else pos
        self.target_pos = self._motor.current_position + pos
        self._op_flag.set()

    async def _run(self):
        while True:
            await self._op_flag.wait()
            try:
                await asyncio.wait_for(self._operation(), timeout)
            except asyncio.TimeoutError:
                self.iserror = True
                self.isr.set()
            finally:
                self._op_flag.clear()

    async def _operation(self):
        self.running = True
        await self._enable_torque()

        if self.target_pos > self._motor.current_position:
            while self._motor.current_position < self.target_pos - tolerance:
                await asyncio.sleep_ms(50)
        else:
            while self._motor.current_position > self.target_pos + tolerance:
                await asyncio.sleep_ms(50)
        await self._stop()
        self.running = False

    async def _stop(self):
        if self.running:
            self._motor.torque_enabled = False
            self._ismoving = False
            self.isr.set()

    async def _enable_torque(self):
        if self.running:
            self._motor.torque_enabled = True
            self._motor.goal_extend_position = self.target_pos
            self._ismoving = True
            self.isr.set()
