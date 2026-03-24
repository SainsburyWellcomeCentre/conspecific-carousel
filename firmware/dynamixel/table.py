"""
Dynamixel Control Table Definitions for MicroPython
Converted from C/C++ Arduino library
"""

from .model import DynamixelModel


# Control Table Item Constants
class ControlTableItem:
    MODEL_NUMBER = 0
    MODEL_INFORMATION = 1
    FIRMWARE_VERSION = 2
    PROTOCOL_VERSION = 3
    ID = 4
    SECONDARY_ID = 5
    BAUD_RATE = 6
    DRIVE_MODE = 7
    CONTROL_MODE = 8
    OPERATING_MODE = 9
    CW_ANGLE_LIMIT = 10
    CCW_ANGLE_LIMIT = 11
    TEMPERATURE_LIMIT = 12
    MIN_VOLTAGE_LIMIT = 13
    MAX_VOLTAGE_LIMIT = 14
    PWM_LIMIT = 15
    CURRENT_LIMIT = 16
    VELOCITY_LIMIT = 17
    MAX_POSITION_LIMIT = 18
    MIN_POSITION_LIMIT = 19
    ACCELERATION_LIMIT = 20
    MAX_TORQUE = 21
    HOMING_OFFSET = 22
    MOVING_THRESHOLD = 23
    MULTI_TURN_OFFSET = 24
    RESOLUTION_DIVIDER = 25
    EXTERNAL_PORT_MODE_1 = 26
    EXTERNAL_PORT_MODE_2 = 27
    EXTERNAL_PORT_MODE_3 = 28
    EXTERNAL_PORT_MODE_4 = 29
    STATUS_RETURN_LEVEL = 30
    RETURN_DELAY_TIME = 31
    ALARM_LED = 32
    SHUTDOWN = 33
    TORQUE_ENABLE = 34
    DXL_LED = 35
    DXL_LED_RED = 36
    DXL_LED_GREEN = 37
    DXL_LED_BLUE = 38
    REGISTERED_INSTRUCTION = 39
    HARDWARE_ERROR_STATUS = 40
    VELOCITY_P_GAIN = 41
    VELOCITY_I_GAIN = 42
    POSITION_P_GAIN = 43
    POSITION_I_GAIN = 44
    POSITION_D_GAIN = 45
    FEEDFORWARD_1ST_GAIN = 46
    FEEDFORWARD_2ND_GAIN = 47
    P_GAIN = 48
    I_GAIN = 49
    D_GAIN = 50
    CW_COMPLIANCE_MARGIN = 51
    CCW_COMPLIANCE_MARGIN = 52
    CW_COMPLIANCE_SLOPE = 53
    CCW_COMPLIANCE_SLOPE = 54
    GOAL_PWM = 55
    GOAL_TORQUE = 56
    GOAL_CURRENT = 57
    GOAL_POSITION = 58
    GOAL_VELOCITY = 59
    GOAL_ACCELERATION = 60
    MOVING_SPEED = 61
    PRESENT_PWM = 62
    PRESENT_LOAD = 63
    PRESENT_SPEED = 64
    PRESENT_CURRENT = 65
    PRESENT_POSITION = 66
    PRESENT_VELOCITY = 67
    PRESENT_VOLTAGE = 68
    PRESENT_TEMPERATURE = 69
    TORQUE_LIMIT = 70
    REGISTERED = 71
    MOVING = 72
    LOCK = 73
    PUNCH = 74
    CURRENT = 75
    SENSED_CURRENT = 76
    REALTIME_TICK = 77
    TORQUE_CTRL_MODE_ENABLE = 78
    BUS_WATCHDOG = 79
    PROFILE_ACCELERATION = 80
    PROFILE_VELOCITY = 81
    MOVING_STATUS = 82
    VELOCITY_TRAJECTORY = 83
    POSITION_TRAJECTORY = 84
    PRESENT_INPUT_VOLTAGE = 85
    EXTERNAL_PORT_DATA_1 = 86
    EXTERNAL_PORT_DATA_2 = 87
    EXTERNAL_PORT_DATA_3 = 88
    EXTERNAL_PORT_DATA_4 = 89
    STARTUP_CONFIGURATION = 90
    POSITION_LIMIT_THRESHOLD = 91
    IN_POSITION_THRESHOLD = 92
    FOLLOWING_ERROR_THRESHOLD = 93
    INVERTER_TEMPERATURE_LIMIT = 94
    MOTOR_TEMPERATURE_LIMIT = 95
    ELECTRONIC_GEAR_RATIO_NUMERATOR = 96
    ELECTRONIC_GEAR_RATIO_DENOMINATOR = 97
    SAFE_STOP_TIME = 98
    BRAKE_DELAY = 99
    GOAL_UPDATE_DELAY = 100
    OVEREXCITATION_VOLTAGE = 101
    NORMAL_EXCITATION_VOLTAGE = 102
    OVEREXCITATION_TIME = 103
    PRESENT_VELOCITY_LPF_FREQUENCY = 104
    GOAL_CURRENT_LPF_FREQUENCY = 105
    POSITION_FF_LPF_TIME = 106
    VELOCITY_FF_LPF_TIME = 107
    CONTROLLER_STATE = 108
    ERROR_CODE = 109
    ERROR_CODE_HISTORY1 = 110
    HYBRID_SAVE = 111
    PROFILE_ACCELERATION_TIME = 112
    PROFILE_TIME = 113
    PWM_OFFSET = 114
    CURRENT_OFFSET = 115
    VELOCITY_OFFSET = 116
    PRESENT_MOTOR_TEMPERATURE = 117


