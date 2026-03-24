import threading
import queue
import json
from pathlib import Path

from protocol import REGISTER_NAMES


# ── Trigger tree nodes ────────────────────────────────────────────────

class TriggerLeaf:
    """Matches when a register equals a specific value."""

    def __init__(self, register, value, label=""):
        self.register = register
        self.value = value
        self.label = label

    def evaluate(self, state):
        return state.get(self.register) == self.value

    def describe(self):
        return self.label or f"{REGISTER_NAMES.get(self.register, '?')} = 0x{self.value:02X}"

    def to_dict(self):
        return {"type": "leaf", "register": self.register, "value": self.value, "label": self.label}


class TriggerAnd:
    """True when ALL children are true."""

    def __init__(self, children=None):
        self.children = children or []

    def evaluate(self, state):
        return all(c.evaluate(state) for c in self.children) if self.children else False

    def describe(self):
        parts = [c.describe() for c in self.children]
        return "(" + " AND ".join(parts) + ")"

    def to_dict(self):
        return {"type": "and", "children": [c.to_dict() for c in self.children]}


class TriggerOr:
    """True when ANY child is true."""

    def __init__(self, children=None):
        self.children = children or []

    def evaluate(self, state):
        return any(c.evaluate(state) for c in self.children) if self.children else False

    def describe(self):
        parts = [c.describe() for c in self.children]
        return "(" + " OR ".join(parts) + ")"

    def to_dict(self):
        return {"type": "or", "children": [c.to_dict() for c in self.children]}


class TriggerNot:
    """Negates a single child."""

    def __init__(self, child=None):
        self.child = child

    def evaluate(self, state):
        return not self.child.evaluate(state) if self.child else False

    def describe(self):
        return f"NOT ({self.child.describe()})" if self.child else "NOT (?)"

    def to_dict(self):
        return {"type": "not", "child": self.child.to_dict() if self.child else None}


def trigger_from_dict(d):
    """Reconstruct a trigger node from a dict."""
    t = d["type"]
    if t == "leaf":
        return TriggerLeaf(d["register"], d["value"], d.get("label", ""))
    if t == "and":
        return TriggerAnd([trigger_from_dict(c) for c in d.get("children", [])])
    if t == "or":
        return TriggerOr([trigger_from_dict(c) for c in d.get("children", [])])
    if t == "not":
        child = trigger_from_dict(d["child"]) if d.get("child") else None
        return TriggerNot(child)
    raise ValueError(f"Unknown trigger type: {t}")


# ── Condition ─────────────────────────────────────────────────────────

class Condition:
    def __init__(self, name, trigger, action_register, action_value, enabled=True):
        self.name = name
        self.trigger = trigger          # TriggerLeaf | TriggerAnd | TriggerOr | TriggerNot
        self.action_register = action_register
        self.action_value = action_value
        self.enabled = enabled
        self._was_true = False          # for rising-edge detection

    def to_dict(self):
        return {
            "name": self.name,
            "trigger": self.trigger.to_dict(),
            "action_register": self.action_register,
            "action_value": self.action_value,
            "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(d):
        return Condition(
            name=d["name"],
            trigger=trigger_from_dict(d["trigger"]),
            action_register=d["action_register"],
            action_value=d["action_value"],
            enabled=d.get("enabled", True),
        )


class ConditionEngine:
    """Evaluates composite conditions against device state, firing on rising edge."""

    def __init__(self, send_command):
        self._conditions = []
        self._event_queue = queue.Queue()
        self._send_command = send_command
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._action_callbacks = []
        self._state = {}

    def on_action(self, cb):
        self._action_callbacks.append(cb)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._event_queue.put(None)
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def add_condition(self, condition):
        with self._lock:
            self._conditions.append(condition)

    def remove_condition(self, index):
        with self._lock:
            if 0 <= index < len(self._conditions):
                self._conditions.pop(index)

    def toggle_condition(self, index):
        with self._lock:
            if 0 <= index < len(self._conditions):
                c = self._conditions[index]
                c.enabled = not c.enabled
                if not c.enabled:
                    c._was_true = False

    def get_conditions(self):
        with self._lock:
            return list(self._conditions)

    def push_event(self, register, value):
        self._event_queue.put((register, value))

    def save(self, path):
        """Persist all conditions to a JSON file."""
        with self._lock:
            data = [c.to_dict() for c in self._conditions]
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")  # type: ignore[call-overload]

    def load(self, path):
        """Restore conditions from a JSON file. Returns the loaded conditions."""
        p = Path(path)
        if not p.is_file():
            return []
        data = json.loads(p.read_text(encoding="utf-8"))
        conditions = [Condition.from_dict(d) for d in data]
        with self._lock:
            self._conditions = conditions
        return conditions

    def _run(self):
        while self._running:
            try:
                item = self._event_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                break

            register, value = item
            with self._lock:
                self._state[register] = value
                for cond in self._conditions:
                    if not cond.enabled:
                        continue
                    now_true = cond.trigger.evaluate(self._state)
                    if now_true and not cond._was_true:
                        try:
                            self._send_command(cond.action_register, cond.action_value)
                            for cb in self._action_callbacks:
                                cb(cond)
                        except Exception:
                            pass
                    cond._was_true = now_true
