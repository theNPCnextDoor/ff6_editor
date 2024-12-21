import re

import pytest

from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.string import String
from src.lib.structures.bytes import BlobBytes, Bytes


class TestString:

    @pytest.mark.parametrize(
        ["line", "string"],
        [
            ('  "A"', String(data=BlobBytes(0x80))),
            ('  "<0x01>"', String(data=BlobBytes(0xEFCDAB8967452301))),
            ('  "  " # C0/0000', String(data=BlobBytes(0xFFFF))),
            ('  "A" $00', String(data=BlobBytes(0x80), delimiter=Bytes(0x00))),
            ('  "<0x01>" $FF', String(data=BlobBytes(0xEFCDAB8967452301), delimiter=Bytes(0xFF))),
            ('  "  " $12 # C0/0000', String(data=BlobBytes(0xFFFF), delimiter=Bytes(0x12))),
        ],
    )
    def test_from_regex_match(self, line: str, string: String):
        match = re.match(Regex.MENU_STRING, line)
        assert String.from_regex_match(match) == string

    @pytest.mark.parametrize(
        ["data", "delimiter", "string"],
        [
            (b"\x00\x80\xD8\xEB\xFF", None, String(data=BlobBytes(0x0080D8EBFF))),
            (b"\x00\x80\xD8\xEB\xFF", Bytes(0xEE), String(data=BlobBytes(0x0080D8EBFF), delimiter=Bytes(0xEE))),
        ],
    )
    def test_from_bytes(self, data: bytes, delimiter: Bytes | None, string: String):
        assert String.from_bytes(data=data, delimiter=delimiter) == string

    @pytest.mark.parametrize(
        ["string", "expected"], [(String(data=BlobBytes(value=0x0080D8EBFF, length=5)), '"<0x00>A<KNIFE><0xEB> "')]
    )
    def test_str(self, string: String, expected: str):
        assert str(string) == expected

    @pytest.mark.parametrize(
        ["string", "show_address", "expected"],
        [
            (String(data=BlobBytes(value=0x0080D8EBFF, length=5)), False, '  "<0x00>A<KNIFE><0xEB> "'),
            (String(data=BlobBytes(value="0080D8EBFF")), True, '  "<0x00>A<KNIFE><0xEB> " # C0/0000'),
            (
                String(data=BlobBytes(value=0x0080D8EBFF, length=5), delimiter=Bytes(0x00)),
                False,
                '  "<0x00>A<KNIFE><0xEB> " $00',
            ),
            (
                String(data=BlobBytes(value="0080D8EBFF"), delimiter=Bytes(0xFF)),
                True,
                '  "<0x00>A<KNIFE><0xEB> " $FF # C0/0000',
            ),
        ],
    )
    def test_to_line(self, string: String, show_address: bool, expected: str):
        assert string.to_line(show_address=show_address) == expected
