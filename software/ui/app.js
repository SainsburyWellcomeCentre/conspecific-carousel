/* ── Register hex→decimal map (mirrors protocol.py) ───────────── */
const REG = {
  LED_SYNC:     0x01,
  DOOR_SENSOR:  0x02,
  TABLE_SENSOR: 0x03,
  CAM_A:        0x04,
  CAM_B:        0x05,
  DOOR_STATUS:  0x10,
  DOOR_CMD:     0x11,
  TABLE_STATUS: 0x18,
  TABLE_CMD:    0x19,
  PA_LED:       0x21,
  PA_VALVE:     0x22,
  PA_IR:        0x23,
  PB_LED:       0x24,
  PB_VALVE:     0x25,
  PB_IR:        0x26,
  PC_LED:       0x27,
  PC_VALVE:     0x28,
  PC_IR:        0x29,
};

/* ── Chart instance ──────────────────────────────────────────── */
let chartInstance = null;

/* ═══════════════════════════════════════════════════════════════ */
/*  app – called by Python backend via evaluate_js               */
/* ═══════════════════════════════════════════════════════════════ */
const app = {

  /** Called once after page load with condition files + task files. */
  init(conditionFiles, taskFiles) {
    _initConditionBuilder();
    conditionFiles.forEach(_appendConditionRow);
    taskFiles.forEach(t => _appendTaskRow(t.filename, 'idle'));
    _log(`Loaded ${conditionFiles.length} condition(s), ${taskFiles.length} task(s)`);
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

let _triggerOptions = [];
let _actionOptions = [];

async function _initConditionBuilder() {
  try {
    _triggerOptions = await window.pywebview.api.get_trigger_options();
    _actionOptions = await window.pywebview.api.get_action_options();
  } catch (e) {
    _log(`ERROR: Failed to load condition options: ${e}`);
    _triggerOptions = [];
    _actionOptions = [];
  }

  const actionSelect = document.getElementById('cond-action');
  actionSelect.innerHTML = _actionOptions.map(o =>
    `<option value="${o.register}:${o.value}">${_esc(o.label)}</option>`
  ).join('');

  document.getElementById('btn-cond-add-group').addEventListener('click', _addConditionGroup);
  document.getElementById('btn-cond-create').addEventListener('click', _createConditionFromBuilder);

  _addConditionGroup();
}

function _addConditionGroup() {
  const container = document.getElementById('cond-group-rows');
  const group = document.createElement('div');
  group.className = 'cond-group';

  const header = document.createElement('div');
  header.className = 'group-header';

  const modeLabel = document.createElement('label');
  modeLabel.textContent = 'Group match:';
  const modeSelect = document.createElement('select');
  modeSelect.className = 'cond-group-mode';
  modeSelect.innerHTML = `
    <option value="or">Any (OR)</option>
    <option value="and">All (AND)</option>
  `;
  modeLabel.appendChild(modeSelect);

  const removeGroup = document.createElement('button');
  removeGroup.type = 'button';
  removeGroup.className = 'btn-cond-remove-group';
  removeGroup.textContent = 'Remove Group';
  removeGroup.addEventListener('click', () => group.remove());

  header.appendChild(modeLabel);
  header.appendChild(removeGroup);

  const rows = document.createElement('div');
  rows.className = 'cond-trigger-rows';

  const addTriggerButton = document.createElement('button');
  addTriggerButton.type = 'button';
  addTriggerButton.className = 'btn-cond-add-trigger';
  addTriggerButton.textContent = 'Add Trigger';
  addTriggerButton.addEventListener('click', () => _addConditionTriggerRow(rows));

  group.appendChild(header);
  group.appendChild(rows);
  group.appendChild(addTriggerButton);
  container.appendChild(group);

  _addConditionTriggerRow(rows);
}

function _addConditionTriggerRow(container) {
  const row = document.createElement('div');
  row.className = 'cond-trigger-row';

  const select = document.createElement('select');
  select.className = 'cond-trigger-select';
  select.innerHTML = _triggerOptions.map((o, idx) =>
    `<option value="${idx}">${_esc(o.label)}</option>`
  ).join('');

  const removeButton = document.createElement('button');
  removeButton.type = 'button';
  removeButton.className = 'cond-trigger-remove';
  removeButton.textContent = 'Remove';
  removeButton.addEventListener('click', () => {
    row.remove();
  });

  row.appendChild(select);
  row.appendChild(removeButton);
  container.appendChild(row);
}

function _buildConditionPayload() {
  const name = document.getElementById('cond-name').value.trim();
  const rootMode = document.getElementById('cond-root-mode').value;
  const groups = Array.from(document.querySelectorAll('.cond-group'));
  const actionValue = document.getElementById('cond-action').value;

  if (!name) {
    throw new Error('Enter a condition name.');
  }
  if (groups.length === 0) {
    throw new Error('Add at least one group.');
  }

  const children = groups.map(group => {
    const modeSelect = group.querySelector('.cond-group-mode');
    const rows = Array.from(group.querySelectorAll('.cond-trigger-select'));
    if (rows.length === 0) {
      throw new Error('Each group must contain at least one trigger.');
    }
    return {
      type: modeSelect && modeSelect.value === 'and' ? 'and' : 'or',
      children: rows.map(select => {
        const option = _triggerOptions[parseInt(select.value, 10)];
        if (!option) {
          throw new Error('Invalid trigger selection.');
        }
        return {
          type: 'leaf',
          register: option.register,
          value: option.value,
          label: option.label,
        };
      }),
    };
  });

  const [actionReg, actionVal] = actionValue.split(':').map(Number);
  if (Number.isNaN(actionReg) || Number.isNaN(actionVal)) {
    throw new Error('Invalid action selection.');
  }

  return {
    name,
    enabled: true,
    trigger: {
      type: rootMode === 'and' ? 'and' : 'or',
      children,
    },
    action_register: actionReg,
    action_value: actionVal,
  };
}

async function _createConditionFromBuilder() {
  try {
    const payload = _buildConditionPayload();
    const res = await window.pywebview.api.save_condition(payload);
    if (!res || !res.ok) {
      _log('ERROR: ' + (res ? res.error : 'Failed to save condition'));
      return;
    }
    _log(`Condition created: ${payload.name}`);
    _refreshConditionList();
  } catch (e) {
    _log('ERROR: ' + e.message);
  }
}

async function _refreshConditionList() {
  try {
    const files = await window.pywebview.api.list_condition_files();
    const tbody = document.getElementById('cond-tbody');
    tbody.innerHTML = '';
    files.forEach(_appendConditionRow);
  } catch (e) {
    _log('ERROR: Failed to refresh conditions: ' + e);
  }
}

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
  const resizer = document.getElementById('row-resizer');
  const main = document.getElementById('main');
  if (!resizer || !main) return;

  let isDragging = false;
  let startY = 0;
  let startHeight = 0;

  resizer.addEventListener('pointerdown', e => {
    isDragging = true;
    startY = e.clientY;
    const topPanel = document.getElementById('left-panel');
    startHeight = topPanel ? topPanel.getBoundingClientRect().height : main.getBoundingClientRect().height / 2;
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
    resizer.setPointerCapture(e.pointerId);
  });

  resizer.addEventListener('pointermove', e => {
    if (!isDragging) return;
    const delta = e.clientY - startY;
    const containerHeight = main.clientHeight;
    const minHeight = 200;
    const maxHeight = Math.max(containerHeight - 180, minHeight);
    const newHeight = Math.min(Math.max(startHeight + delta, minHeight), maxHeight);
    document.documentElement.style.setProperty('--top-row-height', `${newHeight}px`);
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

function _initLogToggle() {
  const button = document.getElementById('btn-toggle-log');
  const logBar = document.getElementById('log-bar');
  const logResizer = document.getElementById('log-resizer');
  if (!button || !logBar) return;

  const updateLabel = () => {
    const collapsed = logBar.classList.contains('log-collapsed');
    button.textContent = collapsed ? 'Show' : 'Hide';
    if (logResizer) {
      logResizer.style.display = collapsed ? 'none' : 'block';
    }
  };

  button.addEventListener('click', () => {
    logBar.classList.toggle('log-collapsed');
    updateLabel();
  });

  updateLabel();
}

function _initLogResizer() {
  const resizer = document.getElementById('log-resizer');
  const logBar = document.getElementById('log-bar');
  if (!resizer || !logBar) return;

  let isDragging = false;
  let startY = 0;
  let startHeight = 0;

  resizer.addEventListener('pointerdown', e => {
    isDragging = true;
    startY = e.clientY;
    startHeight = logBar.getBoundingClientRect().height;
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
    resizer.setPointerCapture(e.pointerId);
    if (logBar.classList.contains('log-collapsed')) {
      logBar.classList.remove('log-collapsed');
    }
  });

  resizer.addEventListener('pointermove', e => {
    if (!isDragging) return;
    const delta = startY - e.clientY;
    const newHeight = Math.max(120, startHeight + delta);
    const maxHeight = Math.max(window.innerHeight - 200, 160);
    document.documentElement.style.setProperty('--log-height', `${Math.min(newHeight, maxHeight)}px`);
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

_initPanelResizer();
_initRowResizer();
_initLogToggle();
_initLogResizer();

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
function _appendConditionRow(entry) {
  const tbody = document.getElementById('cond-tbody');
  const tr = document.createElement('tr');
  tr.dataset.filename = entry.filename;

  const tdToggle = document.createElement('td');
  tdToggle.style.textAlign = 'center';
  const lbl = document.createElement('label');
  lbl.className = 'toggle';
  lbl.style.cssText = 'width:32px;height:18px;display:inline-block';
  const cb = document.createElement('input');
  cb.type = 'checkbox'; cb.checked = entry.enabled;
  cb.addEventListener('change', async () => {
    const fn = entry.filename;
    const res = cb.checked
      ? await window.pywebview.api.enable_condition_file(fn)
      : await window.pywebview.api.disable_condition_file(fn);
    if (res && !res.ok) { _log('ERROR: ' + res.error); cb.checked = !cb.checked; }
  });
  const sliderSpan = document.createElement('span');
  sliderSpan.className = 'slider';
  lbl.appendChild(cb); lbl.appendChild(sliderSpan);
  tdToggle.appendChild(lbl);
  tr.appendChild(tdToggle);

  tr.insertAdjacentHTML('beforeend', `
    <td>${_esc(entry.filename)}</td>
    <td>${_esc(entry.name)}</td>
    <td style="color:var(--text-dim);font-size:11px">${_esc(entry.trigger_desc)}</td>
    <td style="color:var(--text-dim);font-size:11px">${_esc(entry.action_text)}</td>
  `);

  const tdDelete = document.createElement('td');
  tdDelete.style.textAlign = 'center';
  const delButton = document.createElement('button');
  delButton.type = 'button';
  delButton.textContent = 'Delete';
  delButton.addEventListener('click', async e => {
    e.stopPropagation();
    const res = await window.pywebview.api.delete_condition_file(entry.filename);
    if (res && res.ok) {
      tr.remove();
      _log(`Condition deleted: ${entry.filename}`);
    } else {
      _log('ERROR: ' + (res ? res.error : 'Unknown'));
    }
  });
  tdDelete.appendChild(delButton);
  tr.appendChild(tdDelete);

  tr.addEventListener('click', e => {
    if (e.target.type === 'checkbox' || e.target === delButton) return;
    document.querySelectorAll('#cond-tbody tr').forEach(r => r.classList.remove('selected'));
    tr.classList.add('selected');
  });
  tbody.appendChild(tr);
}

function _selectedCondFilename() {
  const sel = document.querySelector('#cond-tbody tr.selected');
  return sel ? sel.dataset.filename : null;
}

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
