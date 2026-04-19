from typing import Self, Any

from src.lib.assembly.artifact.artifact import Artifact


class RegisterWidth:
    EIGHT_BITS = 8
    SIXTEEN_BITS = 16


class Flags(Artifact):

    def __init__(self, m: int = RegisterWidth.SIXTEEN_BITS, x: int = RegisterWidth.SIXTEEN_BITS):
        self.m = m
        self.x = x

    @classmethod
    def from_string(cls, m_flag: str, x_flag: str) -> Self:
        """
        Will take a string that matches Regex.FLAGS and will return a Flags object. It will consider either
         "8" or "true" for True and "16" or "false" for False.
        :param match: The regex Match.
        :return: A Flags object.
        :note: The reason that 8 and 16 are used is that it is more readable to see the width in bits of the accumulator
         and the indexes than having to convert the bool into number of bits.
        """
        flags = cls()
        flags.m = int(m_flag)
        flags.x = int(x_flag)
        return flags

    def __str__(self) -> str:
        m = str(self.m)
        x = str(self.x)
        return f"m={m},x={x}"

    def to_line(self, **kwargs: Any) -> str:
        return str(self)

    def __eq__(self, other: Self) -> bool:
        return self.m == other.m and self.x == other.x
