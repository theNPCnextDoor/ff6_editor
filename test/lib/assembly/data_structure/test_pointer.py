from typing import Type

import pytest

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.bytes import Bytes
from src.lib.assembly.artifact.variable import Label
from src.lib.assembly.data_structure.instruction.operand import Operand, OperandType
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.misc.exception import ImpossibleDestination, NoVariableException
from test.lib.assembly.conftest import TEST_ADDRESS, TEST_WORD, CHARLIE, addr, DEFAULT_ADDRESS


class TestPointer:
    @pytest.mark.parametrize(
        ["operand", "address", "anchor", "pointer"],
        [
            (
                "$1413",
                addr(0x111111),
                None,
                Pointer(
                    address=addr(0x111111),
                    operand=Operand(Bytes([0x14, 0x13]), "_", OperandType.DEFAULT),
                ),
            ),
            (
                "!label_1",
                addr(0xD2FF00),
                None,
                Pointer(
                    address=addr(0xD2FF00),
                    operand=Operand(Bytes([0x34, 0x56]), "_", OperandType.DEFAULT, Label(addr(0xD23456), "label_1")),
                ),
            ),
            (
                "!label_1",
                addr(0x000001),
                Operand(addr(0xD21111)),
                Pointer(
                    address=addr(0x000001),
                    operand=Operand(Bytes([0x23, 0x45]), "_", OperandType.DEFAULT, Label(addr(0xD23456), "label_1")),
                    anchor=Operand(addr(0xD21111)),
                ),
            ),
            (
                "$1413",
                addr(0x000001),
                Operand(addr(0x121111)),
                Pointer(
                    address=addr(0x000001),
                    operand=Operand(Bytes([0x14, 0x13]), "_", OperandType.DEFAULT, None),
                    anchor=Operand(addr(0x121111)),
                ),
            ),
        ],
    )
    def test_from_line(self, operand: str, address: Bytes, anchor: Operand | None, pointer: Pointer, labels: Variables):
        assert Pointer.from_line(operand, address, anchor, labels) == pointer

    @pytest.mark.parametrize(
        ["operand", "address", "anchor", "exception"],
        [
            ("label_3", addr(0x12FF00), None, NoVariableException),
            ("label_1", addr(0x000000), None, ImpossibleDestination),
        ],
    )
    def test_from_line_raise_exception(
        self, operand: str, address: Bytes, anchor: Bytes | None, exception: Type[Exception], labels: Variables
    ):
        with pytest.raises(exception):
            Pointer.from_line(operand, address, anchor, labels)

    @pytest.mark.parametrize(
        ["value", "address", "anchor", "expected", "destination"],
        [
            (
                b"\x00\x01",
                addr(0),
                None,
                Pointer(address=addr(0), operand=Operand(Bytes([0x01, 0x00]))),
                addr(0x000100),
            ),
            (
                b"\x12\x34",
                addr(0x123456),
                None,
                Pointer(address=addr(0x123456), operand=Operand(Bytes([0x34, 0x12]))),
                addr(0x123412),
            ),
            (
                b"\x26\x38",
                addr(0x123456),
                Operand(addr(0x300123)),
                Pointer(
                    address=addr(0x123456),
                    operand=Operand(Bytes([0x38, 0x26])),
                    anchor=Operand(Bytes.from_address(0x300123)),
                ),
                Bytes.from_address(0x303949),
            ),
        ],
    )
    def test_from_bytes(
        self, value: bytes, address: Bytes, anchor: Bytes | None, expected: Pointer, destination: Bytes
    ):
        pointer = Pointer.from_bytes(value=value, address=address, anchor=anchor)
        assert pointer == expected
        assert pointer.destination == destination

    @pytest.mark.parametrize(
        ["pointer", "show_address", "current_anchor", "line"],
        [
            (
                Pointer(address=Bytes.from_address(0), operand=Operand(Bytes([0x11, 0x22]))),
                False,
                Bytes.from_address(0x270123),
                "  ptr $1122",
            ),
            (
                Pointer(address=Bytes.from_address(0x120123), operand=Operand(Bytes([0x34, 0x56]), variable=CHARLIE)),
                False,
                Bytes.from_address(0x270123),
                "  ptr !charlie",
            ),
            (
                Pointer(
                    address=Bytes.from_address(0),
                    operand=Operand(Bytes([0x01, 0x02])),
                    anchor=Operand(Bytes.from_address(0x001010)),
                ),
                False,
                Operand(Bytes.from_address(0x001010)),
                "  rptr $0102",
            ),
            (
                Pointer(
                    address=DEFAULT_ADDRESS,
                    operand=Operand(Bytes([0x01, 0x02])),
                    anchor=Operand(Bytes.from_address(0xC01010)),
                ),
                False,
                Operand(Bytes.from_address(0xE789AB)),
                "\n#$C01010\n  rptr $0102",
            ),
            (
                Pointer(
                    address=Bytes.from_address(0),
                    operand=Operand(Bytes([0x01, 0x02])),
                    anchor=Operand(addr(0xD23456)),
                ),
                False,
                Operand(Bytes.from_address(0xE789AB)),
                "\n#label_1\n  rptr $0102",
            ),
            (
                Pointer(
                    address=Bytes.from_address(0),
                    operand=Operand(Bytes([0x00, 0x00]), variable=CHARLIE),
                    anchor=Operand(Bytes.from_address(0xD23456)),
                ),
                False,
                Operand(Bytes.from_address(0xE789AB)),
                "\n#label_1\n  rptr !charlie",
            ),
        ],
    )
    def test_to_line(
        self,
        pointer: Pointer,
        show_address: bool,
        current_anchor: Bytes,
        line: str,
        labels: Variables,
    ):
        assert pointer.to_line(show_address=show_address, labels=labels, current_anchor=current_anchor) == line

    @pytest.mark.parametrize(
        ["pointer", "expected_bytes"],
        [
            (Pointer(address=Bytes([0x00, 0x00, 0x00]), operand=Operand(Bytes([0x11, 0x22]))), b"\x22\x11"),
            (Pointer(address=Bytes([0x33, 0x33, 0x33]), operand=Operand(Bytes([0x44, 0x55]))), b"\x55\x44"),
        ],
    )
    def test_bytes(self, pointer: Pointer, expected_bytes: bytes):
        assert bytes(pointer) == expected_bytes

    @pytest.mark.parametrize(
        ["pointer", "expected"],
        [
            (Pointer(address=Bytes([0x12, 0x00, 0x00]), operand=Operand(Bytes([0x34, 0x56]))), "ptr $3456"),
            (Pointer(operand=Operand(TEST_WORD)), "ptr $1234"),
        ],
    )
    def test_str(self, pointer: Pointer, expected: str):
        assert str(pointer) == expected

    @pytest.mark.parametrize(
        ["pointer", "expected"],
        [
            (
                Pointer(address=Bytes([0x12, 0x00, 0x01]), operand=Operand(Bytes([0x34, 0x56]))),
                "Pointer(address=0x120001, as_str='ptr $3456', as_bytes=b'V4', as_hexa=0x3456, destination=0x123456)",
            ),
            (
                Pointer(
                    address=Bytes.from_address(0),
                    operand=Operand(TEST_WORD),
                    anchor=Operand(Bytes([0x34, 0x56, 0x78])),
                ),
                "Pointer(address=0x000000, as_str='ptr $1234', as_bytes=b'4\\x12', as_hexa=0x1234, destination=0x3468AC, anchor=0x345678)",
            ),
        ],
    )
    def test_repr(self, pointer: Pointer, expected: str):
        assert repr(pointer) == expected

    def test_len(self):
        assert len(Pointer(address=TEST_ADDRESS, operand=Operand(Bytes([0x45, 0x67])))) == 2

    def test_find_length(self):
        assert Pointer.find_length() == 2
