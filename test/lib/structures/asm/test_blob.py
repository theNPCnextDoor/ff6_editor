from __future__ import annotations

import re

import pytest

from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import Bytes, Position, BEBytes
from src.lib.structures.asm.blob import Blob


class TestBlob:
    @pytest.mark.parametrize(
        ["blob", "position", "data"],
        [
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78])), Position([0x00]), BEBytes([0x12, 0x34, 0x56, 0x78])),
            (
                Blob(data=BEBytes([0x9A, 0xBC, 0xDE, 0xF0]), position=Position([0x56, 0x34, 0x12])),
                Position([0x56, 0x34, 0x12]),
                BEBytes([0x9A, 0xBC, 0xDE, 0xF0]),
            ),
        ],
    )
    def test_init(self, blob: Blob, position: Position, data: BEBytes):
        assert blob.position == position
        assert blob.data == data

    @pytest.mark.parametrize(
        ["line", "blob"],
        [
            ("  $12", Blob(data=Bytes([0x12]))),
            ("  $0123456789ABCDEF", Blob(data=Bytes([0xEF, 0xCD, 0xAB, 0x89, 0x67, 0x45, 0x23, 0x01]))),
            ("  $FFFF # C0/0000", Blob(data=Bytes([0xFF, 0xFF]))),
        ],
    )
    def test_from_regex_match(self, line: str, blob: Blob):
        match = re.match(Regex.BLOB_LINE, line)
        assert Blob.from_regex_match(match) == blob

    @pytest.mark.parametrize(
        ["data", "blob"],
        [
            (b"\x12", Blob(data=Bytes([0x12]))),
            (b"\x01\x23\x45\x67\x89\xab\xcd\xef", Blob(data=Bytes([0xEF, 0xCD, 0xAB, 0x89, 0x67, 0x45, 0x23, 0x01]))),
            (b"\xff\xff", Blob(data=Bytes([0xFF, 0xFF]))),
        ],
    )
    def test_from_bytes(self, data: Bytes, blob: Blob):
        assert Blob.from_bytes(data) == blob

    @pytest.mark.parametrize(
        ["blob", "expected"],
        [
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78])), "$12345678"),
        ],
    )
    def test_str(self, blob: Blob, expected: str):
        assert str(blob) == expected

    @pytest.mark.parametrize(
        ["blob", "show_address", "expected"],
        [
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78])), False, "  $12345678"),
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78])), True, "  $12345678 ; C00000"),
        ],
    )
    def test_to_line(self, blob: Blob, show_address: bool, expected: str):
        assert blob.to_line(show_address=show_address) == expected

    @pytest.mark.parametrize(
        ["blob", "length"],
        [
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78])), 4),
        ],
    )
    def test_len(self, blob: Blob, length: int):
        assert len(blob) == length

    @pytest.mark.parametrize(
        ["blob", "output"],
        [
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78])), b"\x12\x34\x56\x78"),
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78]), delimiter=Bytes([0x00])), b"\x12\x34\x56\x78\x00"),
            (Blob(data=BEBytes([0x12, 0x34, 0x56, 0x78]), delimiter=Bytes([0xFF])), b"\x12\x34\x56\x78\xff"),
        ],
    )
    def test_bytes(self, blob: Blob, output: Bytes):
        assert bytes(blob) == output
