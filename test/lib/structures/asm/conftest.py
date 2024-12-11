from __future__ import annotations
import pytest

from src.lib.structures.asm.label import Label
from src.lib.structures.bytes import Position


@pytest.fixture
def labels() -> list[Label]:
    return [
        Label(name="label_1", position=Position(0x123456)),
        Label(name="label_2", position=Position(0X34FFFE))
    ]
