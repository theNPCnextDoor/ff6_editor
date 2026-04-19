import pytest

from src.lib.assembly.bytes import Bytes
from src.lib.assembly.artifact.variable import SimpleVar, Label, Variable
from src.lib.misc.exception import ForbiddenVarName
from test.lib.assembly.conftest import ALFA, BRAVO, CHARLIE, ECHO


class TestVariable:
    @pytest.mark.parametrize(["variable", "name"], [(ALFA, "alfa"), (CHARLIE, "charlie")])
    def test_str(self, variable: Variable, name: str):
        assert str(variable) == name

    @pytest.mark.parametrize(
        ["variable", "expected"],
        [(ALFA, "SimpleVar(0x12, 'alfa')"), (CHARLIE, "Label(0x123456, 'charlie')"), (ECHO, "Label(0x7E0123, 'echo')")],
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
        ["length", "name", "operand", "variable"],
        [
            ("b", "alfa", "$12", ALFA),
            ("w", "bravo", "$1234", BRAVO),
        ],
    )
    def test_from_string(self, length: str, name: str, operand: str, variable: SimpleVar):
        assert SimpleVar.from_string(length, name, operand) == variable

    @pytest.mark.parametrize(
        "name",
        ["db", "x"],
    )
    def test_from_string_but_name_is_forbidden(self, name: str):
        with pytest.raises(ForbiddenVarName):
            SimpleVar.from_string("b", name, "$12")

    @pytest.mark.parametrize(
        ["length", "name", "operand"],
        [
            ("b", "bravo", "$1234"),
            ("w", "alfa", "$12"),
            ("b", "charlie", "$123456"),
            ("w", "charlie", "$123456"),
        ],
    )
    def test_from_match_but_length_doesnt_correspond_to_expectation(self, length: str, name: str, operand: str):
        with pytest.raises(ValueError):
            SimpleVar.from_string(length, name, operand)

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
        ["name", "snes_address", "position", "label"],
        [
            ("golf", None, Bytes.from_position(0x123456), Label(Bytes.from_position(0x123456), "golf")),
            ("hotel", "$C3FFFF", None, Label(Bytes.from_position(0x03FFFF), "hotel")),
            ("india", "$7E4455", None, Label(Bytes.from_position(0x7E4455), "india")),
            ("juliett", None, Bytes.from_position(0x7E3690), Label(Bytes.from_position(0x7E3690), "juliett")),
        ],
    )
    def test_from_string(self, name: str, snes_address: str | None, position: Bytes | None, label: Label):
        assert Label.from_string(name, snes_address, position) == label

    @pytest.mark.parametrize(
        "name",
        ["db", "x"],
    )
    def test_from_string_but_name_is_forbidden(self, name: str):
        with pytest.raises(ForbiddenVarName):
            Label.from_string(name, "$D23456")

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
