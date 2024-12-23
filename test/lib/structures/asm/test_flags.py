import re

import pytest

from src.lib.structures.asm.flags import Flags, RegisterWidth
from src.lib.structures.asm.regex import Regex


class TestFlags:
    @pytest.mark.parametrize(
        ["flags", "output"],
        [
            (Flags(), "m=16,x=16"),
            (Flags(m=RegisterWidth.EIGHT_BITS), "m=8,x=16"),
            (Flags(x=RegisterWidth.EIGHT_BITS), "m=16,x=8"),
        ],
    )
    def test_str(self, flags: Flags, output: str):
        assert str(flags) == output

    @pytest.mark.parametrize(
        "line,m,x",
        [
            ("m=8,x=16", True, False),
            ("m=16,x=8", False, True),
            ("m=true,x=false", True, False),
            ("m=false,x=true", False, True),
        ],
    )
    def test_from_regex_match(self, line: str, m: bool, x: bool):
        match = re.match(Regex.FLAGS_LINE, line)
        flags = Flags.from_regex_match(match)
        assert flags.m is m
        assert flags.x is x
