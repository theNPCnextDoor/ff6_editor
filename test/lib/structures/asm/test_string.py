import re

import pytest

from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.string import String
from src.lib.structures.bytes import BEBytes, LEBytes


class TestString:

    @pytest.mark.parametrize(
        ["line", "string"],
        [
            ('  "A"', String(data=BEBytes([0x80]))),
            ('  "<0x01>"', String(data=BEBytes([0xEF, 0xCD, 0xAB, 0x89, 0x67, 0x45, 0x23, 0x01]))),
            ('  "  " # C0/0000', String(data=BEBytes([0xFF, 0xFF]))),
            ('  "A" $00', String(data=BEBytes([0x80]), delimiter=LEBytes([0x00]))),
            (
                '  "<0x01>" $FF',
                String(data=BEBytes([0xEF, 0xCD, 0xAB, 0x89, 0x67, 0x45, 0x23, 0x01]), delimiter=LEBytes([0xFF])),
            ),
            ('  "  " $12 # C0/0000', String(data=BEBytes([0xFF, 0xFF]), delimiter=LEBytes([0x12]))),
        ],
    )
    def test_from_regex_match(self, line: str, string: String):
        match = re.match(Regex.MENU_STRING_LINE, line)
        assert String.from_regex_match(match) == string

    @pytest.mark.parametrize(
        ["data", "delimiter", "string"],
        [
            (b"\x00\x80\xd8\xeb\xff", None, String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]))),
            (
                b"\x00\x80\xd8\xeb\xff",
                b"\xee",
                String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]), delimiter=LEBytes([0xEE])),
            ),
        ],
    )
    def test_from_bytes(self, data: bytes, delimiter: LEBytes | None, string: String):
        assert String.from_bytes(data=data, delimiter=delimiter) == string

    @pytest.mark.parametrize(
        ["string", "expected"],
        [(String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF], length=5)), '"<0x00>A<KNIFE><0xEB> "')],
    )
    def test_str(self, string: String, expected: str):
        assert str(string) == expected

    @pytest.mark.parametrize(
        ["string", "show_address", "expected"],
        [
            (String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF], length=5)), False, '  "<0x00>A<KNIFE><0xEB> "'),
            (String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), True, '  "<0x00>A<KNIFE><0xEB> " # C0/0000'),
            (
                String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF], length=5), delimiter=LEBytes([0x00])),
                False,
                '  "<0x00>A<KNIFE><0xEB> ",$00',
            ),
            (
                String(data=BEBytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]), delimiter=LEBytes([0xFF])),
                True,
                '  "<0x00>A<KNIFE><0xEB> ",$FF # C0/0000',
            ),
        ],
    )
    def test_to_line(self, string: String, show_address: bool, expected: str):
        assert string.to_line(show_address=show_address) == expected
