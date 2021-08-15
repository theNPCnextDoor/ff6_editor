from typing import Union

from src.lib.structures import Bytes


class Hunk:
    def __init__(
        self,
        offset: Union[Bytes, int, bytes, bytearray],
        payload: Union[bytes, bytearray],
    ):
        self.offset = Bytes(value=offset, length=3, endianness="big")
        self.payload = payload

    @property
    def length(self):
        return len(self.payload)

    def is_compressible(self):
        for i in range(len(self.payload) - 1):
            if self.payload[i] != self.payload[i + 1]:
                return False
        return True

    def __bytes__(self):
        output = bytearray(bytes(self.offset))
        if self.is_compressible():
            output += b"\x00\x00"
            output += bytes(Bytes(value=self.length, length=2, endianness="big"))
            output.append(self.payload[0])
        else:
            output += bytes(Bytes(value=self.length, length=2, endianness="big"))
            output += self.payload
        return bytes(output)

    def __str__(self):
        return f"{self.offset} {self.length} {self.payload.hex().upper()}"
