import csv
import os
from datetime import datetime
import threading

from protocol import REGISTER_NAMES


class CsvLogger:

    def __init__(self, filepath=None):
        self._lock = threading.Lock()
        self._has_data = False
        if filepath is None:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".log")
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(log_dir, f"device_log_{timestamp}.csv")
        self._filepath = filepath
        self._file = None
        self._writer = None

    def log_tx(self, register, msg_type, value):
        type_name = "Write" if msg_type == 0x01 else "Read"
        self._write_row("TX", register, type_name, value)

    def log_rx(self, register, msg_type, value):
        type_name = "ACK" if msg_type == 0x02 else "Event"
        self._write_row("RX", register, type_name, value)

    def _ensure_open(self):
        if self._file is None:
            write_header = not os.path.exists(self._filepath)
            self._file = open(self._filepath, "a", newline="")
            self._writer = csv.writer(self._file)
            if write_header:
                self._writer.writerow(
                    ["Timestamp", "Direction", "Register", "Register Name", "Type", "Value"]
                )
                self._file.flush()

    def _write_row(self, direction, register, type_name, value):
        with self._lock:
            self._ensure_open()
            self._has_data = True
            self._writer.writerow([
                datetime.now().isoformat(timespec="milliseconds"),
                direction,
                f"0x{register:02X}",
                REGISTER_NAMES.get(register, "Unknown"),
                type_name,
                f"0x{value:02X}",
            ])
            self._file.flush()

    def close(self):
        if self._file is not None:
            self._file.close()
        if not self._has_data and os.path.exists(self._filepath):
            os.remove(self._filepath)
