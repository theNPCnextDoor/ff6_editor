from __future__ import annotations
import pytest

from src.lib.assembly.artifact.label import Label
from src.lib.assembly.bytes import Bytes


TEST_BYTE = Bytes([0x12])
TEST_WORD = Bytes([0x12, 0x34])
TEST_POSITION = Bytes([0x12, 0x34, 0x56])


@pytest.fixture
def labels() -> list[Label]:
    return [
        Label(name="label_1", value=TEST_POSITION),
        Label(name="label_2", value=Bytes([0x34, 0xFF, 0xFE])),
    ]
