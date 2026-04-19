from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.instruction.operand import Operand, OperandType
from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.assembly.bytes import Bytes

if TYPE_CHECKING:
    from src.lib.assembly.artifact.variable import Label


class Blob(DataStructure):
    def __init__(self, operand: Operand, position: Bytes | None = None, delimiter: Operand | None = None):
        super().__init__(position=position)
        self.operand = operand
        self.delimiter = delimiter

    @classmethod
    def from_string(
        cls,
        operand: str,
        delimiter: str | None = None,
        position: Bytes | None = None,
        variables: Variables | None = None,
    ) -> Self:
        variables = variables or list()
        _operand = Operand.from_string(operand, position, OperandType.DEFAULT, variables)
        _delimiter = Operand.from_string(delimiter, position, OperandType.DEFAULT, variables) if delimiter else None

        if _delimiter and len(_delimiter) != 1:
            raise ValueError(f"Delimiter '{str(delimiter)}' must have a length of one.")

        return cls(position=position, operand=_operand, delimiter=_delimiter)

    @classmethod
    def from_bytes(cls, data: bytes, position: Bytes | None = None, delimiter: bytes | None = None) -> Self:
        data = Operand(Bytes.from_bytes(data))
        if delimiter is not None:
            delimiter = Operand(Bytes.from_bytes(delimiter))
        return Blob(position=position, operand=data, delimiter=delimiter)

    def __str__(self) -> str:
        output = f"{self.operand}"
        if self.delimiter is not None:
            output += f",{self.delimiter}"
        return output

    def __repr__(self) -> str:
        hexa = str(self.operand.value) + (str(self.delimiter.value) if self.delimiter else "")
        output = f"Blob(position=0x{self.position}, as_str='{str(self)}', as_bytes={bytes(self)}, as_hexa=0x{hexa}"
        if self.operand.variable:
            output += f", operand_var={repr(self.operand.variable)}"
        if self.delimiter and self.delimiter.variable:
            output += f", delimiter_var={repr(self.delimiter.variable)}"
        output += ")"
        return output

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output

    def __len__(self) -> int:
        output = len(self.operand)
        output += 1 if self.delimiter is not None else 0
        return output

    def __bytes__(self) -> bytes:
        output = bytes(self.operand)
        if self.delimiter is not None:
            output += bytes(self.delimiter)
        return output

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position and self.operand == other.operand and self.delimiter == other.delimiter
