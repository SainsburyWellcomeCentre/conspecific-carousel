"""
example_no_gui.py – Run the Conspecific Carousel controller without a GUI.

Usage:
    python example_no_gui.py               # auto-detect the first serial port
    python example_no_gui.py COM4          # specify a port explicitly
    python example_no_gui.py COM4 115200   # specify port and baud rate

The script:
  1. Lists available serial ports.
  2. Connects to the device.
  3. Reads all registers and prints them.
  4. Flashes the LED/Sync output 3 times.
  5. Opens the door, waits, then closes it.
  6. Disconnects and shuts down cleanly.

Press Ctrl+C at any time to abort.
"""

import sys
import time

# The Controller class lives in the same directory as this file.
# If you run this script from a different working directory, adjust sys.path:
#   sys.path.insert(0, r"d:\Github\conspecific-carousel\software")

from controller import Controller
from protocol import REGISTER_NAMES, format_value

# ── Configuration ──────────────────────────────────────────────────────
PORT = sys.argv[1] if len(sys.argv) > 1 else None
BAUD = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000


def on_event(register, value, formatted, reg_name):
    """Called from a background thread whenever the device sends an event packet."""
    print(f"  [EVENT] {reg_name} = {formatted}")


def on_error(message):
    """Called from a background thread on serial/timeout errors."""
    print(f"  [ERROR] {message}", file=sys.stderr)


def main():
    ctrl = Controller()
    ctrl.on_event(on_event)
    ctrl.on_error(on_error)

    # ── 1. List ports ───────────────────────────────────────────────
    ports = ctrl.list_ports()
    print(f"Available ports: {ports or '(none found)'}")

    port = PORT or (ports[0] if ports else None)
    if not port:
        print("No serial port found. Pass a port as the first argument.")
        ctrl.shutdown()
        return

    # ── 2. Connect ──────────────────────────────────────────────────
    print(f"Connecting to {port} @ {BAUD} baud …")
    ctrl.connect(port, BAUD)
    print("Connected.")

    try:
        # ── 3. Read all registers ───────────────────────────────────
        print("\nRegister snapshot:")
        values = ctrl.refresh_all()
        for reg, val in sorted(values.items()):
            name = REGISTER_NAMES.get(reg, f"0x{reg:02X}")
            print(f"  {name:<20} = {format_value(reg, val)}")

        # ── 4. Flash LED/Sync 3 times ───────────────────────────────
        print("\nFlashing LED/Sync 3x …")
        for i in range(3):
            ctrl.led_sync(True)
            time.sleep(0.3)
            ctrl.led_sync(False)
            time.sleep(0.3)
            print(f"  Flash {i + 1}/3")

        # ── 5. Open door → wait → close ─────────────────────────────
        print("\nOpening door …")
        ctrl.door_open()
        time.sleep(3.0)

        print("Closing door …")
        ctrl.door_close()
        time.sleep(3.0)

        print("\nDone.")

    except KeyboardInterrupt:
        print("\nAborted by user.")
    finally:
        # ── 6. Clean shutdown ───────────────────────────────────────
        ctrl.disconnect()
        ctrl.shutdown()
        print("Disconnected.")


if __name__ == "__main__":
    main()
