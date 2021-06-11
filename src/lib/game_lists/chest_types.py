from enum import Enum


class ChestTypes:
    EMPTY = 0x00
    GOLD = 0x80
    MIAB = 0x20
    ITEM = 0x40
    ESPER = 0x10
    RARE_ITEM = 0x08

    @classmethod
    def all(cls):
        return [cls.EMPTY, cls.GOLD, cls.MIAB, cls.ITEM]

    @classmethod
    def safe(cls):
        return [cls.GOLD, cls.ITEM, cls.ESPER, cls.RARE_ITEM]

