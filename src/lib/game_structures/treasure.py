import random
from src.lib.structures.fields.byte_field import ByteField
from src.lib.game_lists import Espers, RomMap
from src.lib.game_lists import RareItems
from src.lib.game_lists import ChestTypes


class Treasure:
    x = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=0)
    y = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=1)
    identifier = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=2)
    sort = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=3)
    value = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=4)

    def __init__(self, id: int):
        self.id = id

    def __len__(self):
        return 5

    def randomize(self, randomization="chaotic"):
        if randomization == "chaotic":
            self.sort = random.choice(ChestTypes.all())
            self.value = random.randint(0x00, 0xFF)
        elif randomization == "safe":
            if self.sort != ChestTypes.MIAB:
                self.sort = random.choice(ChestTypes.safe())
                if self.sort == ChestTypes.GOLD:
                    self.value = random.randint(0x01, 0xFF)
                elif self.sort == ChestTypes.ITEM:
                    self.value = random.randint(0x00, 0xFE)
                elif self.sort == ChestTypes.ESPER:
                    self.value = random.choice(Espers.all())
                else:
                    self.value = random.choice(RareItems.all())
