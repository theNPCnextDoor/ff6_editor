import pytest

from src.lib.assembly.artifact.variable import SimpleVar
from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.array import Array
from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.bytes import Bytes
from test.lib.assembly.conftest import TEST_WORD

GROUP = Array(
    blobs=[
        Blob(operand=Operand(Bytes([0xAA]))),
        String(operand=Operand(Bytes([0x9A])), position=Bytes([0x00, 0x00, 0x01]), string_type=StringTypes.DESCRIPTION),
        Blob(operand=Operand(Bytes([0xBB])), position=Bytes([0x00, 0x00, 0x02]), delimiter=Operand(Bytes([0xFF]))),
        String(
            operand=Operand(Bytes([0x9B])),
            position=Bytes([0x00, 0x00, 0x04]),
            delimiter=Operand(Bytes([0x00]), variable=SimpleVar(Bytes.from_int(0), "zero")),
            string_type=StringTypes.MENU,
        ),
    ]
)


class TestArray:
    @pytest.mark.parametrize(
        ["line", "group"],
        [
            ('$AA | desc "a" | $BB,$FF | "b",zero', GROUP),
            (
                '"This is a string # " | $01',
                Array(
                    blobs=[
                        String(operand=Operand(TEST_WORD)),
                        Blob(operand=Operand(Bytes([0x01])), position=Bytes([0x00, 0x00, 0x13])),
                    ]
                ),
            ),
            (
                '$CD78 | "Status",$00',
                Array(
                    blobs=[
                        Blob(operand=Operand(Bytes([0xCD, 0x78]))),
                        String(operand=Operand(TEST_WORD), delimiter=Operand(Bytes([0x00]))),
                    ]
                ),
            ),
        ],
    )
    @pytest.mark.parametrize("comment", ["", " ; some comment"])
    def test_from_string(self, line: str, comment: str, group: Array):
        assert (
            Array.from_string(
                line=line,
                position=Bytes([0x00, 0x00, 0x00]),
                variables=Variables(SimpleVar(Bytes.from_position(0), "zero")),
            )
            == Array()
        )

    @pytest.mark.parametrize(
        ["expected", "group"],
        [
            ('$AA | desc "a" | $BB,$FF | "b",zero', GROUP),
        ],
    )
    def test_str(self, group: Array, expected: str):
        assert str(group) == expected

    @pytest.mark.parametrize(
        ["expected", "group"],
        [
            (
                "Array(position=0x000000, as_str='$AA | desc \"a\" | $BB,$FF | \"b\",zero', as_bytes=b'\\xaa\\x9a\\xbb\\xff\\x9b\\x00', as_hexa=0xAA9ABB9B, blobs=["
                "Blob(position=0x000000, as_str='$AA', as_bytes=b'\\xaa', as_hexa=0xAA), "
                "String(position=0x000001, as_str='desc \"a\"', as_bytes=b'\\x9a', as_hexa=0x9A), "
                "Blob(position=0x000002, as_str='$BB,$FF', as_bytes=b'\\xbb\\xff', as_hexa=0xBBFF), "
                "String(position=0x000004, as_str='\"b\",zero', as_bytes=b'\\x9b\\x00', as_hexa=0x9B00, delimiter_var=SimpleVar(0x00, 'zero'))])",
                GROUP,
            ),
        ],
    )
    def test_repr(self, group: Array, expected: str):
        assert repr(group) == expected

    @pytest.mark.parametrize(
        ["expected", "group"],
        [
            ('  $AA | desc "a" | $BB,$FF | "b",zero', GROUP),
        ],
    )
    @pytest.mark.parametrize("show_address", [True, False])
    def test_to_line(self, group: Array, show_address: bool, expected: str):
        if show_address:
            expected += " ; C00000"
        assert group.to_line(show_address=show_address) == expected

    @pytest.mark.parametrize(
        ["group", "length"],
        [
            (GROUP, 6),
        ],
    )
    def test_len(self, group: Array, length: int):
        assert len(group) == length

    @pytest.mark.parametrize(
        ["group", "expected"],
        [
            (GROUP, b"\xaa\x9a\xbb\xff\x9b\x00"),
        ],
    )
    def test_bytes(self, group: Array, expected: bytes):
        assert bytes(group) == expected
