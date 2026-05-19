import re
from typing import Self, Any

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.regex import DataStructureRegex
from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.assembly.data_structure.string.string import String
from src.lib.assembly.bytes import Bytes
from src.lib.misc.exception import UnrecognizedBlob


class Array(DataStructure):
    """
    An Array is a group of Blobs and Strings assembled in a single script line for convenience. It can be used to
    define, for example, a Menu String alongside its coordinates of the screen.
    """

    def __init__(self, parts: list[Blob] | None = None, position: Bytes | None = None):
        super().__init__(position=position)
        self.parts = parts or list()

    @classmethod
    def from_line(cls, line: str, position: Bytes | None = None, variables: Variables | None = None) -> Self:
        """
        Converts a script line into an Array. Each part will be parsed separately.
        :param line: The script line.
        :param position: The position of the line in the script.
        :param variables: The list of Variables that will be used to determine the value of Blobs and delimiters.
        :return: An Array.
        """
        parts = [part.strip() for part in line.split("|")]
        cursor = int(position)
        blobs = list()

        for i, part in enumerate(parts):
            cleaned_part = re.sub(' [^"]+$', "", part.strip())

            if blob_match := re.search(DataStructureRegex.STRING, cleaned_part):
                blob = String.from_line(
                    string=blob_match.group("string"),
                    string_type=blob_match.group("string_type"),
                    delimiter=blob_match.group("delimiter"),
                    position=Bytes.from_position(cursor),
                    variables=variables.simple_variables,
                )

            elif blob_match := re.search(DataStructureRegex.BLOB, cleaned_part):
                blob = Blob.from_line(
                    operand=blob_match.group("operand"),
                    delimiter=blob_match.group("delimiter"),
                    position=Bytes.from_position(cursor),
                    variables=variables,
                )

            else:
                raise UnrecognizedBlob(f"Blob part {i} is unrecognized.\n{cleaned_part=}\n{line}")
            blobs.append(blob)
            cursor += len(blob)
        return cls(parts=blobs, position=position)

    @classmethod
    def from_bytes(cls, *args, **kwargs) -> Self:
        raise ValueError("An Array must be built by appending Blobs and Strings.")

    def __str__(self) -> str:
        return " | ".join([str(blob) for blob in self.parts])

    def __repr__(self) -> str:
        hexa = ""
        for blob in self.parts:
            hexa += str(blob.operand.value)
        blobs_output = ", ".join(repr(blob) for blob in self.parts)
        return (
            f"Array(position=0x{self.position}, as_str='{str(self)}', as_bytes={bytes(self)}, as_hexa=0x{hexa}, "
            f"parts=[{blobs_output}])"
        )

    def to_line(self, show_address: bool = False, **kwargs: Any) -> str:
        """
        Converts an Array into the exact string which will be put in a script to declare it. It will match
        against DataStructureRegex.ARRAY.
        :param show_address:
        :param kwargs: Unused. Included to prevent errors.
        :return: A script line.
        """
        output = f"  {self}"
        if show_address:
            output += f" ; {self.position.to_snes_address()}"
        return output

    def __len__(self) -> int:
        return sum([len(part) for part in self.parts])

    def __bytes__(self) -> bytes:
        return b"".join([bytes(part) for part in self.parts])
