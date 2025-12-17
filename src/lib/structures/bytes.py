from __future__ import annotations
from enum import Enum, auto
from typing import Self, Any


class Endian(Enum):
    LITTLE: bool = auto()
    BIG: bool = auto()


class Bytes:
    endian = Endian.LITTLE

    def __init__(self, value: list[int], length: int | None = None):
        if not isinstance(value, list):
            raise ValueError(f"Type of value must be list[int]. Actual type: {type(value)}")
        if length is None:
            self.value = value
        elif len(value) < length:
            self.value = [0] * (length - len(value)) + value
        else:
            self.value = value[-length:]

    @classmethod
    def from_int(cls, value: int, length: int | None = None) -> Self:
        remainder = value
        _list = list()
        if remainder == 0:
            _list = [0]

        while remainder > 0:
            next_byte = remainder % 256
            if cls.endian == Endian.BIG:
                _list.insert(0, next_byte)
            else:
                _list.append(next_byte)
            remainder //= 256

        return cls(value=_list, length=length)

    @classmethod
    def from_str(cls, value: str) -> Self:
        if len(value) % 2 != 0 or not value:
            raise ValueError("Value must be a non-empty string with an even number of characters.")

        _list = list()
        for i in range(len(value) // 2):
            hex = value[i * 2 : i * 2 + 2]
            _list.append(int(f"0x{hex}", 16))
        return cls(value=_list)

    @classmethod
    def from_bytes(cls, value: bytes):
        if len(value) == 0:
            raise ValueError("Value must be a non-empty bytes object.")
        _list = list()
        for _byte in value:
            if cls.endian == Endian.BIG:
                _list.append(int(_byte))
            else:
                _list.insert(0, int(_byte))
        return cls(value=_list)

    @classmethod
    def from_other(cls, other: Bytes, length: int | None = None):
        return cls(value=other.value, length=length)

    def __int__(self) -> int:
        output = 0
        value = self.value if self.endian == Endian.BIG else self.value[::-1]
        for n in value:
            output *= 0x0100
            output += n
        return output

    def __str__(self) -> str:
        output = ""
        for n in self.value:
            output += n.to_bytes(length=1, byteorder="big").hex()
        return output.upper()

    def __bytes__(self) -> bytes:
        output = b""
        for n in self.value:
            output += n.to_bytes(length=1, byteorder="big")
        if self.endian == Endian.LITTLE:
            output = output[::-1]
        return output

    def __repr__(self) -> str:
        return str(self)

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

    def __getitem__(self, item: Any) -> Self:
        new_value = self.value[item]
        new_value = new_value if isinstance(new_value, list) else [new_value]
        return type(self)(value=new_value)

    def __add__(self, other: Self | int) -> Self:
        sum = int(self) + int(other)
        if sum >= 256 ** len(self):
            raise ValueError(f"Value exceeds {len(self)} bytes.")

        return type(self).from_int(sum)

    def __sub__(self, other: Self | int) -> Self:
        difference = int(self) - int(other)
        if difference < 0:
            raise ValueError("Value is below 0.")

        return type(self).from_int(difference)


class BEBytes(Bytes):
    endian = Endian.BIG


class Position(BEBytes):
    def __init__(self, value: list[int], length: None = None):
        super().__init__(value=value, length=3)

    def bank(self):
        return self.value[0] * 0x010000

    @classmethod
    def from_snes_address(cls, address: str):
        return cls.from_str(value=address) - 0xC00000

    def to_snes_address(self):
        address = str(self + 0xC00000)
        return address
