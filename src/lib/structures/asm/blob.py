from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.lib.structures.asm.regex import ToLineMixin
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import Position, Bytes, Endian, BlobBytes

if TYPE_CHECKING:
    from re import Match
    from src.lib.structures.asm.label import Label


class Blob(ScriptLine, ToLineMixin):
    def __init__(self, data: BlobBytes, position: Position | None = None, delimiter: Bytes | None = None):
        super().__init__(position=position)
        self.data = data
        self.delimiter = delimiter

    @classmethod
    def from_regex_match(cls, match: Match, position: Position | None = None) -> Self:
        data = match.group("n1") or match.group("n2")
        delimiter = match.group("d1")

        if delimiter is not None:
            delimiter = Bytes(delimiter)

        return cls(position=position, data=BlobBytes(data), delimiter=delimiter)

    @classmethod
    def from_bytes(cls, data: bytes, position: Position | None = None, delimiter: bytes | None = None) -> Self:
        data = Bytes(value=data, in_endian=Endian.BIG, out_endian=Endian.BIG)
        if delimiter is not None:
            delimiter = Bytes(value=delimiter)
        return Blob(position=position, data=data, delimiter=delimiter)

    def __str__(self) -> str:
        output = f"${self.data}"
        if self.delimiter is not None:
            output += f",${self.delimiter}"
        return output

    def __repr__(self) -> str:
        return f"{self.position}: {self}"

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        if show_address:
            output += f" # {self.position.to_snes_address()}"
        return output

    def __len__(self) -> int:
        output = len(self.data)
        output += 1 if self.delimiter is not None else 0
        return output

    def __bytes__(self) -> bytes:
        output = bytes(self.data)
        if self.delimiter is not None:
            output += bytes(self.delimiter)
        return output
