import re

import pytest

from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import LEBytes, Position


class TestLabel:
    @pytest.mark.parametrize(
        ["line", "position", "expected_position"],
        [
            ("label_123", Position([0x12, 0x34, 0x56]), Position([0x12, 0x34, 0x56])),
            ("label_456=C3FFFF", Position([0x12, 0x34, 0x56]), Position([0x03, 0xFF, 0xFF])),
        ],
    )
    def test_position(self, line: str, position: Position, expected_position: Position):
        match = re.match(Regex.LABEL_LINE, line)
        label = Label.from_regex_match(match=match, position=position)
        assert label.position == expected_position

    @pytest.mark.parametrize(
        ["label", "show_address", "name"],
        [
            (Label(name="alice", position=Position([0x01, 0x23, 0x45])), True, "\nalice=C12345"),
            (Label(position=Position([0x01, 0x23, 0x45])), False, "label_c12345"),
        ],
    )
    def test_name(self, label: Label, show_address: bool, name: str):
        assert label.to_line(show_address=show_address) == name

    def test_len(self):
        assert len(Label(position=Position([0x12, 0x34, 0x56]))) == 0
