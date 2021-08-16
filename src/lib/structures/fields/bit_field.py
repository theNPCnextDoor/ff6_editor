from src.lib.structures import Binary, Bytes
from src.lib.structures.fields import ByteField


class BitField(ByteField):
    def __init__(self, base_location, position: int, bit_value: int):
        if not (0x01 <= bit_value <= 0xFF):
            raise ValueError("The bit_value must be between 0x01 and 0xFF inclusively.")
        super().__init__(base_location=base_location, position=position)
        self.bit_value = bit_value
        self.bitmask = 0x0100 - bit_value
        self.first_bit = self.least_significant_bit()

    def __get__(self, instance, owner):
        start = self.start(instance)
        return (int(Bytes(Binary()[start : start + 1])) & self.bit_value) >> self.first_bit

    def __set__(self, instance, value):
        value = int(Bytes(value=value, length=1, endianness="little")) << self.first_bit
        start = self.start(instance)
        original_value = Binary()[start : start + 1]
        value = (original_value & self.bitmask) + (value & self.bit_value)
        Binary()[start : start + self.length] = bytes(Bytes(value))

    def least_significant_bit(self):
        for i in range(8):
            if self.bit_value & (2 ** i):
                return i
