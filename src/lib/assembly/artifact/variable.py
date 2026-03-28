from dataclasses import dataclass
from re import Match

from typing import Self, Any

from src.lib.assembly.artifact.artifact import Artifact
from src.lib.assembly.bytes import Bytes


VAR_LENGTH = {"b": 1, "w": 2}


class Variable(Artifact):
    def __init__(self, value: Bytes, name: str):
        self.value = value
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(0x{str(self.value)}, {self.name})"

    def __eq__(self, other: Self):
        if other is None:
            return False
        return self.value == other.value and self.name == other.name


class SimpleVar(Variable):
    """
    Used to store a value in order to raise readability and/or use it in multiple places at once.
    """

    @classmethod
    def from_match(cls, match: Match) -> Self:
        """
        Creates a Variable out of successful regex match.
        :param match: A Match object created out of a successful match against Regex.VARIABLE_ASSIGNMENT.
        :return: A Variable.
        :raises ReassignmentException: Raised when we are trying to assign a value a second time to an existing value.
        :raises ValueError: Raised when the expected length of the Variable does not match its given value.
        """
        name = match.group("name")

        value = Bytes.from_str(match.group("value"))
        length = VAR_LENGTH[match.group("length")]
        if length != len(value):
            raise ValueError(f"Length of value {match.group('value')} does not match expected length: {length}.")
        return cls(value, name)

    def to_line(self) -> str:
        """
        :return: The assignment line that would match against Regex.VARIABLE_ASSIGNMENT.
        """
        length_char = "b" if len(self.value) == 1 else "w"

        return f"d{length_char} {self.name} = ${self.value}"


class Label(SimpleVar):

    def __init__(self, value: Bytes, name: str | None = None):
        name = (name or f"label_{value.to_snes_address()}").lower()
        super().__init__(name=name, value=value)

    @property
    def position(self) -> Bytes:
        return self.value

    @classmethod
    def from_match(cls, match: Match, position: Bytes | None = None) -> Self:
        name = match.group(1)
        position = Bytes.from_snes_address(match.group("snes_address")) if match.group("snes_address") else position

        return cls(
            value=position,
            name=name,
        )

    def to_line(self, show_address: bool = False, **kwargs: Any) -> str:
        output = ""
        if show_address:
            output += "\n"
        output += f"@{str(self)}"
        output += f" = ${self.value.to_snes_address()}" if show_address else ""
        return output

    def __hash__(self) -> int:
        return hash(int(self.position))
