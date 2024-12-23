class Esper:
    RAMUH = 0x00
    IFRIT = 0x01
    SHIVA = 0x02
    SIREN = 0x03
    TERRATO = 0x04
    SHOAT = 0x05
    MADUIN = 0x06
    BISMARK = 0x07
    STRAY = 0x08
    PALIDOR = 0x09
    TRITOCH = 0x0A
    ODIN = 0x0B
    RAIDEN = 0x0C
    BAHAMUT = 0x0D
    ALEXANDR = 0x0E
    CRUSADER = 0x0F
    RAGNAROK = 0x10
    KIRIN = 0x11
    ZONESEEK = 0x12
    CARBUNKL = 0x13
    PHANTOM = 0x14
    SRAPHIM = 0x15
    GOLEM = 0x16
    UNICORN = 0x17
    FENRIR = 0x18
    STARLET = 0x19
    PHOENIX = 0x1A

    @classmethod
    def all(cls):
        return list(range(cls.PHOENIX + 1))
