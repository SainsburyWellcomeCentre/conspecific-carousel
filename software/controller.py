"""
Controller – public Python API for the Conspecific Carousel device.

Usable without any GUI:

    from controller import Controller

    ctrl = Controller()
    ctrl.connect("COM3", 1000000)
    ctrl.write_register(0x11, 0x00)   # open door
    ctrl.disconnect()
    ctrl.shutdown()

Conditions are stored as individual JSON files in a ``.conditions/`` folder
next to this file.  Task scripts are ``.py`` files in a ``.task/`` folder.
"""

import io
import json
import re
import shutil
import sys
import threading
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from protocol import (
    REGISTER_NAMES,
    READABLE_REGISTERS,
    REG_LED_SYNC,
    REG_DOOR_SENSOR,
    REG_TABLE_SENSOR,
    REG_DOOR_STATUS,
    REG_DOOR_CMD,
    REG_TABLE_STATUS,
    REG_TABLE_CMD,
    REG_PA_LED, REG_PA_VALVE, REG_PA_IR,
    REG_PB_LED, REG_PB_VALVE, REG_PB_IR,
    REG_PC_LED, REG_PC_VALVE, REG_PC_IR,
    MSG_WRITE,
    MSG_ACK,
    MSG_EVENT,
    build_table_command,
    format_value,
    reg_name,
)
from serial_comm import DeviceConnection, list_serial_ports
from csv_logger import CsvLogger
 


_BASE = Path(__file__).resolve().parent
_TASKS_DIR = _BASE / ".task"


def _safe_filename(name: str) -> str:
    """Turn a condition name into a safe filename stem."""
    stem = re.sub(r'[^\w\-]', '_', name).strip('_') or "condition"
    return stem[:64]


