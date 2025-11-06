import os

from src.lib.game_structures.field_dialog import FieldDialog
from src.lib.game_structures.monster import Monster
from src.lib.structures import Binary, Transcript
from src.lib.structures import Array
from src.lib.game_structures import Treasure, GeneralAction
from src.lib.game_lists import RomMap


class Rom:
    def __init__(self, filename: str, header: bool = False):
        self.filename = filename
        with open(self.filename, "rb") as f:
            self.file = Binary(bytearray(f.read()))
        self.treasures = Array(cls=Treasure, quantity=RomMap.TREASURE_CHEST_QUANTITY)
        self.monsters = Array(cls=Monster, quantity=RomMap.MONSTER_QUANTITY)
        self.general_actions = Array(cls=GeneralAction, quantity=0x0100 - 0x0035)
        self.header = header
        self.dialogs = Transcript(cls=FieldDialog, quantity=RomMap.DIALOG_QUANTITY)
        self.scripts = []

    def save(self):
        self.save_as(self.filename)

    def save_as(self, filename: str):
        with open(filename, "wb") as f:
            if self.header:
                f.write(b"\x00" * 0x200)
            f.write(self.file)

    def add_header(self, strict=True):
        if strict:
            header_size = len(self.file) % (1024 * 1024)
            if header_size == 0x200:
                raise ValueError("File size suggests that the rom already has a header.")
            elif header_size:
                raise ValueError("File size suggests unconventional file size.")
        self.header = True

    def remove_header(self, strict=True):
        if strict:
            header_size = len(self.file) % (1024 * 1024)
            if not header_size:
                raise ValueError("File size suggests that the rom already has no header.")
            elif header_size != 0x200:
                raise ValueError("File size suggests unconventional file size.")

        self.header = False

    @classmethod
    def expand(cls, filename: str) -> None:
        size = os.path.getsize(filename)
        with open(filename, "rb+") as f:
            f.read()
            f.write(b"\xff" * (0x400000 - size))
