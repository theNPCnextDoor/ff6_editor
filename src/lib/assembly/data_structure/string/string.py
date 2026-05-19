import re
from dataclasses import dataclass
from typing import Self, Any

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.bytes import Bytes, Endian
from src.lib.assembly.data_structure.regex import Regex

from src.lib.assembly.data_structure.string.charset import Charset, MENU_CHARSET, DESCRIPTION_CHARSET
from src.lib.misc.exception import DelimiterLengthError


@dataclass
class StringType:
    """
    StringTypes helps determine how to parse a string in a script. The prefix is a word that precedes the string in a
    script line, such as "desc" for menu descriptions for example. The corresponding charset will be used to parse the
    string.
    """

    prefix: str | None
    charset: Charset


class StringTypes:
    MENU = StringType(None, Charset(MENU_CHARSET))
    DESCRIPTION = StringType("desc", Charset(DESCRIPTION_CHARSET))

    @classmethod
    def get_by_prefix(cls, prefix: str | None = None) -> StringType:
        """
        Determines the StringType by the script line prefix.
        :param prefix: The word that precedes the string in a script line, such as "desc".
        :return: A StringType.
        :raise ValueError: Raised when the prefix is unrecognized.
        """
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
    def from_line(
        cls,
        string: str,
        string_type: str | None = None,
        delimiter: str | None = None,
        position: Bytes | None = None,
        variables: Variables | None = None,
    ) -> Self:
        """
        Converts a script line into a String.
        :param string: The actual string part of the line.
        :param string_type: The StringType of the line to determine how to convert the String into bytes.
        :param delimiter: The byte that helps determine where the String ends in-game.
        :param position: The position of the String in the ROM.
        :param variables: The list of Variables used to determine the value of the delimiter, if needed.
        :return: A String.
        :raises DelimiterLengthError: Raised when there is a variable delimiter, but the variable doesn't have a length of 1.
        """
        _string_type = StringTypes.get_by_prefix(string_type)
        chars = re.findall(Regex.CHAR, string)
        data = b""

        simple_vars = variables.simple_variables if variables else None

        _delimiter = (
            Operand.from_line(value=delimiter, variables=simple_vars, parent_position=position) if delimiter else None
        )

        if _delimiter and len(_delimiter) != 1:
            raise DelimiterLengthError(f"Delimiter '{str(delimiter)}' must have a length of one.")

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
        """
        Converts bytes into a String.
        :param data: The bytes to be converted.
        :param position: The position of the String.
        :param delimiter: The byte that helps determine where the String ends in-game.
        :param string_type: The StringType of the line to determine how to convert the bytes into a String.
        :return: A String.
        """
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

    def to_line(self, show_address: bool = False, **kwargs: Any) -> str:
        """
        Converts a String into a script line.
        :param show_address: Whether the position of the script line will be added as a comment.
        :param kwargs: Unused. Added to prevent errors.
        :return: A script line.
        """
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output

    @classmethod
    def find_length(cls, string: str, delimiter: str | None = None) -> int:
        """
        Determines the length of the script line in number of bytes during the pre-parsing phase.
        :param string: The actual string of the script line.
        :param delimiter: The delimiter part of the script line, if it exists. Adds one to the length.
        :return: The number of bytes contained in the String.
        """
        length = len(re.findall(Regex.CHAR, string))
        if delimiter:
            length += 1
        return length
