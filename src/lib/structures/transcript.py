from src.lib.game_lists import RomMap
from src.lib.game_structures.field_dialog import FieldDialog
from src.lib.structures import Array


class Transcript(Array):
    def __setitem__(self, key, value):
        FieldDialog(id=key).message = value

    def append(self, message):
        last_dialog = FieldDialog(id=RomMap.DIALOG_QUANTITY)
        length = len(last_dialog)
        RomMap.DIALOG_QUANTITY += 1
        new_dialog = FieldDialog(id=RomMap.DIALOG_QUANTITY)
        new_dialog.pointer = last_dialog.pointer + length
        new_dialog.message = message
