from abc import ABC, abstractmethod
from typing import Self, Any

from src.lib.assembly.artifact.artifact import Artifact
from src.lib.assembly.bytes import Bytes
from src.lib.misc.exception import ForbiddenVarName


VAR_LENGTH = {"b": 1, "w": 2}
FORBIDDEN_NAMES = ["db", "desc", "dw", "m", "ptr", "rptr", "x"]


class Variable(Artifact, ABC):
    """
    Variables are Artifact in a script where a specific value is represented by a name.
    """

    def __init__(self, value: Bytes, name: str):
        self.value = value
        self.name = name

    @property
    @abstractmethod
    def position(self) -> Bytes:
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}(0x{str(self.value)}, '{self.name}')"

    def __eq__(self, other: Self):
        if other is None:
            return False
        return self.value == other.value and self.name == other.name

    @staticmethod
    def is_name_forbidden(name: str) -> bool:
        return name in FORBIDDEN_NAMES


class SimpleVar(Variable):
    """
    Used to store a value in order to raise readability and/or use it in multiple places at once.
    """

    @classmethod
    def from_line(cls, length: str, name: str, operand: str) -> Self:
        """
        Creates a Variable out of successful regex match.
        :param length: Either 'b', for 'byte' or 'w' for 'word', to represent the length of the variable. A 'byte' is 1
        byte and a word is 2.
        :param name: The name of the variable.
        :param operand: The value of the variable.
        :return: A Variable.
        :raises ReassignmentException: Raised when we are trying to assign a value a second time to an existing value.
        :raises ValueError: Raised when the expected length of the Variable does not match its given value.
        """
        if cls.is_name_forbidden(name):
            raise ForbiddenVarName(f"Variable name '{name}' is forbidden. All forbidden names: {FORBIDDEN_NAMES}")

        _operand = Bytes.from_str(operand.replace("$", ""))
        _length = VAR_LENGTH[length]

        if _length != len(_operand):
            raise ValueError(f"Length of value '{operand}' does not match expected length: {_length}.")
        return cls(_operand, name)

    @property
    def position(self) -> Bytes:
        return Bytes.from_position(0)

    def to_line(self, **kwargs: Any) -> str:
        """
        Converts a SimpleVar into the exact string which will be put in a script to declare it.
        :return: A script line.
        """
        length_char = "b" if len(self.value) == 1 else "w"

        return f"d{length_char} {self.name} = ${self.value}"


class Label(SimpleVar):
    """
    A Label is a 24-bit Variable that is used to define an address in the ROM.
    """

    def __init__(self, value: Bytes, name: str | None = None):
        """
        :param value: The value, or the position, of the Label.
        :param name: The name of the Label.
        """
        name = (name or f"label_{value.to_snes_address()}").lower()
        super().__init__(name=name, value=value)

    @property
    def position(self) -> Bytes:
        """
        For a Label, its value is its position.
        :return: The value of the Label.
        """
        return self.value

    @classmethod
    def from_line(cls, name: str, snes_address: str | None = None, position: Bytes | None = None) -> Self:
        """
        Converts a string into a Label.
        :param name: The name of the Label.
        :param snes_address: The SNES address of the Label. When omitted, will use the current position in the script
        as the Label value.
        :param position: The current position of the Label in the script.
        :return: A Label.
        """
        if cls.is_name_forbidden(name):
            raise ForbiddenVarName(f"Variable name '{name}' is forbidden. All forbidden names: {FORBIDDEN_NAMES}")

        position = Bytes.from_snes_address(snes_address.replace("$", "")) if snes_address else position

        return cls(
            value=position,
            name=name,
        )

    def to_line(self, show_address: bool = False, **kwargs: Any) -> str:
        """
        Converts a Label into the exact string which will be put in a script to declare it.
        :param show_address: Whether the position of the label should be added. Usually added when there is a skip
        happening in the script.
        :return: A script line.
        """
        output = ""
        if show_address:
            output += "\n"
        output += f"@{str(self)}"
        output += f" = ${self.value.to_snes_address()}" if show_address else ""
        return output
