from re import Match
from typing import Self

from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import Position


class Label(ScriptLine):

    def __init__(
        self,
        position: Position,
        name: str = None
    ):
        super().__init__(position=position)
        self.name = (name or f"label_{self.position.to_snes_address().replace('/', '')}").lower()

    @classmethod
    def from_regex_match(cls, match: Match, position: Position = None) -> Self:
        name = match.group(1)
        position = Position.from_snes_address(match.group("snes_address")) if match.group("snes_address") else position

        return cls(
            position=position,
            name=name,
        )

    def to_line(self, show_address: bool = False, labels: list[Self] | None = None) -> str:
        output = ""
        if show_address:
            output += "\n"
        output += str(self)
        output += f"={self.position.to_snes_address()}" if show_address else ""
        return output

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.position}: {self.name}"

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position

    def __lt__(self, other: Self) -> bool:
        return self.position < other.position

    def __len__(self) -> int:
        return 0

    def __bool__(self):
        return True

    def __hash__(self):
        return hash(int(self.position))
