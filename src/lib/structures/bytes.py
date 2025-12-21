from __future__ import annotations
from enum import Enum, auto
from typing import Self, Any

from src.lib.misc.exception import UnderflowError


class Endian(Enum):
    LITTLE: bool = auto()
    BIG: bool = auto()


class Bytes:
    def __init__(self, value: list[int], endian: Endian = Endian.LITTLE, length: int | None = None):
        if not isinstance(value, list):
            raise ValueError(f"Type of value must be list[int]. Actual type: {type(value)}")
        self.endian = endian
        self.value = value
        if length:
            self.adjust(length=length)

    def adjust(self, length: int) -> None:
        if len(self.value) < length:
            self.value = [0] * (length - len(self.value)) + self.value
        else:
            self.value = self.value[-length:]

    @classmethod
    def from_int(cls, value: int, length: int | None = None) -> Self:
        remainder = value
        _list = list()
        if remainder == 0:
            _list = [0]

        while remainder > 0:
            next_byte = remainder % 256
            _list.insert(0, next_byte)
            remainder //= 256

        return cls(value=_list, length=length)

    @classmethod
    def from_position(cls, value: int) -> Self:
        return cls.from_int(value=value, length=3)

    @classmethod
    def from_str(cls, value: str, endian: Endian = Endian.LITTLE) -> Self:
        if len(value) % 2 != 0 or not value:
            raise ValueError("Value must be a non-empty string with an even number of characters.")

        _list = list()
        for i in range(len(value) // 2):
            hex = value[i * 2 : i * 2 + 2]
            _list.append(int(f"0x{hex}", 16))
        return cls(value=_list, endian=endian)

    @classmethod
    def from_bytes(cls, value: bytes, endian: Endian = Endian.LITTLE) -> Self:
        if len(value) == 0:
            raise ValueError("Value must be a non-empty bytes object.")
        _list = list()
        for _byte in value:
            if endian == Endian.BIG:
                _list.append(int(_byte))
            else:
                _list.insert(0, int(_byte))
        return cls(value=_list, endian=endian)

    @classmethod
    def from_other(cls, other: Bytes, length: int | None = None) -> Self:
        instance = cls(value=other.value)
        if length:
            instance.adjust(length=length)
        return instance

    def __int__(self) -> int:
        output = 0
        value = self.value
        for n in value:
            output *= 0x0100
            output += n
        return output

    def __str__(self) -> str:
        output = ""
        for n in self.value:
            output += n.to_bytes(length=1, byteorder="big").hex()
        return output.upper()

    def __repr__(self) -> str:
        return (
            f"Bytes(value={self.value}, as_decimal={int(self)}, "
            f"as_hexa=0x{self}, as_bytes={bytes(self)}, endian={self.endian})"
        )

    def __bytes__(self) -> bytes:
        output = b""
        for n in self.value:
            output += n.to_bytes(length=1, byteorder="big")
        if self.endian == Endian.LITTLE:
            output = output[::-1]
        return output

    def __len__(self) -> int:
        return len(self.value)

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, type(self)):
            raise ValueError(f"Can't only compare two Bytes together. {other=}")

        return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            raise ValueError(f"Can't only compare two Bytes together. {other=}")

        return int(self) < int(other)

    def __getitem__(self, item: slice) -> Self:
        new_value = self.value[item]
        new_value = new_value if isinstance(new_value, list) else [new_value]
        return type(self)(value=new_value)

    def __add__(self, other: Self | int) -> Self:
        sum = int(self) + int(other)
        if sum > 2 ** (8 * len(self.value)) - 1:
            raise OverflowError(f"Overflow when adding {self} and {other}.")
        instance = type(self).from_int(sum)
        instance.endian = self.endian
        return instance

    def __sub__(self, other: Self | int) -> Self:
        difference = int(self) - int(other)
        if difference < 0:
            raise UnderflowError("Value is below 0.")

        instance = type(self).from_int(difference)
        instance.endian = self.endian
        return instance

    def bank(self):
        return self.value[0] * 0x010000

    @classmethod
    def from_snes_address(cls, address: str):
        if len(address) != 6:
            raise ValueError(f"Address should consist of 6 characters. Address: {address}")

        instance = cls.from_str(value=address, endian=Endian.BIG) - 0xC00000
        instance.adjust(length=3)
        return instance

    def to_snes_address(self):
        if len(self.value) != 3:
            raise AttributeError(
                f"Can't convert to SNES address has the value of the Bytes object is not 3. Actual value: {self.value}"
            )

        instance = type(self).from_position(0xC00000) + self
        address = str(instance)
        return address
