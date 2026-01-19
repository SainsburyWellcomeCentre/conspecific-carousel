from machine import Pin
from asyncio import Event
from dynamixel.dynamixel import Dynamixel
from micropython import const
import time
import asyncio
from utility import WaitAny
op_close = const(0)
op_open = const(1)
moving = const(2)
tolerance = const(50)
timeout = const(5)


class Door:

    def __init__(self, motor: Dynamixel, limiter_pin: int, length: int = 7200, dir: int = 0):

        self._motor = motor
        self._limiter = Pin(limiter_pin, Pin.IN, Pin.PULL_UP)
        self.isr = Event()
        self.iserror = False

        self._home()

        self._isclosed = True
        self._closed_pos = self._motor.current_position
        length = length * -1 if dir else length
        self._open_pos = self._closed_pos + length
        self._ismoving = False
        self._open_flag = Event()
        self._close_flag = Event()
        self._task = asyncio.create_task(self._run())

    @property
    def status(self) -> int:
        if self._ismoving:
            return moving
        return op_close if self._isclosed else op_open

    def open(self):
        self._open_flag.set()

    def close(self):
        self._close_flag.set()

    async def _run(self):
        while True:
            evt = await WaitAny(self._close_flag, self._open_flag).wait()
            op = op_open if evt is self._open_flag else op_close
            try:
                await asyncio.wait_for(self._spin(op), timeout)
            except asyncio.TimeoutError:
                self.iserror = True
                self.isr.set()
            finally:
                evt.clear()

    async def _spin(self, op=op_close):
        op = op & 1
        pos = self._open_pos if op == op_open else self._closed_pos
    
        self._motor.torque_enabled = True
        self._motor.goal_extend_position = pos
        self._ismoving = True
        self.isr.set()

        if pos > self._motor.current_position:
            while self._motor.current_position < pos - tolerance:
                await asyncio.sleep_ms(50)
        else:
            while self._motor.current_position > pos + tolerance:
                await asyncio.sleep_ms(50)
        await self._stop()
      
        self._isclosed = True if op == op_close else False
        self.isr.set()

    async def _stop(self):
        self._motor.torque_enabled = False
        self._ismoving = False

    def _home(self):
        self._motor.torque_enabled = False  # Disable torque
        if self._limiter.value() == 1:
            self._motor.operating_mode = 16  # PWM Mode
            self._motor.torque_enabled = True
            self._motor.goal_pwm = -400  # 550 if mice setup
            while self._limiter.value() == 1:
                time.sleep(0.01)
            self._motor.goal_pwm = 0
        self._motor.torque_enabled = False  # Disable torque
        self._motor.operating_mode = 4  # Position Control Mode
