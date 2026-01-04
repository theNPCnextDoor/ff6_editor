import re
from typing import Type

import pytest

from src.lib.assembly.bytes import Bytes
from src.lib.assembly.artifact.label import Label
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.misc.exception import ImpossibleDestination, NoLabelException
from src.lib.assembly.data_structure.regex import Regex
from test.lib.assembly.conftest import TEST_POSITION, TEST_WORD


class TestPointer:
    @pytest.mark.parametrize(
        ["pointer", "data"],
        [
            (Pointer(destination=Bytes([0x00, 0x34, 0x12]), anchor=None), Bytes([0x34, 0x12])),
            (
                Pointer(position=Bytes([0x11, 0x22, 0x33]), anchor=None, destination=Bytes([0x11, 0x44, 0x55])),
                Bytes([0x44, 0x55]),
            ),
            (Pointer(destination=Bytes([0x12, 0x34, 0x66]), anchor=TEST_POSITION), Bytes([0x00, 0x10])),
        ],
    )
    def test_init_data_is_properly_set_when_destination_is_given(self, pointer: Pointer, data: Bytes):
        assert pointer.data == data

    @pytest.mark.parametrize(
        ["pointer", "destination"],
        [
            (Pointer(data=Bytes([0x34, 0x12]), anchor=None), Bytes([0x00, 0x34, 0x12])),
            (
                Pointer(position=Bytes([0x11, 0x22, 0x33]), anchor=None, data=Bytes([0x44, 0x55])),
                Bytes([0x11, 0x44, 0x55]),
            ),
            (Pointer(data=Bytes([0x00, 0x10]), anchor=TEST_POSITION), Bytes([0x12, 0x34, 0x66])),
        ],
    )
    def test_init_destination_is_properly_set_when_data_is_given(self, pointer: Pointer, destination: Bytes):
        assert pointer.destination == destination

    def test_init_value_error_is_raised_when_both_destination_and_data_are_omitted(self):
        with pytest.raises(ValueError):
            Pointer(position=TEST_POSITION)

    @pytest.mark.parametrize(
        ["position", "anchor", "destination"],
        [
            (Bytes([0x00, 0x00, 0x00]), None, Bytes([0x01, 0x00, 0x00])),
            (Bytes([0x11, 0x22, 0x33]), None, Bytes([0x12, 0x00, 0x00])),
            (Bytes([0x11, 0x22, 0x33]), TEST_POSITION, Bytes([0x11, 0x00, 0x00])),
        ],
    )
    def test_init_impossible_destination_raise_an_impossible_destination(
        self, position: Bytes, anchor: Bytes | None, destination: Bytes
    ):
        with pytest.raises(ImpossibleDestination):
            Pointer(position=position, destination=destination, anchor=anchor)

    @pytest.mark.parametrize(
        ["line", "position", "anchor", "data", "destination"],
        [
            (" ptr $1413", Bytes([0x11, 0x11, 0x11]), None, Bytes([0x14, 0x13]), Bytes([0x11, 0x14, 0x13])),
            (" ptr label_1", Bytes([0x12, 0xFF, 0x00]), None, Bytes([0x34, 0x56]), TEST_POSITION),
            (" ptr label_2", Bytes([0x34, 0x00, 0x03]), None, Bytes([0xFF, 0xFE]), Bytes([0x34, 0xFF, 0xFE])),
            (
                " rptr $1413",
                Bytes([0x01, 0x11, 0x11]),
                TEST_POSITION,
                Bytes([0x14, 0x13]),
                Bytes([0x12, 0x48, 0x69]),
            ),
            (
                " rptr label_1",
                Bytes([0x01, 0xFF, 0x00]),
                TEST_POSITION,
                Bytes([0x00, 0x00]),
                TEST_POSITION,
            ),
            (
                " rptr label_2",
                Bytes([0x01, 0x00, 0x03]),
                Bytes([0x34, 0x00, 0x01]),
                Bytes([0xFF, 0xFD]),
                Bytes([0x34, 0xFF, 0xFE]),
            ),
        ],
    )
    def test_from_regex_match(
        self, line: str, position: Bytes, anchor: Bytes | None, data: Bytes, destination: Bytes, labels: list[Label]
    ):
        match = re.match(Regex.POINTER_LINE, line)
        pointer = Pointer.from_regex_match(match=match, position=position, labels=labels, anchor=anchor)
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
        ["value", "pointer"],
        [
            (b"\x00\x01", Pointer(destination=Bytes([0x00, 0x01, 0x00]))),
            (b"\x12\x34", Pointer(destination=Bytes([0x00, 0x34, 0x12]))),
        ],
    )
    def test_from_bytes(self, value: bytes, pointer: Pointer):
        assert Pointer.from_bytes(value=value) == pointer

    @pytest.mark.parametrize(
        ["current_anchor", "anchor", "expected"],
        [
            (None, None, "  ptr"),
            (None, Bytes([0x12, 0x11, 0x11]), "  rptr"),
            (Bytes([0x00, 0x00, 0x01]), Bytes([0x12, 0x11, 0x11]), "  rptr"),
        ],
    )
    @pytest.mark.parametrize(["destination", "has_label"], [(TEST_POSITION, True), (Bytes([0x12, 0x34, 0x57]), False)])
    @pytest.mark.parametrize("debug", [True, False])
    def test_to_line(
        self,
        labels: list[Label],
        current_anchor: Bytes | None,
        anchor: Bytes | None,
        destination: Bytes,
        has_label: bool,
        expected: str,
        debug: bool,
    ):
        pointer = Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=destination, anchor=anchor)
        if current_anchor:
            expected = "anchor: $D21111\n" + expected
        expected += " label_1" if has_label else f" ${str(pointer.data)}"
        expected += " ; D20000" if debug else ""
        assert pointer.to_line(show_address=debug, labels=labels, current_anchor=current_anchor) == expected

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
        ["left", "right", "expected"],
        [
            (
                Pointer(position=Bytes([0x00, 0x12, 0x34]), destination=Bytes([0x00, 0x56, 0x78])),
                Pointer(position=Bytes([0x00, 0x12, 0x34]), destination=Bytes([0x00, 0x56, 0x78])),
                True,
            ),
            (
                Pointer(
                    position=Bytes([0x00, 0x12, 0x34]),
                    anchor=Bytes([0x00, 0x00, 0x01]),
                    destination=Bytes([0x00, 0x56, 0x78]),
                ),
                Pointer(position=Bytes([0x00, 0x12, 0x34]), destination=Bytes([0x00, 0x56, 0x78])),
                True,
            ),
            (
                Pointer(position=Bytes([0x00, 0x12, 0x34]), destination=Bytes([0x00, 0x56, 0x78])),
                Pointer(position=Bytes([0x00, 0x12, 0x35]), destination=Bytes([0x00, 0x56, 0x78])),
                False,
            ),
        ],
    )
    def test_eq(self, left: Pointer, right: Pointer, expected: bool):
        assert (left == right) is expected

    @pytest.mark.parametrize(
        ["pointer", "expected"],
        [
            (Pointer(position=Bytes([0x12, 0x00, 0x00]), destination=TEST_POSITION), "ptr $3456"),
            (Pointer(data=TEST_WORD), "ptr $1234"),
        ],
    )
    def test_str(self, pointer: Pointer, expected: str):
        assert str(pointer) == expected

    @pytest.mark.parametrize(
        ["pointer", "expected"],
        [
            (
                Pointer(position=Bytes([0x12, 0x00, 0x01]), destination=TEST_POSITION),
                "Pointer(position=0x120001, data=0x3456, destination=0x123456, anchor=0x120000)",
            ),
            (
                Pointer(data=TEST_WORD, anchor=Bytes([0x34, 0x56, 0x78])),
                "Pointer(position=0x000000, data=0x1234, destination=0x3468AC, anchor=0x345678)",
            ),
        ],
    )
    def test_repr(self, pointer: Pointer, expected: str):
        assert repr(pointer) == expected

    def test_len(self):
        assert len(Pointer(position=TEST_POSITION, destination=Bytes([0x12, 0x45, 0x67]))) == 2

    @pytest.mark.parametrize(
        ["data", "destination", "anchor"],
        [
            (TEST_WORD, Bytes([0x12, 0x46, 0x8A]), TEST_POSITION),
            (Bytes([0x00, 0x01]), Bytes([0x00, 0x00, 0x02]), Bytes([0x00, 0x00, 0x01])),
        ],
    )
    def test_data_to_destination(self, data: Bytes, destination: Bytes, anchor: Bytes):
        pointer = Pointer(data=data, anchor=anchor)
        assert pointer._data_to_destination(data=data) == destination
