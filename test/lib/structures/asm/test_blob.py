from __future__ import annotations

import re

import pytest

from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import Bytes, Position, Endian, BlobBytes
from src.lib.structures.asm.blob import Blob


class TestBlob:
    @pytest.mark.parametrize(
        ["blob", "position", "data"], [
            (Blob(data=BlobBytes("12345678")), Position(0x00), BlobBytes(0x12345678)),
            (Blob(data=BlobBytes("9ABCDEF0"), position=Position(0x563412)), Position(0x563412), BlobBytes(0x9ABCDEF0))
        ]
    )
    def test_init(self, blob: Blob, position: Position, data: BlobBytes):
        assert blob.position == position
        assert blob.data == data

    @pytest.mark.parametrize(
        ["line", "blob"], [
            ("  blob $12", Blob(data=BlobBytes(0x12))),
            ("  blob $0123456789ABCDEF", Blob(data=BlobBytes(0xEFCDAB8967452301))),
            ("  blob $FFFF # C0/0000", Blob(data=BlobBytes(0xFFFF)))
        ]
    )
    def test_from_regex_match(self, line: str, blob: Blob):
        match = re.match(Regex.BLOB, line)
        assert Blob.from_regex_match(match) == blob

    @pytest.mark.parametrize(
        ["data", "blob"], [
            (b"\x12", Blob(data=BlobBytes(0x12))),
            (b"\x01\x23\x45\x67\x89\xAB\xCD\xEF", Blob(data=BlobBytes(0xEFCDAB8967452301))),
            (b"\xFF\xFF", Blob(data=BlobBytes(0xFFFF)))
        ]
    )
    def test_from_bytes(self, data: bytes, blob: Blob):
        assert Blob.from_bytes(data) == blob

    @pytest.mark.parametrize(
        ["blob", "expected"], [
            (Blob(data=BlobBytes("12345678")), "blob $12345678"),
        ]
    )
    def test_str(self, blob: Blob, expected: str):
        assert str(blob) == expected

    @pytest.mark.parametrize(
        ["blob", "show_address", "expected"], [
            (Blob(data=BlobBytes("12345678")), False, "  blob $12345678"),
            (Blob(data=BlobBytes("12345678")), True, "  blob $12345678 # C0/0000"),
        ]
    )
    def test_to_line(self, blob: Blob, show_address: bool, expected: str):
        assert blob.to_line(show_address=show_address) == expected

    @pytest.mark.parametrize(
        ["blob", "length"], [
            (Blob(data=BlobBytes("12345678")), 4),
        ]
    )
    def test_len(self, blob: Blob, length: int):
        assert len(blob) == length

    @pytest.mark.parametrize(
        ["blob", "output"], [
            (Blob(data=BlobBytes("12345678")), b"\x12\x34\x56\x78"),
            (Blob(data=BlobBytes(0x12345678), delimiter=Bytes(0x00)), b"\x12\x34\x56\x78\x00"),
            (Blob(data=BlobBytes(0x12345678), delimiter=Bytes(0xFF)), b"\x12\x34\x56\x78\xFF")
        ]
    )
    def test_bytes(self, blob: Blob, output: bytes):
        assert bytes(blob) == output
