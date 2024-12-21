import re
from re import Match
from typing import Self

from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import BlobBytes, Position, Bytes

from src.lib.structures.charset.charset import Charset, MENU_CHARSET


class String(Blob):
    def __init__(
        self,
        data: BlobBytes,
        position: Position | None = None,
        delimiter: Bytes | None = None,
        charset: Charset | None = None,
    ):
        super().__init__(data=data, position=position, delimiter=delimiter)
        self.charset = charset or Charset(charset=MENU_CHARSET)

    @classmethod
    def from_regex_match(cls, match: Match, position: Position | None = None, charset: Charset | None = None) -> Self:
        value = match.group("s1") or match.group("s2")
        charset = charset or Charset(charset=MENU_CHARSET)
        delimiter = Bytes(match.group("delimiter"))
        chars = re.findall(Regex.MENU_CHAR, value)
        data = b""
        for char in chars:
            data += charset.get_bytes(char)
        return cls(data=data, position=position, delimiter=delimiter, charset=charset)

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        position: Position | None = None,
        delimiter: bytes | None = None,
        charset: Charset | None = None,
    ) -> Self:
        data = BlobBytes(value=data)
        if delimiter is not None:
            delimiter = Bytes(value=delimiter)
        return String(position=position, data=data, delimiter=delimiter, charset=charset)

    def __str__(self) -> str:
        output = '"'
        for number in self.data:
            output += self.charset.get_char(value=int(number))
        output += '"'
        if self.delimiter is not None:
            output += f" ${self.delimiter}"
        return output

    def __repr__(self):
        return f"{self.position}: {self}"
