from typing import List, Union

from src.lib.structures import Bytes, Binary
from src.utils.ips.hunk import Hunk


class Ips:
    def __init__(self, hunks: List[Hunk] = None):
        self.hunks = hunks if hunks else []

    @classmethod
    def compare(cls, original_filename, destination_filename):
        with open(original_filename, "rb") as original_rom:
            original_bytes = original_rom.read()
        with open(destination_filename, "rb") as destination_rom:
            destination_bytes = destination_rom.read()
        file_size = min(len(original_bytes), len(destination_bytes), 0x03000000)
        streak, position, i = 0, 0, 0
        hunks = []
        while position < file_size:

            for i in range(position, file_size):
                if original_bytes[i] == destination_bytes[i]:
                    break
                streak += 1

            if streak:
                hunks.append(
                    Hunk(
                        offset=position,
                        payload=destination_bytes[position : position + streak],
                    )
                )

            position = i + 1
            streak = 0

        return cls(hunks)

    def to_file(self):
        output = b"PATCH"
        for hunk in self.hunks:
            output += bytes(hunk)
        output += b"EOF"
        return output

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, "rb") as patch:
            length = len(patch.read())
            if not cls.is_ips_format(patch, length):
                raise ValueError("The file provided is not of the IPS format.")
            binary_hunks = patch.read()[5:-3]
            position = 0
            hunks = []
            while position < len(binary_hunks):
                offset = binary_hunks[position : position + 3]
                if binary_hunks[position + 3 : position + 5] == b"\x00\x00":
                    payload = binary_hunks[position + 7] * int(
                        Bytes(
                            value=binary_hunks[position + 5 : position + 7],
                            length=2,
                            endianness="big",
                        )
                    )
                else:
                    payload = bytes(binary_hunks[position + 5]) * int(
                        Bytes(
                            value=binary_hunks[position + 3 : position + 5],
                            length=2,
                            endianness="big",
                        )
                    )
                hunk = Hunk(offset=offset, payload=payload)
                position += len(bytes(hunk))
                hunks.append(hunk)
        return cls(hunks)

    def apply(self):
        for hunk in self.hunks:
            start = int(hunk.offset)
            end = start + len(hunk)
            Binary()[start:end] = hunk.payload

    @classmethod
    def is_ips_format(cls, patch: Union[bytes, bytearray], length: int):
        patch.seek(0)
        if patch.read(5) != b"PATCH":
            return False
        patch.seek(length - 3)
        if patch.read() != b"EOF":
            return False
        patch.seek(0)
        return True

    def __str__(self):
        return "\n".join([f"{str(hunk)}\n" for hunk in self.hunks])

    def save_as(self, filename: str):
        with open(filename, "wb") as f:
            f.write(self.to_file())

    def rom_addresses(self):
        output = []
        for hunk in self.hunks:
            start = hunk.offset.to_address()
            if hunk.length == 1:
                output.append(start)
            else:
                end = Bytes(value=int(hunk.offset.value) + hunk.length - 1).to_address()
                output.append(f"{start}-{end}")
        return "\n".join(output)
