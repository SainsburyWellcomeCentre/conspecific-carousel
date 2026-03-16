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
paused = const(3)
tolerance = const(50)
timeout = const(15)

max_vel = const(50)

length_rat = const(7200)  # Default length in encoder units
length_mice = const(-3700)  # Default length in encoder units
length_gap = const(500)  # Additional length for mice setting in encoder units
rat_setting = const(0)
mice_setting = const(1)


class Door:

    def __init__(self, motor: Dynamixel, limiter_pin: int, setting: int = rat_setting):

        self._motor = motor
        self._limiter = Pin(limiter_pin, Pin.IN, Pin.PULL_UP)
        self.isr = Event()
        self.iserror = False
        self._motor.torque_enabled = False  # Disable torque
        self._motor.profile_velocity = max_vel
        self._home(setting)

        self._isclosed = True
        self._closed_pos = self._motor.current_position
        length = length_mice if setting == mice_setting else length_rat

        if setting == mice_setting:
            self._closed_pos -= length_gap
            length += length_gap

        self._open_pos = self._closed_pos + length
        self._ismoving = False
        self._open_flag = Event()
        self._close_flag = Event()
        self._motor.torque_enabled = False  # Disable torque
        self._motor.profile_velocity = max_vel
        self._task = asyncio.create_task(self._run())
        self.target_pos = self._closed_pos
        self.running = False
        self.interlock = True

    @property
    def status(self) -> int:
        if self._ismoving:
            return moving
        elif self.running:
            return paused
        return op_close if self._isclosed else op_open

    def open(self):
        if self.status == op_close:
            self.target_pos = self._open_pos
            self._motor.profile_velocity = int(max_vel * 2)
            self._open_flag.set()

    def close(self):
        if self.status == op_open:
            self.target_pos = self._closed_pos
            self._motor.profile_velocity = max_vel
            self._close_flag.set()

    async def _run(self):
        while True:
            evt = await WaitAny((self._close_flag, self._open_flag)).wait()

            try:
                await asyncio.wait_for(self._operation(), timeout)
            except asyncio.TimeoutError:
                self.iserror = True
                self.isr.set()
            finally:
                if evt is not None:
                    evt.clear()

    async def _operation(self):
        self.running = True
        await self._enable_torque()

        if self.target_pos > self._motor.current_position:
            while self._motor.current_position < self.target_pos - tolerance:
                await asyncio.sleep_ms(50)
        else:
            while self._motor.current_position > self.target_pos + tolerance:
                await asyncio.sleep_ms(50)

        self._isclosed = True if self.target_pos == self._closed_pos else False
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

    def _home(self, setting=rat_setting):
        self._motor.torque_enabled = False  # Disable torque
        if self._limiter.value() == 1:
            self._motor.operating_mode = 16  # PWM Mode
            self._motor.torque_enabled = True
            pwm = -700 if setting == rat_setting else 700
            while self._limiter.value() == 1:
                if abs(pwm) > 300:
                    pwm = round(pwm * 0.99)
                self._motor.goal_pwm = pwm
                time.sleep(0.02)
            self._motor.goal_pwm = 0
        self._motor.torque_enabled = False  # Disable torque
        self._motor.operating_mode = 4  # Position Control Mode
