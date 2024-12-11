from __future__ import annotations

import pytest

from src.lib.structures.bytes import Bytes, BytesType, Endian, Position


class TestBytes:

    @pytest.mark.parametrize(
        ["value", "output", "in_endian", "length"], [
            (None, list(), Endian.BIG, 0),
            (0, [0x00], Endian.BIG, None),
            (0, [0x00, 0x00, 0x00], Endian.BIG, 3),
            (0x123456, [0x12, 0x34, 0x56], Endian.BIG, None),
            (0x123456, [0x34, 0x56], Endian.BIG, 2),
            ("", [], Endian.BIG, None),
            ("00", [0x00], Endian.BIG, None),
            ("00", [0x00, 0x00], Endian.BIG, 2),
            ("123456", [0x12, 0x34, 0x56], Endian.BIG, None),
            ("123456", [0x56, 0x34, 0x12], Endian.LITTLE, None),
            ("123456", [0x34, 0x56], Endian.BIG, 2),
            ("123456", [0x34, 0x12], Endian.LITTLE, 2),
            (b"", list(), Endian.BIG, None),
            (b"", [0x00, 0x00, 0x00], Endian.BIG, 3),
            (b"\x00", [0x00], Endian.BIG, None),
            (b"\x00", [0x00, 0x00, 0x00], Endian.BIG, 3),
            (b"\x12\x34\x56", [0x12, 0x34, 0x56], Endian.BIG, None),
            (b"\x12\x34\x56", [0x56, 0x34, 0x12], Endian.LITTLE, None),
            (b"\x12\x34\x56", [0x34, 0x56], Endian.BIG, 2),
            (b"\x12\x34\x56", [0x34, 0x12], Endian.LITTLE, 2),
        ]
    )
    @pytest.mark.parametrize("is_wrapped", [True, False])
    def test_init(self, value: BytesType, output: list[int], in_endian: bool, length: int, is_wrapped: bool):
        if is_wrapped:
            assert Bytes(value=Bytes(value, length=length, in_endian=in_endian))._value == output
        else:
            assert Bytes(value=value, length=length, in_endian=in_endian)._value == output


    @pytest.mark.parametrize(
        ["value", "output"], [
            (Bytes(value=b"", in_endian=Endian.BIG, out_endian=Endian.BIG, length=None), b""),
            (Bytes(value=b"", in_endian=Endian.BIG, out_endian=Endian.BIG, length=2), b"\x00\x00"),
            (Bytes(value=b"\x00", in_endian=Endian.BIG, out_endian=Endian.BIG, length=None), b"\x00"),
            (Bytes(value=b"\x00", in_endian=Endian.BIG, out_endian=Endian.BIG, length=4), b"\x00\x00\x00\x00"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, out_endian=Endian.BIG, length=None), b"\x12\x34\x56"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, out_endian=Endian.BIG, length=None), b"\x56\x34\x12"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, out_endian=Endian.LITTLE, length=None), b"\x12\x34\x56"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, out_endian=Endian.LITTLE, length=None), b"\x56\x34\x12"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, out_endian=Endian.BIG, length=2), b"\x34\x56"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, out_endian=Endian.BIG, length=2), b"\x34\x12"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, out_endian=Endian.LITTLE, length=2), b"\x12\x34"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, out_endian=Endian.LITTLE, length=2), b"\x56\x34"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, out_endian=Endian.BIG, length=4), b"\x00\x12\x34\x56"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, out_endian=Endian.BIG, length=4), b"\x00\x56\x34\x12"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, out_endian=Endian.LITTLE, length=4), b"\x12\x34\x56\x00"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, out_endian=Endian.LITTLE, length=4), b"\x56\x34\x12\x00"),
        ]
    )
    def test_bytes(self, value: Bytes, output: bytes):
        assert bytes(value) == output

    @pytest.mark.parametrize(
        ["value", "output"], [
            (Bytes(value=b"", in_endian=Endian.BIG, length=None), 0),
            (Bytes(value=b"\x00", in_endian=Endian.BIG, length=None), 0),
            (Bytes(value=b"\x01", in_endian=Endian.BIG, length=None), 1),
            (Bytes(value=b"\xFF", in_endian=Endian.BIG, length=None), 255),
            (Bytes(value=b"\xFF\xFF", in_endian=Endian.BIG, length=None), 65535),
            (Bytes(value=b"\xFF\xFE", in_endian=Endian.BIG, length=None), 65534),
            (Bytes(value=b"\xFF\xFE", in_endian=Endian.LITTLE, length=None), 65279),
            (Bytes(value=b"\xFE\xFF", in_endian=Endian.BIG, length=None), 65279),
            (Bytes(value=b"\xFE\xFF", in_endian=Endian.LITTLE, length=None), 65534),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=None), 1193046),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=None), 5649426),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=2), 13398),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=2), 13330),
        ]
    )
    def test_int(self, value: Bytes, output: int):
        assert int(value) == output

    @pytest.mark.parametrize(
        ["value", "output"], [
            (Bytes(value=b"", in_endian=Endian.BIG, length=None, out_endian=Endian.BIG), ""),
            (Bytes(value=b"", in_endian=Endian.BIG, length=2, out_endian=Endian.BIG), "0000"),
            (Bytes(value=b"\x00", in_endian=Endian.BIG, length=None, out_endian=Endian.BIG), "00"),
            (Bytes(value=b"\x00", in_endian=Endian.BIG, length=4, out_endian=Endian.BIG), "00000000"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=None, out_endian=Endian.BIG), "123456"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=None, out_endian=Endian.BIG), "563412"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=None, out_endian=Endian.LITTLE), "123456"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=None, out_endian=Endian.LITTLE), "563412"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=2, out_endian=Endian.BIG), "3456"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=2, out_endian=Endian.BIG), "3412"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=2, out_endian=Endian.LITTLE), "1234"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=2, out_endian=Endian.LITTLE), "5634"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=4, out_endian=Endian.BIG), "00123456"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=4, out_endian=Endian.BIG), "00563412"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=4, out_endian=Endian.LITTLE), "12345600"),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=4, out_endian=Endian.LITTLE), "56341200"),
            (Bytes(value=b"\xAB\xCD\xEF", in_endian=Endian.BIG, length=None, out_endian=Endian.BIG), "ABCDEF"),
        ]
    )
    def test_str(self, value: Bytes, output: bytes):
        assert str(value) == output

    @pytest.mark.parametrize(
        ["left", "right", "is_equal"], [
            (Bytes(), Bytes(), True),
            (Bytes(value=0), Bytes(value=0), True),
            (Bytes(value=1), Bytes(value=0), False),
            (Bytes(value=1), Bytes(value=1), True),
            (Bytes(value=1), Bytes(value=2), False)
        ]
    )
    def test_eq(self, left: Bytes, right: Bytes, is_equal: bool):
        assert (left == right) is is_equal

    def test_eq_raises_value_error(self):
        with pytest.raises(ValueError):
            assert Bytes(value="0x00") == 0x00

    @pytest.mark.parametrize(
        ["left", "right", "is_less_than"], [
            (Bytes(value=0), Bytes(value=0), False),
            (Bytes(value=1), Bytes(value=0), False),
            (Bytes(value=1), Bytes(value=1), False),
            (Bytes(value=1), Bytes(value=2), True),
            (Bytes(value=2), Bytes(value=1), False),
            (Bytes(value=0), Bytes(value=1), True),
        ]
    )
    def test_lt(self, left: Bytes, right: Bytes, is_less_than: bool):
        assert (left < right) is is_less_than

    @pytest.mark.parametrize(
        ["value", "length"], [
            (Bytes(value=0x12345), 3),
            (Bytes(value=0x123456, length=2), 2),
            (Bytes(value=0x00), 1),
            (Bytes(value=0x00, length=3), 3),
            (Position(value=0x00), 3),
        ]
    )
    def test_len(self, value: Bytes, length: int):
        assert len(value) == length

    @pytest.mark.parametrize(
        ["value", "output"], [
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.BIG, length=None), Bytes(value=b"\x34\x56", in_endian=Endian.BIG)),
            (Bytes(value=b"\x12\x34\x56", in_endian=Endian.LITTLE, length=None), Bytes(value=b"\x34\x12", in_endian=Endian.BIG)),
        ]
    )
    def test_get_item(self, value: Bytes, output: int):
        assert value[1:] == output

class TestPosition:

    @pytest.mark.parametrize(
        ["value", "bank"], [
            (Position(value=0x00), 0x000000),
            (Position(value=0x123456), 0x120000)
        ]
    )
    def test_bank(self, value: Position, bank: int):
        assert value.bank() == bank

    @pytest.mark.parametrize(
        ["address", "position"], [
            ("C0/0000", Position(value=0x000000)),
            ("FF/FFFF", Position(value=0x3FFFFF))
        ]
    )
    def test_from_snes_address(self, address: str, position: Position):
        assert Position.from_snes_address(value=address) == position

    @pytest.mark.parametrize(
        ["value", "output"], [
            (Position(value=b""), "C0/0000"),
            (Position(value=b"\x00"), "C0/0000"),
            (Position(value=b"\x12\x34\x56"), "D2/3456"),
            (Position(value=b"\x56\x34\x12", in_endian=Endian.LITTLE), "D2/3456")
        ]
    )
    def test_to_snes_address(self, value: Position, output: str):
        assert value.to_snes_address() == output
