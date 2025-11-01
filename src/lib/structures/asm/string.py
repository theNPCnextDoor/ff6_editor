import re
from dataclasses import dataclass
from enum import Enum
from re import Match
from typing import Self

from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex, ToLineMixin
from src.lib.structures.bytes import BEBytes, Position, LEBytes

from src.lib.structures.charset.charset import Charset, MENU_CHARSET, DESCRIPTION_CHARSET


@dataclass
class StringType:
    prefix: str | None
    charset: Charset


class StringTypes:
    MENU = StringType(None, Charset(MENU_CHARSET))
    DESCRIPTION = StringType("txt2", Charset(DESCRIPTION_CHARSET))

    @classmethod
    def get_by_prefix(cls, prefix: str | None = None) -> StringType:
        for string_type in cls.__dict__.values():
            if isinstance(string_type, StringType) and string_type.prefix == prefix:
                return string_type
        else:
            raise ValueError(f"Prefix {prefix} is not recognized.")


class String(Blob, ToLineMixin):
    def __init__(
        self,
        data: BEBytes,
        position: Position | None = None,
        delimiter: LEBytes | None = None,
        charset: Charset | None = None,
        string_type: StringType | None = None,
    ):
        super().__init__(data=data, position=position, delimiter=delimiter)
        self.charset = charset or Charset(charset=MENU_CHARSET)
        self.string_type = string_type or StringTypes.MENU

    @classmethod
    def from_regex_match(cls, match: Match, position: Position | None = None) -> Self:
        value = match.group("s1") or match.group("s2")
        try:
            string_prefix = match.group("string_type")
        except IndexError:
            string_prefix = None
        string_type = StringTypes.get_by_prefix(string_prefix)
        delimiter = LEBytes.from_str(d) if (d := match.group("d2")) else None
        chars = re.findall(Regex.MENU_CHAR, value)
        data = b""
        for char in chars:
            data += string_type.charset.get_bytes(char)
        return cls(data=data, position=position, delimiter=delimiter, string_type=string_type)

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        position: Position | None = None,
        delimiter: bytes | None = None,
        string_type: StringType | None = None,
    ) -> Self:
        data = BEBytes.from_bytes(value=data)
        if delimiter is not None:
            delimiter = LEBytes.from_bytes(value=delimiter)
        return String(position=position, data=data, delimiter=delimiter, string_type=string_type)

    def __str__(self) -> str:
        output = ""

        if self.string_type and self.string_type.prefix:
            output = f"{self.string_type.prefix} "

        output += '"'
        for number in self.data.value:
            output += self.string_type.charset.get_char(value=number)
        output += '"'

        if self.delimiter is not None:
            output += f",${self.delimiter}"
        return output

    def __repr__(self) -> str:
        return f"{self.position}: {self}"

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output
