import re
from typing import Type

import pytest

from src.lib.structures.bytes import Bytes
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.script_line import NoLabelException, ImpossibleDestination
from src.lib.structures.asm.regex import Regex


class TestPointer:
    @pytest.mark.parametrize(
        ["pointer", "data"],
        [
            (Pointer(destination=Bytes([0x00, 0x34, 0x12])), Bytes([0x34, 0x12])),
            (
                Pointer(position=Bytes([0x11, 0x22, 0x33]), destination=Bytes([0x11, 0x44, 0x55])),
                Bytes([0x44, 0x55]),
            ),
        ],
    )
    def test_init_data_is_properly_set_when_destination_is_given(self, pointer: Pointer, data: Bytes):
        assert pointer.data == data

    @pytest.mark.parametrize(
        ["pointer", "destination"],
        [
            (Pointer(data=Bytes([0x34, 0x12])), Bytes([0x00, 0x34, 0x12])),
            (Pointer(position=Bytes([0x11, 0x22, 0x33]), data=Bytes([0x44, 0x55])), Bytes([0x11, 0x44, 0x55])),
        ],
    )
    def test_init_destination_is_properly_set_when_data_is_given(self, pointer: Pointer, destination: Bytes):
        assert pointer.destination == destination

    def test_init_value_error_is_raised_when_both_destination_and_data_are_omitted(self):
        with pytest.raises(ValueError):
            Pointer(position=Bytes([0x12, 0x34, 0x56]))

    @pytest.mark.parametrize(
        ["position", "destination"],
        [
            (Bytes([0x00, 0x00, 0x00]), Bytes([0x01, 0x00, 0x00])),
            (Bytes([0x11, 0x22, 0x33]), Bytes([0x12, 0x00, 0x00])),
        ],
    )
    def test_init_impossible_destination_raise_an_impossible_destination(self, position: Bytes, destination: Bytes):
        with pytest.raises(ImpossibleDestination):
            Pointer(position=position, destination=destination)

    @pytest.mark.parametrize(
        ["line", "position", "data", "destination"],
        [
            (" ptr $1413", Bytes([0x11, 0x11, 0x11]), Bytes([0x14, 0x13]), Bytes([0x11, 0x14, 0x13])),
            (" ptr label_1", Bytes([0x12, 0xFF, 0x00]), Bytes([0x34, 0x56]), Bytes([0x12, 0x34, 0x56])),
            (" ptr label_2", Bytes([0x34, 0x00, 0x03]), Bytes([0xFF, 0xFE]), Bytes([0x34, 0xFF, 0xFE])),
        ],
    )
    def test_from_regex_match(self, line: str, position: Bytes, data: Bytes, destination: Bytes, labels: list[Label]):
        match = re.match(Regex.POINTER_LINE, line)
        pointer = Pointer.from_regex_match(match=match, position=position, labels=labels)
        assert pointer.position == position
        assert pointer.data == data
        assert pointer.destination == destination

    @pytest.mark.parametrize(
        ["line", "position", "exception"],
        [
            (" ptr label_3", Bytes([0x12, 0xFF, 0x00]), NoLabelException),
            (" ptr label_2", Bytes([0x11, 0x00, 0x03]), ImpossibleDestination),
        ],
    )
    def test_from_regex_match_raise_exception(
        self, line: str, position: Bytes, exception: Type[Exception], labels: list[Label]
    ):
        match = re.match(Regex.POINTER_LINE, line)
        with pytest.raises(exception):
            Pointer.from_regex_match(match=match, position=position, labels=labels)

    @pytest.mark.parametrize(
        ["position", "destination", "expected_result"],
        [
            (Bytes([0x00, 0x00, 0x00]), Bytes([0x00, 0x11, 0x22]), True),
            (Bytes([0xEE, 0xCC, 0xDD]), Bytes([0xEE, 0xFF, 0xAA]), True),
            (Bytes([0x00, 0x11, 0x22]), Bytes([0x11, 0x22, 0x33]), False),
            (Bytes([0xFF, 0xEE, 0xDD]), Bytes([0xDD, 0xEE, 0xFF]), False),
        ],
    )
    def test_is_possible_destination(self, position: Bytes, destination: Bytes, expected_result: bool):
        assert Pointer._is_possible_destination(position=position, destination=destination) == expected_result

    @pytest.mark.parametrize(
        ["pointer", "expected_bytes"],
        [
            (Pointer(position=Bytes([0x00, 0x00, 0x00]), destination=Bytes([0x00, 0x11, 0x22])), b"\x22\x11"),
            (Pointer(position=Bytes([0x33, 0x33, 0x33]), destination=Bytes([0x33, 0x44, 0x55])), b"\x55\x44"),
        ],
    )
    def test_bytes(self, pointer: Pointer, expected_bytes: bytes):
        assert bytes(pointer) == expected_bytes

    @pytest.mark.parametrize(
        ["value", "pointer"],
        [
            (b"\x00\x01", Pointer(destination=Bytes([0x00, 0x01, 0x00]))),
            (b"\x12\x34", Pointer(destination=Bytes([0x00, 0x34, 0x12]))),
        ],
    )
    def test_from_bytes(self, value: bytes, pointer: Pointer):
        assert Pointer.from_bytes(value=value) == pointer

    @pytest.mark.parametrize(
        ["pointer", "expected"],
        [
            (Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=Bytes([0x12, 0x34, 0x56])), "ptr $3456"),
            (Pointer(data=Bytes([0x12, 0x34])), "ptr $1234"),
        ],
    )
    def test_str(self, pointer: Pointer, expected: str):
        assert str(pointer) == expected

    @pytest.mark.parametrize(
        ["pointer", "show_address", "expected"],
        [
            (
                Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=Bytes([0x12, 0x34, 0x56])),
                True,
                "  ptr label_1 ; D20000",
            ),
            (
                Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=Bytes([0x12, 0x34, 0x57])),
                True,
                "  ptr $3457 ; D20000",
            ),
            (
                Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=Bytes([0x12, 0x34, 0x56])),
                False,
                "  ptr label_1",
            ),
            (
                Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=Bytes([0x12, 0x34, 0x57])),
                False,
                "  ptr $3457",
            ),
        ],
    )
    def test_to_line(self, pointer: Pointer, show_address: bool, expected: str, labels: list[Label]):
        assert pointer.to_line(show_address=show_address, labels=labels) == expected

    def test_len(self):
        assert len(Pointer(position=Bytes([0x12, 0x34, 0x56]), destination=Bytes([0x12, 0x45, 0x67]))) == 2
