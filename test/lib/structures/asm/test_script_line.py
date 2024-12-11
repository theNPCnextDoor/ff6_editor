import pytest

from src.lib.structures.asm.label import Label
from src.lib.structures.asm.script_line import ScriptLine
from src.lib.structures.bytes import Position


class TestScriptLine:

    @pytest.mark.parametrize(
        ["left", "right", "are_equal"], [
            (ScriptLine(position=Position(1)), ScriptLine(position=Position(1)), True),
            (ScriptLine(position=Position(1)), ScriptLine(position=Position(2)), False),
        ]
    )
    def test_eq(self, left: ScriptLine, right: ScriptLine, are_equal: bool):
        assert (left == right) == are_equal

    @pytest.mark.parametrize(
        ["left", "right", "expected"], [
            (ScriptLine(position=Position(1)), ScriptLine(position=Position(1)), True),
            (ScriptLine(position=Position(1)), ScriptLine(position=Position(2)), True),
            (ScriptLine(position=Position(2)), ScriptLine(position=Position(1)), False),
            (ScriptLine(position=Position(1)), Label(position=Position(1)), False),
            (Label(position=Position(1)), ScriptLine(position=Position(1)), True)
        ]
    )
    def test_lt(self, left: ScriptLine, right: ScriptLine, expected: bool):
        sorted_left = sorted([left, right], key=lambda x: ScriptLine.sort(x))[0]
        assert (sorted_left.position == left.position and type(sorted_left) == type(left)) is expected
