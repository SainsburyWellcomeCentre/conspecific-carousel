/* ── Register hex→decimal map (mirrors protocol.py) ───────────── */
const REG = {
  LED_SYNC:     0x01,
  DOOR_SENSOR:  0x02,
  TABLE_SENSOR: 0x03,
  CAM_A:        0x04,
  CAM_B:        0x05,
  DOOR_STATUS:  0x10,
  DOOR_CMD:     0x11,
  DOOR_OPN_SPD: 0x12,
  DOOR_CLS_SPD: 0x13,
  TABLE_STATUS: 0x18,
  TABLE_CMD:    0x19,
  TABLE_SPD:    0x1A,
  PA_LED:       0x21,
  PA_VALVE:     0x22,
  PA_IR:        0x23,
  PB_LED:       0x24,
  PB_VALVE:     0x25,
  PB_IR:        0x26,
  PC_LED:       0x27,
  PC_VALVE:     0x28,
  PC_IR:        0x29,
  BZR_EN:       0x30,
  BZR_FREQ:     0x31,
};

/* ── Chart instance ──────────────────────────────────────────── */
let chartInstance = null;

/* ═══════════════════════════════════════════════════════════════ */
/*  app – called by Python backend via evaluate_js               */
/* ═══════════════════════════════════════════════════════════════ */
const app = {

  /** Called once after page load with condition files + task files. */
  init(taskFiles) {
    taskFiles.forEach(t => _appendTaskRow(t.filename, 'idle'));
    _log(`Loaded ${taskFiles.length} task(s)`);
  },

  /** Status update (from ACK or Refresh All). */
  onStatusUpdate(register, value, formatted) {
    _updateStatusVal(register, formatted);
    _updateToggle(register, value);
  },

  /** Async event from device. */
  onEvent(register, value, formatted, regName) {
    _updateStatusVal(register, formatted);
    _updateToggle(register, value);
    _log(`RX Event  ${regName} = ${formatted}`);
  },

  /** TX log entry. */
  onLog(msg) { _log(msg); },

  /** Error message. */
  onError(msg) { _log(`ERROR: ${msg}`); },

  /** Task status update pushed from Python. */
  onTaskStatus(filename, status) {
    const badge = document.getElementById('task-badge-' + _badgeId(filename));
    if (badge) {
      badge.className = `badge badge-${status}`;
      badge.textContent = status;
    }
    _log(`Task '${filename}': ${status}`);
  },
};

/* ═══════════════════════════════════════════════════════════════ */
/*  DOM helpers                                                   */
/* ═══════════════════════════════════════════════════════════════ */
function _updateStatusVal(register, text) {
  const hex = '0x' + register.toString(16).padStart(2, '0');
  document.querySelectorAll(`.status-val[data-reg="${hex}"]`).forEach(el => {
    el.textContent = text;
  });
  // Update slider numeric displays when readable registers change
  if (hex === '0x12') {
    const el = document.getElementById('door-open-speed');
    const val = parseInt(text) || 0;
    if (el) el.value = val;
    const disp = document.getElementById('door-open-speed-val'); if (disp) disp.textContent = String(val);
  }
  if (hex === '0x13') {
    const el = document.getElementById('door-close-speed');
    const val = parseInt(text) || 0;
    if (el) el.value = val;
    const disp = document.getElementById('door-close-speed-val'); if (disp) disp.textContent = String(val);
  }
  if (hex === '0x1a') {
    const el = document.getElementById('table-speed');
    const val = parseInt(text) || 0;
    if (el) el.value = val;
    const disp = document.getElementById('table-speed-val'); if (disp) disp.textContent = String(val);
  }
  if (hex === '0x30') {
    // Buzzer enable checkbox updated by generic checkbox handler, but ensure id reflects state
    const cb = document.getElementById('buzzer-enable');
    if (cb) cb.checked = !!(parseInt(text) || 0);
  }
  if (hex === '0x31') {
    const el = document.getElementById('buzzer-freq');
    const val = parseInt(text) || 0;
    if (el) el.value = val;
    const disp = document.getElementById('buzzer-freq-val'); if (disp) disp.textContent = `${bzRawToHz(val)} Hz`;
  }
}

// Convert buzzer raw register value (0-255) to frequency in Hz.
function bzRawToHz(raw) {
  // Linear mapping 0..255 -> 0..5000 Hz (adjust multiplier if hardware differs)
  const hz = Math.round((Number(raw) / 255) * 5000);
  return hz;
}

