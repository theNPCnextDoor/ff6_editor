import pytest

from src.lib.assembly.artifact.variable import SimpleVar
from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.data_structure.string.string import String
from src.lib.assembly.bytes import Bytes


class TestString:

    @pytest.mark.parametrize(
        ["string_type", "string", "delimiter", "expected"],
        [
            (None, "A", None, String(operand=Operand(Bytes([0x80])))),
            (None, "<0x01>", None, String(operand=Operand(Bytes([0x01])))),
            (None, "  ", None, String(operand=Operand(Bytes([0xFE, 0xFE])))),
            (None, "A", "$00", String(operand=Operand(Bytes([0x80])), delimiter=Operand(Bytes([0x00])))),
            (
                None,
                "<0x01>",
                "$FF",
                String(operand=Operand(Bytes([0x01])), delimiter=Operand(Bytes([0xFF]))),
            ),
            (
                "desc",
                "ABC",
                None,
                String(operand=Operand(Bytes([0x80, 0x81, 0x82]))),
            ),
        ],
    )
    def test_from_string(self, string_type: str | None, string: str, delimiter: str | None, expected: String):
        assert String.from_string(string, string_type, delimiter) == expected

    @pytest.mark.parametrize(
        ["data", "delimiter", "string"],
        [
            (b"\x00\x80\xd8\xeb\xff", None, String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])))),
            (
                b"\x00\x80\xd8\xeb\xff",
                b"\xee",
                String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), delimiter=Operand(Bytes([0xEE]))),
            ),
        ],
    )
    def test_from_bytes(self, data: bytes, delimiter: Bytes | None, string: String):
        assert String.from_bytes(data=data, delimiter=delimiter) == string

    @pytest.mark.parametrize(
        ["string", "expected"],
        [
            (String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]))), '"<0x00>A<KNIFE><0xEB>_"'),
            (
                String(
                    operand=Operand(Bytes([0x80, 0x81, 0x82])),
                    delimiter=Operand(Bytes.from_int(0), variable=SimpleVar(Bytes.from_int(0), "zero")),
                ),
                '"ABC",zero',
            ),
        ],
    )
    def test_str(self, string: String, expected: str):
        assert str(string) == expected

    @pytest.mark.parametrize(
        ["string", "expected"],
        [
            (
                String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]))),
                "String(position=0x000000, as_str='\"<0x00>A<KNIFE><0xEB>_\"', as_bytes=b'\\xff\\xeb\\xd8\\x80\\x00', as_hexa=0x0080D8EBFF)",
            ),
            (
                String(
                    operand=Operand(Bytes([0x80, 0x81, 0x82])),
                    delimiter=Operand(Bytes.from_int(0), variable=SimpleVar(Bytes.from_int(0), "zero")),
                ),
                "String(position=0x000000, as_str='\"ABC\",zero', as_bytes=b'\\x82\\x81\\x80\\x00', as_hexa=0x80818200, delimiter_var=SimpleVar(0x00, 'zero'))",
            ),
        ],
    )
    def test_repr(self, string: String, expected: str):
        assert repr(string) == expected

    @pytest.mark.parametrize(
        ["string", "show_address", "expected"],
        [
            (String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]))), False, '  "<0x00>A<KNIFE><0xEB>_"'),
            (
                String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF]))),
                True,
                '  "<0x00>A<KNIFE><0xEB>_" ; C00000',
            ),
            (
                String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), delimiter=Operand(Bytes([0x00]))),
                False,
                '  "<0x00>A<KNIFE><0xEB>_",$00',
            ),
            (
                String(operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xEB, 0xFF])), delimiter=Operand(Bytes([0xFF]))),
                True,
                '  "<0x00>A<KNIFE><0xEB>_",$FF ; C00000',
            ),
        ],
    )
    def test_to_line(self, string: String, show_address: bool, expected: str):
        assert string.to_line(show_address=show_address) == expected
