from machine import UART
from .table import get_control_table, ControlTableItem
from .packet import DynamixelTXPacket, DynamixelRXPacket
import time
from struct import pack_into, unpack_from
from .model import DynamixelModel

class TimeoutError(Exception):
    pass


class Dynamixel:

    INS_READ = 2
    INS_WRITE = 3
    INS_FACTORY_RESET = 6
    INS_REBOOT = 8
    TIMEOUT = 225  # milliseconds

    def __init__(self, connector: UART, model: DynamixelModel, id: int = 1, protocol_version: int = 2):
        self.__connector = connector
        self.__control_table = get_control_table(model)
        self.__id = id
        self.__ver = protocol_version

    def __to_rel(self, value, min, max):
        return (value - min) / (max - min)

    def __to_abs(self, value, min, max):
        return value * (max - min) + min

    def __to_signed(self, bytes=4, value=0):
        """Convert unsigned 32-bit value to signed using two's complement."""
        if value >= 2 ** (bytes * 8 - 1):
            value -= 2 ** (bytes * 8)
        return value

    def __get_addr_length(self, item: int):
        table_entry = self.__control_table.get(item)

        if table_entry is None:
            raise ValueError("Control table item not found.")
        addr, length = table_entry.get("addr"), table_entry.get("length")
        if addr is None or length is None:
            raise ValueError("Control table item is missing address or length.")
        return addr, length

    def __clear_buffer(self):
        try:
            while self.__connector.any():
                self.__connector.read()
        except Exception as e:
            print(f"Error in __clear_buffer: {e}")

    def __read(self, item: int):
        try:
            self.__clear_buffer()
            self.__read_instruction(item)

            rx = DynamixelRXPacket(self.__ver)
            length_to_read = rx.LENGTH_BYTE

            time.sleep(0.01)  # Small delay to allow data to arrive

            t_start = time.ticks_ms()
            while length_to_read > 0:
                if time.ticks_diff(time.ticks_ms(), t_start) > self.TIMEOUT:
                    raise TimeoutError("No response from the Dynamixel motor.")
                data = self.__connector.read(1)
                if data is not None:
                    rx.buffer.extend(data)
                    length_to_read -= 1

            time.sleep(0.01)  # Small delay to allow data to arrive
            length_to_read = rx.length

            t_start = time.ticks_ms()
            while length_to_read > 0:
                if time.ticks_diff(time.ticks_ms(), t_start) > self.TIMEOUT:
                    raise TimeoutError("Timeout while reading parameter data from Dynamixel motor.")
                data = self.__connector.read(1)
                if data is not None:
                    rx.buffer.extend(data)
                    length_to_read -= 1

            if not rx.has_valid_checksum():
                raise ValueError("Invalid checksum in response packet.")

            return rx.param
        except TimeoutError as e:
            print(f"Timeout error: {e}")
            return None
        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in __read: {e}")
            return None

    def __length_to_fmt(self, length: int):
        if length == 1:
            return "B"
        elif length == 2:
            return "H"
        elif length == 4:
            return "I"
        else:
            raise ValueError("Unsupported data length.")

    def __read_value(self, item: int):
        try:
            _, length_of_data = self.__get_addr_length(item)
            data_fmt = self.__length_to_fmt(length_of_data)
            param = self.__read(item)
            return unpack_from("<" + data_fmt, param, 0)[0]
        except Exception as e:
            print(f"Error in __read_value: {e}")
            return 0

    def __write_instruction(self, item: int, data):
        try:
            address, length_of_data = self.__get_addr_length(item)
            data_fmt = self.__length_to_fmt(length_of_data)
            param = bytearray(length_of_data + 2)
            pack_into("<H", param, 0, address)
            pack_into("<" + data_fmt, param, 2, data)
            self.__write(self.INS_WRITE, param)
        except Exception as e:
            print(f"Error in __write_instruction: {e}")

    def __read_instruction(self, item: int):
        try:
            address, data = self.__get_addr_length(item)
            param = bytearray(4)
            pack_into("<H", param, 0, address)
            pack_into("<H", param, 2, data)
            self.__write(self.INS_READ, param)
        except Exception as e:
            print(f"Error in __read_instruction: {e}")

    def __write(self, instruction: int, param: bytearray):
        try:
            if self.__ver == 2:
                length = len(param) + 3  # 1 instruction + 2 checksum
            else:
                length = len(param) + 2  # 1 instruction + 1 checksum

            msg = DynamixelTXPacket(
                id=self.__id,
                instruction=instruction,
                length=length,
                param=param,
                protocol_version=self.__ver,
            )

            self.__connector.write(msg.buffer)
            self.__connector.flush()
            time.sleep(0.02)  # Small delay to allow data to be sent
        except Exception as e:
            print(f"Error in __write: {e}")

    @property
    def led(self) -> bool:
        return True if self.__read_value(ControlTableItem.DXL_LED) else False

    @led.setter
    def led(self, value: bool):
        self.__write_instruction(ControlTableItem.DXL_LED, value)

    @property
    def operating_mode(self):
        return self.__read_value(ControlTableItem.OPERATING_MODE)

    @operating_mode.setter
    def operating_mode(self, value: int):
        self.__write_instruction(ControlTableItem.OPERATING_MODE, value)

    @property
    def position_limit_low(self):
        return self.__read_value(ControlTableItem.MIN_POSITION_LIMIT)

    @property
    def position_limit_high(self):
        return self.__read_value(ControlTableItem.MAX_POSITION_LIMIT)

    @position_limit_low.setter
    def position_limit_low(self, value: int):
        self.__write_instruction(ControlTableItem.MIN_POSITION_LIMIT, value)

    @position_limit_high.setter
    def position_limit_high(self, value: int):
        self.__write_instruction(ControlTableItem.MAX_POSITION_LIMIT, value)

    @property
    def velocity_limit(self):
        return self.__read_value(ControlTableItem.VELOCITY_LIMIT)

    @velocity_limit.setter
    def velocity_limit(self, value: int):
        self.__write_instruction(ControlTableItem.VELOCITY_LIMIT, value)

    @property
    def acceleration_limit(self):
        return self.__read_value(ControlTableItem.ACCELERATION_LIMIT)

    @acceleration_limit.setter
    def acceleration_limit(self, value: int):
        self.__write_instruction(ControlTableItem.ACCELERATION_LIMIT, value)

    @property
    def pwm_limit(self):
        return self.__read_value(ControlTableItem.PWM_LIMIT)

    @pwm_limit.setter
    def pwm_limit(self, value: int):
        self.__write_instruction(ControlTableItem.PWM_LIMIT, value)

    @property
    def current_limit(self):
        return self.__read_value(ControlTableItem.CURRENT_LIMIT)

    @current_limit.setter
    def current_limit(self, value: int):
        self.__write_instruction(ControlTableItem.CURRENT_LIMIT, value)

    @property
    def torque_enabled(self) -> bool:
        return True if self.__read_value(ControlTableItem.TORQUE_ENABLE) else False

    @torque_enabled.setter
    def torque_enabled(self, value: bool):
        val = 1 if value else 0
        self.__write_instruction(ControlTableItem.TORQUE_ENABLE, val)

    @property
    def current_position(self):
        value = self.__read_value(ControlTableItem.PRESENT_POSITION)
        return self.__to_signed(4, value)

    @property
    def current_position_rel(self):
        return self.__to_rel(self.current_position, self.position_limit_low, self.position_limit_high)

    @property
    def current_velocity(self):
        value = self.__read_value(ControlTableItem.PRESENT_VELOCITY)
        return self.__to_signed(4, value)

    @property
    def current_velocity_rel(self):
        return self.__to_rel(self.current_velocity, 0, self.velocity_limit)

    @property
    def goal_position(self):
        value = self.__read_value(ControlTableItem.GOAL_POSITION)
        return self.__to_signed(4, value)

    @goal_position.setter
    def goal_position(self, value: int):
        self.__write_instruction(ControlTableItem.GOAL_POSITION, value)

    @property
    def goal_position_rel(self):
        return self.__to_rel(self.goal_position, self.position_limit_low, self.position_limit_high)

    @goal_position_rel.setter
    def goal_position_rel(self, value: float):
        self.goal_position = int(round(self.__to_abs(value, self.position_limit_low, self.position_limit_high)))

    @property
    def goal_extend_position(self):
        value = self.__read_value(ControlTableItem.GOAL_POSITION)
        return self.__to_signed(4, value)

    @goal_extend_position.setter
    def goal_extend_position(self, value: int):
        self.__write_instruction(ControlTableItem.GOAL_POSITION, value)

    @property
    def goal_extend_position_rel(self):
        return self.__to_rel(self.goal_position, -1_048_575, 1_048_575)

    @goal_extend_position_rel.setter
    def goal_extend_position_rel(self, value: float):
        self.goal_extend_position = int(round(self.__to_abs(value, -1_048_575, 1_048_575)))

    @property
    def goal_velocity(self):
        value = self.__read_value(ControlTableItem.GOAL_VELOCITY)
        return self.__to_signed(4, value)

    @goal_velocity.setter
    def goal_velocity(self, value: int):
        self.__write_instruction(ControlTableItem.GOAL_VELOCITY, value)

    @property
    def goal_velocity_rel(self):
        return self.__to_rel(self.goal_velocity, 0, self.velocity_limit)

    @goal_velocity_rel.setter
    def goal_velocity_rel(self, value: float):
        self.goal_velocity = int(round(self.__to_abs(value, 0, self.velocity_limit)))

    @property
    def goal_acceleration(self):
        return self.__read_value(ControlTableItem.GOAL_ACCELERATION)

    @goal_acceleration.setter
    def goal_acceleration(self, value: int):
        self.__write_instruction(ControlTableItem.GOAL_ACCELERATION, value)

    @property
    def goal_acceleration_rel(self):
        return self.__to_rel(self.goal_acceleration, 0, self.acceleration_limit)

    @goal_acceleration_rel.setter
    def goal_acceleration_rel(self, value: float):
        self.goal_acceleration = int(round(self.__to_abs(value, 0, self.acceleration_limit)))

    @property
    def goal_pwm(self):
        value = self.__read_value(ControlTableItem.GOAL_PWM)
        return self.__to_signed(2, value)

    @goal_pwm.setter
    def goal_pwm(self, value: int):
        self.__write_instruction(ControlTableItem.GOAL_PWM, value)

    @property
    def goal_pwm_rel(self):
        return self.__to_rel(self.goal_pwm, -self.pwm_limit, self.pwm_limit)

    @goal_pwm_rel.setter
    def goal_pwm_rel(self, value: float):
        self.goal_pwm = int(round(self.__to_abs(value, -self.pwm_limit, self.pwm_limit)))
