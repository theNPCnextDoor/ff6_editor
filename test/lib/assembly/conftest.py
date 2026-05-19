from __future__ import annotations
import pytest

from src.lib.assembly.artifact.variable import Label, SimpleVar
from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.bytes import Bytes


def pos(value: int) -> Bytes:
    return Bytes.from_position(value)


DEFAULT_POSITION = pos(0)


TEST_BYTE = Bytes([0x12])
TEST_WORD = Bytes([0x12, 0x34])
TEST_POSITION = Bytes([0x12, 0x34, 0x56])

ALFA = SimpleVar(Bytes.from_int(0x12), "alfa")
BRAVO = SimpleVar(Bytes.from_int(0x1234), "bravo")
CHARLIE = Label(Bytes.from_position(0x123456), "charlie")
DELTA = SimpleVar(Bytes.from_int(0x00), "delta")
ECHO = Label(pos(0x7E0123), "echo")

VARIABLES = Variables(ALFA, BRAVO, CHARLIE, DELTA, ECHO)


@pytest.fixture
def labels() -> Variables:
    return Variables(
        Label(TEST_POSITION, "label_1"),
        Label(pos(0x34FFFE), "label_2"),
    )
