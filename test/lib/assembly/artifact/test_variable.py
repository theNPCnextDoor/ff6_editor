import pytest

from src.lib.assembly.bytes import Bytes
from src.lib.assembly.artifact.variable import SimpleVar, Label, Variable
from src.lib.misc.exception import ForbiddenVarName, VariableLengthMismatch
from test.lib.assembly.conftest import ALFA, BRAVO, CHARLIE, ECHO, addr


class TestVariable:
    @pytest.mark.parametrize(["variable", "name"], [(ALFA, "alfa"), (CHARLIE, "charlie")])
    def test_str(self, variable: Variable, name: str):
        assert str(variable) == name

    @pytest.mark.parametrize(
        ["variable", "expected"],
        [
            (ALFA, "SimpleVar(name='alfa', value=0x12)"),
            (CHARLIE, "Label(name='charlie', value=0xD23456)"),
            (ECHO, "Label(name='echo', value=0x7E0123)"),
        ],
    )
    def test_repr(self, variable: Variable, expected: str):
        assert repr(variable) == expected

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            (ALFA, SimpleVar(Bytes.from_int(0x12), "alfa"), True),
            (CHARLIE, Label(addr(0xD23456), "charlie"), True),
            (ALFA, SimpleVar(Bytes.from_int(0x13), "alfa"), False),
            (ALFA, SimpleVar(Bytes.from_int(0x12), "alfo"), False),
            (ALFA, None, False),
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
    def test_from_line(self, length: str, name: str, operand: str, variable: SimpleVar):
        assert SimpleVar.from_line(length, name, operand) == variable

    @pytest.mark.parametrize(
        "name",
        ["db", "x"],
    )
    def test_from_line_but_name_is_forbidden(self, name: str):
        with pytest.raises(ForbiddenVarName):
            SimpleVar.from_line("b", name, "$12")

    @pytest.mark.parametrize(
        ["length", "name", "operand"],
        [
            ("b", "bravo", "$1234"),
            ("w", "alfa", "$12"),
            ("b", "charlie", "$123456"),
            ("w", "charlie", "$123456"),
        ],
    )
    def test_from_line_but_length_doesnt_correspond_to_expectation(self, length: str, name: str, operand: str):
        with pytest.raises(VariableLengthMismatch):
            SimpleVar.from_line(length, name, operand)

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
            (Label(addr(0x111222)), "label_111222"),
            (Label(addr(0x7E1222)), "label_7e1222"),
            (Label(addr(0x111222), "with_name"), "with_name"),
        ],
    )
    def test_init(self, label: Label, expected: str):
        assert label.name == expected

    @pytest.mark.parametrize(
        ["name", "snes_address", "address", "label"],
        [
            ("golf", None, addr(0x123456), Label(addr(0x123456), "golf")),
            ("hotel", "$C3FFFF", None, Label(addr(0xC3FFFF), "hotel")),
            ("india", "$7E4455", None, Label(addr(0x7E4455), "india")),
            ("juliett", None, addr(0x7E3690), Label(addr(0x7E3690), "juliett")),
        ],
    )
    def test_from_line(self, name: str, snes_address: str | None, address: Bytes | None, label: Label):
        assert Label.from_line(name, snes_address, address) == label

    @pytest.mark.parametrize(
        "name",
        ["db", "x"],
    )
    def test_from_line_but_name_is_forbidden(self, name: str):
        with pytest.raises(ForbiddenVarName):
            Label.from_line(name, "$D23456")

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
