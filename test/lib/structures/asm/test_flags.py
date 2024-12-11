import pytest

from src.lib.structures.asm.flags import Flags, RegisterWidth


class TestFlags:
    @pytest.mark.parametrize(
        ["flags", "output"], [
            (Flags(), "m=16,x=16"),
            (Flags(m=RegisterWidth.EIGHT_BITS), "m=8,x=16"),
            (Flags(x=RegisterWidth.EIGHT_BITS), "m=16,x=8")
        ]
    )
    def test_str(self, flags: Flags, output: str):
        assert str(flags) == output