import pytest

from src.lib.assembly.artifact.flags import Flags, RegisterWidth
from src.lib.assembly.bytes import Bytes
from test.lib.assembly.conftest import addr


class TestFlags:
    @pytest.mark.parametrize(
        ["flags", "output"],
        [
            (Flags(), "m = 16, x = 16"),
            (Flags(m=RegisterWidth.EIGHT_BITS), "m = 8, x = 16"),
            (Flags(x=RegisterWidth.EIGHT_BITS), "m = 16, x = 8"),
        ],
    )
    def test_str(self, flags: Flags, output: str):
        assert str(flags) == output

    @pytest.mark.parametrize(
        ["m_flag", "x_flag", "flags"],
        [("8", "8", Flags(m=8, x=8)), ("8", "16", Flags(m=8)), ("16", "8", Flags(x=8)), ("16", "16", Flags())],
    )
    def test_from_line(self, m_flag: str, x_flag: str, flags: Flags):
        assert Flags.from_line(m_flag, x_flag) == flags

    @pytest.mark.parametrize(
        ["m_flag", "x_flag", "address", "expected"],
        [(16, 16, addr(0x000001), False), (16, 8, addr(0), False), (8, 16, addr(0), False), (16, 16, addr(0), True)],
    )
    def test_eq(self, m_flag: int, x_flag: int, address: Bytes, expected: bool):
        assert (Flags(m_flag, x_flag, address) == Flags()) is expected
