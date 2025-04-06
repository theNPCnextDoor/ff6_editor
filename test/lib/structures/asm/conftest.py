from __future__ import annotations
import pytest

from src.lib.structures.asm.label import Label
from src.lib.structures.bytes import Position


@pytest.fixture
def labels() -> list[Label]:
    return [
        Label(name="label_1", position=Position([0x12, 0x34, 0x56])),
        Label(name="label_2", position=Position([0x34, 0xFF, 0xFE])),
    ]
