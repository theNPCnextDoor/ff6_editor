

class RareItems:
    CIDER = 0x00
    OLD_CLOCK_KEY = 0x01
    FISH_0X02 = 0x02
    FISH_0X03 = 0x03
    FISH_0X04 = 0x04
    FISH_0X05 = 0x05
    LUMP_OF_METAL = 0x06
    LOLA_S_LETTER = 0x07
    CORAL = 0x08
    BOOKS = 0x09
    ROYAL_LETTER = 0x0A
    RUST_RID = 0x0B
    AUTOGRAPH = 0x0C
    MANICURE = 0x0D
    OPERA_RECORD = 0x0E
    MAGN_GLASS = 0x0F
    EERIE_STONE = 0x10
    ODD_PICTURE = 0x11
    DULL_PICTURE = 0x12
    PENDANT = 0x13

    @classmethod
    def all(cls):
        rare_items = list(range(cls.PENDANT + 1))
        del rare_items[cls.CORAL]
        return rare_items
