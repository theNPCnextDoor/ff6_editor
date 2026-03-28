import re

import pytest

from src.lib.assembly.bytes import Bytes
from src.lib.assembly.data_structure.regex import Regex
from src.lib.assembly.artifact.variable import SimpleVar, Label, Variable
from test.lib.assembly.conftest import ALFA, BRAVO, CHARLIE, ECHO


class TestVariable:
    @pytest.mark.parametrize(["variable", "name"], [(ALFA, "alfa"), (CHARLIE, "charlie")])
    def test_str(self, variable: Variable, name: str):
        assert str(variable) == name

    @pytest.mark.parametrize(
        ["variable", "expected"],
        [(ALFA, "SimpleVar(0x12, alfa)"), (CHARLIE, "Label(0x123456, charlie)"), (ECHO, "Label(0x7E0123, echo)")],
    )
    def test_repr(self, variable: Variable, expected: str):
        assert repr(variable) == expected

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            (ALFA, SimpleVar(Bytes.from_int(0x12), "alfa"), True),
            (CHARLIE, Label(Bytes.from_position(0x123456), "charlie"), True),
            (ALFA, SimpleVar(Bytes.from_int(0x13), "alfa"), False),
            (ALFA, SimpleVar(Bytes.from_int(0x12), "alfo"), False),
        ],
    )
    def test_eq(self, left: Variable, right: Variable, expected: bool):
        assert (left == right) is expected


class TestSimpleVariable:
    @pytest.mark.parametrize(
        ["line", "variable"],
        [
            ("db alfa = $12", ALFA),
            ("dw bravo = $1234", BRAVO),
        ],
    )
    def test_from_match(self, line: str, variable: SimpleVar):
        match = re.fullmatch(Regex.VARIABLE_ASSIGNMENT, line)
        assert SimpleVar.from_match(match) == variable

    @pytest.mark.parametrize(
        "line",
        [
            "dw alice = $12",
            "db bob = $1234",
            "db charlie = $123456",
            "dw charlie = $123456",
        ],
    )
    def test_from_match_but_length_doesnt_correspond_to_expectation(self, line: str):
        match = re.fullmatch(Regex.VARIABLE_ASSIGNMENT, line)
        with pytest.raises(ValueError):
            SimpleVar.from_match(match)

    @pytest.mark.parametrize(
        ["variable", "line"],
        [(ALFA, "db alfa = $12"), (BRAVO, "dw bravo = $1234")],
    )
    def test_to_line(self, variable: SimpleVar, line: str):
        assert variable.to_line() == line


class TestLabel:
    @pytest.mark.parametrize(
        ["label", "expected"],
        [
            (Label(Bytes.from_position(0x111222)), "label_d11222"),
            (Label(Bytes.from_position(0x7E1222)), "label_7e1222"),
            (Label(Bytes.from_position(0x111222), "with_name"), "with_name"),
        ],
    )
    def test_init(self, label: Label, expected: str):
        assert label.name == expected

    @pytest.mark.parametrize(
        ["line", "position", "expected"],
        [
            ("@golf", Bytes.from_position(0x123456), Label(Bytes.from_position(0x123456), "golf")),
            ("@hotel = $C3FFFF", Bytes.from_position(0), Label(Bytes.from_position(0x03FFFF), "hotel")),
            ("@india = $7E4455", Bytes.from_position(0), Label(Bytes.from_position(0x7E4455), "india")),
            ("@juliett", Bytes.from_position(0x7E3690), Label(Bytes.from_position(0x7E3690), "juliett")),
        ],
    )
    def test_from_match(self, line: str, position: Bytes, expected: Label):
        match = re.match(Regex.LABEL_LINE, line)
        assert Label.from_match(match=match, position=position) == expected

    @pytest.mark.parametrize(
        ["label", "show_address", "line"],
        [
            (CHARLIE, False, "@charlie"),
            (CHARLIE, True, "\n@charlie = $D23456"),
            (ECHO, False, "@echo"),
            (ECHO, True, "\n@echo = $7E0123"),
        ],
    )
    def test_to_line(self, label: Label, show_address: bool, line: str):
        assert label.to_line(show_address=show_address) == line