CONTROL_TABLE_1_0 = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 2, "length": 1},
    ControlTableItem.ID: {"addr": 3, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 4, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 5, "length": 1},
    ControlTableItem.CW_ANGLE_LIMIT: {"addr": 6, "length": 2},
    ControlTableItem.CCW_ANGLE_LIMIT: {"addr": 8, "length": 2},
    ControlTableItem.TEMPERATURE_LIMIT: {"addr": 11, "length": 1},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 12, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 13, "length": 1},
    ControlTableItem.MAX_TORQUE: {"addr": 14, "length": 2},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 16, "length": 1},
    ControlTableItem.ALARM_LED: {"addr": 17, "length": 1},
    ControlTableItem.SHUTDOWN: {"addr": 18, "length": 1},
    ControlTableItem.TORQUE_ENABLE: {"addr": 24, "length": 1},
    ControlTableItem.DXL_LED: {"addr": 25, "length": 1},
    ControlTableItem.CW_COMPLIANCE_MARGIN: {"addr": 26, "length": 1},
    ControlTableItem.CCW_COMPLIANCE_MARGIN: {"addr": 27, "length": 1},
    ControlTableItem.CW_COMPLIANCE_SLOPE: {"addr": 28, "length": 1},
    ControlTableItem.CCW_COMPLIANCE_SLOPE: {"addr": 29, "length": 1},
    ControlTableItem.GOAL_POSITION: {"addr": 30, "length": 2},
    ControlTableItem.MOVING_SPEED: {"addr": 32, "length": 2},
    ControlTableItem.TORQUE_LIMIT: {"addr": 34, "length": 2},
    ControlTableItem.PRESENT_POSITION: {"addr": 36, "length": 2},
    ControlTableItem.PRESENT_SPEED: {"addr": 38, "length": 2},
    ControlTableItem.PRESENT_LOAD: {"addr": 40, "length": 2},
    ControlTableItem.PRESENT_VOLTAGE: {"addr": 42, "length": 1},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 43, "length": 1},
    ControlTableItem.REGISTERED: {"addr": 44, "length": 1},
    ControlTableItem.MOVING: {"addr": 46, "length": 1},
    ControlTableItem.LOCK: {"addr": 47, "length": 1},
    ControlTableItem.PUNCH: {"addr": 48, "length": 2},
}


EX_CONTROL_TABLE = {
    ControlTableItem.DRIVE_MODE: {"addr": 10, "length": 1},
    ControlTableItem.SENSED_CURRENT: {"addr": 56, "length": 2},
}

CONTROL_TABLE_1_1 = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 2, "length": 1},
    ControlTableItem.ID: {"addr": 3, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 4, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 5, "length": 1},
    ControlTableItem.CW_ANGLE_LIMIT: {"addr": 6, "length": 2},
    ControlTableItem.CCW_ANGLE_LIMIT: {"addr": 8, "length": 2},
    ControlTableItem.TEMPERATURE_LIMIT: {"addr": 11, "length": 1},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 12, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 13, "length": 1},
    ControlTableItem.MAX_TORQUE: {"addr": 14, "length": 2},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 16, "length": 1},
    ControlTableItem.ALARM_LED: {"addr": 17, "length": 1},
    ControlTableItem.SHUTDOWN: {"addr": 18, "length": 1},
    ControlTableItem.MULTI_TURN_OFFSET: {"addr": 20, "length": 2},
    ControlTableItem.RESOLUTION_DIVIDER: {"addr": 22, "length": 1},
    ControlTableItem.TORQUE_ENABLE: {"addr": 24, "length": 1},
    ControlTableItem.DXL_LED: {"addr": 25, "length": 1},
    ControlTableItem.D_GAIN: {"addr": 26, "length": 1},
    ControlTableItem.I_GAIN: {"addr": 27, "length": 1},
    ControlTableItem.P_GAIN: {"addr": 28, "length": 1},
    ControlTableItem.GOAL_POSITION: {"addr": 30, "length": 2},
    ControlTableItem.MOVING_SPEED: {"addr": 32, "length": 2},
    ControlTableItem.TORQUE_LIMIT: {"addr": 34, "length": 2},
    ControlTableItem.PRESENT_POSITION: {"addr": 36, "length": 2},
    ControlTableItem.PRESENT_SPEED: {"addr": 38, "length": 2},
    ControlTableItem.PRESENT_LOAD: {"addr": 40, "length": 2},
    ControlTableItem.PRESENT_VOLTAGE: {"addr": 42, "length": 1},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 43, "length": 1},
    ControlTableItem.REGISTERED: {"addr": 44, "length": 1},
    ControlTableItem.MOVING: {"addr": 46, "length": 1},
    ControlTableItem.LOCK: {"addr": 47, "length": 1},
    ControlTableItem.PUNCH: {"addr": 48, "length": 2},
    ControlTableItem.REALTIME_TICK: {"addr": 50, "length": 2},
    ControlTableItem.GOAL_ACCELERATION: {"addr": 73, "length": 1},
}

