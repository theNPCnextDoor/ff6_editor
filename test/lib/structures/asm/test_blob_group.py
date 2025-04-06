import re

import pytest

from src.lib.structures.asm.blob import Blob
from src.lib.structures.asm.blob_group import BlobGroup
from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.string import String
from src.lib.structures.bytes import Position, BEBytes, LEBytes

GROUP = BlobGroup(
    blobs=[
        Blob(data=BEBytes([0xAA])),
        String(data=BEBytes([0x9A]), position=Position([0x00, 0x00, 0x01])),
        Blob(data=BEBytes([0xBB]), position=Position([0x00, 0x00, 0x02]), delimiter=LEBytes([0xFF])),
        String(data=BEBytes([0x9B]), position=Position([0x00, 0x00, 0x04]), delimiter=LEBytes([0x00])),
    ]
)


class TestBlobGroup:
    @pytest.mark.parametrize(
        ["line", "group"],
        [
            ('  $AA | "a" | $BB,$FF | "b",$00', GROUP),
            (
                '  "This is a string # " | $01',
                BlobGroup(
                    blobs=[
                        String(data=BEBytes([0x12, 0x34])),
                        Blob(data=BEBytes([0x01]), position=Position([0x00, 0x00, 0x13])),
                    ]
                ),
            ),
            (
                '  $CD78 | "Status",$00',
                BlobGroup(
                    blobs=[
                        Blob(data=BEBytes([0xCD, 0x78])),
                        String(data=BEBytes([0x12, 0x34]), delimiter=LEBytes([0x00])),
                    ]
                ),
            ),
        ],
    )
    @pytest.mark.parametrize("comment", ["", " # some comment"])
    def test_from_regex_match(self, line: str, comment: str, group: BlobGroup):
        match = re.fullmatch(Regex.BLOB_GROUP_LINE, f"{line}{comment}")
        assert bool(match)
        assert BlobGroup.from_regex_match(match=match, position=Position([0x00])) == BlobGroup()

    @pytest.mark.parametrize(
        ["expected", "group"],
        [
            ('$AA | "a" | $BB,$FF | "b",$00', GROUP),
        ],
    )
    def test_str(self, group: BlobGroup, expected: str):
        assert str(group) == expected

    @pytest.mark.parametrize(
        ["expected", "group"],
        [
            ('  $AA | "a" | $BB,$FF | "b",$00', GROUP),
        ],
    )
    @pytest.mark.parametrize("show_address", [True, False])
    def test_to_line(self, group: BlobGroup, show_address: bool, expected: str):
        if show_address:
            expected += " # C0/0000"
        assert group.to_line(show_address=show_address) == expected

    @pytest.mark.parametrize(
        ["group", "length"],
        [
            (GROUP, 6),
        ],
    )
    def test_len(self, group: BlobGroup, length: int):
        assert len(group) == length

    @pytest.mark.parametrize(
        ["group", "expected"],
        [
            (GROUP, b"\xaa\x9a\xbb\xff\x9b\x00"),
        ],
    )
    def test_bytes(self, group: BlobGroup, expected: bytes):
        assert bytes(group) == expected
