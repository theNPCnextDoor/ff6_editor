from __future__ import annotations
import pytest

from src.lib.assembly.artifact.variable import Label, SimpleVar
from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.bytes import Bytes


DEFAULT_POSITION = Bytes.from_position(0)


TEST_BYTE = Bytes([0x12])
TEST_WORD = Bytes([0x12, 0x34])
TEST_POSITION = Bytes([0x12, 0x34, 0x56])

ALFA = SimpleVar(Bytes.from_int(0x12), "alfa")
BRAVO = SimpleVar(Bytes.from_int(0x1234), "bravo")
CHARLIE = Label(Bytes.from_position(0x123456), "charlie")
DELTA = SimpleVar(Bytes.from_int(0xFF), "delta")
ECHO = Label(Bytes.from_position(0x7E0123), "echo")

VARIABLES = [ALFA, BRAVO, CHARLIE, DELTA, ECHO]


@pytest.fixture
def labels() -> Variables:
    return Variables(
        Label(name="label_1", value=TEST_POSITION),
        Label(name="label_2", value=Bytes([0x34, 0xFF, 0xFE])),
    )
