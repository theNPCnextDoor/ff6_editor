from src.lib.structures import Binary, Bytes


class Pointer:
    def __init__(self):
        pass

    def __get__(self, instance, owner):
        start = instance.pointer_location + 2 * instance.id
        address = int(Bytes(Binary()[start : start + 2], length=2, endianness="little"))
        return address

    def __set__(self, instance, value):
        value %= 0x010000
        start = instance.pointer_location + 2 * instance.id
        Binary()[start : start + 2] = bytes(Bytes(value, length=2, endianness="little"))
