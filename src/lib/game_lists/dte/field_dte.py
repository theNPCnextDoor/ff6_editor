import re

from src.lib.structures import Bytes


class FieldDte:
    char_map = {
        0x00: "<END>",
        0x01: "\n",
        0x02: "<TERRA>",
        0x03: "<LOCKE>",
        0x04: "<CYAN>",
        0x05: "<SHADOW>",
        0x06: "<EDGAR>",
        0x07: "<SABIN>",
        0x08: "<CELES>",
        0x09: "<STRAGO>",
        0x0A: "<RELM>",
        0x0B: "<SETZER>",
        0x0C: "<MOG>",
        0x0D: "<GAU>",
        0x0E: "<GOGO>",
        0x0F: "<UMARO>",
        0x10: "<WAIT 60 FRAMES>",
        0x11: "<WAIT 15 FRAMES TIMES: _>",
        0x12: "<WAIT 1 FRAME>",
        0x13: "<PAGE>\n",
        0x14: "<SPACES: _>",
        0x15: "<CHOICE>",
        0x16: "<WAIT FOR KEY 15 FRAMES TIMES: _>",
        0x17: "<0x17: _>",
        0x18: "<0x18: _>",
        0x19: "<GP>",
        0x1A: "<ITEM>",
        0x1B: "<SKILL>",
        0x1C: "<RARE ITEM>",
        0x1D: "<0x1D: _>",
        0x1E: "<0x1E: _>",
        0x1F: "<0x1F: _>",
        0x20: "A",
        0x21: "B",
        0x22: "C",
        0x23: "D",
        0x24: "E",
        0x25: "F",
        0x26: "G",
        0x27: "H",
        0x28: "I",
        0x29: "J",
        0x2A: "K",
        0x2B: "L",
        0x2C: "M",
        0x2D: "N",
        0x2E: "O",
        0x2F: "P",
        0x30: "Q",
        0x31: "R",
        0x32: "S",
        0x33: "T",
        0x34: "U",
        0x35: "V",
        0x36: "W",
        0x37: "X",
        0x38: "Y",
        0x39: "Z",
        0x3A: "a",
        0x3B: "b",
        0x3C: "c",
        0x3D: "d",
        0x3E: "e",
        0x3F: "f",
        0x40: "g",
        0x41: "h",
        0x42: "i",
        0x43: "j",
        0x44: "k",
        0x45: "l",
        0x46: "m",
        0x47: "n",
        0x48: "o",
        0x49: "p",
        0x4A: "q",
        0x4B: "r",
        0x4C: "s",
        0x4D: "t",
        0x4E: "u",
        0x4F: "v",
        0x50: "w",
        0x51: "x",
        0x52: "y",
        0x53: "z",
        0x54: "0",
        0x55: "1",
        0x56: "2",
        0x57: "3",
        0x58: "4",
        0x59: "5",
        0x5A: "6",
        0x5B: "7",
        0x5C: "8",
        0x5D: "9",
        0x5E: "!",
        0x5F: "?",
        0x60: "/",
        0x61: ":",
        0x62: "»",
        0x63: "'",
        0x64: "-",
        0x65: ".",
        0x66: ",",
        0x67: "…",
        0x68: ";",
        0x69: "#",
        0x6A: "+",
        0x6B: "(",
        0x6C: ")",
        0x6D: "%",
        0x6E: "~",
        0x6F: "*",
        0x70: "@",
        0x71: "♪",
        0x72: "=",
        0x73: "«",
        0x74: "<0x74>",
        0x75: "<0x75>",
        0x76: "<HOLY>",
        0x77: "<DEATH>",
        0x78: "<LIGHTNING>",
        0x79: "<WIND>",
        0x7A: "<EARTH>",
        0x7B: "<ICE>",
        0x7C: "<FIRE>",
        0x7D: "<WATER>",
        0x7E: "<POISON>",
        0x7F: " ",
        0x80: "e ",
        0x81: " t",
        0x82: ": ",
        0x83: "th",
        0x84: "t ",
        0x85: "he",
        0x86: "s ",
        0x87: "er",
        0x88: " a",
        0x89: "re",
        0x8A: "in",
        0x8B: "ou",
        0x8C: "d ",
        0x8D: " w",
        0x8E: " s",
        0x8F: "an",
        0x90: "o ",
        0x91: " h",
        0x92: " o",
        0x93: "r ",
        0x94: "n ",
        0x95: "at",
        0x96: "to",
        0x97: " i",
        0x98: ", ",
        0x99: "ve",
        0x9A: "ng",
        0x9B: "ha",
        0x9C: " m",
        0x9D: "Th",
        0x9E: "st",
        0x9F: "on",
        0xA0: "yo",
        0xA1: " b",
        0xA2: "me",
        0xA3: "y ",
        0xA4: "en",
        0xA5: "it",
        0xA6: "ar",
        0xA7: "ll",
        0xA8: "ea",
        0xA9: "I ",
        0xAA: "ed",
        0xAB: " f",
        0xAC: " y",
        0xAD: "hi",
        0xAE: "is",
        0xAF: "es",
        0xB0: "or",
        0xB1: "l ",
        0xB2: " c",
        0xB3: "ne",
        0xB4: "'s",
        0xB5: "nd",
        0xB6: "le",
        0xB7: "se",
        0xB8: " I",
        0xB9: "a ",
        0xBA: "te",
        0xBB: " l",
        0xBC: "pe",
        0xBD: "as",
        0xBE: "ur",
        0xBF: "u ",
        0xC0: "al",
        0xC1: " p",
        0xC2: "g ",
        0xC3: "om",
        0xC4: " d",
        0xC5: "f ",
        0xC6: " g",
        0xC7: "ow",
        0xC8: "rs",
        0xC9: "be",
        0xCA: "ro",
        0xCB: "us",
        0xCC: "ri",
        0xCD: "wa",
        0xCE: "we",
        0xCF: "Wh",
        0xD0: "et",
        0xD1: " r",
        0xD2: "nt",
        0xD3: "m ",
        0xD4: "ma",
        0xD5: "I'",
        0xD6: "li",
        0xD7: "ho",
        0xD8: "of",
        0xD9: "Yo",
        0xDA: "h ",
        0xDB: " n",
        0xDC: "ee",
        0xDD: "de",
        0xDE: "so",
        0xDF: "gh",
        0xE0: "ca",
        0xE1: "ra",
        0xE2: "n'",
        0xE3: "ta",
        0xE4: "ut",
        0xE5: "el",
        0xE6: "! ",
        0xE7: "fo",
        0xE8: "ti",
        0xE9: "We",
        0xEA: "lo",
        0xEB: "e!",
        0xEC: "ld",
        0xED: "no",
        0xEE: "ac",
        0xEF: "ce",
        0xF0: "k ",
        0xF1: " u",
        0xF2: "oo",
        0xF3: "ke",
        0xF4: "ay",
        0xF5: "w ",
        0xF6: "!!",
        0xF7: "ag",
        0xF8: "il",
        0xF9: "ly",
        0xFA: "co",
        0xFB: ". ",
        0xFC: "ch",
        0xFD: "go",
        0xFE: "ge",
        0xFF: "e…",
    }

    @classmethod
    def to_bytes(cls, string):
        output = Bytes(None, endianness="big")
        position = 0
        while position < len(string):
            if regex := re.search(r"^( {3,})", string[position:]):
                multiple_spaces = regex.groups(1)[0]
                output.append(0x14)
                output.append(len(multiple_spaces))
                position += len(multiple_spaces)
            elif regex := re.search(r"^<PAGE>\n", string[position:]):
                output.append(0x13)
                position += len(regex.group(0))

            elif regex := re.search(r"^(<[^:>]+(: ([0-9A-F]{1,2}))?>)", string[position:]):
                special_character = re.sub(r"(.+): [0-9A-F]{1,2}(.+)", r"\1: _\2", regex.group(1))
                output.append(cls.get_by_name(special_character))
                if regex.groups()[2]:
                    quantity = int(Bytes(regex.group(3), length=1, endianness="big"))
                    output.append(quantity)
                position += len(regex.group(1))
            else:
                next_two_characters = string[position : position + 2]
                try:
                    output.append(cls.get_by_name(next_two_characters))
                    position += 2
                except ValueError:
                    next_character = string[position : position + 1]
                    output.append(cls.get_by_name(next_character))
                    position += 1

        return output

    @classmethod
    def to_string(cls, value):
        output = ""
        position = 0
        while position < len(value) and value[position] != 0:
            if (next_byte := value[position]) == 0x14:
                second_byte = value[position + 1]
                output += " " * second_byte
                position += 2
            else:
                character = cls.char_map[next_byte]
                position += 1
                second_byte = value[position]
                if ": _" in character:
                    character = character.replace(": _", f": {Bytes(second_byte):02X}")
                    position += 1
                output += character
        output += "<END>"
        return output

    @classmethod
    def get_by_name(cls, value):
        candidates = [(k, v) for k, v in cls.char_map.items() if value == v]
        if not len(candidates):
            raise ValueError(f"Character '{value}' has not been found.")
        return candidates[0][0]


if __name__ == "__main__":
    print(FieldDte.to_bytes("\n<TERRA><WAIT 15 FRAMES TIMES: AA> t"))
    print(FieldDte.to_string(b"\x01\x02\x11\xAA\x81"))
    print(3 ** 3 ** 3 ** 3)
