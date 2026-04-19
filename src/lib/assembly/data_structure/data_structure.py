from __future__ import annotations
from typing import TYPE_CHECKING, Self

from src.lib.assembly.bytes import Bytes


class DataStructure:

    def __init__(self, position: Bytes | None = None):
        self.position = position if position is not None else Bytes([0x00, 0x00, 0x00])

    def __hash__(self) -> int:
        return hash(self.position)

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position

    def __lt__(self, other: Self) -> bool:
        return self.position < other.position

    @classmethod
    def sort(cls, value: Self) -> tuple[Bytes, bool]:
        from src.lib.assembly.artifact.variable import Label

        return value.position, not isinstance(value, Label)
