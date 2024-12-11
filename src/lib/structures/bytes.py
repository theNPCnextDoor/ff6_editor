from __future__ import annotations

from types import NoneType
from typing import Self


class Endian:
    LITTLE: bool = True
    BIG: bool = False


class Bytes:
    def __init__(
        self,
        value: BytesType = None,
        length: int | None = None,
        in_endian: bool = Endian.LITTLE,
        out_endian: bool = Endian.LITTLE
    ):
        """
        Will initialize a Bytes object. It will always store its value as a list of integers in big endian.

        :param value: Can be a string, an integer, a bytes object, an object of this class or None.
        :param length: Used to either pad will leading zeros when the provided value is not big enough or will remove
         the most significant bytes when the value is too big.
        :param in_endian: The order of significance of the incoming bytes. Is useful when the value is a string or a
         bytes object. For int, it is unused as the int is expected to a big endian. For Bytes, since we simply pass the
          _value list directly, there is no need for it.
        :param out_endian: The order of significance of the outgoing bytes. Used when representing the object as a
         string or as bytes.
        """

        self._value: list[int] = list()
        self.length = length
        self.out_endian = out_endian

        if value is None:
            return

        if isinstance(value, list):
            self._value = value
            return

        if isinstance(value, str):
            self._from_str(value=value, in_endian=in_endian)

        elif isinstance(value, int):
            self._from_int(value=value)

        elif isinstance(value, bytes):
            self._from_bytes(value=value, in_endian=in_endian)

        elif isinstance(value, Bytes):
            self._from_other(value=value, length=length, out_endian=out_endian)

        self._pad_and_strip()

    def _from_str(self, value: str, in_endian: bool) -> None:
        if len(value) % 2 == 1:
            value = f"0{value}"
        for i in range(len(value) // 2):
            hex = value[i * 2: i * 2 + 2]
            self._value.append(int(f"0x{hex}", 16))
        if in_endian:
            self._value = self._value[::-1]

    def _from_bytes(self, value: bytes, in_endian: bool) -> None:
        for byte in value:
            self._value.append(int(byte))
        if in_endian:
            self._value = self._value[::-1]

    def _from_int(self, value: int) -> None:
        if value == 0:
            self._value.append(0)
        else:
            while value > 0:
                n = value % 0x0100
                self._value.append(n)
                value //= 0x0100
            self._value = self._value[::-1]

    def _from_other(self, value: Self, length: int = None, out_endian: bool = None) -> None:
        self._value = value._value
        self.length = length if length is not None else value.length
        self.out_endian = out_endian if out_endian is not None else value.out_endian

    def _pad_and_strip(self) -> None:
        if self.length is None:
            return

        while len(self._value) < self.length:
            self._value = [0] + self._value
        if len(self._value) > self.length:
            self._value = self._value[-self.length:]

    def _ordered_value(self, out_endian: bool) -> list[int]:
        output = self._value[::-1] if out_endian is Endian.LITTLE else self._value
        return output

    def __bytes__(self) -> str:
        ordered_value = self._ordered_value(out_endian=self.out_endian)
        output = b""
        for n in ordered_value:
            output += n.to_bytes(length=1, byteorder="big")
        return output

    def __int__(self) -> int:
        output = 0
        for n in self._value:
            output *= 0x0100
            output += n
        return output

    def __str__(self) -> str:
        ordered_value = self._ordered_value(out_endian=self.out_endian)
        output = ""
        for n in ordered_value:
            output += n.to_bytes(length=1, byteorder="big").hex()
        return output.upper()

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self._value)

    def __eq__(self, other: Bytes | None) -> bool:
        if isinstance(other, NoneType):
            return self._value is None and other is None

        if not isinstance(other, Bytes):
            raise ValueError(f"Can't only compare two Bytes together. {other=}")

        return self._value == other._value

    def __lt__(self, other: Bytes) -> bool:
        if not isinstance(other, Bytes):
            raise ValueError("Can't only compare two Bytes together.")
        return int(self) < int(other)

    def __getitem__(self, item) -> Self:
        return Bytes(value=self._value[item], in_endian=Endian.BIG, out_endian=self.out_endian)

class Position(Bytes):
    def __init__(self, value: BytesType = 0, in_endian: bool = Endian.BIG):
        super().__init__(value=value, length=3, in_endian=in_endian, out_endian=Endian.BIG)

    def bank(self) -> int:
        return self._value[0] * 0x010000

    @classmethod
    def from_snes_address(cls, value: str) -> Self:
        normal_address = int(Position(value=value.replace("/", ""))) - 0xC00000
        return Position(value=normal_address)

    def to_snes_address(self) -> str:
        if self.length > 3:
            raise Exception("Length is too big. This probably isn't a SNES address.")
        snes_position = Position(int(self) + 0xC00000)
        output = f"{str(snes_position[:1])}/{str(snes_position[1:])}"
        return output.upper()

BytesType = Bytes | int | str | bytes | list[int] | None
