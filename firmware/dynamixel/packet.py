from struct import pack_into, unpack_from
from .crc import CRC_TABLE_V2


class DynamixelPacket:

    def __init__(self, buffer: bytearray, protocol_version=2):

        self.buffer = buffer

        if protocol_version not in (1, 2):
            raise ValueError("Unsupported protocol version.")
        self.param_length = 1
        self.ver = protocol_version

        if self.ver == 2:
            self.LENGTH_BYTE = 7
        else:
            self.LENGTH_BYTE = 4

    # @property
    # def header(self):
    #     if self.ver == 2:
    #         return unpack_from(">I", self.buffer, 0)
    #     return unpack_from(">H", self.buffer, 0)

    # @header.setter
    # def header(self, value):
    #     value = value & 0xFFFFFFFF
    #     pack_into(">I", self.buffer, 0, *value)

    @property
    def length(self):
        if self.ver == 2:
            return unpack_from("<H", self.buffer, self.LENGTH_BYTE - 2)[0]
        return self.buffer[self.LENGTH_BYTE - 1]

    @length.setter
    def length(self, value):
        value = value & 0xFFFF
        if self.ver == 2:
            pack_into("<H", self.buffer, self.LENGTH_BYTE - 2, value)
        else:
            self.buffer[self.LENGTH_BYTE - 1] = value

    @property
    def instruction(self):
        return self.buffer[self.LENGTH_BYTE]

    @instruction.setter
    def instruction(self, value):
        self.buffer[self.LENGTH_BYTE] = value & 0xFF

    @property
    def id(self):
        if self.ver == 2:
            return self.buffer[self.LENGTH_BYTE - 3]
        return self.buffer[self.LENGTH_BYTE - 2]

    @id.setter
    def id(self, value):
        if self.ver == 2:
            self.buffer[self.LENGTH_BYTE - 3] = value & 0xFF
        else:
            self.buffer[self.LENGTH_BYTE - 2] = value & 0xFF

    @property
    def param(self) -> bytearray:
        if self.ver == 2:
            offset = ~self.length + 3
            return self.buffer[offset:-2]
        else:
            offset = ~self.length + 2
            return self.buffer[offset:-1]

    @param.setter
    def param(self, value: bytearray):
        offset = ~len(value)
        if self.ver == 2:
            offset -= 1
            self.buffer[offset : -2] = value
        else:
            self.buffer[offset : -1] = value

    @property
    def checksum(self):
        if self.ver == 2:
            return unpack_from("<H", self.buffer, -2)[0]
        else:
            return self.buffer[-1]

    @checksum.setter
    def checksum(self, value):
        if self.ver == 2:
            pack_into("<H", self.buffer, -2, value)
        else:
            self.buffer[-1] = value

    def __repr__(self):
        return f"DynamixelPacket(ver={self.ver}, buffer={self.buffer})"

    def __len__(self):
        return len(self.buffer)

    def calc_checksum(self):
        if self.ver == 2:
            crc = 0x0000
            data = self.buffer[0:-2]
            for byte in data:
                i = ((crc >> 8) ^ byte) & 0xFF
                crc = CRC_TABLE_V2[i] ^ ((crc << 8) & 0xFFFF)
            return crc
        else:
            idx = self.LENGTH_BYTE - 2
            return ~(sum(self.buffer[idx:-1]) & 0xFF)


class DynamixelRXPacket(DynamixelPacket):

    def __init__(self, protocol_version=2):
        super().__init__(bytearray(), protocol_version)

    @property
    def error(self):
        if self.ver == 2:
            return self.buffer[8]
        return self.buffer[4]

    def has_valid_checksum(self):
        return self.checksum == self.calc_checksum()


class DynamixelTXPacket(DynamixelPacket):

    def __init__(self, id, instruction, length, param, protocol_version=2):

        if protocol_version == 2:
            buffer = bytearray(7 + length)  # 4 header + 1 id + 2 address + length
            buffer[0:4] = b"\xff\xff\xfd\x00"
        else:
            buffer = bytearray(4 + length)  # 2 header + 1 id  + 1 address + length
            buffer[0:2] = b"\xff\xff"

        super().__init__(buffer, protocol_version)
        self.id = id
        self.length = length
        self.instruction = instruction
        if len(param):
            self.param = param

        self.checksum = self.calc_checksum()


# from dy.packet import DynamixelTXPacket
# a = DynamixelTXPacket(id=1, instruction=3, length=6, address=65, param=1, protocol_version=2)
# b=a.buffer
# b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11], b[12], b[13], b[14], b[15]

# z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7], z[8], z[9], z[10], z[11], z[12], z[13], z[14], z[15]
# a = DynamixelTXPacket(id=1, instruction=3, length=4, address=65, param=1, protocol_version=1)
# msg = DynamixelTXPacket(id=1, instruction=3, length=6, address=65, param=1, protocol_version=2)
# msg = DynamixelTXPacket(id=1, instruction=2, length=7, address=65, param=1, protocol_version=2)
# (255, 255, 253, 0, 1, 6, 0, 1, 65, 0, 1, 207, 78)
# (255, 255, 253, 0, 1, 7, 0, 2, 65, 0, 1, 0, 63, 79)


# (255, 255, 253, 0, 1, 5, 0, 85, 128, 0, 90, 161)
# b = [0xFF, 0xFF, 0xFD, 0x00, 0x01, 0x07, 0x00, 0x02, 0x84, 0x00, 0x04, 0x00, 0x1D, 0x15]
