import random
from src.lib.structures.fields.byte_field import ByteField
from src.lib.game_lists import Esper, RomMap, RareItem, ChestType


class Treasure:
    x = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=0)
    y = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=1)
    identifier = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=2)
    kind = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=3)
    value = ByteField(base_location=RomMap.TREASURE_CHEST_LOCATION, position=4)

    def __init__(self, id: int):
        self.id = id

    def __len__(self):
        return 5

    def randomize(self, randomization="safe"):
        if randomization == "chaotic":
            self.kind = random.choice(ChestType.all())
            self.value = random.randint(0x00, 0xFF)
        elif randomization == "safe":
            if self.kind != ChestType.MIAB:
                self.kind = random.choice(ChestType.safe())
                if self.kind == ChestType.GOLD:
                    self.value = random.randint(0x01, 0xFF)
                elif self.kind == ChestType.ITEM:
                    self.value = random.randint(0x00, 0xFE)
                elif self.kind == ChestType.ESPER:
                    self.value = random.choice(Esper.all())
                else:
                    self.value = random.choice(RareItem.all())
