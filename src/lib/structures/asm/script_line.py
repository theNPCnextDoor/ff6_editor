from __future__ import annotations
from typing import Match, Optional, TYPE_CHECKING, Self

from src.lib.structures.bytes import Position

if TYPE_CHECKING:
    from src.lib.structures.asm.label import Label


class ScriptLine:

    def __init__(self, position: Position | None):
        self.position = position if position is not None else Position([0x00])

    def __hash__(self) -> int:
        return hash(self.position)

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position

    def __lt__(self, other: Self) -> bool:
        return self.position < other.position

    @classmethod
    def sort(cls, value: Self) -> tuple[Position, bool]:
        from src.lib.structures.asm.label import Label

        return value.position, not isinstance(value, Label)


class DataMixin:
    @staticmethod
    def data(match: Match) -> Optional[str]:
        if not match:
            return None

        if match.group("mov2"):
            return "".join([match.group("mov2"), match.group("n5")])

        for i in range(1, 7):
            if number := match.group(f"n{i}"):
                return number

        return None


class BankMixin:
    @staticmethod
    def bank(position: Position) -> Position:
        return Position.from_int(int(position) & 0xFF0000)


class NoLabelException(Exception):
    pass


class ImpossibleDestination(Exception):
    pass


class DestinationMixin:
    @classmethod
    def find_destination(cls, label_name: str, labels: list[Label]) -> Position:
        candidates = [label for label in labels if label.name == label_name]
        if len(candidates) == 0:
            raise NoLabelException(f"Can't find a label with name '{label_name}'.")
        label = candidates[0]
        destination = label.position
        return destination

    @staticmethod
    def find_label(destination: Position, labels: list[Label]) -> Label:
        for label in labels:
            if destination == label.position:
                return label
