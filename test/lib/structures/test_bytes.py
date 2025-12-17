import pytest

from src.lib.structures.bytes import Bytes, BEBytes, Position


class TestBytes:

    @pytest.mark.parametrize(
        ["input_value", "length", "expected"],
        [([1, 2, 3], None, [1, 2, 3]), ([1, 2, 3], 2, [2, 3]), ([1, 2, 3], 3, [1, 2, 3]), ([1, 2, 3], 4, [0, 1, 2, 3])],
    )
    def test_init(self, input_value: list[int] | None, length: int | None, expected: list[int]):
        input = Bytes(value=input_value, length=length)
        assert input.value == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"], [("00", [0x00]), ("12", [0x12]), ("0000", [0x00, 0x00]), ("1234", [0x12, 0x34])]
    )
    def test_from_str(self, input_value: str, expected: list[int]):
        assert Bytes.from_str(value=input_value).value == expected

    @pytest.mark.parametrize("input_value", ["", "C"])
    def test_from_str_malformed_string_raises_error(self, input_value: str):
        with pytest.raises(ValueError):
            Bytes.from_str(value=input_value)

    def test_from_bytes_empty_object_raises_error(self):
        with pytest.raises(ValueError):
            Bytes.from_bytes(value=b"")

    @pytest.mark.parametrize(["input_value", "expected"], [([0x00], "00"), ([0x12], "12"), ([0x12, 0x34], "1234")])
    @pytest.mark.parametrize("method", ["__str__", "__repr__"])
    def test_str(self, input_value: list[int], expected: str, method: str):
        assert getattr(Bytes(value=input_value), method)() == expected

    @pytest.mark.parametrize(["input_value", "expected"], [([0x00], 1), ([0x12], 1), ([0x12, 0x34], 2)])
    def test_len(self, input_value: list[int], expected: int):
        assert len(Bytes(value=input_value)) == expected

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            ([0x00], [0x00], True),
            ([0x12], [0x12], True),
            ([0x00, 0x12], [0x12], False),
            ([0x12, 0x34], [0x12, 0x34], True),
            ([0x12, 0x34], [0x34, 0x12], False),
        ],
    )
    def test_eq(self, left: list[int], right: list[int], expected: bool):
        assert (Bytes(value=left) == Bytes(value=right)) is expected

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            ([0x00], [0x00], False),
            ([0x12], [0x12], False),
            ([0x00, 0x12], [0x12], False),
            ([0x12, 0x34], [0x12, 0x34], False),
            ([0x34, 0x12], [0x12, 0x34], True),
        ],
    )
    def test_lt(self, left: list[int], right: list[int], expected: bool):
        assert (Bytes(value=left) < Bytes(value=right)) is expected

    @pytest.mark.parametrize("method", ["__eq__", "__lt__"])
    def test_comparison_when_not_comparing_with_bytes_raises_error(self, method: str):
        with pytest.raises(ValueError):
            getattr(Bytes(value=[0x00]), method)(0x00)

    @pytest.mark.parametrize(
        ["input_value", "expected"],
        [(Bytes([0x00])[0], [0x00]), (Bytes([0x12])[0], [0x12]), (Bytes([0x12, 0x34, 0x56])[1:], [0x34, 0x56])],
    )
    def test_get_item(self, input_value: Bytes, expected: list[int]):
        assert input_value.value == expected

    @pytest.mark.parametrize("right", [0x34, Bytes(value=[0x34]), Bytes(value=[0x34, 0x00])])
    def test_add(self, right: int | Bytes):
        assert Bytes(value=[0x12]) + right == Bytes(value=[0x46])

    @pytest.mark.parametrize("right", [0xFF, Bytes(value=[0xFF])])
    def test_add_raises_error_when_overflow(self, right: int | Bytes):
        with pytest.raises(ValueError):
            Bytes(value=[0x01]) + right

    @pytest.mark.parametrize("right", [0x34, Bytes(value=[0x34]), Bytes(value=[0x34, 0x00])])
    def test_sub(self, right: int | Bytes):
        assert Bytes(value=[0x46]) - right == Bytes(value=[0x12])

    @pytest.mark.parametrize("right", [0xFF, Bytes(value=[0xFF])])
    def test_sub_raises_error_when_underflow(self, right: int | Bytes):
        with pytest.raises(ValueError):
            Bytes(value=[0x01]) - right

    @pytest.mark.parametrize(
        ["input_value", "length", "expected"],
        [
            (0x00, None, [0x00]),
            (0x00, 2, [0x00, 0x00]),
            (0x1234, None, [0x12, 0x34]),
            (0x1234, 1, [0x34]),
            (0x1234, 3, [0x00, 0x12, 0x34]),
        ],
    )
    def test_from_int(self, input_value: int, length: int, expected: list[int]):
        input = Bytes.from_int(value=input_value, length=length)
        assert input.value == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"],
        [(b"\x00", [0x00]), (b"\x12", [0x12]), (b"\x00\x00", [0x00, 0x00]), (b"\x12\x34", [0x34, 0x12])],
    )
    def test_from_bytes(self, input_value: bytes, expected: list[int]):
        assert Bytes.from_bytes(value=input_value).value == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"],
        [([0x00], 0), ([0x12], 0x12), ([0x12, 0x34], 0x3412), ([0x56, 0x34, 0x12], 0x123456)],
    )
    def test_int(self, input_value: list[int], expected: int):
        assert int(Bytes(value=input_value)) == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"], [([0x00], b"\x00"), ([0x12], b"\x12"), ([0x12, 0x34], b"\x34\x12")]
    )
    def test_bytes(self, input_value: list[int], expected: bytes):
        assert bytes(Bytes(value=input_value)) == expected


