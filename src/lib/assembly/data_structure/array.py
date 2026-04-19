import re
from typing import Self

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.artifact.variable import Label
from src.lib.assembly.data_structure.regex import Regex
from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.assembly.data_structure.string.string import String
from src.lib.assembly.bytes import Bytes
from src.lib.misc.exception import UnrecognizedBlob


class Array(DataStructure):

    def __init__(self, blobs: list[Blob] | None = None, position: Bytes | None = None):
        super().__init__(position=position)
        self.blobs = blobs or list()

    @classmethod
    def from_string(cls, line: str, position: Bytes | None = None, variables: Variables | None = None) -> Self:
        variables = variables or Variables()
        parts = [part.strip() for part in line.split("|")]
        cursor = int(position)
        blobs = list()

        for i, part in enumerate(parts):
            cleaned_part = re.sub(' #[^"]*$', "", part)

            if blob_match := re.search(Regex.STRING, cleaned_part):
                blob = String.from_string(
                    string=blob_match.group("string"),
                    string_type=blob_match.group("string_type"),
                    delimiter=blob_match.group("delimiter"),
                    position=Bytes.from_position(cursor),
                    variables=variables,
                )

            elif blob_match := re.search(Regex.BLOB, cleaned_part):
                blob = Blob.from_string(
                    operand=blob_match.group("operand"),
                    delimiter=blob_match.group("delimiter"),
                    position=Bytes.from_position(cursor),
                    variables=variables,
                )

            else:
                raise UnrecognizedBlob(f"Blob part {i} is unrecognized.\n{cleaned_part=}\n{line}")
            blobs.append(blob)
            cursor += len(blob)
        return cls(blobs=blobs, position=position)

    def __str__(self) -> str:
        return " | ".join([str(blob) for blob in self.blobs])

    def __repr__(self) -> str:
        hexa = ""
        for blob in self.blobs:
            hexa += str(blob.operand.value)
        blobs_output = ", ".join(repr(blob) for blob in self.blobs)
        return f"Array(position=0x{self.position}, as_str='{str(self)}', as_bytes={bytes(self)}, as_hexa=0x{hexa}, blobs=[{blobs_output}])"

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output

    def __len__(self) -> int:
        return sum([len(blob) for blob in self.blobs])

    def __bytes__(self) -> bytes:
        return b"".join([bytes(blob) for blob in self.blobs])
