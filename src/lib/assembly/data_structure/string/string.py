import re
from dataclasses import dataclass
from typing import Self

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.artifact.variable import Label
from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.bytes import Bytes, Endian
from src.lib.assembly.data_structure.regex import Regex

from src.lib.assembly.data_structure.string.charset import Charset, MENU_CHARSET, DESCRIPTION_CHARSET


@dataclass
class StringType:
    prefix: str | None
    charset: Charset


class StringTypes:
    MENU = StringType(None, Charset(MENU_CHARSET))
    DESCRIPTION = StringType("desc", Charset(DESCRIPTION_CHARSET))

    @classmethod
    def get_by_prefix(cls, prefix: str | None = None) -> StringType:
        for string_type in cls.__dict__.values():
            if isinstance(string_type, StringType) and string_type.prefix == prefix:
                return string_type
        else:
            raise ValueError(f"Prefix {prefix} is not recognized.")


class String(Blob):
    def __init__(
        self,
        operand: Operand,
        position: Bytes | None = None,
        delimiter: Operand | None = None,
        charset: Charset | None = None,
        string_type: StringType | None = None,
    ):
        super().__init__(operand=operand, position=position, delimiter=delimiter)
        self.charset = charset or Charset(charset=MENU_CHARSET)
        self.string_type = string_type or StringTypes.MENU

    @classmethod
    def from_string(
        cls,
        string: str,
        string_type: str | None = None,
        delimiter: str | None = None,
        position: Bytes | None = None,
        variables: Variables | None = None,
    ) -> Self:
        _string_type = StringTypes.get_by_prefix(string_type)
        chars = re.findall(Regex.CHAR, string)
        data = b""
        _delimiter = (
            Operand.from_string(value=delimiter, variables=variables, parent_position=position) if delimiter else None
        )
        for char in chars:
            data += _string_type.charset.get_bytes(char)
        data_bytes = Operand(Bytes.from_bytes(value=data, endian=Endian.BIG))
        return cls(operand=data_bytes, position=position, delimiter=_delimiter, string_type=_string_type)

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        position: Bytes | None = None,
        delimiter: bytes | None = None,
        string_type: StringType | None = None,
    ) -> Self:
        data = Operand(Bytes.from_bytes(value=data, endian=Endian.BIG))
        if delimiter is not None:
            delimiter = Operand(Bytes.from_bytes(value=delimiter))
        return String(position=position, operand=data, delimiter=delimiter, string_type=string_type)

    def __str__(self) -> str:
        output = ""

        if self.string_type and self.string_type.prefix:
            output = f"{self.string_type.prefix} "

        output += '"'
        for number in self.operand.value.value:
            output += self.string_type.charset.get_char(value=number)
        output += '"'

        if self.delimiter is not None:
            output += f",{self.delimiter}"
        return output

    def __repr__(self) -> str:
        hexa = str(self.operand.value) + (str(self.delimiter.value) if self.delimiter else "")
        output = f"String(position=0x{self.position}, as_str='{str(self)}', as_bytes={bytes(self)}, as_hexa=0x{hexa}"
        if self.delimiter and self.delimiter.variable:
            output += f", delimiter_var={repr(self.delimiter.variable)}"
        output += ")"
        return output

    def __eq__(self, other: Self) -> bool:
        return self.position == other.position and self.operand == other.operand

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output