class TestBEBytes:

    @pytest.mark.parametrize(
        ["input_value", "length", "expected"],
        [
            (0x00, None, [0x00]),
            (0x00, 2, [0x00, 0x00]),
            (0x1234, None, [0x12, 0x34]),
            (0x1234, 1, [0x34]),
            (0x1234, 3, [0x00, 0x12, 0x34]),
        ],
    )
    def test_from_int(self, input_value: int, length: int, expected: list[int]):
        input = BEBytes.from_int(value=input_value, length=length)
        assert input.value == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"],
        [(b"\x00", [0x00]), (b"\x12", [0x12]), (b"\x00\x00", [0x00, 0x00]), (b"\x12\x34", [0x12, 0x34])],
    )
    def test_from_bytes(self, input_value: bytes, expected: list[int]):
        assert BEBytes.from_bytes(value=input_value).value == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"],
        [([0x00], 0x00), ([0x12], 0x12), ([0x12, 0x34], 0x1234), ([0x56, 0x34, 0x12], 0x563412)],
    )
    def test_int(self, input_value: list[int], expected: int):
        assert int(BEBytes(value=input_value)) == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"], [([0x00], b"\x00"), ([0x12], b"\x12"), ([0x12, 0x34], b"\x12\x34")]
    )
    def test_bytes(self, input_value: list[int], expected: bytes):
        assert bytes(BEBytes(value=input_value)) == expected


class TestPosition:
    @pytest.mark.parametrize(
        ["input_value", "expected"],
        [([0x00], [0x00, 0x00, 0x00]), ([0x12, 0x34], [0x00, 0x12, 0x34]), ([0x12, 0x34, 0x56], [0x12, 0x34, 0x56])],
    )
    def test_init(self, input_value: list[int], expected: list[int]):
        assert Position(value=[0x00]).value == [0x00, 0x00, 0x00]

    @pytest.mark.parametrize(["address", "expected"], [("C00000", [0x00, 0x00, 0x00]), ("D23456", [0x12, 0x34, 0x56])])
    def test_from_snes_address(self, address: str, expected: list[int]):
        assert Position.from_snes_address(address=address).value == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"], [([0x00, 0x00, 0x00], "C00000"), ([0x12, 0x34, 0x56], "D23456")]
    )
    def test_to_snes_address(self, input_value: list[int], expected: str):
        assert Position(value=input_value).to_snes_address() == expected

    @pytest.mark.parametrize(
        ["input_value", "expected"], [([0x00, 0x00, 0x00], 0x000000), ([0x12, 0x34, 0x56], 0x120000)]
    )
    def test_to_bank(self, input_value: list[int], expected: int):
        assert Position(value=input_value).bank() == expected
