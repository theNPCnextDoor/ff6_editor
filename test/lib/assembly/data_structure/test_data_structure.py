import pytest

from src.lib.assembly.artifact.label import Label
from src.lib.assembly.data_structure.data_structure import DataStructure
from src.lib.assembly.bytes import Bytes


class TestDataStructure:

    @pytest.mark.parametrize(
        ["left", "right", "are_equal"],
        [
            (DataStructure(Bytes([0x01])), DataStructure(Bytes([0x01])), True),
            (DataStructure(Bytes([0x01])), DataStructure(Bytes([0x02])), False),
        ],
    )
    def test_eq(self, left: DataStructure, right: DataStructure, are_equal: bool):
        assert (left == right) == are_equal

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            (DataStructure(Bytes([0x00, 0x00, 0x01])), DataStructure(Bytes([0x00, 0x00, 0x01])), True),
            (DataStructure(Bytes([0x00, 0x00, 0x01])), DataStructure(Bytes([0x00, 0x00, 0x02])), True),
            (DataStructure(Bytes([0x00, 0x00, 0x02])), DataStructure(Bytes([0x00, 0x00, 0x01])), False),
            (DataStructure(Bytes([0x00, 0x00, 0x01])), Label(Bytes([0x00, 0x00, 0x01])), False),
            (Label(Bytes([0x00, 0x00, 0x01])), DataStructure(Bytes([0x00, 0x00, 0x01])), True),
        ],
    )
    def test_lt(self, left: DataStructure, right: DataStructure, expected: bool):
        sorted_left = sorted([left, right], key=lambda x: DataStructure.sort(x))[0]
        assert (sorted_left.position == left.position and type(sorted_left) is type(left)) is expected
