import re


class CharTable:

    @classmethod
    def convert(cls, char):
        if type(char) == int:
            char = bytes([char])
        if char not in cls.table.keys():
            raise ValueError(f"Table doesn't contain value for {char}.")
        regex = r"[x]"
        match = re.search(regex, cls.table[char])
        if match:
            return re.sub(regex, str(ord(cls.rom.read())), cls.table[char])
        return cls.table[char]
