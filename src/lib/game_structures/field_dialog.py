from resources.char_tables.field_dialog_table import FieldDialogTable
from rom_editor.field_dialog import Dialog
from tools.functions import int2byte, byte2int


class FieldDialog(Dialog):
    CHAR_TABLE = FieldDialogTable

    def __init__(
        self,
        id,
        char_table=None,
        message=None,
        length=None,
        uncompressed_binary=None,
        ending_character=b'\x00'
    ):
        if not char_table and not self.__class__.CHAR_TABLE:
            raise ValueError("Please select a character table for this Dialog.")
        self.id = id
        self.pointer_position = self.id * 2 + self.DIALOG_POINTER_ADDRESS
        self.pointer = byte2int(self.rom.read(self.pointer_position, 2))
        self._message = message
        self._raw = None
        self.length = length
        self.ending_character = ending_character
        super().__init__()

    def read(self):
        position = self.pointer
        position += self.DIALOG_1ST_BANK if self.id < self.second_bank_first_id else self.DIALOG_2ND_BANK
        self.rom.seek(position)
        char = b''
        message = ''
        raw = b''
        while char != self.ending_character:
            char = self.rom.read()
            raw += char
            message += self.CHAR_TABLE.convert(char)
        self._raw = raw
        return message

    def write(self):
        self.rom.seek(self.pointer_position)
        self.rom.write(int2byte(self.pointer))
        position = self.pointer

        # if self.id >

    @property
    def second_bank_first_id(self):
        return byte2int(self.rom.read(self.POINTER_2ND_BANK_START, 2))

