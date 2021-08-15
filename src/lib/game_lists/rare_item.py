class RareItem:
    CIDER = 0x00
    OLD_CLOCK_KEY = 0x01
    YUMMY_FISH = 0x02
    JUST_A_FISH = 0x03
    ROTTEN_FISH = 0x04
    FISH = 0x05
    LUMP_OF_METAL = 0x06
    LOLAS_LETTER = 0x07
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
        return list(range(cls.PENDANT + 1))
