import re

import pytest

from src.lib.misc.exception import ReassignmentException
from src.lib.structures import Bytes
from src.lib.structures.asm.regex import Regex
from src.lib.structures.asm.variable import Variable
from test.lib.structures.conftest import TEST_POSITION, TEST_BYTE, TEST_WORD


class TestVariable:
    def test_init(self):
        variable = Variable("bob", TEST_POSITION)
        assert variable.name == "bob"
        assert variable.value == TEST_POSITION

    @pytest.mark.parametrize(
        ["line", "variable"],
        [
            ("let .alice = $12", Variable("alice", TEST_BYTE)),
            ("let !bob = $1234", Variable("bob", TEST_WORD)),
            ("let @charlie = $123456", Variable("charlie", TEST_POSITION)),
        ],
    )
    def test_from_match(self, line: str, variable: Variable):
        match = re.fullmatch(Regex.VARIABLE_ASSIGNMENT, line)
        assert Variable.from_match(match) == variable

    @pytest.mark.parametrize(
        "line",
        [
            "let !alice = $12",
            "let @alice = $12",
            "let .bob = $1234",
            "let @bob = $1234",
            "let .charlie = $123456",
            "let !charlie = $123456",
        ],
    )
    def test_from_match_but_length_doesnt_correspond_to_expectation(self, line: str):
        match = re.fullmatch(Regex.VARIABLE_ASSIGNMENT, line)
        with pytest.raises(ValueError):
            Variable.from_match(match)

    def test_from_match_but_name_already_exists(self):
        vars = [Variable("charlie", TEST_POSITION)]
        line = "let @charlie = $112233"
        match = re.fullmatch(Regex.VARIABLE_ASSIGNMENT, line)
        with pytest.raises(ReassignmentException):
            Variable.from_match(match, vars)

    @pytest.mark.parametrize(
        ["left", "right", "expected"],
        [
            (Variable("alice", TEST_BYTE), Variable("alice", TEST_POSITION), False),
            (Variable("alice", TEST_POSITION), Variable("charlie", TEST_POSITION), False),
            (Variable("charlie", TEST_POSITION), Variable("charlie", TEST_POSITION), True),
        ],
    )
    def test_eq(self, left: Variable, right: Variable, expected: bool):
        pass

    @pytest.mark.parametrize(
        ["variable", "length"],
        [(Variable("alice", TEST_BYTE), 1), (Variable("bob", TEST_WORD), 2), (Variable("alice", TEST_POSITION), 3)],
    )
    def test_len(self, variable: Variable, length: int):
        assert len(variable) == length

    @pytest.mark.parametrize(
        ["variable", "line"],
        [
            (Variable("alice", TEST_BYTE), "let .alice = $12"),
            (Variable("bob", TEST_WORD), "let !bob = $1234"),
            (Variable("charlie", TEST_POSITION), "let @charlie = $123456"),
        ],
    )
    def test_to_line(self, variable: Variable, line: str):
        assert variable.to_line() == line

    @pytest.mark.parametrize(
        ["variable", "expected"],
        [
            (Variable("alice", TEST_BYTE), "Variable(name=alice, value=0x12)"),
            (Variable("bob", TEST_WORD), "Variable(name=bob, value=0x1234)"),
            (Variable("charlie", TEST_POSITION), "Variable(name=charlie, value=0x123456)"),
        ],
    )
    def test_repr(self, variable: Variable, expected: str):
        assert repr(variable) == expected

    @pytest.mark.parametrize(
        ["variable", "length", "expected"],
        [
            (Variable("alice", TEST_BYTE), None, b"\x12"),
            (Variable("bob", TEST_WORD), None, b"\x34\x12"),
            (Variable("charlie", TEST_POSITION), None, b"\x56\x34\x12"),
            (Variable("charlie", TEST_POSITION), 1, b"\x12"),
            (Variable("charlie", TEST_POSITION), 2, b"\x56\x34"),
            (Variable("charlie", TEST_POSITION), 3, b"\x56\x34\x12"),
        ],
    )
    def test_to_bytes(self, variable: Variable, length: int | None, expected: bytes):
        assert variable.to_bytes(length) == expected
