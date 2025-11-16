import re
from typing import Optional

import pytest as pytest

from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.regex import Regex


class TestRegex:
    @pytest.mark.parametrize(
        "line,is_match",
        [
            ("00", True),
            ("AA", True),
            ("9F", True),
            ("1G", False),
        ],
    )
    def test_byte(self, line: str, is_match: bool):
        assert bool(re.search(Regex.BYTE, line)) == is_match

    @pytest.mark.parametrize(
        "line,is_match",
        [
            ("0000", True),
            ("AAAA", True),
            ("9F9F", True),
            ("1G89", False),
        ],
    )
    def test_two_bytes(self, line: str, is_match: bool):
        assert bool(re.search(Regex.TWO_BYTES, line)) == is_match

    @pytest.mark.parametrize(
        "line,is_match", [("00", True), ("AAAA", True), ("9F9F9F", True), ("1G89", False), ("$00", False)]
    )
    def test_data(self, line: str, is_match: bool):
        assert bool(re.fullmatch(Regex.DATA, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ("", False),
            ("a", True),
            ("abc", False),
            ("<WHITE>", True),
            ("<ATB 0>", True),
            ("abc<BLACK><ATB 4>.   fjj:;+=12345", False),
            ("$", False),
            ("abc", False),
            ("<>", False),
            ("<ATB 0", False),
        ],
    )
    def test_menu_char(self, line: str, is_match: bool):
        assert bool(re.fullmatch(Regex.MENU_CHAR, line)) == is_match

    @pytest.mark.parametrize(["line", "is_match"], [(",$FF", True), (" $FF", False), (",$FG", False)])
    @pytest.mark.parametrize("regex", [Regex.DELIMITER_1, Regex.DELIMITER_2])
    def test_delimiter(self, line: str, is_match: bool, regex: str):
        assert bool(re.fullmatch(regex, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match", "group"],
        [
            ("$FF", True, 6),
            ("#$FF", True, 5),
            ("#$FF,#$FF", True, 5),
            ("#$FF,$FF", False, None),
            ("#$FF,S", False, None),
            ("#$FF,X", False, None),
            ("#$FF,Y", False, None),
            ("[#$FF]", False, None),
            ("(#$FF)", False, None),
            ("$FF,S", True, 4),
            ("$FF,X", True, 4),
            ("$FF,Y", True, 4),
            ("($FF)", True, 3),
            ("($FF,X)", True, 3),
            ("($FF,S)", False, None),
            ("($FF,Y)", False, None),
            ("($FF),Y", True, 2),
            ("($FF,S),Y", True, 2),
            ("($FF,X),Y", False, None),
            ("($FF,Y),Y", False, None),
            ("($FF),X", False, None),
            ("($FF),S", False, None),
            ("[$FF]", True, 1),
            ("[$FF],Y", True, 1),
            ("[$FF],X", False, None),
            ("[$FF],S", False, None),
            ("[$FF,S]", False, None),
            ("[$FF,X]", False, None),
            ("[$FF,Y]", False, None),
        ],
    )
    def test_chunk(self, line: str, is_match: bool, group: int):
        match = re.fullmatch(Regex.CHUNK, line)
        assert bool(match) == is_match
        if is_match:
            assert match.group(f"n{group}") == "FF"

    @pytest.mark.parametrize(
        "line,is_match",
        [
            ("C00000", True),
            ("FFFFFF", True),
            ("000000", False),
            ("C00G00", False),
        ],
    )
    def test_snes_address(self, line: str, is_match: bool):
        assert bool(re.match(Regex.SNES_ADDRESS, line)) == is_match

    @pytest.mark.parametrize(
        "line,is_match",
        [
            ("abulita", True),
            ("3bulita", False),
            ("Abulita", False),
            ("aBulita", False),
            ("abu_lita", True),
            ("abul1t4", True),
            ("abulita=granma", False),
        ],
    )
    def test_label(self, line: str, is_match):
        assert bool(re.fullmatch(Regex.LABEL, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ("", False),
            ("$12", True),
            ("$0123456789ABCDEF", True),
            ("$12 # C0/00000", True),
            ("$123", False),
            ("$123,$FF", False),
            ("$12,$FF", True),
            ("$12,$FF # C0/00000", True),
            ("$12,$FFF", False),
        ],
    )
    def test_blob(self, line: str, is_match: bool):
        assert bool(re.match(Regex.BLOB, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ('""', False),
            ('"a"', True),
            ('"abc"', True),
            ('"<WHITE>"', True),
            ('"<ATB 0>"', True),
            ('"abc<BLACK><ATB 4>.   fjj:;+=12345"', True),
            ('"$"', False),
            ("abc", False),
            ('"<>"', False),
            ('"<ATB 0', False),
            ('"a" $00', True),
            ('"a  $00', False),
            ('"<GREY>",$FF', True),
            ('"a",$FFF', False),
            ('"a<LINE>",$FF', True),
            ('"<0x00>"', True),
            ('"<0xFF>",$88', True),
        ],
    )
    def test_menu_string(self, line: str, is_match: bool):
        assert bool(re.match(Regex.MENU_STRING, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ("", False),
            ("$12", True),
            ("$0123456789ABCDEF", True),
            ("$12 # C0/00000", True),
            ("$123", False),
            ("$123,$FF", False),
            ("$12,$FF", True),
            ("$12,$FF # C0/00000", True),
            ("$12,$FFF", False),
            ('""', False),
            ('"a"', True),
            ('"abc"', True),
            ('"<WHITE>"', True),
            ('"<ATB 0>"', True),
            ('"abc<BLACK><ATB 4>.   fjj:;+=12345"', True),
            ('"$"', False),
            ("abc", False),
            ('"<>"', False),
            ('"<ATB 0', False),
            ('"a" $00', True),
            ('"a<LINE>" $00', True),
            ('"a  $00', False),
            ('"<GREY>",$FF', True),
            ('"a",$FFF', False),
            ('"<0x00>"', True),
            ('"<0xFF>",$88', True),
        ],
    )
    def test_any_blob(self, line: str, is_match: bool):
        assert bool(re.match(Regex.ANY_BLOB, line)) == is_match

    @pytest.mark.parametrize(
        "line,m,x",
        [
            ("m=8,x=16", 8, 16),
            ("m=16,x=8", 16, 8),
            ("m=true,x=false", 8, 16),
            ("m=false,x=true", 16, 8),
        ],
    )
    def test_flags_line(self, line: str, m: bool, x: bool):
        match = re.match(Regex.FLAGS_LINE, line)
        flags = Flags.from_regex_match(match)
        assert flags.m is m
        assert flags.x is x

    @pytest.mark.parametrize(
        "line,label,snes_address",
        [
            ("@abulita=C00000", "abulita", "C00000"),
            ("@label_c34567=C34567", "label_c34567", "C34567"),
            ("@abulita", "abulita", None),
        ],
    )
    def test_label_line(self, line: str, label: str, snes_address: Optional[str]):
        match = re.match(Regex.LABEL_LINE, line)
        assert match.group("label") == label
        assert match.group("snes_address") == snes_address

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ("  ", False),
            ("  $12", True),
            ("  $0123456789ABCDEF", True),
            ("  $12 # C0/00000", True),
            ("  $123", False),
            ("  $123,$FF", False),
            ("  $12,$FF", True),
            ("  $12,$FF # C0/00000", True),
            ("  $12,$FFF", False),
        ],
    )
    def test_blob_line(self, line: str, is_match: bool):
        match = re.match(Regex.BLOB_LINE, line)
        assert bool(match) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ('  ""', False),
            ('  "a"', True),
            ('  "abc"', True),
            ('  "<WHITE>"', True),
            ('  "<ATB 0>"', True),
            ('  "abc<BLACK><ATB 4>.   fjj:;+=12345"', True),
            ('  "$"', False),
            ("  abc", False),
            ('  "<>"', False),
            ('  "<ATB 0', False),
            ('  "a" $00', True),
            ('  "a  $00', False),
            ('  "<GREY>",$FF', True),
            ('  "a",$FFF', False),
            ('  "<0x00>"', True),
            ('  "<0xFF>",$88', True),
        ],
    )
    def test_menu_string_line(self, line: str, is_match: bool):
        assert bool(re.match(Regex.MENU_STRING_LINE, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ('  ""', False),
            ('  txt2 ""', False),
            ('  txt2 "abc"', True),
            ('  txt2 "<WHITE>"', True),
            ('  txt2 "<ATB 0>"', True),
            ('  txt2 "abc<BLACK><ATB 4>.   fjj:;+=12345"', True),
            ('  txt2 "$"', False),
            ("  txt2 abc", False),
            ('  txt2 "<>"', False),
            ('  txt2 "<ATB 0', False),
            ('  txt2 "a" $00', True),
            ('  txt2 "a  $00', False),
            ('  txt2 "<GREY>",$FF', True),
            ('  txt2 "a",$FFF', False),
            ('  txt2 "<0x00>"', True),
            ('  txt2 "<0xFF>",$88', True),
            (r'  txt2 "Bob<LINE><FIRE>",$00', True),
        ],
    )
    def test_description_line(self, line: str, is_match: bool):
        assert bool(re.match(Regex.DESCRIPTION_LINE, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "is_match"],
        [
            ('  "a" | $00', True),
            ('  "a" | $00,$FF', True),
            ('  "a",$88 | $00', True),
            ('  "" | $00', False),
            ('  "a" | ', False),
            ('  "a" | "b",$44 | $44 | $44,$44', True),
            ('  $44 | $44,$44 | "a" | "a",$55', True),
            ('  $44 | $44,$44 | "a", | "a",$55', False),
            ('  $CD78 | "Status",$00', True),
        ],
    )
    def test_blob_group_line(self, line: str, is_match: bool):
        assert bool(re.fullmatch(Regex.BLOB_GROUP_LINE, line)) == is_match

    @pytest.mark.parametrize(
        ["line", "command", "chunk"],
        [
            (" AAA", "AAA", None),
            (" AAA $12", "AAA", "$12"),
            (" AAA #$12", "AAA", "#$12"),
            (" AAA #$12,#$34", "AAA", "#$12,#$34"),
            (" AAA $12,S", "AAA", "$12,S"),
            (" AAA $12,X", "AAA", "$12,X"),
            (" AAA $12,Y", "AAA", "$12,Y"),
            (" AAA ($12)", "AAA", "($12)"),
            (" AAA ($12),Y", "AAA", "($12),Y"),
            (" AAA ($12,S),Y", "AAA", "($12,S),Y"),
            (" AAA ($12,X)", "AAA", "($12,X)"),
            (" AAA [$12]", "AAA", "[$12]"),
            (" AAA [$12],Y", "AAA", "[$12],Y"),
        ],
    )
    def test_instruction_line(self, line: str, command: str, chunk: str):
        match = re.match(Regex.INSTRUCTION_LINE, line)
        assert match.group("command") == command
        assert match.group("chunk") == chunk

    @pytest.mark.parametrize(
        ["line", "command", "chunk", "label"],
        [
            (" BCC $AABBCC", "BCC", "$AABBCC", None),
            (" BCS something_something", "BCS", None, "something_something"),
            (" JMP $1234", "JMP", "$1234", None),
            (" JML $123456", "JML", "$123456", None),
            (" JML something_something", "JML", None, "something_something"),
            (" JSR something_something", "JSR", None, "something_something"),
        ],
    )
    def test_branching_instruction_line(self, line: str, command: str, chunk: str, label: str):
        match = re.match(Regex.BRANCHING_INSTRUCTION_LINE, line)
        assert match.group("command") == command
        assert match.group("chunk") == chunk
        assert match.group("label") == label

    @pytest.mark.parametrize(
        ["line", "is_match", "chunk", "label"],
        [
            (" ptr $1234", True, "$1234", None),
            (" ptr $123456", False, None, None),
            (" ptr pastagate", True, None, "pastagate"),
        ],
    )
    def test_pointer_line(self, line: str, is_match: bool, chunk: str, label: str):
        match = re.match(Regex.POINTER_LINE, line)
        assert bool(match) is is_match
        if is_match:
            assert match.group("chunk") == chunk
            assert match.group("label") == label
