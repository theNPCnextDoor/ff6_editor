from src.lib.structures.fields import Binary, Bytes
from src.lib.game_lists import RomMap


class FieldDialog:
    data = bytearray()
    message = ""

    def __init__(self, id: int):
        self.id = id

    def __get__(self, instance, owner):
        first_dialog_in_second_bank = int(Bytes(Binary()[
            RomMap.DIALOG_POINTER_2ND_BANK_START:RomMap.DIALOG_POINTER_2ND_BANK_START + 1
        ], length=2, endianness="little"))
        start = RomMap.DIALOG_1ST_BANK + int(Bytes(Binary()[
           RomMap.DIALOG_POINTER_ADDRESS + self.id * 2
           ], length=2, endianness="little"))
        if self.id >= first_dialog_in_second_bank:
            start += 0x010000

