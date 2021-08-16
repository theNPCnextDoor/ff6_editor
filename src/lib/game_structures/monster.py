from src.lib.game_lists import RomMap
from src.lib.structures.fields import ByteField
from src.lib.structures.fields.bit_field import BitField


class Monster:
    speed = ByteField(base_location=RomMap.MONSTER_DATA, position=0x00)
    vigor = ByteField(base_location=RomMap.MONSTER_DATA, position=0x01)
    hit_rate = ByteField(base_location=RomMap.MONSTER_DATA, position=0x02)
    evade_rate = ByteField(base_location=RomMap.MONSTER_DATA, position=0x03)
    magic_block_rate = ByteField(base_location=RomMap.MONSTER_DATA, position=0x04)
    defense = ByteField(base_location=RomMap.MONSTER_DATA, position=0x05)
    magic_defense = ByteField(base_location=RomMap.MONSTER_DATA, position=0x06)
    magic_power = ByteField(base_location=RomMap.MONSTER_DATA, position=0x07)
    hp = ByteField(base_location=RomMap.MONSTER_DATA, length=2, position=0x08)
    mp = ByteField(base_location=RomMap.MONSTER_DATA, length=2, position=0x0A)
    xp = ByteField(base_location=RomMap.MONSTER_DATA, length=2, position=0x0C)
    gold = ByteField(base_location=RomMap.MONSTER_DATA, length=2, position=0x0E)
    level = ByteField(base_location=RomMap.MONSTER_DATA, length=2, position=0x10)
    morph_pack = BitField(base_location=RomMap.MONSTER_DATA, position=0x11, bit_value=0x1F)
    morph_hit_rate = BitField(base_location=RomMap.MONSTER_DATA, position=0x11, bit_value=0xE0)
    death_at_0_mp = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x01)
    byte_12_bit_1 = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x02)
    no_name = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x04)
    byte_12_bit_3 = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x08)
    human = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x10)
    byte_12_bit_5 = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x20)
    crit_if_imp = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x40)
    undead = BitField(base_location=RomMap.MONSTER_DATA, position=0x12, bit_value=0x80)
    harder_to_run = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x01)
    attack_first = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x02)
    no_suplex = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x04)
    no_run = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x08)
    no_scan = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x10)
    no_sketch = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x20)
    special_event = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x40)
    no_control = BitField(base_location=RomMap.MONSTER_DATA, position=0x13, bit_value=0x80)

    def __init__(self, id: int):
        self.id = id

    def __len__(self):
        return 20
