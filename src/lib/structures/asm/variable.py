from re import Match
from typing import Self

from src.lib.misc.exception import ReassignmentException
from src.lib.structures import Bytes
from src.lib.structures.asm.script_line import ScriptLine


VAR_LENGTH = {".": 1, "!": 2, "@": 3}


class Variable(ScriptLine):
    """
    Used to store a value in order to raise readability and/or use it in multiple places at once.
    """

    def __init__(self, name: str, value: Bytes):
        """
        Instantiates a Variable
        :param name: The name of the Variable.
        :param value: The value of the Variable, as a Bytes object.
        """
        self.name = name
        self.value = value

    @classmethod
    def from_match(cls, match: Match, variables: list[Self] | None = None) -> Self:
        """
        Creates a Variable out of successful regex match.
        :param match: A Match object created out of a successful match against Regex.VARIABLE_ASSIGNMENT.
        :param variables: A list of existing variables.
        :return: A Variable.
        :raises ReassignmentException: Raised when we are trying to assign a value a second time to an existing value.
        :raises ValueError: Raised when the expected length of the Variable does not match its given value.
        """
        name = match.group("name")

        if variables and name in [v.name for v in variables]:
            raise ReassignmentException(f"Attempting to redefine variable '{name}'.")

        value = Bytes.from_str(match.group("value"))
        length = VAR_LENGTH[match.group("length")]
        if length != len(value):
            raise ValueError(f"Length of value {match.group('value')} does not match expected length: {length}.")
        return cls(name, value)

    def __eq__(self, other: Self) -> bool:
        """
        Compares two Variables.
        :param other: Another Variable.
        :return: If both Variables have the same name and value.
        :raises ValueError: Raised when the other is not a Variable.
        """
        if not isinstance(other, self.__class__):
            raise ValueError("Can only compare two Variables together.")
        return self.name == other.name and self.value == other.value

    def __len__(self) -> int:
        """
        :return: The length of the value of the Variable.
        """
        return len(self.value)

    def to_line(self) -> str:
        """
        :return: The assignment line that would match against Regex.VARIABLE_ASSIGNMENT.
        """
        if len(self.value) == 1:
            length_char = "."
        elif len(self.value) == 2:
            length_char = "!"
        else:
            length_char = "@"

        return f"let {length_char}{self.name} = ${self.value}"

    def __repr__(self) -> str:
        """
        :return: A representation of the Variable that would help debugging.
        """
        return f"Variable(name={self.name}, value=0x{str(self.value)})"

    def to_bytes(self, length: int | None = None) -> bytes:
        """
        Converts the Variable into a byte array.
        :param length: Can only be given against a Variable of length 3, which represents a position. If given, will
         return a byte representation of either the bank of the position, when length is 1, or its relative position in
         the bank, when length is 2. Length can be 3, but it has the same effect as not providing a length.
        :return: A byte array.
        :raises ValueError: Raised when a length is provided against a Variable of length 1 or 2.
        """
        if length and len(self.value) != 3:
            raise ValueError("Length argument can only be used by variables of length 3.")

        if not length or length == 3:
            return bytes(self.value)

        if length == 1:
            return bytes(self.value[0])

        return bytes(self.value[1:])
