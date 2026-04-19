from __future__ import annotations

import pytest

from src.lib.assembly.data_structure.instruction.operand import Operand
from src.lib.assembly.bytes import Bytes
from src.lib.assembly.data_structure.blob import Blob
from test.lib.assembly.conftest import TEST_BYTE, BRAVO, ALFA


class TestBlob:
    @pytest.mark.parametrize(
        ["blob", "position", "data"],
        [
            (Blob(operand=Bytes([0x12, 0x34, 0x56, 0x78])), Bytes([0x00, 0x00, 0x00]), Bytes([0x12, 0x34, 0x56, 0x78])),
            (
                Blob(operand=Bytes([0x9A, 0xBC, 0xDE, 0xF0]), position=Bytes([0x56, 0x34, 0x12])),
                Bytes([0x56, 0x34, 0x12]),
                Bytes([0x9A, 0xBC, 0xDE, 0xF0]),
            ),
        ],
    )
    def test_init(self, blob: Blob, position: Bytes, data: Bytes):
        assert blob.position == position
        assert blob.operand == data

    @pytest.mark.parametrize(
        ["operand", "delimiter", "blob"],
        [
            ("$12", None, Blob(operand=Operand(TEST_BYTE))),
            ("$0123456789ABCDEF", None, Blob(operand=Operand(Bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF])))),
        ],
    )
    def test_from_string(self, operand: str, delimiter: str | None, blob: Blob):
        assert Blob.from_string(operand, delimiter) == blob

    @pytest.mark.parametrize(
        ["data", "blob"],
        [
            (b"\x12", Blob(operand=Operand(TEST_BYTE))),
            (
                b"\x01\x23\x45\x67\x89\xab\xcd\xef",
                Blob(operand=Operand(Bytes([0xEF, 0xCD, 0xAB, 0x89, 0x67, 0x45, 0x23, 0x01]))),
            ),
            (b"\xff\xff", Blob(operand=Operand(Bytes([0xFF, 0xFF])))),
        ],
    )
    def test_from_bytes(self, data: bytes, blob: Blob):
        assert Blob.from_bytes(data) == blob

    @pytest.mark.parametrize(
        ["blob", "expected"],
        [
            (Blob(operand=Operand(Bytes([0x12, 0x34, 0x56, 0x78]))), "$12345678"),
            (
                Blob(
                    operand=Operand(Bytes([0x12, 0x34]), variable=BRAVO),
                    delimiter=Operand(Bytes([0x12]), variable=ALFA),
                ),
                "bravo,alfa",
            ),
        ],
    )
    def test_str(self, blob: Blob, expected: str):
        assert str(blob) == expected

    @pytest.mark.parametrize(
        ["blob", "expected"],
        [
            (
                Blob(operand=Operand(Bytes([0x12, 0x34, 0x56, 0x78]))),
                "Blob(position=0x000000, as_str='$12345678', as_bytes=b'xV4\\x12', as_hexa=0x12345678)",
            ),
            (
                Blob(
                    operand=Operand(Bytes([0x12, 0x34]), variable=BRAVO),
                    delimiter=Operand(Bytes([0x12]), variable=ALFA),
                ),
                "Blob(position=0x000000, as_str='bravo,alfa', as_bytes=b'4\\x12\\x12', as_hexa=0x123412, operand_var=SimpleVar(0x1234, 'bravo'), delimiter_var=SimpleVar(0x12, 'alfa'))",
            ),
        ],
    )
    def test_repr(self, blob: Blob, expected: str):
        assert repr(blob) == expected

    @pytest.mark.parametrize(
        ["blob", "show_address", "expected"],
        [
            (Blob(operand=Operand(Bytes([0x12, 0x34, 0x56, 0x78]))), False, "  $12345678"),
            (Blob(operand=Operand(Bytes([0x12, 0x34, 0x56, 0x78]))), True, "  $12345678 ; C00000"),
        ],
    )
    def test_to_line(self, blob: Blob, show_address: bool, expected: str):
        assert blob.to_line(show_address=show_address) == expected

    @pytest.mark.parametrize(
        ["blob", "length"],
        [
            (Blob(operand=Bytes([0x12, 0x34, 0x56, 0x78])), 4),
        ],
    )
    def test_len(self, blob: Blob, length: int):
        assert len(blob) == length

    @pytest.mark.parametrize(
        ["blob", "output"],
        [
            (Blob(operand=Bytes([0x12, 0x34, 0x56, 0x78])), b"\x78\x56\x34\x12"),
            (Blob(operand=Bytes([0x12, 0x34, 0x56, 0x78]), delimiter=Bytes([0x00])), b"\x78\x56\x34\x12\x00"),
            (Blob(operand=Bytes([0x12, 0x34, 0x56, 0x78]), delimiter=Bytes([0xFF])), b"\x78\x56\x34\x12\xff"),
        ],
    )
    def test_bytes(self, blob: Blob, output: Bytes):
        assert bytes(blob) == output
