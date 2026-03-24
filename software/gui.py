import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import threading
import csv
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from protocol import (
    REGISTER_NAMES,
    READABLE_REGISTERS,
    TRIGGER_OPTIONS,
    ACTION_OPTIONS,
    REG_LED_SYNC,
    REG_DOOR_STATUS,
    REG_DOOR_CMD,
    REG_TABLE_STATUS,
    REG_TABLE_CMD,
    REG_DOOR_SENSOR,
    REG_TABLE_SENSOR,
    REG_CAM_A,
    REG_CAM_B,
    REG_PA_LED,
    REG_PA_VALVE,
    REG_PA_IR,
    REG_PB_LED,
    REG_PB_VALVE,
    REG_PB_IR,
    REG_PC_LED,
    REG_PC_VALVE,
    REG_PC_IR,
    MSG_WRITE,
    MSG_ACK,
    MSG_EVENT,
    build_table_command,
    format_value,
    reg_name,
)
from serial_comm import DeviceConnection, list_serial_ports
from csv_logger import CsvLogger
from conditions import ConditionEngine, Condition, TriggerLeaf, TriggerAnd, TriggerOr, TriggerNot

GREEN = "#4ec9b0"
RED = "#f44747"


def _style_treeview():
    """Style ttk.Treeview to match CustomTkinter dark theme (static parts)."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Dark.Treeview",
        background="#343638",
        foreground="#dce4ee",
        fieldbackground="#343638",
        borderwidth=0,
    )
    style.map(
        "Dark.Treeview",
        background=[("selected", "#1f6aa5")],
        foreground=[("selected", "#ffffff")],
    )
    style.map(
        "Dark.Treeview.Heading",
        background=[("active", "#3a3a3a")],
        relief=[("active", "flat")],
    )
    style.layout("Dark.Treeview", [("Dark.Treeview.treearea", {"sticky": "nswe"})])


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Conspecific Carousel Controller")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 650)

        self.conn = None
        self.logger = CsvLogger()
        self.status_vars = {}
        self._toggle_vars = {}  # register -> tk.BooleanVar

        # Condition engine (always alive; only fires when connected)
        self._conditions_path = str(Path(__file__).resolve().parent / "conditions.json")
        self.condition_engine = ConditionEngine(self._condition_send)
        self.condition_engine.on_action(self._on_condition_action)
        self.condition_engine.start()

        _style_treeview()
        self._apply_treeview_fonts()
        self._build_gui()
        self._load_conditions()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    #  DPI-aware treeview fonts                                           #
    # ------------------------------------------------------------------ #

    def _apply_treeview_fonts(self):
        """Apply DPI-scaled fonts to treeview styles using CTkFont."""
        self._tv_body_font = ctk.CTkFont(family="Segoe UI", size=23)
        self._tv_heading_font = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        row_h = self._tv_body_font.metrics("linespace") + 10
        style = ttk.Style()
        style.configure("Dark.Treeview", font=self._tv_body_font, rowheight=row_h)
        style.configure(
            "Dark.Treeview.Heading",
            background="#2b2b2b",
            foreground="#dce4ee",
            borderwidth=1,
            relief="solid",
            bordercolor="#555555",
            font=self._tv_heading_font,
            padding=(5, 16),
        )

    # ------------------------------------------------------------------ #
    #  GUI layout                                                         #
    # ------------------------------------------------------------------ #

    def _build_gui(self):
        self._build_connection_bar()

        middle = ctk.CTkFrame(self.root, fg_color="transparent")
        middle.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=1)
        middle.rowconfigure(0, weight=1)

        self._build_command_panel(middle)
        self._build_condition_panel(middle)
        self._build_log_panel()

    # ---- connection bar -----------------------------------------------

    def _build_connection_bar(self):
        bar = ctk.CTkFrame(self.root)
        bar.pack(fill=tk.X, padx=5, pady=(5, 2))

        ctk.CTkLabel(bar, text="Port:").pack(side=tk.LEFT, padx=(10, 2))
        self.port_var = tk.StringVar()
        self.port_combo = ctk.CTkComboBox(
            bar, variable=self.port_var, width=140, state="readonly", values=[]
        )
        self.port_combo.pack(side=tk.LEFT, padx=2)
        self._refresh_ports()
        ctk.CTkButton(bar, text="↻", width=32, command=self._refresh_ports).pack(
            side=tk.LEFT, padx=2
        )

        ctk.CTkLabel(bar, text="Baud:").pack(side=tk.LEFT, padx=(10, 2))
        self.baud_var = tk.StringVar(value="1000000")
        ctk.CTkComboBox(
            bar,
            variable=self.baud_var,
            values=["9600", "19200", "38400", "57600", "115200", "250000", "1000000", "2000000"],
            width=120,
        ).pack(side=tk.LEFT, padx=2)

        self.connect_btn = ctk.CTkButton(bar, text="Connect", command=self._connect, width=90)
        self.connect_btn.pack(side=tk.LEFT, padx=(10, 2))
        self.disconnect_btn = ctk.CTkButton(
            bar, text="Disconnect", command=self._disconnect, width=90, state="disabled"
        )
        self.disconnect_btn.pack(side=tk.LEFT, padx=2)

        ctk.CTkButton(bar, text="Refresh All", width=90, command=self._refresh_all_status).pack(
            side=tk.LEFT, padx=(10, 2)
        )
        ctk.CTkButton(bar, text="Plot Log", width=80, command=self._open_log_plot).pack(
            side=tk.LEFT, padx=2
        )

        self.conn_status = ctk.CTkLabel(bar, text="● Disconnected", text_color=RED)
        self.conn_status.pack(side=tk.RIGHT, padx=10)

    # ---- toggle helper ------------------------------------------------

    def _add_toggle(self, parent, register, text=""):
        var = tk.BooleanVar(value=False)

        def _on_toggle():
            self._send_write(register, 1 if var.get() else 0)

        if text:
            ctk.CTkLabel(parent, text=text, width=50, anchor="w").pack(side=tk.LEFT, padx=(15, 2))
        sw = ctk.CTkSwitch(parent, text="", variable=var, command=_on_toggle,
                           onvalue=True, offvalue=False)
        sw.pack(side=tk.LEFT, padx=(0, 10))
        self._toggle_vars[register] = var

    # ---- status indicator helper --------------------------------------

    def _add_indicator(self, parent, register):
        """Add a read-only label that shows a register's current value."""
        var = tk.StringVar(value="--")
        self.status_vars[register] = var
        ctk.CTkLabel(
            parent, textvariable=var, width=100, anchor="w",
            text_color="#8a8a8a", font=ctk.CTkFont(size=12),
        ).pack(side=tk.LEFT, padx=(4, 10))

    # ---- command panel ------------------------------------------------

    def _build_command_panel(self, parent):
        inner = ctk.CTkFrame(parent)
        inner.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=0)
        ctk.CTkLabel(inner, text="Commands", font=ctk.CTkFont(size=14, weight="bold")).pack(
            padx=10, pady=(10, 5), anchor="w"
        )

        # LED/Sync, Door, Table  (three columns, same format as Ports)
        top_row = ctk.CTkFrame(inner)
        top_row.pack(fill=tk.X, padx=5, pady=2)
        top_row.columnconfigure((0, 1, 2), weight=1)

        # LED / Sync
        sync_f = ctk.CTkFrame(top_row)
        sync_f.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        sync_f.columnconfigure(0, weight=1)
        ctk.CTkLabel(sync_f, text="LED / Sync", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(5, 2)
        )
        sync_row = ctk.CTkFrame(sync_f, fg_color="transparent")
        sync_row.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        self._add_toggle(sync_row, REG_LED_SYNC)

        # Door
        door_f = ctk.CTkFrame(top_row)
        door_f.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        door_f.columnconfigure(0, weight=1)
        ctk.CTkLabel(door_f, text="Door", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(5, 2)
        )
        btn_row = ctk.CTkFrame(door_f, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        ctk.CTkButton(btn_row, text="Open", width=55, height=28,
                       command=lambda: self._send_write(REG_DOOR_CMD, 0x00)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(btn_row, text="Close", width=55, height=28,
                       command=lambda: self._send_write(REG_DOOR_CMD, 0x01)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(btn_row, text="Stop", width=55, height=28,
                       command=lambda: self._send_write(REG_DOOR_CMD, 0x02)).pack(side=tk.LEFT, padx=2)
        d_ind1 = ctk.CTkFrame(door_f, fg_color="transparent")
        d_ind1.grid(row=3, column=0, sticky="ew", padx=10, pady=(2, 0))
        ctk.CTkLabel(d_ind1, text="Status:", width=50, anchor="w").pack(side=tk.LEFT)
        self._add_indicator(d_ind1, REG_DOOR_STATUS)
        d_ind2 = ctk.CTkFrame(door_f, fg_color="transparent")
        d_ind2.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 5))
        ctk.CTkLabel(d_ind2, text="Sensor:", width=50, anchor="w").pack(side=tk.LEFT)
        self._add_indicator(d_ind2, REG_DOOR_SENSOR)

        # Table
        tbl_f = ctk.CTkFrame(top_row)
        tbl_f.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        tbl_f.columnconfigure(0, weight=1)
        ctk.CTkLabel(tbl_f, text="Table", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(5, 2)
        )
        dir_row = ctk.CTkFrame(tbl_f, fg_color="transparent")
        dir_row.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        ctk.CTkLabel(dir_row, text="Dir:").pack(side=tk.LEFT)
        self.table_dir_var = tk.StringVar(value="CW")
        ctk.CTkComboBox(
            dir_row, variable=self.table_dir_var, values=["CW", "CCW"], width=80, state="readonly"
        ).pack(side=tk.LEFT, padx=5)
        steps_row = ctk.CTkFrame(tbl_f, fg_color="transparent")
        steps_row.grid(row=2, column=0, sticky="ew", padx=10, pady=2)
        ctk.CTkLabel(steps_row, text="Steps (1/8):").pack(side=tk.LEFT)
        self.table_steps_var = tk.StringVar(value="1")
        ctk.CTkEntry(steps_row, textvariable=self.table_steps_var, width=60).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(steps_row, text="Turn", width=55, command=self._send_table_command).pack(side=tk.LEFT, padx=2)
        t_ind1 = ctk.CTkFrame(tbl_f, fg_color="transparent")
        t_ind1.grid(row=3, column=0, sticky="ew", padx=10, pady=(2, 0))
        ctk.CTkLabel(t_ind1, text="Status:", width=50, anchor="w").pack(side=tk.LEFT)
        self._add_indicator(t_ind1, REG_TABLE_STATUS)
        t_ind2 = ctk.CTkFrame(tbl_f, fg_color="transparent")
        t_ind2.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 5))
        ctk.CTkLabel(t_ind2, text="Sensor:", width=50, anchor="w").pack(side=tk.LEFT)
        self._add_indicator(t_ind2, REG_TABLE_SENSOR)

        # Synchronize row heights across the three columns
        for f in (sync_f, door_f, tbl_f):
            for r in range(5):
                f.rowconfigure(r, minsize=32)

        # Ports A / B / C  (three columns)
        ctk.CTkLabel(inner, text="Ports", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=5, pady=(8, 2)
        )
        ports_row = ctk.CTkFrame(inner)
        ports_row.pack(fill=tk.X, padx=5, pady=2)
        ports_row.columnconfigure((0, 1, 2), weight=1)

        for col, (label, led_reg, valve_reg, ir_reg) in enumerate([
            ("Port A", REG_PA_LED, REG_PA_VALVE, REG_PA_IR),
            ("Port B", REG_PB_LED, REG_PB_VALVE, REG_PB_IR),
            ("Port C", REG_PC_LED, REG_PC_VALVE, REG_PC_IR),
        ]):
            pf = ctk.CTkFrame(ports_row)
            pf.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)
            ctk.CTkLabel(pf, text=label, font=ctk.CTkFont(weight="bold")).pack(
                anchor="w", padx=5, pady=(5, 2)
            )
            led_row = ctk.CTkFrame(pf, fg_color="transparent")
            led_row.pack(fill=tk.X, padx=5, pady=2)
            self._add_toggle(led_row, led_reg, text="LED")
            valve_row = ctk.CTkFrame(pf, fg_color="transparent")
            valve_row.pack(fill=tk.X, padx=5, pady=2)
            self._add_toggle(valve_row, valve_reg, text="Valve")
            ir_row = ctk.CTkFrame(pf, fg_color="transparent")
            ir_row.pack(fill=tk.X, padx=5, pady=(2, 5))
            ctk.CTkLabel(ir_row, text="IR:", width=50, anchor="w").pack(side=tk.LEFT, padx=(15, 2))
            self._add_indicator(ir_row, ir_reg)

        # Camera
        ctk.CTkLabel(inner, text="Camera", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=5, pady=(8, 2)
        )
        cam = ctk.CTkFrame(inner)
        cam.pack(fill=tk.X, padx=5, pady=2)
        cam_row = ctk.CTkFrame(cam, fg_color="transparent")
        cam_row.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(cam_row, text="Cam A:", width=60, anchor="w").pack(side=tk.LEFT)
        self._add_indicator(cam_row, REG_CAM_A)
        ctk.CTkLabel(cam_row, text="Cam B:", width=60, anchor="w").pack(side=tk.LEFT)
        self._add_indicator(cam_row, REG_CAM_B)

    # ---- condition panel ----------------------------------------------

    def _build_condition_panel(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew", padx=(2, 0))

        ctk.CTkLabel(
            frame, text="Conditions", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")

        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.cond_tree = ttk.Treeview(
            tree_frame,
            columns=("name", "trigger", "action", "active"),
            show="headings",
            height=8,
            style="Dark.Treeview",
        )
        self.cond_tree.heading("name", text="Name")
        self.cond_tree.heading("trigger", text="When")
        self.cond_tree.heading("action", text="Then")
        self.cond_tree.heading("active", text="Active")
        # Scale column widths using the DPI-aware heading font
        em = self._tv_heading_font.measure("M")
        self.cond_tree.column("name", width=em * 7)
        self.cond_tree.column("trigger", width=em * 11)
        self.cond_tree.column("action", width=em * 11)
        self.cond_tree.column("active", width=em * 5)
        self.cond_tree.tag_configure("evenrow", background="#343638")
        self.cond_tree.tag_configure("oddrow", background="#3e4042")
        self.cond_tree.pack(fill=tk.BOTH, expand=True)

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill=tk.X, padx=5, pady=5)
        ctk.CTkButton(btns, text="Add", width=70, command=self._open_condition_dialog).pack(
            side=tk.LEFT, padx=2
        )
        ctk.CTkButton(btns, text="Remove", width=70, command=self._remove_condition).pack(
            side=tk.LEFT, padx=2
        )
        ctk.CTkButton(btns, text="Toggle", width=70, command=self._toggle_condition).pack(
            side=tk.LEFT, padx=2
        )

    # ---- log panel ----------------------------------------------------

    def _build_log_panel(self):
        frame = ctk.CTkFrame(self.root)
        frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=(2, 5))

        ctk.CTkLabel(frame, text="Event Log", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=(5, 0)
        )

        self.log_text = ctk.CTkTextbox(
            frame, height=150, font=("Consolas", 12), state="disabled", wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ------------------------------------------------------------------ #
    #  Connection                                                         #
    # ------------------------------------------------------------------ #

    def _refresh_ports(self):
        ports = list_serial_ports()
        self.port_combo.configure(values=ports)
        if ports and not self.port_var.get():
            self.port_combo.set(ports[0])

    def _connect(self):
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("Connection", "Select a serial port.")
            return
        try:
            baud = int(self.baud_var.get())
            self.conn = DeviceConnection(port, baud)
            self.conn.on_event(self._on_event)
            self.conn.on_ack(self._on_ack)
            self.conn.on_tx(self._on_tx)
            self.conn.on_error(self._on_error)
            self.conn.connect()

            self.connect_btn.configure(state="disabled")
            self.disconnect_btn.configure(state="normal")
            self.conn_status.configure(text="● Connected", text_color=GREEN)
            self._log_msg("Connected to " + port)
            self._refresh_all_status()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def _disconnect(self):
        if self.conn:
            self.conn.disconnect()
            self.conn = None
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self.conn_status.configure(text="● Disconnected", text_color=RED)
        self._log_msg("Disconnected")

    def _on_close(self):
        self._disconnect()
        self._save_conditions()
        self.condition_engine.stop()
        self.logger.close()
        self.root.destroy()

    # ------------------------------------------------------------------ #
    #  Callbacks from worker threads (must schedule GUI updates)          #
    # ------------------------------------------------------------------ #

    def _on_event(self, register, value):
        self.logger.log_rx(register, MSG_EVENT, value)
        self.condition_engine.push_event(register, value)
        self.root.after(0, self._update_status, register, value)
        self.root.after(
            0,
            self._log_msg,
            f"RX Event  {reg_name(register)} = {format_value(register, value)}",
        )

    def _on_ack(self, register, value):
        self.logger.log_rx(register, MSG_ACK, value)
        self.condition_engine.push_event(register, value)
        self.root.after(0, self._update_status, register, value)

    def _on_tx(self, register, msg_type, value):
        self.logger.log_tx(register, msg_type, value)
        type_str = "Write" if msg_type == MSG_WRITE else "Read"
        self.root.after(
            0,
            self._log_msg,
            f"TX {type_str:5s} {reg_name(register)} = 0x{value:02X}",
        )

    def _on_error(self, message):
        self.root.after(0, self._log_msg, f"ERROR: {message}")

    def _on_condition_action(self, condition):
        self.root.after(0, self._log_msg, f"Condition fired: '{condition.name}'")

    # ------------------------------------------------------------------ #
    #  GUI helpers                                                        #
    # ------------------------------------------------------------------ #

    def _update_status(self, register, value):
        if register in self.status_vars:
            self.status_vars[register].set(format_value(register, value))
        if register in self._toggle_vars:
            self._toggle_vars[register].set(bool(value))

    def _log_msg(self, text):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{ts}] {text}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    # ------------------------------------------------------------------ #
    #  Commands                                                           #
    # ------------------------------------------------------------------ #

    def _send_write(self, register, value):
        if not self.conn or not self.conn.is_connected:
            messagebox.showwarning("Not Connected", "Connect to a device first.")
            return
        threading.Thread(target=self._do_write, args=(register, value), daemon=True).start()

    def _do_write(self, register, value):
        try:
            self.conn.write_register(register, value)
        except TimeoutError as e:
            self.root.after(0, lambda msg=str(e): messagebox.showerror("Command Failed", msg))

    def _send_table_command(self):
        try:
            steps = int(self.table_steps_var.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Steps must be a number.")
            return
        if not 1 <= steps <= 127:
            messagebox.showwarning("Invalid Input", "Steps must be between 1 and 127.")
            return
        direction = 0 if self.table_dir_var.get() == "CW" else 1
        self._send_write(REG_TABLE_CMD, build_table_command(direction, steps))

    def _refresh_all_status(self):
        if not self.conn or not self.conn.is_connected:
            return
        threading.Thread(target=self._do_refresh_all, daemon=True).start()

    def _do_refresh_all(self):
        for reg in READABLE_REGISTERS:
            try:
                _, value = self.conn.read_register(reg)
                self.root.after(0, self._update_status, reg, value)
            except Exception:
                pass

    def _condition_send(self, register, value):
        if self.conn and self.conn.is_connected:
            self.conn.write_register(register, value)

    # ------------------------------------------------------------------ #
    #  Log plot                                                           #
    # ------------------------------------------------------------------ #

    def _open_log_plot(self):
        log_dir = Path(__file__).resolve().parent / ".log"
        filepath = filedialog.askopenfilename(
            title="Select Log CSV",
            initialdir=str(log_dir) if log_dir.is_dir() else ".",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not filepath:
            return

        # Parse CSV
        timestamps = []
        register_data = {}  # register_name -> (times, values)
        try:
            with open(filepath, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ts = datetime.fromisoformat(row["Timestamp"])
                        reg_name_str = row["Register Name"]
                        val = int(row["Value"], 16)
                    except (ValueError, KeyError):
                        continue
                    if reg_name_str not in register_data:
                        register_data[reg_name_str] = ([], [])
                    register_data[reg_name_str][0].append(ts)
                    register_data[reg_name_str][1].append(val)
        except Exception as e:
            messagebox.showerror("Plot Error", f"Failed to read log:\n{e}")
            return

        if not register_data:
            messagebox.showinfo("Plot", "No data found in log file.")
            return

        # Build plot window
        win = ctk.CTkToplevel(self.root)
        win.title(f"Log Plot — {Path(filepath).name}")
        win.geometry("900x600")
        win.transient(self.root)

        # Register selector (flow-wrap into multiple rows on resize)
        sel_frame = ctk.CTkFrame(win, fg_color="transparent")
        sel_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        reg_names = sorted(register_data.keys())
        check_vars = {}
        _cb_widgets = []
        lbl = ctk.CTkLabel(sel_frame, text="Registers:")
        _cb_widgets.append(lbl)
        for name in reg_names:
            var = tk.BooleanVar(value=True)
            check_vars[name] = var
            cb = ctk.CTkCheckBox(sel_frame, text=name, variable=var, width=20,
                                 command=lambda: _replot())
            _cb_widgets.append(cb)

        def _reflow(event=None):
            max_w = sel_frame.winfo_width()
            if max_w <= 1:
                return
            col = 0
            row = 0
            x = 0
            for w in _cb_widgets:
                w.update_idletasks()
                w_width = w.winfo_reqwidth() + 10
                if x + w_width > max_w and col > 0:
                    row += 1
                    col = 0
                    x = 0
                w.grid(row=row, column=col, padx=(0, 5), pady=2, sticky="w")
                x += w_width
                col += 1

        sel_frame.bind("<Configure>", _reflow)
        win.after(50, _reflow)

        # Matplotlib figure
        fig = Figure(figsize=(9, 4.5), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=win)
        toolbar = NavigationToolbar2Tk(canvas, win)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        def _replot():
            ax.clear()
            ax.set_facecolor("#343638")
            ax.tick_params(colors="#dce4ee", labelsize=9)
            ax.xaxis.label.set_color("#dce4ee")
            ax.yaxis.label.set_color("#dce4ee")
            ax.title.set_color("#dce4ee")
            for spine in ax.spines.values():
                spine.set_color("#555555")

            for name in reg_names:
                if check_vars[name].get():
                    times, values = register_data[name]
                    ax.step(times, values, where="post", label=name, linewidth=1.2)

            ax.set_xlabel("Time")
            ax.set_ylabel("Value")
            ax.set_title("Register Values Over Time")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            fig.autofmt_xdate(rotation=30, ha="right")
            ax.legend(loc="upper left", fontsize=8, facecolor="#2b2b2b",
                      edgecolor="#555555", labelcolor="#dce4ee")
            ax.grid(True, color="#444444", linewidth=0.5, alpha=0.7)
            canvas.draw()

        _replot()

    # ------------------------------------------------------------------ #
    #  Condition management                                               #
    # ------------------------------------------------------------------ #

    def _recolor_cond_rows(self):
        """Re-apply alternating row colours after any insert / delete."""
        for i, item in enumerate(self.cond_tree.get_children("")):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.cond_tree.item(item, tags=(tag,))

    def _save_conditions(self):
        try:
            self.condition_engine.save(self._conditions_path)
        except Exception as e:
            self._log_msg(f"Failed to save conditions: {e}")

    def _load_conditions(self):
        try:
            conditions = self.condition_engine.load(self._conditions_path)
            for cond in conditions:
                mark = "\u2713" if cond.enabled else "\u2717"
                action_text = f"reg 0x{cond.action_register:02X} = 0x{cond.action_value:02X}"
                for a in ACTION_OPTIONS:
                    if a[1] == cond.action_register and a[2] == cond.action_value:
                        action_text = a[0]
                        break
                self.cond_tree.insert(
                    "", tk.END,
                    values=(cond.name, cond.trigger.describe(), action_text, mark),
                )
            self._recolor_cond_rows()
            if conditions:
                self._log_msg(f"Restored {len(conditions)} condition(s)")
        except Exception as e:
            self._log_msg(f"Failed to load conditions: {e}")

    def _open_condition_dialog(self):
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Add Condition")
        dlg.geometry("520x560")
        dlg.transient(self.root)
        dlg.grab_set()

        # ── Name ──
        name_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        name_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        ctk.CTkLabel(name_frame, text="Name:").pack(side=tk.LEFT)
        name_var = tk.StringVar()
        ctk.CTkEntry(name_frame, textvariable=name_var, width=250).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True
        )

        # ── Trigger builder ──
        trig_container = ctk.CTkFrame(dlg)
        trig_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ctk.CTkLabel(
            trig_container, text="Trigger (When)", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=5, pady=(5, 2))

        tree_wrapper = ctk.CTkFrame(trig_container, fg_color="transparent")
        tree_wrapper.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        trigger_tree = ttk.Treeview(tree_wrapper, show="tree", height=8, style="Dark.Treeview")
        trigger_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trigger_items = {}  # treeview item id -> data dict

        def _selected_group():
            sel = trigger_tree.selection()
            if not sel:
                return ""
            item = sel[0]
            data = trigger_items.get(item)
            if data and data["type"] in ("and", "or"):
                return item
            if data and data["type"] == "not" and not trigger_tree.get_children(item):
                return item
            return trigger_tree.parent(item)

        def _add_leaf():
            text = trig_var.get()
            if not text:
                return
            opt = next((t for t in TRIGGER_OPTIONS if t[0] == text), None)
            if not opt:
                return
            parent = _selected_group()
            iid = trigger_tree.insert(parent, tk.END, text=text)
            trigger_items[iid] = {"type": "leaf", "register": opt[1], "value": opt[2], "label": text}
            trigger_tree.see(iid)

        def _add_group(kind):
            parent = _selected_group()
            iid = trigger_tree.insert(parent, tk.END, text=kind.upper(), open=True)
            trigger_items[iid] = {"type": kind}
            trigger_tree.see(iid)

        def _wrap_not():
            sel = trigger_tree.selection()
            if not sel:
                return
            item = sel[0]
            parent = trigger_tree.parent(item)
            idx = trigger_tree.index(item)
            not_id = trigger_tree.insert(parent, idx, text="NOT", open=True)
            trigger_items[not_id] = {"type": "not"}
            trigger_tree.move(item, not_id, 0)
            trigger_tree.selection_set(not_id)

        def _del_recursive(item):
            for ch in trigger_tree.get_children(item):
                _del_recursive(ch)
            trigger_items.pop(item, None)
            trigger_tree.delete(item)

        def _remove_node():
            sel = trigger_tree.selection()
            if sel:
                _del_recursive(sel[0])

        # selector row
        sel_row = ctk.CTkFrame(trig_container, fg_color="transparent")
        sel_row.pack(fill=tk.X, padx=5, pady=2)
        trig_var = tk.StringVar()
        ctk.CTkComboBox(
            sel_row,
            variable=trig_var,
            values=[t[0] for t in TRIGGER_OPTIONS],
            state="readonly",
            width=260,
        ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(sel_row, text="+Trigger", width=80, command=_add_leaf).pack(
            side=tk.LEFT, padx=2
        )

        # logic buttons row
        btn_row = ctk.CTkFrame(trig_container, fg_color="transparent")
        btn_row.pack(fill=tk.X, padx=5, pady=(0, 5))
        ctk.CTkButton(btn_row, text="AND", width=60, command=lambda: _add_group("and")).pack(
            side=tk.LEFT, padx=2
        )
        ctk.CTkButton(btn_row, text="OR", width=60, command=lambda: _add_group("or")).pack(
            side=tk.LEFT, padx=2
        )
        ctk.CTkButton(btn_row, text="NOT", width=60, command=_wrap_not).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(btn_row, text="Remove", width=80, command=_remove_node).pack(
            side=tk.LEFT, padx=2
        )

        # ── Action ──
        act_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        act_frame.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(act_frame, text="Then:").pack(side=tk.LEFT)
        action_var = tk.StringVar()
        ctk.CTkComboBox(
            act_frame,
            variable=action_var,
            values=[a[0] for a in ACTION_OPTIONS],
            state="readonly",
            width=280,
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # ── build trigger node from tree ──
        def _build_node(item):
            data = trigger_items.get(item)
            if not data:
                return None
            if data["type"] == "leaf":
                return TriggerLeaf(data["register"], data["value"], data["label"])
            children = trigger_tree.get_children(item)
            child_nodes = [_build_node(c) for c in children]
            child_nodes = [n for n in child_nodes if n is not None]
            if data["type"] == "and":
                return TriggerAnd(child_nodes) if child_nodes else None
            if data["type"] == "or":
                return TriggerOr(child_nodes) if child_nodes else None
            if data["type"] == "not":
                return TriggerNot(child_nodes[0]) if child_nodes else None
            return None

        def _on_ok():
            name = name_var.get().strip()
            action_text = action_var.get()
            if not name or not action_text:
                messagebox.showwarning("Missing Fields", "Fill in name and action.", parent=dlg)
                return

            root_children = trigger_tree.get_children("")
            if not root_children:
                messagebox.showwarning("No Trigger", "Add at least one trigger.", parent=dlg)
                return

            if len(root_children) == 1:
                trigger_node = _build_node(root_children[0])
            else:
                nodes = [_build_node(c) for c in root_children]
                nodes = [n for n in nodes if n is not None]
                trigger_node = TriggerAnd(nodes) if len(nodes) > 1 else (nodes[0] if nodes else None)

            if trigger_node is None:
                messagebox.showwarning("Invalid Trigger", "Build a valid trigger tree.", parent=dlg)
                return

            action = next((a for a in ACTION_OPTIONS if a[0] == action_text), None)
            if not action:
                return

            cond = Condition(name, trigger_node, action[1], action[2])
            self.condition_engine.add_condition(cond)
            self.cond_tree.insert("" , tk.END, values=(name, trigger_node.describe(), action_text, "\u2713"))
            self._recolor_cond_rows()
            self._save_conditions()
            self._log_msg(f"Condition added: '{name}'")
            dlg.destroy()

        # ── OK / Cancel ──
        ok_cancel = ctk.CTkFrame(dlg, fg_color="transparent")
        ok_cancel.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkButton(ok_cancel, text="OK", width=80, command=_on_ok).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(ok_cancel, text="Cancel", width=80, command=dlg.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def _remove_condition(self):
        sel = self.cond_tree.selection()
        if not sel:
            return
        idx = self.cond_tree.index(sel[0])
        self.condition_engine.remove_condition(idx)
        self.cond_tree.delete(sel[0])
        self._recolor_cond_rows()
        self._save_conditions()

    def _toggle_condition(self):
        sel = self.cond_tree.selection()
        if not sel:
            return
        idx = self.cond_tree.index(sel[0])
        self.condition_engine.toggle_condition(idx)
        conditions = self.condition_engine.get_conditions()
        if idx < len(conditions):
            mark = "\u2713" if conditions[idx].enabled else "\u2717"
            vals = self.cond_tree.item(sel[0])["values"]
            self.cond_tree.item(sel[0], values=(vals[0], vals[1], vals[2], mark))
        self._save_conditions()