MX64_CONTROL_TABLE = {
    ControlTableItem.CURRENT: {"addr": 68, "length": 2},
    ControlTableItem.TORQUE_CTRL_MODE_ENABLE: {"addr": 70, "length": 1},
    ControlTableItem.GOAL_TORQUE: {"addr": 71, "length": 2},
}

MX106_CONTROL_TABLE = {
    ControlTableItem.DRIVE_MODE: {"addr": 10, "length": 1},
    ControlTableItem.CURRENT: {"addr": 68, "length": 2},
    ControlTableItem.TORQUE_CTRL_MODE_ENABLE: {"addr": 70, "length": 1},
    ControlTableItem.GOAL_TORQUE: {"addr": 71, "length": 2},
}

XL320_CONTROL_TABLE = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 2, "length": 1},
    ControlTableItem.ID: {"addr": 3, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 4, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 5, "length": 1},
    ControlTableItem.CW_ANGLE_LIMIT: {"addr": 6, "length": 2},
    ControlTableItem.CCW_ANGLE_LIMIT: {"addr": 8, "length": 2},
    ControlTableItem.CONTROL_MODE: {"addr": 11, "length": 1},
    ControlTableItem.TEMPERATURE_LIMIT: {"addr": 12, "length": 1},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 13, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 14, "length": 1},
    ControlTableItem.MAX_TORQUE: {"addr": 15, "length": 2},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 17, "length": 1},
    ControlTableItem.SHUTDOWN: {"addr": 18, "length": 1},
    ControlTableItem.TORQUE_ENABLE: {"addr": 24, "length": 1},
    ControlTableItem.DXL_LED: {"addr": 25, "length": 1},
    ControlTableItem.D_GAIN: {"addr": 27, "length": 1},
    ControlTableItem.I_GAIN: {"addr": 28, "length": 1},
    ControlTableItem.P_GAIN: {"addr": 29, "length": 1},
    ControlTableItem.GOAL_POSITION: {"addr": 30, "length": 2},
    ControlTableItem.MOVING_SPEED: {"addr": 32, "length": 2},
    ControlTableItem.TORQUE_LIMIT: {"addr": 35, "length": 2},
    ControlTableItem.PRESENT_POSITION: {"addr": 37, "length": 2},
    ControlTableItem.PRESENT_SPEED: {"addr": 39, "length": 2},
    ControlTableItem.PRESENT_LOAD: {"addr": 41, "length": 2},
    ControlTableItem.PRESENT_VOLTAGE: {"addr": 45, "length": 1},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 46, "length": 1},
    ControlTableItem.REGISTERED: {"addr": 47, "length": 1},
    ControlTableItem.MOVING: {"addr": 49, "length": 1},
    ControlTableItem.HARDWARE_ERROR_STATUS: {"addr": 50, "length": 1},
    ControlTableItem.PUNCH: {"addr": 51, "length": 2},
}

