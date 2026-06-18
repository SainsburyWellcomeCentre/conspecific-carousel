from asyncio import Event
from dynamixel import Dynamixel, DynamixelModel
from micropython import const
import time
import asyncio
from machine import UART

CLOSE = const(0)
OPEN = const(1)
MOVING = const(2)
PAUSED = const(3)

TOLERANCE = const(20)
TIMEOUT = const(15)

VEL_OPEN_DEFAULT = const(255)
VEL_CLOSE_DEFAULT = const(40)

TRQ_OPEN = const(50)
TRQ_CLOSE = const(15)

LENGTH_RAT = const(6000)  # Default length in encoder units
LENGTH_MICE = const(-2000)  # Default length in encoder units

LENGTH_GAP = const(500)  # Additional length for mice setting in encoder units

RAT_SETTING = const(0)
MICE_SETTING = const(1)


class Door(Dynamixel):

    def __init__(self, uart: UART, setting: int = RAT_SETTING):
        super().__init__(uart, model=DynamixelModel.XM430_W350, id=1)
        self.isr = Event()
        self.torque_enabled = False  # Disable torque
        self.operating_mode = 5  # current control mode
        
        length = LENGTH_MICE if setting == MICE_SETTING else LENGTH_RAT
        self.home_pos = self.present_position - length
        self.speed = 40
        self.torque = 15
        self._calibrate_home()
        self.open_pos = self.home_pos + length

        self._isclosed = True
        self._isopened = False
        self._ismoving = False
        self._task = None
        self._closed_pos = self.home_pos
        self.target_pos = self._closed_pos
        self.interlock = True
        self.speed_open = VEL_OPEN_DEFAULT
        self.speed_close = VEL_CLOSE_DEFAULT

    @property
    def status(self) -> int:
        if self._ismoving:
            return MOVING
        elif self._isopened:
            return OPEN
        elif self._isclosed:
            return CLOSE
        return PAUSED

    @property
    def torque(self):
        return self.current_limit

    @torque.setter
    def torque(self, val):
        self.torque_enabled = False
        self.current_limit = val
        self.torque_enabled = True

    @property
    def speed(self):
        return self.profile_velocity

    @speed.setter
    def speed(self, vel):
        self.torque_enabled = False
        self.profile_velocity = vel
        self.torque_enabled = True

    # @property
    # def offset(self):
    #     return self._offset

    # @offset.setter
    # def offset(self, val):
    #     val = max(min(val, POS_OFFSET_MAX), POS_OFFSET_MIN)
    #     self._offset = val

    def open(self):
        if self.status != OPEN:
            self.speed = self.speed_open
            self.torque = TRQ_OPEN
            self.move(self.open_pos)

    def close(self):
        if self.status != CLOSE:
            self.speed = self.speed_close
            self.torque = TRQ_CLOSE
            self.move(self.home_pos)

    def move(self, pos):
        self.target_pos = pos
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None
            self.torque_enabled = False
            self._ismoving = False
            self.isr.set()

    async def _run(self):
        self._enable()

        if self.target_pos > self.present_position:
            while self.present_position < self.target_pos - TOLERANCE:
                await asyncio.sleep_ms(100)
        else:
            while self.present_position > self.target_pos + TOLERANCE:
                await asyncio.sleep_ms(100)

        if self.target_pos == self.home_pos:
            self._isclosed = True
        elif self.target_pos == self.open_pos:
            self._isopened = True

        await asyncio.sleep_ms(100)
        self._disable()

    def _disable(self):
        self._ismoving = False
        self.torque_enabled = False
        self.isr.set()

    def _enable(self):
        self.torque_enabled = True
        self.goal_extend_position = self.target_pos
        self._isopened = False
        self._isclosed = False
        self._ismoving = True
        self.isr.set()

    def _calibrate_home(self):
        self.torque_enabled = True
        self.goal_extend_position = self.home_pos
        last_pos = self.present_position
        time.sleep(1)
        conuter = 0
        while True:
            pos = self.present_position
            if abs(last_pos - pos) < TOLERANCE:  # Check if the motor is close to the home position
                conuter += 1
            if conuter > 10:
                break
            last_pos = pos
            time.sleep(0.05)
        self.torque_enabled = False
        time.sleep(0.5)
        self.home_pos = self.present_position
        
