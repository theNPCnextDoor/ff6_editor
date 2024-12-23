from src.lib.game_lists import RomMap
from src.lib.game_lists.dte import FieldDte
from src.lib.structures import Binary, Bytes, Pointer
from src.lib.structures.fields import DialogField


class FieldDialog:
    pointer = Pointer()
    message = DialogField()
    pointer_location = RomMap.DIALOG_POINTER_ADDRESS
    end = RomMap.DIALOG_POINTER_2ND_BANK
    dte = FieldDte

    def __init__(self, id: int):
        self.id = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value
        self.dialog_location = RomMap.DIALOG_1ST_BANK
        if value >= int(
            Bytes(
                Binary()[
                    RomMap.DIALOG_POINTER_2ND_BANK : RomMap.DIALOG_POINTER_2ND_BANK + 2
                ],
                length=2,
                endianness="little",
            )
        ):
            self.dialog_location += 0x010000

    def __str__(self):
        return self.dte.to_string(self.message)

    @property
    def address(self):
        return self.dialog_location + self.pointer

    @property
    def available_space(self):
        if self.id < RomMap.DIALOG_QUANTITY:
            return self.__class__(id=self.id + 1).address - self.address
        else:
            return RomMap.DIALOG_2ND_BANK_END - self.address

    def __len__(self):
        start = self.address
        end = self.end_address(start)
        return end - start

    def end_address(self, start):
        end = start + self.available_space
        for i in range(self.available_space):
            next_byte = Binary()[start + i]

            if next_byte == 0:
                end = start + i + 1
                break
            elif ": _" in self.dte.char_map[next_byte]:
                i += 1
        return end
