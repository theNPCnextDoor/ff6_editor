import re

import pytest

from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import Bytes, Position


class TestLabel:
    @pytest.mark.parametrize(
        ["line", "position", "expected_position"], [
            ("label_123", Position("123456"), Position("123456")),
            ("label_456=C3/FFFF", Position("123456"), Position("03FFFF"))
        ]
    )
    def test_position(self, line: str, position: Bytes, expected_position):
        match = re.match(Regex.LABEL_LINE, line)
        label = Label.from_regex_match(match=match, position=position)
        assert label.position == expected_position

    @pytest.mark.parametrize(
        ["label", "show_address", "name"], [
            (Label(name="alice", position=Position("012345")), True, "\nalice=C1/2345"),
            (Label(position=Position("012345")), False, "label_c12345")
        ]
    )
    def test_name(self, label: Label, show_address: bool, name: str):
        assert label.to_line(show_address=show_address) == name

    def test_len(self):
        assert len(Label(position=Position("123456"))) == 0