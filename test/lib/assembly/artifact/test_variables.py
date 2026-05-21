import pytest

from src.lib.assembly.artifact.variable import SimpleVar, Variable, Label
from src.lib.assembly.artifact.variables import Variables
from src.lib.misc.exception import VariableConflict
from src.lib.assembly.bytes import Bytes
from test.lib.assembly.conftest import ALFA, CHARLIE, VARIABLES, BRAVO, DELTA, ECHO, pos


class TestVariables:
    def test_append(self):
        variables = Variables()
        variables.append(ALFA)
        variables.append(CHARLIE)
        assert variables == Variables(ALFA, CHARLIE)

    def test_append_raises_variable_conflict_because_of_existing_position(self):
        variables = Variables(CHARLIE)
        with pytest.raises(VariableConflict) as e:
            variables.append(CHARLIE)
        assert "position" in str(e.value).lower()

    def test_append_raises_variable_conflict_because_of_existing_name(self):
        variables = Variables(ALFA)
        with pytest.raises(VariableConflict) as e:
            variables.append(SimpleVar(pos(0), "alfa"))
        assert "name" in str(e.value).lower()

    @pytest.mark.parametrize(["name", "variable"], [("alfa", ALFA), ("charlie", CHARLIE), ("non_existing", None)])
    def test_find_by_name(self, name: str, variable: Variable | None):
        assert VARIABLES.find_by_name(name) == variable

    @pytest.mark.parametrize(["position", "label"], [(0x123456, CHARLIE), (0x7EFFFF, None)])
    def test_find_by_position(self, position: int, label: Label | None):
        variables = Variables(*VARIABLES)
        assert variables.find_by_position(pos(position)) == label

    def test_sort(self):
        variables = Variables(*VARIABLES[::-1])

        assert variables == Variables(DELTA, BRAVO, ALFA, ECHO, CHARLIE)

        variables.sort()

        assert variables == Variables(ALFA, BRAVO, DELTA, CHARLIE, ECHO)

    @pytest.mark.parametrize(
        ["variable", "expected"], [(ALFA, True), (CHARLIE, True), (SimpleVar(Bytes.from_int(0), "non_existing"), False)]
    )
    def test_contains(self, variable: Variable, expected: bool):
        assert (variable in VARIABLES) is expected
