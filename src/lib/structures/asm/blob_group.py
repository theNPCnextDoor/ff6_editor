from re import Match
import re
from typing import Self

from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex, ToLineMixin
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.asm.string import String
from src.lib.structures.bytes import Bytes
from src.lib.structures.charset.charset import Charset
from src.lib.misc.exception import UnrecognizedBlob


class BlobGroup(ScriptLine, ToLineMixin):

    def __init__(self, blobs: list[Blob] | None = None, position: Bytes | None = None):
        super().__init__(position=position)
        self.blobs = blobs or list()

    @classmethod
    def from_regex_match(cls, match: Match, position: Bytes | None = None, charset: Charset | None = None) -> Self:
        parts = [part.strip() for part in match.group(0).split("|")]
        cursor = int(position)
        blobs = list()

        for i, part in enumerate(parts):
            cleaned_part = re.sub(' #[^"]*$', "", part)

            if blob_match := re.search(Regex.MENU_STRING, cleaned_part):
                blob = String.from_regex_match(blob_match, position=Bytes.from_position(cursor))

            elif blob_match := re.search(Regex.BLOB, cleaned_part):
                blob = Blob.from_regex_match(blob_match, position=Bytes.from_position(cursor))

            else:
                raise UnrecognizedBlob(f"Blob part {i} is unrecognized.\n{cleaned_part=}\n{match.group(0)}")
            blobs.append(blob)
            cursor += len(blob)
        return cls(blobs=blobs, position=position)

    def __str__(self) -> str:
        return " | ".join([str(blob) for blob in self.blobs])

    def __repr__(self) -> str:
        return f"{self.blobs[0].position}: {self}"

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output

    def __len__(self) -> int:
        return sum([len(blob) for blob in self.blobs])

    def __bytes__(self) -> bytes:
        return b"".join([bytes(blob) for blob in self.blobs])
