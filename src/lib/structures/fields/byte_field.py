from src.lib.structures import Bytes
from src.lib.structures import Binary


class ByteField:
    def __init__(
        self,
        base_location,
        position: int,
        length: int = 1,
        endianness: str = "little",
    ):
        self.base_location = base_location
        self.length = length
        self.endianness = endianness
        self.position = position

    def __get__(self, instance, owner):
        start = self.start(instance)
        output = Binary()[start : start + self.length]
        return Bytes(value=output, length=self.length, endianness=self.endianness)

    def start(self, instance):
        return self.base_location + len(instance) * instance.id + self.position

    def __set__(self, instance, value):
        value = Bytes(value=value, length=self.length, endianness=self.endianness)
        start = self.start(instance)
        Binary()[start : start + self.length] = bytes(value)
