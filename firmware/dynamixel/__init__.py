from .dynamixel import Dynamixel
from .model import DynamixelModel


# dynamixel/__init__.py
_attrs = {
    "DynamixelPacket": "packet",
    "DynamixelRXPacket": "packet",
    "DynamixelTXPacket": "packet",
    "Dynamixel": "dynamixel",
    "TimeoutError": "dynamixel",
    "DynamixelModel": "model",
    "ControlTableItem": "table",
    "get_control_table": "table",
    "CRC": "crc",
}


def __getattr__(attr):
    if attr in _attrs:
        module_name = _attrs[attr]
        module = __import__(f"dynamixel.{module_name}", fromlist=[attr])
        return getattr(module, attr)
    raise AttributeError(f"module 'dynamixel' has no attribute '{attr}'")
