import re

import pytest

from src.lib.assembly.artifact.label import Label
from src.lib.assembly.data_structure.regex import Regex
from src.lib.assembly.bytes import Bytes
from test.lib.assembly.conftest import TEST_POSITION


class TestLabel:
    @pytest.mark.parametrize(
        ["line", "position", "expected_position"],
        [
            ("@label_123", TEST_POSITION, TEST_POSITION),
            ("@label_456=C3FFFF", TEST_POSITION, Bytes([0x03, 0xFF, 0xFF])),
        ],
    )
    def test_position(self, line: str, position: Bytes, expected_position: Bytes):
        match = re.match(Regex.LABEL_LINE, line)
        label = Label.from_regex_match(match=match, position=position)
        assert label.position == expected_position

    @pytest.mark.parametrize(
        ["label", "show_address", "name"],
        [
            (Label(name="alice", value=Bytes([0x01, 0x23, 0x45])), True, "\n@alice=C12345"),
            (Label(value=Bytes([0x01, 0x23, 0x45])), False, "@label_c12345"),
        ],
    )
    def test_name(self, label: Label, show_address: bool, name: str):
        assert label.to_line(show_address=show_address) == name

    def test_len(self):
        assert len(Label(value=TEST_POSITION)) == 0
