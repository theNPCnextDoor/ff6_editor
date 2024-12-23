from src.lib.game_lists import RomMap
from src.lib.structures import Pointer


class GeneralAction:
    pointer = Pointer()
    pointer_location = RomMap.GENERAL_ACTION_POINTER_ADDRESS - RomMap.GENERAL_ACTION_FIRST_INDEX * 2

    def __init__(self, id: int):
        self.id = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: int):
        if not (0x35 <= value <= 0xFF):
            raise IndexError("General Action index must be between 0x35 and 0xFF inclusively.")
        self._id = value
