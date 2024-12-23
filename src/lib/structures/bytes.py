import logging
import math
from typing import Union


class Bytes:

    def __init__(self, value: Union[int, bytes, str], length: int = None, endianness="little"):
        self.endianness = endianness
        self.fixed_length = length
        self.value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: Union[int, bytes, str]):
        if type(value) == int:
            self._value = value
        elif value and type(value) == str:
            if self.endianness == "big":
                self._value = int(f"0x{value}", 16)
            else:
                reverse_value = value[::-1]
                self._value = int("0x" + "".join([
                    reverse_value[2 * i + 1] + reverse_value[2 * i] for i in range(len(reverse_value) // 2)
                ]), 16)
        elif type(value) in (bytes, bytearray):
            self._value = int.from_bytes(bytes=value, byteorder=self.endianness)
        elif type(value) == type(self):
            self._value = value._value
            self.endianness = value.endianness
        else:
            self._value = None
        if not self.fixed_length:
            if self._value is None:
                self._length = 0
            elif self._value == 0:
                self._length = 1
            else:
                self._length = int(math.log(max(self._value, 1), 0x100) + 1)

    @property
    def length(self) -> int:
        if self.fixed_length:
            return self.fixed_length
        return self._length

    def to_address(self):
        address = f"{self.value + 0xC00000:02X}"
        return f"{address[:2]}/{address[-4:]}"

    def __int__(self):
        return self._value

    def __str__(self):
        if self._value is not None:
            return f"{bytes(self).hex()}".zfill(self.length * 2).upper()
        else:
            return ""

    def string(self, endianness):
        if self._value is not None:
            hex_representation = int.to_bytes(self._value, length=self.length, byteorder=endianness).hex()
            return f"{hex_representation}".zfill(self.length * 2).upper()
        else:
            return ""

    def bytes(self, endianness):
        if self._value is not None:
            try:
                return self._value.to_bytes(length=self.length, byteorder=endianness)
            except OverflowError as e:
                output = b""
                i = 0
                value = self._value
                while i <= self.length:
                    output += (value % 0x0100).to_bytes(length=1, byteorder=endianness)
                    value //= 0x0100
                    i += 1
                return output
        else:
            return b""

    def __repr__(self):
        return self.__str__()

    def __hex__(self):
        return f"0x{self.__str__()}" if self._value else ""

    def __bytes__(self):
        if self._value is not None:
            try:
                return self._value.to_bytes(length=self.length, byteorder=self.endianness)
            except OverflowError as e:
                output = b""
                i = 0
                value = self._value
                while i <= self.length:
                    output += (value % 0x0100).to_bytes(length=1, byteorder=self.endianness)
                    value //= 0x0100
                    i += 1
                return output
        else:
            return b""

    def __add__(self, other):
        if type(other) == int:
            return self.__class__(self._value + other, length=self.length, endianness=self.endianness)
        else:
            return self.__class__(self._value + other._value, length=self.length, endianness=self.endianness)

    def __radd__(self, other):
        return self.__class__(other + self._value, length=self.length, endianness=self.endianness)

    def __floordiv__(self, other):
        if type(other) == int:
            return self.__class__(self._value // other, length=self.length, endianness=self.endianness)
        else:
            return self.__class__(self._value // other._value, length=self.length, endianness=self.endianness)

    def __sub__(self, other):
        if type(other) == int:
            return self.__class__(self._value - other, length=self.length, endianness=self.endianness)
        else:
            return self.__class__(self._value - other._value, length=self.length, endianness=self.endianness)

    def __rsub__(self, other):
        return self.__class__(other - self._value, length=self.length, endianness=self.endianness)

    def __mod__(self, other):
        if type(other) == int:
            return self.__class__(self._value % other, length=self.length, endianness=self.endianness)
        else:
            return self.__class__(self._value % other._value, lenght=self.length, endianness=self.endianness)

    def __getitem__(self, item):
        return bytes(self)[item]

    def __eq__(self, other):
        if type(other) == type(self):
            return self._value == other._value
        else:
            return self._value == other

    def __lt__(self, other):
        if type(other) == type(self):
            return self._value < other._value
        else:
            return self._value < other

    def __hash__(self):
        return hash(self._value)

    def __len__(self):
        return self.length

    def __format__(self, format_spec):
        if format_spec == "02X":
            return f"{int(self):02X}"
        elif format_spec == "04X":
            return f"{int(self):04X}"
        else:
            return self.__str__()

    @classmethod
    def from_address(cls, address: str):
        address = address.replace("/", "")
        return cls(value=int(f"0x{address}", 16) - 0xC00000, length=3, endianness="little")

    def append(self, other):
        if type(other) == bytes:
            self._value = int(Bytes(bytes(self) + other))
            self.fixed_length = self.length + len(other)
        elif type(other) in (int, str):
            other = Bytes(value=other)
            self._value = int(str(self) + str(other), 16)
            self.fixed_length = self.length + other.length