CONTROL_TABLE_2_0 = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.MODEL_INFORMATION: {"addr": 2, "length": 4},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 6, "length": 1},
    ControlTableItem.ID: {"addr": 7, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 8, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 9, "length": 1},
    ControlTableItem.DRIVE_MODE: {"addr": 10, "length": 1},
    ControlTableItem.OPERATING_MODE: {"addr": 11, "length": 1},
    ControlTableItem.SECONDARY_ID: {"addr": 12, "length": 1},
    ControlTableItem.PROTOCOL_VERSION: {"addr": 13, "length": 1},
    ControlTableItem.HOMING_OFFSET: {"addr": 20, "length": 4},
    ControlTableItem.MOVING_THRESHOLD: {"addr": 24, "length": 4},
    ControlTableItem.TEMPERATURE_LIMIT: {"addr": 31, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 32, "length": 2},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 34, "length": 2},
    ControlTableItem.PWM_LIMIT: {"addr": 36, "length": 2},
    ControlTableItem.VELOCITY_LIMIT: {"addr": 44, "length": 4},
    ControlTableItem.MAX_POSITION_LIMIT: {"addr": 48, "length": 4},
    ControlTableItem.MIN_POSITION_LIMIT: {"addr": 52, "length": 4},
    ControlTableItem.SHUTDOWN: {"addr": 63, "length": 1},
    ControlTableItem.TORQUE_ENABLE: {"addr": 64, "length": 1},
    ControlTableItem.DXL_LED: {"addr": 65, "length": 1},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 68, "length": 1},
    ControlTableItem.REGISTERED_INSTRUCTION: {"addr": 69, "length": 1},
    ControlTableItem.HARDWARE_ERROR_STATUS: {"addr": 70, "length": 1},
    ControlTableItem.VELOCITY_I_GAIN: {"addr": 76, "length": 2},
    ControlTableItem.VELOCITY_P_GAIN: {"addr": 78, "length": 2},
    ControlTableItem.POSITION_D_GAIN: {"addr": 80, "length": 2},
    ControlTableItem.POSITION_I_GAIN: {"addr": 82, "length": 2},
    ControlTableItem.POSITION_P_GAIN: {"addr": 84, "length": 2},
    ControlTableItem.FEEDFORWARD_2ND_GAIN: {"addr": 88, "length": 2},
    ControlTableItem.FEEDFORWARD_1ST_GAIN: {"addr": 90, "length": 2},
    ControlTableItem.BUS_WATCHDOG: {"addr": 98, "length": 2},
    ControlTableItem.GOAL_PWM: {"addr": 100, "length": 2},
    ControlTableItem.GOAL_VELOCITY: {"addr": 104, "length": 4},
    ControlTableItem.PROFILE_ACCELERATION: {"addr": 108, "length": 4},
    ControlTableItem.PROFILE_VELOCITY: {"addr": 112, "length": 4},
    ControlTableItem.GOAL_POSITION: {"addr": 116, "length": 4},
    ControlTableItem.REALTIME_TICK: {"addr": 120, "length": 2},
    ControlTableItem.MOVING: {"addr": 122, "length": 1},
    ControlTableItem.MOVING_STATUS: {"addr": 123, "length": 1},
    ControlTableItem.PRESENT_PWM: {"addr": 124, "length": 2},
    ControlTableItem.PRESENT_VELOCITY: {"addr": 128, "length": 4},
    ControlTableItem.PRESENT_POSITION: {"addr": 132, "length": 4},
    ControlTableItem.VELOCITY_TRAJECTORY: {"addr": 136, "length": 4},
    ControlTableItem.POSITION_TRAJECTORY: {"addr": 140, "length": 4},
    ControlTableItem.PRESENT_INPUT_VOLTAGE: {"addr": 144, "length": 2},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 146, "length": 1},
}

MX28_2_CONTROL_TABLE = {
    ControlTableItem.ACCELERATION_LIMIT: {"addr": 40, "length": 4},
    ControlTableItem.PRESENT_LOAD: {"addr": 126, "length": 2},
}

MX64_106_2_CONTROL_TABLE = {
    ControlTableItem.CURRENT_LIMIT: {"addr": 38, "length": 2},
    ControlTableItem.ACCELERATION_LIMIT: {"addr": 40, "length": 4},
    ControlTableItem.GOAL_CURRENT: {"addr": 102, "length": 2},
    ControlTableItem.PRESENT_CURRENT: {"addr": 126, "length": 2},
}

XC430_XL430_CONTROL_TABLE = {
    ControlTableItem.PRESENT_LOAD: {"addr": 126, "length": 2},
}

XMH430_XL330_CONTROL_TABLE = {
    ControlTableItem.CURRENT_LIMIT: {"addr": 38, "length": 2},
    ControlTableItem.GOAL_CURRENT: {"addr": 102, "length": 2},
    ControlTableItem.PRESENT_CURRENT: {"addr": 126, "length": 2},
}

