import pytest

from src.lib.structures.asm.label import Label
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import Position


class TestScriptLine:

    @pytest.mark.parametrize(
        ["left", "right", "are_equal"],
        [
            (ScriptLine(Position([0x01])), ScriptLine(Position([0x01])), True),
            (ScriptLine(Position([0x01])), ScriptLine(Position([0x02])), False),
        ],
    )
    def test_eq(self, left: ScriptLine, right: ScriptLine, are_equal: bool):
        assert (left == right) == are_equal

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            (ScriptLine(Position([0x01])), ScriptLine(Position([0x01])), True),
            (ScriptLine(Position([0x01])), ScriptLine(Position([0x02])), True),
            (ScriptLine(Position([0x02])), ScriptLine(Position([0x01])), False),
            (ScriptLine(Position([0x01])), Label(Position([0x01])), False),
            (Label(Position([0x01])), ScriptLine(Position([0x01])), True),
        ],
    )
    def test_lt(self, left: ScriptLine, right: ScriptLine, expected: bool):
        sorted_left = sorted([left, right], key=lambda x: ScriptLine.sort(x))[0]
        assert (sorted_left.position == left.position and type(sorted_left) is type(left)) is expected
