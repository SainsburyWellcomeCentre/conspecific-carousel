"""
WebApp – pywebview JS API.

All public methods are callable from JavaScript via:
    window.pywebview.api.methodName(arg1, arg2, ...)

Push-style updates (events, acks, errors, task status) are injected into the
page via window.evaluate_js() calling JS functions on the global ``app`` object.
"""

import csv
import json
import threading
from pathlib import Path

import webview

from protocol import (
    MSG_WRITE,
    format_value,
    reg_name,
    TRIGGER_OPTIONS,
    ACTION_OPTIONS,
    REGISTER_NAMES,
)
from controller import Controller


class WebApp:
    """Thin pywebview bridge that delegates all device logic to Controller."""

    def __init__(self):
        self._window: webview.Window | None = None
        self._ctrl = Controller()

        # Wire Controller callbacks → JS push
        self._ctrl.on_event(self._on_event)
        self._ctrl.on_ack(self._on_ack)
        self._ctrl.on_tx(self._on_tx)
        self._ctrl.on_error(self._on_error)
        self._ctrl.on_log(self._on_log)
        self._ctrl.on_task_status(self._on_task_status)

    # ------------------------------------------------------------------ #
    #  Window injection                                                   #
    # ------------------------------------------------------------------ #

    def set_window(self, window: webview.Window):
        self._window = window

    def _js(self, code: str):
        """Safely evaluate JS; swallow errors if window not ready."""
        if self._window:
            try:
                self._window.evaluate_js(code)
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    #  Device callbacks → JS push                                        #
    # ------------------------------------------------------------------ #

    def _on_event(self, register: int, value: int, formatted: str, reg_name_str: str):
        self._js(
            f"app.onEvent({register}, {value}, "
            f"{json.dumps(formatted)}, {json.dumps(reg_name_str)})"
        )

    def _on_ack(self, register: int, value: int, formatted: str):
        self._js(
            f"app.onStatusUpdate({register}, {value}, {json.dumps(formatted)})"
        )

    def _on_tx(self, register: int, msg_type: int, value: int):
        type_str = "Write" if msg_type == MSG_WRITE else "Read"
        msg = f"TX {type_str:5s} {reg_name(register)} = 0x{value:02X}"
        self._js(f"app.onLog({json.dumps(msg)})")

    def _on_error(self, message: str):
        self._js(f"app.onError({json.dumps(message)})")

    def _on_log(self, message: str):
        self._js(f"app.onLog({json.dumps(message)})")

    def _on_task_status(self, filename: str, status: str):
        self._js(f"app.onTaskStatus({json.dumps(filename)}, {json.dumps(status)})")

    # ------------------------------------------------------------------ #
    #  JS-callable: ports & connection                                   #
    # ------------------------------------------------------------------ #

    def list_ports(self) -> list:
        return self._ctrl.list_ports()

    def connect(self, port: str, baud: int) -> dict:
        if not port:
            return {"ok": False, "error": "No port selected."}
        try:
            self._ctrl.connect(port, int(baud))
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def disconnect(self):
        self._ctrl.disconnect()

    def is_connected(self) -> bool:
        return self._ctrl.is_connected

    # ------------------------------------------------------------------ #
    #  JS-callable: register I/O                                        #
    # ------------------------------------------------------------------ #

    def write_register(self, register: int, value: int) -> dict:
        if not self._ctrl.is_connected:
            return {"ok": False, "error": "Not connected."}
        threading.Thread(
            target=self._do_write, args=(int(register), int(value)), daemon=True
        ).start()
        return {"ok": True}

    def _do_write(self, register: int, value: int):
        try:
            self._ctrl.write_register(register, value)
        except TimeoutError as e:
            self._js(f"app.onError({json.dumps(str(e))})")

    def refresh_all(self):
        if not self._ctrl.is_connected:
            return
        threading.Thread(target=self._do_refresh_all, daemon=True).start()

    def _do_refresh_all(self):
        result = self._ctrl.refresh_all()
        for reg, value in result.items():
            self._js(
                f"app.onStatusUpdate({reg}, {value}, "
                f"{json.dumps(format_value(reg, value))})"
            )

    def send_table_command(self, direction: str, steps: int) -> dict:
        try:
            self._ctrl.send_table_command(direction, int(steps))
            return {"ok": True}
        except (ValueError, RuntimeError) as e:
            return {"ok": False, "error": str(e)}

    # ------------------------------------------------------------------ #
    #  JS-callable: condition files                                      #
    # ------------------------------------------------------------------ #

    def list_condition_files(self) -> list:
        return self._ctrl.list_condition_files()

    def enable_condition_file(self, filename: str) -> dict:
        try:
            self._ctrl.enable_condition_file(filename)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def disable_condition_file(self, filename: str) -> dict:
        try:
            self._ctrl.disable_condition_file(filename)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_condition_file(self, filename: str) -> dict:
        try:
            self._ctrl.delete_condition_file(filename)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def browse_and_import_condition(self) -> dict:
        """Open a file picker then copy the selected .json into .conditions/."""
        if not self._window:
            return {"ok": False, "error": "Window not ready."}
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("Condition JSON (*.json)", "All files (*.*)"),
        )
        if not result:
            return {"ok": False, "error": "cancelled"}
        try:
            new_filename = self._ctrl.copy_condition_file(result[0])
            self._ctrl.enable_condition_file(new_filename)
            files = self._ctrl.list_condition_files()
            entry = next((f for f in files if f["filename"] == new_filename), None)
            return {"ok": True, "entry": entry}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def save_condition(self, condition: dict) -> dict:
        try:
            new_filename = self._ctrl.save_condition(condition)
            files = self._ctrl.list_condition_files()
            entry = next((f for f in files if f["filename"] == new_filename), None)
            return {"ok": True, "entry": entry}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ------------------------------------------------------------------ #
    #  JS-callable: task files                                           #
    # ------------------------------------------------------------------ #

    def list_task_files(self) -> list:
        return self._ctrl.list_task_files()

    def run_task(self, filename: str) -> dict:
        try:
            self._ctrl.run_task(filename)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_task_file(self, filename: str) -> dict:
        try:
            self._ctrl.delete_task_file(filename)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def browse_and_import_task(self) -> dict:
        """Open a file picker then copy the selected .py into .task/."""
        if not self._window:
            return {"ok": False, "error": "Window not ready."}
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("Python scripts (*.py)", "All files (*.*)"),
        )
        if not result:
            return {"ok": False, "error": "cancelled"}
        try:
            new_filename = self._ctrl.copy_task_file(result[0])
            return {"ok": True, "filename": new_filename}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ------------------------------------------------------------------ #
    #  JS-callable: metadata                                             #
    # ------------------------------------------------------------------ #

    def get_trigger_options(self) -> list:
        return [{"label": t[0], "register": t[1], "value": t[2]} for t in TRIGGER_OPTIONS]

    def get_action_options(self) -> list:
        return [{"label": a[0], "register": a[1], "value": a[2]} for a in ACTION_OPTIONS]

    def get_register_names(self) -> dict:
        return {str(k): v for k, v in REGISTER_NAMES.items()}

    # ------------------------------------------------------------------ #
    #  JS-callable: log file / chart                                     #
    # ------------------------------------------------------------------ #

    def open_log_file(self) -> dict:
        if not self._window:
            return {"ok": False, "error": "Window not ready."}
        log_dir = str(Path(__file__).resolve().parent / ".log")
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            directory=log_dir if Path(log_dir).is_dir() else "",
            allow_multiple=False,
            file_types=("CSV files (*.csv)", "All files (*.*)"),
        )
        # Normalise pywebview return types (some platforms return a str, others a list)
        paths = []
        if isinstance(result, str):
            paths = [result]
        elif isinstance(result, (list, tuple)):
            paths = list(result)
        if not paths:
            return {"ok": False, "error": "cancelled"}
        rows = []
        try:
            with open(paths[0], newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
        except Exception as e:
            return {"ok": False, "error": str(e)}

        return {"ok": True, "filename": Path(paths[0]).name, "rows": rows}

    # ------------------------------------------------------------------ #
    #  Shutdown                                                          #
    # ------------------------------------------------------------------ #

    def shutdown(self):
        self._ctrl.shutdown()