XMH540_CONTROL_TABLE = {
    ControlTableItem.CURRENT_LIMIT: {"addr": 38, "length": 2},
    ControlTableItem.EXTERNAL_PORT_MODE_1: {"addr": 56, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_2: {"addr": 57, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_3: {"addr": 58, "length": 1},
    ControlTableItem.GOAL_CURRENT: {"addr": 102, "length": 2},
    ControlTableItem.PRESENT_CURRENT: {"addr": 126, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_1: {"addr": 152, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_2: {"addr": 154, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_3: {"addr": 156, "length": 2},
}

XW430_540_CONTROL_TABLE = {
    ControlTableItem.CURRENT_LIMIT: {"addr": 38, "length": 2},
    ControlTableItem.GOAL_CURRENT: {"addr": 102, "length": 2},
    ControlTableItem.PRESENT_CURRENT: {"addr": 126, "length": 2},
}

PRO_R_CONTROL_TABLE = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.MODEL_INFORMATION: {"addr": 2, "length": 4},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 6, "length": 1},
    ControlTableItem.ID: {"addr": 7, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 8, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 9, "length": 1},
    ControlTableItem.OPERATING_MODE: {"addr": 11, "length": 1},
    ControlTableItem.HOMING_OFFSET: {"addr": 13, "length": 4},
    ControlTableItem.MOVING_THRESHOLD: {"addr": 17, "length": 4},
    ControlTableItem.TEMPERATURE_LIMIT: {"addr": 21, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 22, "length": 2},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 24, "length": 2},
    ControlTableItem.ACCELERATION_LIMIT: {"addr": 26, "length": 4},
    ControlTableItem.TORQUE_LIMIT: {"addr": 30, "length": 2},
    ControlTableItem.VELOCITY_LIMIT: {"addr": 32, "length": 4},
    ControlTableItem.MAX_POSITION_LIMIT: {"addr": 36, "length": 4},
    ControlTableItem.MIN_POSITION_LIMIT: {"addr": 40, "length": 4},
    ControlTableItem.EXTERNAL_PORT_MODE_1: {"addr": 44, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_2: {"addr": 45, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_3: {"addr": 46, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_4: {"addr": 47, "length": 1},
    ControlTableItem.SHUTDOWN: {"addr": 48, "length": 1},
    ControlTableItem.TORQUE_ENABLE: {"addr": 562, "length": 1},
    ControlTableItem.DXL_LED_RED: {"addr": 563, "length": 1},
    ControlTableItem.DXL_LED_GREEN: {"addr": 564, "length": 1},
    ControlTableItem.DXL_LED_BLUE: {"addr": 565, "length": 1},
    ControlTableItem.VELOCITY_I_GAIN: {"addr": 586, "length": 2},
    ControlTableItem.VELOCITY_P_GAIN: {"addr": 588, "length": 2},
    ControlTableItem.POSITION_P_GAIN: {"addr": 594, "length": 2},
    ControlTableItem.GOAL_POSITION: {"addr": 596, "length": 4},
    ControlTableItem.GOAL_VELOCITY: {"addr": 600, "length": 4},
    ControlTableItem.GOAL_TORQUE: {"addr": 604, "length": 2},
    ControlTableItem.GOAL_ACCELERATION: {"addr": 606, "length": 4},
    ControlTableItem.MOVING: {"addr": 610, "length": 1},
    ControlTableItem.PRESENT_POSITION: {"addr": 611, "length": 4},
    ControlTableItem.PRESENT_VELOCITY: {"addr": 615, "length": 4},
    ControlTableItem.PRESENT_CURRENT: {"addr": 621, "length": 2},
    ControlTableItem.PRESENT_INPUT_VOLTAGE: {"addr": 623, "length": 2},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 625, "length": 1},
    ControlTableItem.EXTERNAL_PORT_DATA_1: {"addr": 626, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_2: {"addr": 628, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_3: {"addr": 630, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_4: {"addr": 632, "length": 2},
    ControlTableItem.REGISTERED_INSTRUCTION: {"addr": 890, "length": 1},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 891, "length": 1},
    ControlTableItem.HARDWARE_ERROR_STATUS: {"addr": 892, "length": 1},
}

PRO_RA_PRO_PLUS_CONTROL_TABLE = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.MODEL_INFORMATION: {"addr": 2, "length": 4},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 6, "length": 1},
    ControlTableItem.ID: {"addr": 7, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 8, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 9, "length": 1},
    ControlTableItem.DRIVE_MODE: {"addr": 10, "length": 1},
    ControlTableItem.OPERATING_MODE: {"addr": 11, "length": 1},
    ControlTableItem.SECONDARY_ID: {"addr": 12, "length": 1},
    ControlTableItem.HOMING_OFFSET: {"addr": 20, "length": 4},
    ControlTableItem.MOVING_THRESHOLD: {"addr": 24, "length": 4},
    ControlTableItem.TEMPERATURE_LIMIT: {"addr": 31, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 32, "length": 2},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 34, "length": 2},
    ControlTableItem.PWM_LIMIT: {"addr": 36, "length": 2},
    ControlTableItem.CURRENT_LIMIT: {"addr": 38, "length": 2},
    ControlTableItem.ACCELERATION_LIMIT: {"addr": 40, "length": 4},
    ControlTableItem.VELOCITY_LIMIT: {"addr": 44, "length": 4},
    ControlTableItem.MAX_POSITION_LIMIT: {"addr": 48, "length": 4},
    ControlTableItem.MIN_POSITION_LIMIT: {"addr": 52, "length": 4},
    ControlTableItem.EXTERNAL_PORT_MODE_1: {"addr": 56, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_2: {"addr": 57, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_3: {"addr": 58, "length": 1},
    ControlTableItem.EXTERNAL_PORT_MODE_4: {"addr": 59, "length": 1},
    ControlTableItem.SHUTDOWN: {"addr": 63, "length": 1},
    ControlTableItem.TORQUE_ENABLE: {"addr": 512, "length": 1},
    ControlTableItem.DXL_LED_RED: {"addr": 513, "length": 1},
    ControlTableItem.DXL_LED_GREEN: {"addr": 514, "length": 1},
    ControlTableItem.DXL_LED_BLUE: {"addr": 515, "length": 1},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 516, "length": 1},
    ControlTableItem.REGISTERED_INSTRUCTION: {"addr": 517, "length": 1},
    ControlTableItem.HARDWARE_ERROR_STATUS: {"addr": 518, "length": 1},
    ControlTableItem.VELOCITY_I_GAIN: {"addr": 524, "length": 2},
    ControlTableItem.VELOCITY_P_GAIN: {"addr": 526, "length": 2},
    ControlTableItem.POSITION_D_GAIN: {"addr": 528, "length": 2},
    ControlTableItem.POSITION_I_GAIN: {"addr": 530, "length": 2},
    ControlTableItem.POSITION_P_GAIN: {"addr": 532, "length": 2},
    ControlTableItem.FEEDFORWARD_2ND_GAIN: {"addr": 536, "length": 2},
    ControlTableItem.FEEDFORWARD_1ST_GAIN: {"addr": 538, "length": 2},
    ControlTableItem.BUS_WATCHDOG: {"addr": 546, "length": 2},
    ControlTableItem.GOAL_PWM: {"addr": 548, "length": 2},
    ControlTableItem.GOAL_CURRENT: {"addr": 550, "length": 2},
    ControlTableItem.GOAL_VELOCITY: {"addr": 552, "length": 4},
    ControlTableItem.PROFILE_ACCELERATION: {"addr": 556, "length": 4},
    ControlTableItem.PROFILE_VELOCITY: {"addr": 560, "length": 4},
    ControlTableItem.GOAL_POSITION: {"addr": 564, "length": 4},
    ControlTableItem.REALTIME_TICK: {"addr": 568, "length": 2},
    ControlTableItem.MOVING: {"addr": 570, "length": 1},
    ControlTableItem.MOVING_STATUS: {"addr": 571, "length": 1},
    ControlTableItem.PRESENT_PWM: {"addr": 572, "length": 2},
    ControlTableItem.PRESENT_CURRENT: {"addr": 574, "length": 2},
    ControlTableItem.PRESENT_VELOCITY: {"addr": 576, "length": 4},
    ControlTableItem.PRESENT_POSITION: {"addr": 580, "length": 4},
    ControlTableItem.VELOCITY_TRAJECTORY: {"addr": 584, "length": 4},
    ControlTableItem.POSITION_TRAJECTORY: {"addr": 588, "length": 4},
    ControlTableItem.PRESENT_INPUT_VOLTAGE: {"addr": 592, "length": 2},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 594, "length": 1},
    ControlTableItem.EXTERNAL_PORT_DATA_1: {"addr": 600, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_2: {"addr": 602, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_3: {"addr": 604, "length": 2},
    ControlTableItem.EXTERNAL_PORT_DATA_4: {"addr": 606, "length": 2},
}


Y_CONTROL_TABLE = {
    ControlTableItem.MODEL_NUMBER: {"addr": 0, "length": 2},
    ControlTableItem.MODEL_INFORMATION: {"addr": 2, "length": 4},
    ControlTableItem.FIRMWARE_VERSION: {"addr": 6, "length": 1},
    ControlTableItem.ID: {"addr": 7, "length": 1},
    ControlTableItem.BUS_WATCHDOG: {"addr": 8, "length": 2},
    ControlTableItem.SECONDARY_ID: {"addr": 10, "length": 1},
    ControlTableItem.BAUD_RATE: {"addr": 12, "length": 1},
    ControlTableItem.RETURN_DELAY_TIME: {"addr": 13, "length": 1},
    ControlTableItem.STATUS_RETURN_LEVEL: {"addr": 15, "length": 1},
    ControlTableItem.REGISTERED_INSTRUCTION: {"addr": 16, "length": 1},
    ControlTableItem.DRIVE_MODE: {"addr": 32, "length": 1},
    ControlTableItem.OPERATING_MODE: {"addr": 33, "length": 1},
    ControlTableItem.STARTUP_CONFIGURATION: {"addr": 34, "length": 1},
    ControlTableItem.POSITION_LIMIT_THRESHOLD: {"addr": 38, "length": 2},
    ControlTableItem.IN_POSITION_THRESHOLD: {"addr": 40, "length": 4},
    ControlTableItem.FOLLOWING_ERROR_THRESHOLD: {"addr": 44, "length": 4},
    ControlTableItem.MOVING_THRESHOLD: {"addr": 48, "length": 4},
    ControlTableItem.HOMING_OFFSET: {"addr": 52, "length": 4},
    ControlTableItem.INVERTER_TEMPERATURE_LIMIT: {"addr": 56, "length": 1},
    ControlTableItem.MOTOR_TEMPERATURE_LIMIT: {"addr": 57, "length": 1},
    ControlTableItem.MAX_VOLTAGE_LIMIT: {"addr": 60, "length": 2},
    ControlTableItem.MIN_VOLTAGE_LIMIT: {"addr": 62, "length": 2},
    ControlTableItem.PWM_LIMIT: {"addr": 64, "length": 2},
    ControlTableItem.CURRENT_LIMIT: {"addr": 66, "length": 2},
    ControlTableItem.ACCELERATION_LIMIT: {"addr": 68, "length": 4},
    ControlTableItem.VELOCITY_LIMIT: {"addr": 72, "length": 4},
    ControlTableItem.MAX_POSITION_LIMIT: {"addr": 76, "length": 4},
    ControlTableItem.MIN_POSITION_LIMIT: {"addr": 84, "length": 4},
    ControlTableItem.ELECTRONIC_GEAR_RATIO_NUMERATOR: {"addr": 96, "length": 4},
    ControlTableItem.ELECTRONIC_GEAR_RATIO_DENOMINATOR: {"addr": 100, "length": 4},
    ControlTableItem.SAFE_STOP_TIME: {"addr": 104, "length": 2},
    ControlTableItem.BRAKE_DELAY: {"addr": 106, "length": 2},
    ControlTableItem.GOAL_UPDATE_DELAY: {"addr": 108, "length": 2},
    ControlTableItem.OVEREXCITATION_VOLTAGE: {"addr": 110, "length": 1},
    ControlTableItem.NORMAL_EXCITATION_VOLTAGE: {"addr": 111, "length": 1},
    ControlTableItem.OVEREXCITATION_TIME: {"addr": 112, "length": 2},
    ControlTableItem.PRESENT_VELOCITY_LPF_FREQUENCY: {"addr": 132, "length": 2},
    ControlTableItem.GOAL_CURRENT_LPF_FREQUENCY: {"addr": 134, "length": 2},
    ControlTableItem.POSITION_FF_LPF_TIME: {"addr": 136, "length": 2},
    ControlTableItem.VELOCITY_FF_LPF_TIME: {"addr": 138, "length": 2},
    ControlTableItem.CONTROLLER_STATE: {"addr": 152, "length": 1},
    ControlTableItem.ERROR_CODE: {"addr": 153, "length": 1},
    ControlTableItem.ERROR_CODE_HISTORY1: {"addr": 154, "length": 1},
    ControlTableItem.HYBRID_SAVE: {"addr": 170, "length": 1},
    ControlTableItem.VELOCITY_I_GAIN: {"addr": 212, "length": 4},
    ControlTableItem.VELOCITY_P_GAIN: {"addr": 216, "length": 4},
    ControlTableItem.FEEDFORWARD_2ND_GAIN: {"addr": 220, "length": 4},
    ControlTableItem.POSITION_D_GAIN: {"addr": 224, "length": 4},
    ControlTableItem.POSITION_I_GAIN: {"addr": 228, "length": 4},
    ControlTableItem.POSITION_P_GAIN: {"addr": 232, "length": 4},
    ControlTableItem.FEEDFORWARD_1ST_GAIN: {"addr": 236, "length": 4},
    ControlTableItem.PROFILE_ACCELERATION: {"addr": 240, "length": 4},
    ControlTableItem.PROFILE_VELOCITY: {"addr": 244, "length": 4},
    ControlTableItem.PROFILE_ACCELERATION_TIME: {"addr": 248, "length": 4},
    ControlTableItem.PROFILE_TIME: {"addr": 252, "length": 4},
    ControlTableItem.TORQUE_ENABLE: {"addr": 512, "length": 1},
    ControlTableItem.DXL_LED: {"addr": 513, "length": 1},
    ControlTableItem.PWM_OFFSET: {"addr": 516, "length": 2},
    ControlTableItem.CURRENT_OFFSET: {"addr": 518, "length": 2},
    ControlTableItem.VELOCITY_OFFSET: {"addr": 520, "length": 4},
    ControlTableItem.GOAL_PWM: {"addr": 524, "length": 2},
    ControlTableItem.GOAL_CURRENT: {"addr": 526, "length": 2},
    ControlTableItem.GOAL_VELOCITY: {"addr": 528, "length": 4},
    ControlTableItem.GOAL_POSITION: {"addr": 532, "length": 4},
    ControlTableItem.MOVING_STATUS: {"addr": 541, "length": 1},
    ControlTableItem.REALTIME_TICK: {"addr": 542, "length": 2},
    ControlTableItem.PRESENT_PWM: {"addr": 544, "length": 2},
    ControlTableItem.PRESENT_CURRENT: {"addr": 546, "length": 2},
    ControlTableItem.PRESENT_VELOCITY: {"addr": 548, "length": 4},
    ControlTableItem.PRESENT_POSITION: {"addr": 552, "length": 4},
    ControlTableItem.POSITION_TRAJECTORY: {"addr": 560, "length": 4},
    ControlTableItem.VELOCITY_TRAJECTORY: {"addr": 564, "length": 4},
    ControlTableItem.PRESENT_INPUT_VOLTAGE: {"addr": 568, "length": 2},
    ControlTableItem.PRESENT_TEMPERATURE: {"addr": 570, "length": 1},
    ControlTableItem.PRESENT_MOTOR_TEMPERATURE: {"addr": 571, "length": 1},
}


def get_control_table(model_num: int) -> dict[int, dict[str, int]]:
    """
    Get control table item information for a specific Dynamixel model

    Args,
        Dynamixel model number

    Returns,
        ControlTable dict with address and length
    """

    # Select appropriate control table based on model number
    if model_num in [
        DynamixelModel.AX12A,
        DynamixelModel.AX12W,
        DynamixelModel.AX18A,
        DynamixelModel.DX113,
        DynamixelModel.DX116,
        DynamixelModel.DX117,
        DynamixelModel.RX10,
        DynamixelModel.RX24F,
        DynamixelModel.RX28,
        DynamixelModel.RX64,
    ]:
        return CONTROL_TABLE_1_0

    elif model_num == DynamixelModel.EX106:
        return CONTROL_TABLE_1_0 | EX_CONTROL_TABLE

    elif model_num in [DynamixelModel.MX12W, DynamixelModel.MX28]:
        return CONTROL_TABLE_1_1

    elif model_num == DynamixelModel.MX64:
        return CONTROL_TABLE_1_1 | MX64_CONTROL_TABLE

    elif model_num == DynamixelModel.MX106:
        return CONTROL_TABLE_1_1 | MX106_CONTROL_TABLE

    elif model_num == DynamixelModel.MX28_2:
        return CONTROL_TABLE_2_0 | MX28_2_CONTROL_TABLE

    elif model_num in [DynamixelModel.MX64_2, DynamixelModel.MX106_2]:
        return CONTROL_TABLE_2_0

    elif model_num == DynamixelModel.XL320:
        return XL320_CONTROL_TABLE

    elif model_num in [
        DynamixelModel.XC430_W150,
        DynamixelModel.XC430_W240,
        DynamixelModel.XL430_W250,
        DynamixelModel.XXL430_W250,
        DynamixelModel.XXC430_W250,
    ]:
        return CONTROL_TABLE_2_0 | XC430_XL430_CONTROL_TABLE

    elif model_num in [
        DynamixelModel.XL330_M288,
        DynamixelModel.XL330_M077,
        DynamixelModel.XC330_M181,
        DynamixelModel.XC330_M288,
        DynamixelModel.XC330_T181,
        DynamixelModel.XC330_T288,
        DynamixelModel.XM430_W210,
        DynamixelModel.XM430_W350,
        DynamixelModel.XH430_V210,
        DynamixelModel.XH430_V350,
        DynamixelModel.XH430_W210,
        DynamixelModel.XH430_W350,
        DynamixelModel.XD430_T210,
        DynamixelModel.XD430_T350,
    ]:
        return CONTROL_TABLE_2_0 | XMH430_XL330_CONTROL_TABLE

    elif model_num in [
        DynamixelModel.XM540_W150,
        DynamixelModel.XM540_W270,
        DynamixelModel.XH540_W150,
        DynamixelModel.XH540_W270,
        DynamixelModel.XH540_V150,
        DynamixelModel.XH540_V270,
        DynamixelModel.XD540_T150,
        DynamixelModel.XD540_T270,
    ]:
        return CONTROL_TABLE_2_0 | XMH540_CONTROL_TABLE

    elif model_num in [
        DynamixelModel.XW540_T140,
        DynamixelModel.XW540_T260,
        DynamixelModel.XW430_T200,
        DynamixelModel.XW430_T333,
    ]:
        return CONTROL_TABLE_2_0

    elif model_num in [
        DynamixelModel.PRO_M42_10_S260_R,
        DynamixelModel.PRO_M54_40_S250_R,
        DynamixelModel.PRO_M54_60_S250_R,
        DynamixelModel.PRO_H42_20_S300_R,
        DynamixelModel.PRO_H54_100_S500_R,
        DynamixelModel.PRO_H54_200_S500_R,
    ]:
        return PRO_R_CONTROL_TABLE

    elif model_num in [
        DynamixelModel.PRO_M42_10_S260_RA,
        DynamixelModel.PRO_M54_40_S250_RA,
        DynamixelModel.PRO_M54_60_S250_RA,
        DynamixelModel.PRO_H42_20_S300_RA,
        DynamixelModel.PRO_H54_100_S500_RA,
        DynamixelModel.PRO_H54_200_S500_RA,
        DynamixelModel.PRO_H42P_020_S300_R,
        DynamixelModel.PRO_H54P_100_S500_R,
        DynamixelModel.PRO_H54P_200_S500_R,
        DynamixelModel.PRO_M42P_010_S260_R,
        DynamixelModel.PRO_M54P_040_S250_R,
        DynamixelModel.PRO_M54P_060_S250_R,
    ]:
        return PRO_RA_PRO_PLUS_CONTROL_TABLE

    elif model_num in [
        DynamixelModel.YM070_210_M001_RH,
        DynamixelModel.YM070_210_B001_RH,
        DynamixelModel.YM070_210_R051_RH,
        DynamixelModel.YM070_210_R099_RH,
        DynamixelModel.YM070_210_A051_RH,
        DynamixelModel.YM070_210_A099_RH,
        DynamixelModel.YM080_230_M001_RH,
        DynamixelModel.YM080_230_B001_RH,
        DynamixelModel.YM080_230_R051_RH,
        DynamixelModel.YM080_230_R099_RH,
        DynamixelModel.YM080_230_A051_RH,
        DynamixelModel.YM080_230_A099_RH,
    ]:
        return Y_CONTROL_TABLE
    else:
        raise ValueError("Unsupported model number")