class Controller:
    """
    Device controller.  All methods are thread-safe.

    Event callbacks registered via ``on_event``, ``on_ack``, ``on_tx``,
    ``on_error``, and ``on_log`` are called from background threads.
    """

    def __init__(self):
        self._conn: DeviceConnection | None = None
        self._logger = CsvLogger()
        self._lock = threading.Lock()

        self._event_cbs: list = []
        self._ack_cbs: list = []
        self._tx_cbs: list = []
        self._error_cbs: list = []
        self._log_cbs: list = []
        self._task_status_cbs: list = []

        # Ensure tasks folder exists
        _TASKS_DIR.mkdir(exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Callback registration                                             #
    # ------------------------------------------------------------------ #

    def on_event(self, cb):
        """cb(register: int, value: int, formatted: str, reg_name: str)"""
        self._event_cbs.append(cb)

    def on_ack(self, cb):
        """cb(register: int, value: int, formatted: str)"""
        self._ack_cbs.append(cb)

    def on_tx(self, cb):
        """cb(register: int, msg_type: int, value: int)"""
        self._tx_cbs.append(cb)

    def on_error(self, cb):
        """cb(message: str)"""
        self._error_cbs.append(cb)

    def on_log(self, cb):
        """cb(message: str)  — general informational log line."""
        self._log_cbs.append(cb)

    def on_task_status(self, cb):
        """cb(filename: str, status: str)  — 'running' | 'done' | 'error'"""
        self._task_status_cbs.append(cb)

    def _fire(self, cbs, *args):
        for cb in cbs:
            try:
                cb(*args)
            except Exception:
                pass

    def _log(self, msg: str):
        self._fire(self._log_cbs, msg)

    # ------------------------------------------------------------------ #
    #  Ports & connection                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def list_ports() -> list[str]:
        return list_serial_ports()

    def connect(self, port: str, baud: int):
        """Connect to the device.  Raises RuntimeError on failure."""
        baud = int(baud)
        with self._lock:
            if self._conn and self._conn.is_connected:
                return
            try:
                conn = DeviceConnection(port, baud)
                conn.on_event(self._handle_event)
                conn.on_ack(self._handle_ack)
                conn.on_tx(self._handle_tx)
                conn.on_error(self._handle_error)
                conn.connect()
                self._conn = conn
            except Exception as e:
                self._conn = None
                raise RuntimeError(str(e)) from e

    def disconnect(self):
        with self._lock:
            if self._conn:
                self._conn.disconnect()
                self._conn = None

    @property
    def is_connected(self) -> bool:
        return bool(self._conn and self._conn.is_connected)

    # ------------------------------------------------------------------ #
    #  Register I/O                                                      #
    # ------------------------------------------------------------------ #

    def write_register(self, register: int, value: int):
        """Blocking write.  Raises RuntimeError if not connected or TimeoutError on no-ACK."""
        if not self.is_connected:
            raise RuntimeError("Not connected.")
        self._conn.write_register(int(register), int(value))

    def read_register(self, register: int) -> int:
        """Blocking read.  Returns the register value."""
        if not self.is_connected:
            raise RuntimeError("Not connected.")
        _, value = self._conn.read_register(int(register))
        return value

    def refresh_all(self) -> dict:
        """Read all readable registers.  Returns {register: value}."""
        result = {}
        for reg in READABLE_REGISTERS:
            try:
                value = self.read_register(reg)
                result[reg] = value
            except Exception:
                pass
        return result

    def send_table_command(self, direction: str, steps: int):
        """Send a table movement command.  direction='CW'|'CCW', steps=1–127."""
        steps = int(steps)
        if not 1 <= steps <= 127:
            raise ValueError("Steps must be between 1 and 127.")
        direction_byte = 0 if direction == "CW" else 1
        self.write_register(REG_TABLE_CMD, build_table_command(direction_byte, steps))

    # ------------------------------------------------------------------ #
    #  Named device wrappers                                             #
    # ------------------------------------------------------------------ #

    def led_sync(self, enable: bool):
        """Turn the LED/Sync output on or off."""
        self.write_register(REG_LED_SYNC, 1 if enable else 0)

    def door_open(self):
        """Send the door-open command."""
        self.write_register(REG_DOOR_CMD, 0x00)

    def door_close(self):
        """Send the door-close command."""
        self.write_register(REG_DOOR_CMD, 0x01)

    def door_stop(self):
        """Send the door-stop command."""
        self.write_register(REG_DOOR_CMD, 0x02)

    def table_turn(self, direction: str, steps: int = 1):
        """Turn the table.  direction='CW'|'CCW', steps=1/8-turn units (1–127)."""
        self.send_table_command(direction, steps)

    def port_led(self, port: str, enable: bool):
        """Set a port LED.  port='A'|'B'|'C'."""
        reg = {"A": REG_PA_LED, "B": REG_PB_LED, "C": REG_PC_LED}[port.upper()]
        self.write_register(reg, 1 if enable else 0)

    def port_valve(self, port: str, enable: bool):
        """Set a port valve.  port='A'|'B'|'C'."""
        reg = {"A": REG_PA_VALVE, "B": REG_PB_VALVE, "C": REG_PC_VALVE}[port.upper()]
        self.write_register(reg, 1 if enable else 0)

    def read_door_status(self) -> str:
        """Read door status.  Returns 'Closed'|'Opened'|'Moving'|'Paused'."""
        from protocol import format_value
        return format_value(REG_DOOR_STATUS, self.read_register(REG_DOOR_STATUS))

    def read_door_sensor(self) -> str:
        """Read door sensor.  Returns 'Detected'|'Clear'."""
        from protocol import format_value
        return format_value(REG_DOOR_SENSOR, self.read_register(REG_DOOR_SENSOR))

    def read_table_status(self) -> str:
        """Read table status.  Returns 'Stopped'|'Moving'."""
        from protocol import format_value
        return format_value(REG_TABLE_STATUS, self.read_register(REG_TABLE_STATUS))

    def read_table_sensor(self) -> str:
        """Read table sensor.  Returns 'Detected'|'Clear'."""
        from protocol import format_value
        return format_value(REG_TABLE_SENSOR, self.read_register(REG_TABLE_SENSOR))

    def read_port_ir(self, port: str) -> str:
        """Read IR sensor for a port.  port='A'|'B'|'C'. Returns 'Detected'|'Clear'."""
        from protocol import format_value
        reg = {"A": REG_PA_IR, "B": REG_PB_IR, "C": REG_PC_IR}[port.upper()]
        return format_value(reg, self.read_register(reg))

    # ------------------------------------------------------------------ #
    #  Device callbacks                                                  #
    # ------------------------------------------------------------------ #

    def _handle_event(self, register: int, value: int):
        self._logger.log_rx(register, MSG_EVENT, value)
        self._fire(self._event_cbs, register, value,
                   format_value(register, value), reg_name(register))

    def _handle_ack(self, register: int, value: int):
        self._logger.log_rx(register, MSG_ACK, value)
        self._fire(self._ack_cbs, register, value, format_value(register, value))

    def _handle_tx(self, register: int, msg_type: int, value: int):
        self._logger.log_tx(register, msg_type, value)
        self._fire(self._tx_cbs, register, msg_type, value)

    def _handle_error(self, message: str):
        self._fire(self._error_cbs, message)

    # Conditions feature removed — related file management and engine
    # have been deleted as part of feature removal.

    # ------------------------------------------------------------------ #
    #  Tasks — file management                                           #
    # ------------------------------------------------------------------ #

    def list_task_files(self) -> list[dict]:
        """Return list of {filename} for every .py file in .task/."""
        return [{"filename": p.name} for p in sorted(_TASKS_DIR.glob("*.py"))]

    def run_task(self, filename: str):
        """Execute a task script in a daemon thread.

        The script runs with ``controller`` bound to this Controller instance.
        stdout/stderr are captured and emitted via on_log callbacks.
        """
        path = _TASKS_DIR / Path(filename).name
        if not path.is_file():
            raise FileNotFoundError(f"Task file not found: {filename}")
        threading.Thread(
            target=self._exec_task,
            args=(filename, path),
            daemon=True,
        ).start()

    def _exec_task(self, filename: str, path: Path):
        self._fire(self._task_status_cbs, filename, "running")
        buf = io.StringIO()
        try:
            source = path.read_text(encoding="utf-8")
            namespace = {"controller": self}
            with redirect_stdout(buf), redirect_stderr(buf):
                exec(compile(source, str(path), "exec"), namespace)  # noqa: S102
            output = buf.getvalue()
            if output:
                for line in output.splitlines():
                    self._log(f"[{filename}] {line}")
            self._fire(self._task_status_cbs, filename, "done")
        except Exception as e:
            output = buf.getvalue()
            if output:
                for line in output.splitlines():
                    self._log(f"[{filename}] {line}")
            self._log(f"[{filename}] ERROR: {e}")
            self._fire(self._task_status_cbs, filename, "error")

    def copy_task_file(self, src_path: str) -> str:
        """Copy a .py file into .task/. Returns the new filename."""
        src = Path(src_path)
        dest = _TASKS_DIR / src.name
        counter = 1
        while dest.exists():
            dest = _TASKS_DIR / f"{src.stem}_{counter}{src.suffix}"
            counter += 1
        shutil.copy2(src, dest)
        return dest.name

    def delete_task_file(self, filename: str):
        path = _TASKS_DIR / Path(filename).name
        if not path.is_file():
            raise FileNotFoundError(f"{filename} not found.")
        path.unlink()

    # ------------------------------------------------------------------ #
    #  Shutdown                                                          #
    # ------------------------------------------------------------------ #

    def shutdown(self):
        self.disconnect()
        self._logger.close()
