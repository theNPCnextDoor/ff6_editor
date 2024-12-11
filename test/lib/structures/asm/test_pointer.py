import re
from typing import Type

import pytest

from src.lib.structures.bytes import Bytes, Position
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.script_line import NoLabelException, ImpossibleDestination
from src.lib.structures.asm.regex import Regex


class TestPointer:
    @pytest.mark.parametrize(
        ["pointer", "data"], [
            (Pointer(destination=Position(0x001234)), Bytes(0x1234)),
            (Pointer(position=Position(0x112233), destination=Position(0x114455)), Bytes(0x4455))
        ]
    )
    def test_init_data_is_properly_set_when_destination_is_given(self, pointer: Pointer, data: Bytes):
        assert pointer.data == data

    @pytest.mark.parametrize(
        ["pointer", "destination"], [
            (Pointer(data=Bytes(0x1234)), Position(0x001234)),
            (Pointer(position=Position(0x112233), data=Bytes(0x4455)), Position(0x114455))
        ]
    )
    def test_init_destination_is_properly_set_when_data_is_given(self, pointer: Pointer, destination: Bytes):
        assert pointer.destination == destination

    def test_init_value_error_is_raised_when_both_destination_and_data_are_omitted(self):
        with pytest.raises(ValueError):
            Pointer(position=Position(0x123456))

    @pytest.mark.parametrize(
        ["position", "destination"], [
            (Position(), Position(0x010000)),
            (Position(0x112233), Position(0x120000))
        ]
    )
    def test_init_impossible_destination_raise_an_impossible_destination(self, position: Position, destination: Position):
        with pytest.raises(ImpossibleDestination):
            Pointer(position=position, destination=destination)


    @pytest.mark.parametrize(
        ["line", "position", "data", "destination"], [
            (" ptr $1314", Position(0x111111), Bytes(0x1413), Position(0x111413)),
            (" ptr label_1", Position(0x12FF00), Bytes(0x3456), Position(0x123456)),
            (" ptr label_2", Position(0x340003), Bytes(0xFFFE), Position(0x34FFFE))
        ]
    )
    def test_from_regex_match(self, line: str, position: Position, data: Bytes, destination: Position, labels: list[Label]):
        match = re.match(Regex.POINTER, line)
        pointer = Pointer.from_regex_match(match=match, position=position, labels=labels)
        assert pointer.position == position
        assert pointer.data == data
        assert pointer.destination == destination

    @pytest.mark.parametrize(
        ["line", "position", "exception"], [
            (" ptr label_3", Position(0x12FF00), NoLabelException),
            (" ptr label_2", Position(0x110003), ImpossibleDestination)
        ]
    )
    def test_from_regex_match_raise_exception(
        self, line: str, position: Position, exception: Type[Exception], labels: list[Label]
    ):
        match = re.match(Regex.POINTER, line)
        with pytest.raises(exception):
            Pointer.from_regex_match(match=match, position=position, labels=labels)

    @pytest.mark.parametrize(
        ["position", "destination", "expected_result"], [
            (Position("000000"), Position("001122"), True),
            (Position("EECCDD"), Position("EEFFAA"), True),
            (Position("001122"), Position("112233"), False),
            (Position("FFEEDD"), Position("DDEEFF"), False)
        ]
    )
    def test_is_possible_destination(self, position: Position, destination: Position, expected_result: bool):
        assert Pointer._is_possible_destination(position=position, destination=destination) == expected_result

    @pytest.mark.parametrize(
        ["pointer", "expected_bytes"], [
            (Pointer(position=Position("000000"), destination=Position("001122")), b"\x22\x11"),
            (Pointer(position=Position("333333"), destination=Position("334455")), b"\x55\x44")
        ]
    )
    def test_bytes(self, pointer: Pointer, expected_bytes: bytes):
        assert bytes(pointer) == expected_bytes

    @pytest.mark.parametrize(
        ["value", "pointer"], [
            (b"\x00\x01", Pointer(destination=Position("0100"))),
            (b"\x12\x34", Pointer(destination=Position("3412")))
        ]
    )
    def test_from_bytes(self, value: bytes, pointer: Pointer):
        assert Pointer.from_bytes(value=value) == pointer

    @pytest.mark.parametrize(
        ["pointer", "expected"], [
            (Pointer(position=Position(0x120000), destination=Position(value=0x123456)), "ptr $5634"),
            (Pointer(data=Bytes("1234")), "ptr $1234"),
            (Pointer(data=Bytes(0x1234)), "ptr $3412")
        ]
    )
    def test_str(self, pointer: Pointer, expected: str):
        assert str(pointer) == expected

    @pytest.mark.parametrize(
        ["pointer", "show_address", "expected"], [
            (Pointer(position=Position(0x120000), destination=Position(0x123456)), True, "  ptr label_1 # D2/0000"),
            (Pointer(position=Position(0x120000), destination=Position(0x123457)), True, "  ptr $5734 # D2/0000"),
            (Pointer(position=Position(0x120000), destination=Position(0x123456)), False, "  ptr label_1"),
            (Pointer(position=Position(0x120000), destination=Position(0x123457)), False, "  ptr $5734")
        ]
    )
    def test_to_line(self, pointer: Pointer, show_address: bool, expected: str, labels: list[Label]):
        assert pointer.to_line(show_address=show_address, labels=labels) == expected

    def test_len(self):
        assert len(Pointer(position=Position("123456"), destination=Position("124567"))) == 2