function _updateToggle(register, value) {
  const hex = '0x' + register.toString(16).padStart(2, '0');
  const cb = document.querySelector(`input[type="checkbox"][data-reg="${hex}"]`);
  if (cb) cb.checked = !!value;
  if (register === REG.LED_SYNC) {
    const el = document.getElementById('tog-ledsync');
    if (el) el.checked = !!value;
  }
}

function _log(msg) {
  const ts = new Date().toTimeString().slice(0, 8) + '.' +
             String(new Date().getMilliseconds()).padStart(3, '0');
  const el = document.getElementById('log-text');
  el.textContent += `[${ts}] ${msg}\n`;
  el.scrollTop = el.scrollHeight;
}

function _esc(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Conditions UI removed — related builder and helper functions deleted.

// Conditions UI removed — builder and list functions deleted.

function _initPanelResizer() {
  const resizer = document.getElementById('panel-resizer');
  const leftPanel = document.getElementById('left-panel');
  const main = document.getElementById('main');
  if (!resizer || !leftPanel || !main) return;

  let isDragging = false;
  let startX = 0;
  let startWidth = 0;

  resizer.addEventListener('pointerdown', e => {
    isDragging = true;
    startX = e.clientX;
    startWidth = leftPanel.getBoundingClientRect().width;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    resizer.setPointerCapture(e.pointerId);
  });

  resizer.addEventListener('pointermove', e => {
    if (!isDragging) return;
    const delta = e.clientX - startX;
    const containerWidth = main.clientWidth;
    const minWidth = 320;
    const maxWidth = Math.max(containerWidth - 320, minWidth);
    const newWidth = Math.min(Math.max(startWidth + delta, minWidth), maxWidth);
    document.documentElement.style.setProperty('--panel-left-width', `${newWidth}px`);
  });

  const stopDragging = () => {
    if (!isDragging) return;
    isDragging = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  };

  resizer.addEventListener('pointerup', stopDragging);
  resizer.addEventListener('pointercancel', stopDragging);
  window.addEventListener('pointerup', stopDragging);
}

function _initRowResizer() {
  // Row resizer removed — no-op to preserve call sites if any.
}

function _initLogToggle() {
  const button = document.getElementById('btn-toggle-log');
  const logBar = document.getElementById('log-bar');
  const grabber = document.getElementById('log-grabber');
  if (!button || !logBar) return;

  const updateLabel = () => {
    const collapsed = logBar.classList.contains('log-collapsed');
    button.textContent = collapsed ? 'Show' : 'Hide';
    if (grabber) grabber.style.display = collapsed ? 'none' : 'block';
    if (!collapsed) {
      adjustTopForLog();
    } else {
  
  
      // restore default top row behaviour when log is hidden
      document.documentElement.style.removeProperty('--top-row-height');
    }
  };

  button.addEventListener('click', () => {
    logBar.classList.toggle('log-collapsed');
    updateLabel();
  });

  updateLabel();
}

function _initLogGrabber() {
  const grabber = document.getElementById('log-grabber');
  const logBar = document.getElementById('log-bar');
  if (!grabber || !logBar) return;

  let isDragging = false;
  let startY = 0;
  let startHeight = 0;

  grabber.addEventListener('pointerdown', e => {
    isDragging = true;
    startY = e.clientY;
    startHeight = logBar.getBoundingClientRect().height;
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
    grabber.setPointerCapture(e.pointerId);
    if (logBar.classList.contains('log-collapsed')) logBar.classList.remove('log-collapsed');
  });

  grabber.addEventListener('pointermove', e => {
    if (!isDragging) return;
    const delta = startY - e.clientY;
    const newHeight = Math.max(80, startHeight + delta);
    const maxHeight = Math.max(window.innerHeight - 120, 120);
    document.documentElement.style.setProperty('--log-height', `${Math.min(newHeight, maxHeight)}px`);
    adjustTopForLog();
  });

  const stop = () => {
    if (!isDragging) return;
    isDragging = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  };

  grabber.addEventListener('pointerup', stop);
  grabber.addEventListener('pointercancel', stop);
  window.addEventListener('pointerup', stop);
}

function adjustTopForLog() {
  const logBar = document.getElementById('log-bar');
  if (!logBar) return;
  if (logBar.classList.contains('log-collapsed')) return;
  const root = getComputedStyle(document.documentElement);
  let logH = parseInt(root.getPropertyValue('--log-height')) || 0;
  if (!logH) logH = logBar.getBoundingClientRect().height;
  const newTop = Math.max(200, window.innerHeight - logH - 120);
  document.documentElement.style.setProperty('--top-row-height', `${newTop}px`);
}

window.addEventListener('resize', () => {
  adjustTopForLog();
});

_initPanelResizer();
_initRowResizer();
_initLogToggle();
_initLogGrabber();

/* ═══════════════════════════════════════════════════════ */
/*  Connection bar                                                */
/* ═══════════════════════════════════════════════════════════════ */
async function _refreshPorts() {
  const ports = await window.pywebview.api.list_ports();
  const sel = document.getElementById('port-sel');
  const prev = sel.value;
  sel.innerHTML = '';
  ports.forEach(p => {
    const opt = document.createElement('option');
    opt.value = opt.textContent = p;
    sel.appendChild(opt);
  });
  if (prev && ports.includes(prev)) sel.value = prev;
}

document.getElementById('btn-refresh-ports').addEventListener('click', _refreshPorts);

document.getElementById('btn-connect').addEventListener('click', async () => {
  const port = document.getElementById('port-sel').value;
  const baud = parseInt(document.getElementById('baud-sel').value);
  if (!port) { _log('ERROR: No port selected.'); return; }
  _log(`Connecting to ${port} @ ${baud}…`);
  const res = await window.pywebview.api.connect(port, baud);
  if (res.ok) {
    document.getElementById('btn-connect').disabled    = true;
    document.getElementById('btn-disconnect').disabled = false;
    const cs = document.getElementById('conn-status');
    cs.textContent = '● Connected'; cs.className = 'connected';
    _log('Connected to ' + port);
    // Read device status now that connection is established
    try { window.pywebview.api.refresh_all(); } catch (e) { console.warn('refresh_all failed', e); }
  } else {
    _log('ERROR: ' + res.error);
  }
});

document.getElementById('btn-disconnect').addEventListener('click', async () => {
  await window.pywebview.api.disconnect();
  document.getElementById('btn-connect').disabled    = false;
  document.getElementById('btn-disconnect').disabled = true;
  const cs = document.getElementById('conn-status');
  cs.textContent = '● Disconnected'; cs.className = '';
  _log('Disconnected');
});

document.getElementById('btn-refresh-all').addEventListener('click', () => {
  window.pywebview.api.refresh_all();
});

// Speed sliders: write register on change and update numeric display
const doorOpenEl = document.getElementById('door-open-speed');
if (doorOpenEl) {
  const disp = document.getElementById('door-open-speed-val');
  doorOpenEl.addEventListener('input', function () { if (disp) disp.textContent = this.value; });
  doorOpenEl.addEventListener('change', function () { window.pywebview.api.write_register(parseInt(this.dataset.reg, 16), parseInt(this.value)); });
}
const doorCloseEl = document.getElementById('door-close-speed');
if (doorCloseEl) {
  const disp = document.getElementById('door-close-speed-val');
  doorCloseEl.addEventListener('input', function () { if (disp) disp.textContent = this.value; });
  doorCloseEl.addEventListener('change', function () { window.pywebview.api.write_register(parseInt(this.dataset.reg, 16), parseInt(this.value)); });
}
const tableSpeedEl = document.getElementById('table-speed');
if (tableSpeedEl) {
  const disp = document.getElementById('table-speed-val');
  tableSpeedEl.addEventListener('input', function () { if (disp) disp.textContent = this.value; });
  tableSpeedEl.addEventListener('change', function () { window.pywebview.api.write_register(parseInt(this.dataset.reg, 16), parseInt(this.value)); });
}

// Buzzer controls
const buzzerFreqEl = document.getElementById('buzzer-freq');
if (buzzerFreqEl) {
  const disp = document.getElementById('buzzer-freq-val');
  // Throttle writes to device to ~50ms while dragging
  let _bz_lastSend = 0;
  let _bz_timer = null;
  let _bz_pending = null;

  function _bz_send(val) {
    _bz_lastSend = Date.now();
    window.pywebview.api.write_register(parseInt(buzzerFreqEl.dataset.reg, 16), parseInt(val));
  }

  buzzerFreqEl.addEventListener('input', function () {
    const hz = bzRawToHz(this.value);
    if (disp) disp.textContent = `${hz} Hz`;
    _bz_pending = this.value;
    const now = Date.now();
    const elapsed = now - _bz_lastSend;
    if (elapsed >= 50) {
      if (_bz_timer) { clearTimeout(_bz_timer); _bz_timer = null; }
      _bz_send(_bz_pending);
      _bz_pending = null;
    } else {
      if (_bz_timer) clearTimeout(_bz_timer);
      _bz_timer = setTimeout(() => {
        if (_bz_pending != null) _bz_send(_bz_pending);
        _bz_pending = null;
        _bz_timer = null;
      }, 50 - elapsed);
    }
  });

  // Ensure final value is written when interaction ends
  buzzerFreqEl.addEventListener('change', function () {
    if (_bz_timer) { clearTimeout(_bz_timer); _bz_timer = null; }
    _bz_pending = null;
    _bz_send(this.value);
  });
}

// Note: checkbox inputs with data-reg are already wired by the generic checkbox handler above;
// `buzzer-enable` (data-reg="0x30") will be handled there. Ensure numeric display initialized.
const buzzerInitEl = document.getElementById('buzzer-freq');
if (buzzerInitEl) {
  const disp = document.getElementById('buzzer-freq-val'); if (disp) disp.textContent = `${bzRawToHz(buzzerInitEl.value)} Hz`;
}

/* ═══════════════════════════════════════════════════════════════ */
/*  Toggle switches                                               */
/* ═══════════════════════════════════════════════════════════════ */
document.getElementById('tog-ledsync').addEventListener('change', function () {
  window.pywebview.api.write_register(REG.LED_SYNC, this.checked ? 1 : 0);
});

document.querySelectorAll('input[type="checkbox"][data-reg]').forEach(cb => {
  cb.addEventListener('change', function () {
    const reg = parseInt(this.dataset.reg, 16);
    window.pywebview.api.write_register(reg, this.checked ? 1 : 0);
  });
});

/* ═══════════════════════════════════════════════════════════════ */
/*  Button-click register writes (Door, etc.)                     */
/* ═══════════════════════════════════════════════════════════════ */
document.querySelectorAll('button[data-reg][data-val]').forEach(btn => {
  btn.addEventListener('click', () => {
    const reg = parseInt(btn.dataset.reg, 16);
    const val = parseInt(btn.dataset.val, 16);
    window.pywebview.api.write_register(reg, val);
  });
});

/* ═══════════════════════════════════════════════════════════════ */
/*  Table turn command                                            */
/* ═══════════════════════════════════════════════════════════════ */
document.getElementById('btn-table-turn').addEventListener('click', async () => {
  const dir   = document.getElementById('tbl-dir').value;
  const steps = parseInt(document.getElementById('tbl-steps').value);
  const res = await window.pywebview.api.send_table_command(dir, steps);
  if (res && !res.ok) _log('ERROR: ' + res.error);
});

/* ═══════════════════════════════════════════════════════════════ */
/*  Condition file table helpers                                  */
/* ═══════════════════════════════════════════════════════════════ */
// Condition table removed.
// Condition table removed.

/* ═══════════════════════════════════════════════════════════════ */
/*  Condition file management                                     */
/* ═══════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════ */
/*  Task table helpers                                            */
/* ═══════════════════════════════════════════════════════════════ */
function _appendTaskRow(filename, status) {
  const tbody = document.getElementById('task-tbody');
  const tr = document.createElement('tr');
  tr.dataset.filename = filename;
  tr.innerHTML = `
    <td>${_esc(filename)}</td>
    <td><span class="badge badge-${status}" id="task-badge-${_badgeId(filename)}">${status}</span></td>
  `;
  tr.addEventListener('click', () => {
    document.querySelectorAll('#task-tbody tr').forEach(r => r.classList.remove('selected'));
    tr.classList.add('selected');
  });
  tbody.appendChild(tr);
}

function _badgeId(filename) {
  return filename.replace(/[^a-z0-9]/gi, '_');
}

function _selectedTaskFilename() {
  const sel = document.querySelector('#task-tbody tr.selected');
  return sel ? sel.dataset.filename : null;
}

/* ═══════════════════════════════════════════════════════════════ */
/*  Task management                                               */
/* ═══════════════════════════════════════════════════════════════ */
document.getElementById('btn-task-run').addEventListener('click', async () => {
  const fn = _selectedTaskFilename();
  if (!fn) return;
  const res = await window.pywebview.api.run_task(fn);
  if (res && !res.ok) _log('ERROR: ' + res.error);
});

document.getElementById('btn-task-delete').addEventListener('click', async () => {
  const fn = _selectedTaskFilename();
  if (!fn) return;
  const res = await window.pywebview.api.delete_task_file(fn);
  if (res && res.ok) {
    const tr = document.querySelector(`#task-tbody tr[data-filename="${CSS.escape(fn)}"]`);
    if (tr) tr.remove();
    _log(`Task deleted: ${fn}`);
  } else {
    _log('ERROR: ' + (res ? res.error : 'Unknown'));
  }
});

/* ═══════════════════════════════════════════════════════════════ */
/*  Plot Log                                                      */
/* ═══════════════════════════════════════════════════════════════ */
document.getElementById('btn-plot-log').addEventListener('click', async () => {
  const res = await window.pywebview.api.open_log_file();
  if (!res || !res.ok) {
    if (res && res.error !== 'cancelled') _log('ERROR: ' + res.error);
    return;
  }

  document.getElementById('plot-title').textContent = `Log Plot — ${res.filename}`;

  const byReg = {};
  res.rows.forEach(row => {
    const name = row['Register Name'] || 'Unknown';
    const ts   = row['Timestamp'];
    const val  = parseInt(row['Value'], 16);
    if (!byReg[name]) byReg[name] = { times: [], values: [] };
    byReg[name].times.push(ts);
    byReg[name].values.push(val);
  });

  const regNames = Object.keys(byReg).sort();
  const COLORS = [
    '#4ec9b0', '#569cd6', '#dcdcaa', '#ce9178', '#c586c0',
    '#9cdcfe', '#f44747', '#4fc1ff', '#b5cea8', '#d7ba7d',
  ];

  const filtersEl = document.getElementById('plot-filters');
  filtersEl.innerHTML = '';
  const checks = {};
  regNames.forEach((name, i) => {
    const color = COLORS[i % COLORS.length];
    const lbl = document.createElement('label');
    lbl.className = 'plot-filter-cb';
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.checked = true;
    checks[name] = cb;
    lbl.appendChild(cb);
    const dot = document.createElement('span');
    dot.style.cssText = `display:inline-block;width:10px;height:10px;border-radius:50%;background:${color}`;
    lbl.appendChild(dot);
    lbl.append(' ' + name);
    cb.addEventListener('change', _replot);
    filtersEl.appendChild(lbl);
  });

  function _replot() {
    const datasets = regNames
      .filter(n => checks[n].checked)
      .map(n => {
        // Convert timestamp strings to epoch ms for numeric x-axis alignment
        const data = byReg[n].times.map((t, j) => {
          const parsed = Date.parse(t);
          const x = isNaN(parsed) ? j : parsed;
          return { x, y: byReg[n].values[j] };
        }).sort((a, b) => a.x - b.x);
        return {
          label: n,
          data,
          borderColor: COLORS[regNames.indexOf(n) % COLORS.length],
          backgroundColor: 'transparent',
          stepped: 'after',
          borderWidth: 1.5,
          pointRadius: 0,
        };
      });

    if (chartInstance) chartInstance.destroy();
    const ctx = document.getElementById('log-chart').getContext('2d');
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
          x: {
            type: 'linear',
            ticks: {
              color: '#dce4ee', maxTicksLimit: 8,
              callback: v => {
                if (!v && v !== 0) return '';
                try {
                  const d = new Date(Number(v));
                  if (isNaN(d.getTime())) return '';
                  return d.toISOString().slice(11, 19);
                } catch (e) { return ''; }
              },
            },
            grid: { color: '#444' },
          },
          y: {
            ticks: { color: '#dce4ee' },
            grid: { color: '#444' },
          },
        },
        plugins: {
          legend: { labels: { color: '#dce4ee', boxWidth: 12, font: { size: 11 } } },
        },
      },
    });
  }

  _replot();
  document.getElementById('plot-modal').classList.add('open');
});

document.getElementById('btn-plot-close').addEventListener('click', () => {
  document.getElementById('plot-modal').classList.remove('open');
  if (chartInstance) { chartInstance.destroy(); chartInstance = null; }
});

/* ═══════════════════════════════════════════════════════════════ */
/*  Initialise on load                                            */
/* ═══════════════════════════════════════════════════════════════ */
window.addEventListener('pywebviewready', async () => {
  await _refreshPorts();
  // app.init() is called by Python via evaluate_js after page load
});
