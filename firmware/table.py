from asyncio import Event
from dynamixel import Dynamixel, DynamixelModel
from micropython import const
import asyncio
from machine import UART

TOLERANCE = const(20)
TIMEOUT = const(20)
ONE_EIGHTH = const(2048)

VEL_DEFAULT = const(40)
TRQ_DEFAULT = const(500)

class Table(Dynamixel):

    def __init__(self, uart: UART):
        super().__init__(uart, model=DynamixelModel.XM430_W350, id=2)
        self.isr = Event()
        self.interlock = True

        self.torque_enabled = False  # Disable torque initially
        self.operating_mode = 5  # Current-based Position Control Mode
        self.current_limit = TRQ_DEFAULT
        self.speed = VEL_DEFAULT
        
        self.target_pos = self.present_position
        self._task = None
        self._ismoving = False

    @property
    def status(self) -> int:
        if self._ismoving:
            return 0x01
        return 0

    @property
    def speed(self):
        return self.profile_velocity

    @speed.setter
    def speed(self, vel):
        self.torque_enabled = False
        self.profile_velocity = vel
        self.torque_enabled = True

    @property
    def ismoving(self):
        return self._ismoving
    
    def turn(self, pos: int, dir=0):
        pos = pos * -1 if dir else pos
        self.target_pos = self.present_position + pos
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
                await asyncio.sleep_ms(50)
        else:
            while self.present_position > self.target_pos + TOLERANCE:
                await asyncio.sleep_ms(50)
    
        self._disable()

        await asyncio.sleep_ms(2000) # little pause to ensure the motor has fully stopped before disabling torque
        self.torque_enabled = False

    def _disable(self):
        self._ismoving = False
        # self.torque_enabled = False
        self.isr.set()

    def _enable(self):
        self.torque_enabled = True
        self.goal_extend_position = self.target_pos
        self._ismoving = True
        self.isr.set()
