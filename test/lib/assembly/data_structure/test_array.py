import pytest

from src.lib.assembly.artifact.variable import SimpleVar
from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.array import Array
from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.bytes import Bytes
from test.lib.assembly.conftest import TEST_WORD, VARIABLES, DEFAULT_ADDRESS

GROUP = Array(
    address=DEFAULT_ADDRESS,
    parts=[
        Blob(address=DEFAULT_ADDRESS, operand=Operand(Bytes([0xAA]))),
        String(operand=Operand(Bytes([0x9A])), address=Bytes([0xC0, 0x00, 0x01]), string_type=StringTypes.DESCRIPTION),
        Blob(operand=Operand(Bytes([0xBB])), address=Bytes([0xC0, 0x00, 0x02]), delimiter=Operand(Bytes([0xFF]))),
        String(
            operand=Operand(Bytes([0x9B])),
            address=Bytes([0xC0, 0x00, 0x04]),
            delimiter=Operand(Bytes([0x00]), variable=SimpleVar(Bytes([0x00]), "zero")),
            string_type=StringTypes.MENU,
        ),
    ],
)


class TestArray:
    @pytest.mark.parametrize(
        ["line", "group"],
        [
            ('$AA | desc "a" | $BB,$FF | "b",zero', GROUP),
            (
                '"This is a string # " | $01',
                Array(
                    parts=[
                        String(operand=Operand(TEST_WORD)),
                        Blob(operand=Operand(Bytes([0x01])), address=Bytes([0x00, 0x00, 0x13])),
                    ]
                ),
            ),
            (
                '$CD78 | "Status",$00',
                Array(
                    parts=[
                        Blob(operand=Operand(Bytes([0xCD, 0x78]))),
                        String(operand=Operand(TEST_WORD), delimiter=Operand(Bytes([0x00]))),
                    ]
                ),
            ),
        ],
    )
    @pytest.mark.parametrize("comment", ["", " ; some comment"])
    def test_from_line(self, line: str, comment: str, group: Array):
        assert (
            Array.from_line(
                line=line,
                address=Bytes([0x00, 0x00, 0x00]),
                variables=Variables(SimpleVar(Bytes.from_int(0), "zero")),
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
                "Array(address=0xC00000, as_str='$AA | desc \"a\" | $BB,$FF | \"b\",zero', as_bytes=b'\\xaa\\x9a\\xbb\\xff\\x9b\\x00', as_hexa=0xAA9ABB9B, parts=["
                "Blob(address=0xC00000, as_str='$AA', as_bytes=b'\\xaa', as_hexa=0xAA), "
                "String(address=0xC00001, as_str='desc \"a\"', as_bytes=b'\\x9a', as_hexa=0x9A), "
                "Blob(address=0xC00002, as_str='$BB,$FF', as_bytes=b'\\xbb\\xff', as_hexa=0xBBFF), "
                "String(address=0xC00004, as_str='\"b\",zero', as_bytes=b'\\x9b\\x00', as_hexa=0x9B00, delimiter_var=SimpleVar(name='zero', value=0x00))])",
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
            expected += " ; $C00000"
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

    def test_find_length(self):
        assert Array.find_length('  $AA | desc "a" | $BB,$FF | "b",zero', VARIABLES) == 6
