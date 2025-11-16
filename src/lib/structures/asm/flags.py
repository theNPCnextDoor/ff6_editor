from re import Match
from typing import Self

from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import ToLineMixin


class RegisterWidth:
    EIGHT_BITS = 8
    SIXTEEN_BITS = 16


class Flags(ToLineMixin):

    def __init__(self, m: int = RegisterWidth.SIXTEEN_BITS, x: int = RegisterWidth.SIXTEEN_BITS):
        self.m = m
        self.x = x

    @classmethod
    def from_regex_match(cls, match: Match) -> Self:
        """
        Will take a string that matches Regex.FLAGS and will return a Flags object. It will consider either
         "8" or "true" for True and "16" or "false" for False.
        :param match: The regex Match.
        :return: A Flags object.
        :note: The reason that 8 and 16 are used is that it is more readable to see the width in bits of the accumulator
         and the indexes than having to convert the bool into number of bits.
        """
        flags = cls()
        flags.m = 8 if match.group(1) in ("8", "true") else 16
        flags.x = 8 if match.group(2) in ("8", "true") else 16
        return flags

    def __str__(self) -> str:
        m = str(self.m)
        x = str(self.x)
        return f"m={m},x={x}"

    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        return str(self)

    def __eq__(self, other: Self) -> bool:
        return self.m == other.m and self.x == other.x
