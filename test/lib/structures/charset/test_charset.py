import pytest

from src.lib.structures.charset.charset import MENU_CHARSET, Charset


class TestCharset:

    @pytest.mark.parametrize(
        ["value", "char"], [(0x00, "<0x00>"), (0x80, "A"), (0xCF, "<DOTTED PIPE>"), (0xEB, "<0xEB>"), (0xFF, " ")]
    )
    def test_get_char(self, value: int, char: str):
        assert Charset(charset=MENU_CHARSET).get_char(value=value) == char

    @pytest.mark.parametrize(
        ["value", "number"], [("<0x00>", 0x00), ("A", 0x80), ("<DOTTED PIPE>", 0xCF), ("<0xEB>", 0xEB), (" ", 0xFF)]
    )
    def test_get_int(self, value: str, number: int):
        assert Charset(charset=MENU_CHARSET).get_int(value=value) == number

    @pytest.mark.parametrize(
        ["value", "number"],
        [("<0x00>", b"\x00"), ("A", b"\x80"), ("<DOTTED PIPE>", b"\xCF"), ("<0xEB>", b"\xEB"), (" ", b"\xFF")],
    )
    def test_get_bytes(self, value: str, number: bytes):
        assert Charset(charset=MENU_CHARSET).get_bytes(value=value) == number
