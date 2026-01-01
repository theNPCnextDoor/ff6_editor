import re

import pytest

from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.string import String
from src.lib.structures.bytes import Bytes


class TestString:

    @pytest.mark.parametrize(
        ["line", "expected"],
        [
            ('  "A"', String(data=Bytes([0x80]))),
            ('  "<0x01>"', String(data=Bytes([0x01]))),
            ('  "  " # C0/0000', String(data=Bytes([0xFE, 0xFE]))),
            ('  "A" $00', String(data=Bytes([0x80]), delimiter=Bytes([0x00]))),
            (
                '  "<0x01>" $FF',
                String(data=Bytes([0x01]), delimiter=Bytes([0xFF])),
            ),
            ('  "  " $12 # C0/0000', String(data=Bytes([0xFE, 0xFE]), delimiter=Bytes([0x12]))),
        ],
    )
    def test_from_regex_match(self, line: str, expected: String):
        match = re.match(Regex.MENU_STRING_LINE, line)
        assert String.from_regex_match(match) == expected

    @pytest.mark.parametrize(
        ["data", "delimiter", "string"],
        [
            (b"\x00\x80\xd8\xeb\xff", None, String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]))),
            (
                b"\x00\x80\xd8\xeb\xff",
                b"\xee",
                String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]), delimiter=Bytes([0xEE])),
            ),
        ],
    )
    def test_from_bytes(self, data: bytes, delimiter: Bytes | None, string: String):
        assert String.from_bytes(data=data, delimiter=delimiter) == string

    @pytest.mark.parametrize(
        ["string", "expected"],
        [(String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), '"<0x00>A<KNIFE><0xEB>_"')],
    )
    def test_str(self, string: String, expected: str):
        assert str(string) == expected

    @pytest.mark.parametrize(
        ["string", "show_address", "expected"],
        [
            (String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), False, '  "<0x00>A<KNIFE><0xEB>_"'),
            (String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), True, '  "<0x00>A<KNIFE><0xEB>_" ; C00000'),
            (
                String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]), delimiter=Bytes([0x00])),
                False,
                '  "<0x00>A<KNIFE><0xEB>_",$00',
            ),
            (
                String(data=Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]), delimiter=Bytes([0xFF])),
                True,
                '  "<0x00>A<KNIFE><0xEB>_",$FF ; C00000',
            ),
        ],
    )
    def test_to_line(self, string: String, show_address: bool, expected: str):
        assert string.to_line(show_address=show_address) == expected
