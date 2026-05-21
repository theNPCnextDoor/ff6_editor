from __future__ import annotations
from typing import Self

from src.lib.assembly.bytes import Bytes
from abc import ABC, abstractmethod


class DataStructure(ABC):
    def __init__(self, position: Bytes | None = None):
        self.position = position if position is not None else Bytes.from_position(0)

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position

    @classmethod
    @abstractmethod
    def from_line(cls, *args, **kwargs) -> Self:
        pass

    @classmethod
    @abstractmethod
    def from_bytes(cls, *args, **kwargs) -> Self:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __bytes__(self) -> bytes:
        pass

    @abstractmethod
    def to_line(self, *args, **kwargs) -> str:
        pass
