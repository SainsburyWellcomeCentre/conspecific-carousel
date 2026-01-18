from machine import Pin
from asyncio import Event
from dynamixel.dynamixel import Dynamixel
from micropython import const
import time
import asyncio

op_close = const(0)
op_open = const(1)
moving = const(2)
tolerance = const(50)
timeout = const(5000)


class Door:

    def __init__(self, motor: Dynamixel, limiter_pin: int, length: int = 7200, dir: int = 0):

        self._motor = motor
        self._motor.torque_enabled = False  # Disable torque initially
        self._limiter = Pin(limiter_pin, Pin.IN, Pin.PULL_UP)
        self.isr = Event()
        self.iserror = False

        if self._limiter.value() == 1:
            self._home()

        self._isclosed = True
        self._closed_pos = self._motor.current_position
        length = length * -1 if dir else length
        self._open_pos = self._closed_pos + length
        self._ismoving = False

    @property
    def status(self) -> int:
        temp = op_close if self._isclosed else op_open
        return temp and moving if self._ismoving else temp

    async def open(self):
        await self._create_task(self._open_pos)

    async def close(self):
        await self._create_task(self._closed_pos)

    async def _create_task(self, pos: int):
        task = asyncio.create_task(self._run(pos))
        await asyncio.sleep_ms(timeout)
        if task.done() is False:
            task.cancel()
            self.iserror = True
            self.isr.set()

    async def _run(self, op=op_close):
        op = op & 1
        pos = self._open_pos if op == op_open else self._closed_pos
        self._motor.torque_enabled = True
        self._motor.goal_extend_position = pos
        self._ismoving = True
        self.isr.set()

        if pos > self._motor.current_position:
            while self._motor.current_position < pos - tolerance:
                await asyncio.sleep_ms(0)
        else:
            while self._motor.current_position > pos + tolerance:
                await asyncio.sleep_ms(0)
        await self._stop()

    async def _stop(self):
        self._motor.torque_enabled = False
        self._ismoving = False
        self.isr.set()

    def _home(self):
        self._motor.operating_mode = 16  # PWM Mode
        self._motor.torque_enabled = True
        self._motor.goal_pwm = -400  # 550 if mice setup
        while self._limiter.value() == 1:
            time.sleep(0.01)
        self._motor.goal_pwm = 0
        self._motor.torque_enabled = False  # Disable torque
        self._motor.operating_mode = 4  # Position Control Mode
