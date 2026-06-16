# Example task: flash LED/Sync three times.
#
# The `controller` variable is automatically provided when the task runs.
# It is a fully connected Controller instance — use it to read/write registers.
#
# Can also be run directly:  python tasks/example_flash_led.py [PORT] [BAUD]

import sys
import time

# When run directly (not via the GUI), create and connect a Controller.
if "controller" not in dir():
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
    from controller import Controller as _Controller
    controller = _Controller()
    _port = sys.argv[1] if len(sys.argv) > 1 else controller.list_ports()[0]
    _baud = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
    controller.connect(_port, _baud)
    _standalone = True
else:
    _standalone = False

for i in range(3):
    controller.led_sync(True)
    time.sleep(0.3)
    controller.led_sync(False)
    time.sleep(0.3)
    print(f"Flash {i + 1}/3")

print("Done.")

if _standalone:
    controller.shutdown()
