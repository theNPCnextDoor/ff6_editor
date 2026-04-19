import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

from src.lib.assembly.artifact.variable import Label, Variable
from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.bytes import Bytes
from src.lib.misc.exception import NoVariableException


class OperandType(Enum):
    """
    The operand type is used to define how to convert the destination associated to the label (when there is one)
    to the value of the operand and vice versa.
    """

    DEFAULT = auto()
    JUMPING = auto()
    LONG_JUMPING = auto()
    BRANCHING = auto()
    LONG_BRANCHING = auto()


@dataclass(order=True)
class Operand:
    """
    The operand is the part of an instruction containing the data.
    :param value: A Bytes object containing the data.
    :param mode: The mode is used by the processor in order to understand how to interpret the data of the instruction.
    :param operand_type: The OperandType. It is used to understand how to convert the value into the destination of the
    label, when there is one.
    """

    value: Bytes
    mode: str = "_"
    operand_type: OperandType = OperandType.DEFAULT
    variable: Variable | None = None

    @classmethod
    def from_string(
        cls,
        value: str,
        parent_position: Bytes | None = None,
        operand_type: OperandType = OperandType.DEFAULT,
        variables: Variables | None = None,
    ) -> Self:
        """
        Converts a string into an operand.
        :param value: The string to convert. It can represent a hexadecimal value or a variable, both encapsulated in
        the operand mode.
        :param parent_position: The position of the instruction containing the operand.
        :param operand_type: The type of the operand.
        :param variables: A list of existing variables and labels.
        :return: An operand.
        """
        parent_position = parent_position or Bytes.from_position(0)
        variables = variables or Variables()
        mode = cls._to_mode(value, operand_type)
        stripped_value = re.sub(r"[$.!#()\[\],SXY]", "", value)
        match = re.findall(r"[$.!]", value)

        value_type = match[0] if match else None

        if value_type == "$":
            operand = cls(value=Bytes.from_str(stripped_value), mode=mode, operand_type=operand_type)
            if len(operand) == 3 and 0xC00000 <= int(operand.value) <= 0xFFFFFF:
                operand.value -= 0xC00000
            return operand

        variable = variables.find_by_name(stripped_value)

        if variable is None:
            raise NoVariableException(f"Can't find variable named '{stripped_value}'.")

        if not isinstance(variable, Label):
            return cls(value=variable.value, mode=mode, operand_type=operand_type, variable=variable)

        if value_type == ".":
            length = 1
        elif value_type == "!":
            length = 2
        else:
            length = 3

        destination = variable.position
        if length != 1 and not cls._is_destination_possible(
            parent_position=parent_position, destination=destination, length=length
        ):
            raise ValueError(
                f"Destination {repr(destination)} impossible from parent position {repr(parent_position)}."
            )

        operand_value = cls._destination_to_value(
            parent_position=parent_position, operand_type=operand_type, length=length, destination=destination
        )
        return cls(value=operand_value, mode=mode, operand_type=operand_type, variable=variable)

    @classmethod
    def from_bytes(
        cls,
        value: bytes,
        mode: str,
        operand_type: OperandType,
        parent_position: Bytes,
        variables: Variables | None = None,
    ) -> Self:
        """
        Converts bytes into an operand.
        :param value: A bytes array representing the data of the operand.
        :param mode: The mode is used by the processor in order to understand how to interpret the data of the
        instruction.
        :param operand_type: The type of the operand.
        :param parent_position: The position of the instruction containing the operand.
        :param variables: A list of existing variables and labels.
        :return: An operand.
        """
        variables = variables or Variables()
        value = Bytes.from_bytes(value)

        if operand_type == OperandType.DEFAULT and len(value) != 3:
            return cls(value=value, operand_type=operand_type, mode=mode)

        if 0xC00000 <= int(value) <= 0xFFFFFF:
            value -= 0xC00000

        operand = cls(value=value, operand_type=operand_type, mode=mode)
        destination = operand.value_to_destination(parent_position=parent_position)

        operand.variable = variables.find_by_position(destination)
        if operand.variable is None:
            operand.variable = Label(destination)

        return operand

    @staticmethod
    def _to_mode(value: str, operand_type: OperandType) -> str:
        """
        Extracts the mode out of the operand string, except for branching and long branching operands, where it is fixed
        to "_".
        :param value: The operand string.
        :param operand_type: The operand type.
        :return: The mode.
        """
        if operand_type in (OperandType.BRANCHING, OperandType.LONG_BRANCHING):
            return "_"
        return re.sub(r"[$.!A-F0-9a-z_]+", "_", value)

    @staticmethod
    def _destination_to_value(
        parent_position: Bytes, operand_type: OperandType, length: int, destination: Bytes
    ) -> Bytes:
        """
        Converts the destination of the operand into its value.
        :param parent_position:
        :param operand_type:
        :param length:
        :param destination:
        :return:
        """
        if operand_type == OperandType.BRANCHING:
            return Bytes.from_int((int(destination) - int(parent_position) - 2) % 0x0100)
        if operand_type == OperandType.LONG_BRANCHING:
            return Bytes.from_int(((int(destination) - int(parent_position) - 3) % 0x010000), length=2)
        if length == 1:
            return destination[0:1]

        if length == 2:
            return Bytes.from_other(destination, length=2)

        return destination

    def value_to_destination(self, parent_position: Bytes) -> Bytes:
        if self.operand_type == OperandType.BRANCHING:
            return Bytes.from_position((int(self.value) + 0x80) % 0x0100 + int(parent_position) - 0x7E)
        if self.operand_type == OperandType.LONG_BRANCHING:
            return Bytes.from_position(
                int(parent_position.bank()) + (int(parent_position) + int(self.value) + 3) % 0x010000
            )

        if len(self) == 3:
            return self.value
        if len(self) == 2:
            bank = parent_position.bank()
            return Bytes.from_position(int(self.value) + bank)
        raise ValueError("Can't find the destination.")

    def __len__(self) -> int:
        return len(self.value)

    def __bytes__(self) -> bytes:
        value = self.value[:]
        if (
            isinstance(self.variable, Label)
            and 0 <= int(self.variable.value) <= 0x3FFFFF
            and self.operand_type not in (OperandType.BRANCHING, OperandType.LONG_BRANCHING)
        ):
            if len(value) == 1:
                value += 0xC0
            elif len(value) == 3:
                value += 0xC00000
        return bytes(value)

    def __str__(self) -> str:
        if self.variable is None:
            value = self.value[:]
            if len(self.value) == 3 and 0 <= int(self.value) <= 0x3FFFFF:
                value += 0xC00000
            return self.mode.replace("_", f"${str(value)}")
        if (
            isinstance(self.variable, Label)
            and self.operand_type not in (OperandType.BRANCHING, OperandType.LONG_BRANCHING)
            and len(self.value) != 3
        ):
            prefix = "." if len(self.value) == 1 else "!"
            return self.mode.replace("_", f"{prefix}{self.variable.name}")
        return self.mode.replace("_", f"{self.variable.name}")

    def __repr__(self):
        output = f"Operand(value=0x{str(self.value)}, mode='{self.mode}', operand_type={self.operand_type}"
        if self.variable:
            output += f", variable={repr(self.variable)}"
        output += ")"
        return output

    @staticmethod
    def _is_destination_possible(
        parent_position: Bytes, length: int, destination: Bytes, operand_type: OperandType | None = None
    ) -> bool:
        if length == 3:
            return True
        if length == 2:
            return parent_position.bank() == destination.bank()
        return int(parent_position) - 0x7E <= int(destination) <= int(parent_position) + 0x81
