import argparse
import os
import sys
from pathlib import Path


def _run_gui():
    import webview
    from api import WebApp

    def _on_loaded(window, api):
        import json
        api.set_window(window)
        window.evaluate_js(
            f"app.init("
            f"{json.dumps(api.list_condition_files())}, "
            f"{json.dumps(api.list_task_files())}"
            f")"
        )
        # Do not auto-refresh here; refresh when device actually connects from UI

    api = WebApp()
    html_path = Path(__file__).resolve().parent / "ui" / "index.html"

    window = webview.create_window(
        title="Conspecific Carousel Controller",
        url=html_path.as_uri(),
        js_api=api,
        width=1200,
        height=800,
        min_size=(1000, 650),
    )

    webview.start(func=_on_loaded, args=(window, api), debug=False)
    api.shutdown()


def _run_cli(args):
    from controller import Controller
    from protocol import REGISTER_NAMES, format_value

    ctrl = Controller()
    ctrl.on_error(lambda msg: print(f"ERROR: {msg}", file=sys.stderr))

    print(f"Connecting to {args.port} @ {args.baud} baud …")
    ctrl.connect(args.port, args.baud)
    print("Connected.")

    try:
        executed = False

        if args.status:
            values = ctrl.refresh_all()
            print("\nRegister snapshot:")
            for reg, val in sorted(values.items()):
                name = REGISTER_NAMES.get(reg, f"0x{reg:02X}")
                print(f"  {name:<20} = {format_value(reg, val)}")
            executed = True

        if args.led_sync is not None:
            ctrl.led_sync(bool(args.led_sync))
            print(f"LED/Sync {'On' if args.led_sync else 'Off'}")
            executed = True

        if args.door is not None:
            action = args.door.lower()
            if action == "open":
                ctrl.door_open()
            elif action == "close":
                ctrl.door_close()
            elif action == "stop":
                ctrl.door_stop()
            else:
                print(f"Unknown door action '{args.door}'. Use: open | close | stop",
                      file=sys.stderr)
            print(f"Door: {args.door}")
            executed = True

        if args.table is not None:
            direction, *rest = args.table.split(":")
            steps = int(rest[0]) if rest else 1
            ctrl.table_turn(direction.upper(), steps)
            print(f"Table: {direction.upper()} {steps} step(s)")
            executed = True

        if args.port_led is not None:
            port, val = args.port_led.split(":")
            ctrl.port_led(port, bool(int(val)))
            print(f"Port {port.upper()} LED {'On' if int(val) else 'Off'}")
            executed = True

        if args.port_valve is not None:
            port, val = args.port_valve.split(":")
            ctrl.port_valve(port, bool(int(val)))
            print(f"Port {port.upper()} Valve {'On' if int(val) else 'Off'}")
            executed = True

        if args.write is not None:
            reg, val = [int(x, 0) for x in args.write.split(":")]
            ctrl.write_register(reg, val)
            print(f"Wrote 0x{val:02X} to register 0x{reg:02X}")
            executed = True

        if args.read is not None:
            reg = int(args.read, 0)
            val = ctrl.read_register(reg)
            name = REGISTER_NAMES.get(reg, f"0x{reg:02X}")
            print(f"{name} = {format_value(reg, val)}")
            executed = True

        if not executed:
            print("No action specified. Use --status or a command flag. "
                  "See --help for options.")

    finally:
        ctrl.disconnect()
        ctrl.shutdown()


def _build_parser():
    p = argparse.ArgumentParser(
        prog="main.py",
        description="Conspecific Carousel Controller — GUI or CLI mode.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # launch GUI
  python main.py --port COM3 --status         # print register snapshot
  python main.py --port COM3 --led_sync 1     # turn LED/Sync on
  python main.py --port COM3 --door open      # open door
  python main.py --port COM3 --door close
  python main.py --port COM3 --table CW:4     # CW 4/8-turn steps
  python main.py --port COM3 --port_led A:1   # Port A LED on
  python main.py --port COM3 --port_valve B:0 # Port B valve off
  python main.py --port COM3 --write 0x11:0   # raw write reg:value (hex ok)
  python main.py --port COM3 --read 0x10      # raw read register
""",
    )
    p.add_argument("--port",  metavar="PORT",
                   help="Serial port (e.g. COM3 or /dev/ttyUSB0). "
                        "Required for CLI mode; omit to launch the GUI.")
    p.add_argument("--baud",  metavar="BAUD", type=int, default=1_000_000,
                   help="Baud rate (default: 1000000).")
    p.add_argument("--status", action="store_true",
                   help="Print a snapshot of all readable registers.")
    p.add_argument("--led_sync", metavar="0|1", type=int, choices=[0, 1],
                   help="Set LED/Sync output (0=off, 1=on).")
    p.add_argument("--door", metavar="open|close|stop",
                   help="Send a door command.")
    p.add_argument("--table", metavar="DIR[:STEPS]",
                   help="Turn table. DIR=CW|CCW, STEPS=1/8-turn units 1–127 "
                        "(default 1). E.g. CW:4")
    p.add_argument("--port_led", metavar="PORT:0|1",
                   help="Set a port LED. E.g. A:1 or B:0")
    p.add_argument("--port_valve", metavar="PORT:0|1",
                   help="Set a port valve. E.g. A:1 or C:0")
    p.add_argument("--write", metavar="REG:VAL",
                   help="Raw register write (hex or decimal). E.g. 0x11:0x01")
    p.add_argument("--read", metavar="REG",
                   help="Raw register read (hex or decimal). E.g. 0x10")
    return p


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    if args.port:
        _run_cli(args)
    else:
        _run_gui()

