import re

from src.lib.structures.fields import Bytes, Binary
from src.lib.game_lists import RomMap


class FieldDialogField:

    def __init__(self, base_location, dte: str, ending_character: bytes = b'\x00'):
        self.base_location = base_location
        self.ending_character = ending_character
        self.dte = dte
        # self.strict = strict

    def __get__(self, instance, owner):
        start = self.base_location + int(Bytes(value=Binary()[RomMap.DIALOG_POINTER_ADDRESS + instance.id * 2]))
        end = start + instance.max_length
        return Binary()[start:end]

    def __set__(self, instance, value):
        if type(value) in (Bytes, bytes, bytearray):
            if len(bytes(value)) > instance.max_length:
                raise ValueError("The new dialog takes more space than the previous")
        else:
            value = self.convert(value)
        start = self.base_location + int(Bytes(value=Binary()[RomMap.DIALOG_POINTER_ADDRESS + instance.id * 2]))
        end = start + instance.max_length
        Binary()[start:end] = value

    def __str__(self):
        pass

    def to_bytes(self, value: str):
        position = 0
        output = b''
        consecutive_spaces = re.search(r"^( +)", value[position:])
        output += b''

        if position <= len(value) - 2:
            next_two_characters = value[position: position + 2]


