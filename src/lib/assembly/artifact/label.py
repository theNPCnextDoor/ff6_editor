from re import Match
from typing import Self

from src.lib.assembly.artifact.variable import Variable
from src.lib.assembly.bytes import Bytes


class Label(Variable):

    def __init__(self, value: Bytes, name: str | None = None):
        name = (name or f"label_{value.to_snes_address().replace('/', '')}").lower()
        super().__init__(name=name, value=value)

    @property
    def position(self) -> Self:
        return self.value

    @classmethod
    def from_regex_match(cls, match: Match, position: Bytes = None) -> Self:
        name = match.group(1)
        position = Bytes.from_snes_address(match.group("snes_address")) if match.group("snes_address") else position

        return cls(
            value=position,
            name=name,
        )

    def to_line(self, show_address: bool = False, labels: list[Self] | None = None) -> str:
        output = ""
        if show_address:
            output += "\n"
        output += str(self)
        output += f"={self.value.to_snes_address()}" if show_address else ""
        return output

    def __str__(self) -> str:
        return f"@{self.name}"

    def __repr__(self) -> str:
        return f"{self.position}: {self.name}"

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position

    def __lt__(self, other: Self) -> bool:
        return self.position < other.position

    def __len__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash(int(self.position))
