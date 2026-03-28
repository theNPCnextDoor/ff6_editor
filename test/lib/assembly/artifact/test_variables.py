import pytest

from src.lib.assembly.artifact.variable import SimpleVar, Variable, Label
from src.lib.assembly.artifact.variables import Variables, VariableConflict
from src.lib.assembly.bytes import Bytes
from test.lib.assembly.conftest import ALFA, CHARLIE, VARIABLES, BRAVO, DELTA, ECHO


class TestVariables:
    def test_append(self):
        variables = Variables()
        variables.append(ALFA)
        variables.append(CHARLIE)
        assert variables.simple_variables == [ALFA]
        assert variables.labels == [CHARLIE]

    def test_append_raises_variable_conflict_because_of_existing_position(self):
        variables = Variables(CHARLIE)
        with pytest.raises(VariableConflict) as e:
            variables.append(CHARLIE)
        assert "position" in str(e.value).lower()

    def test_append_raises_variable_conflict_because_of_existing_name(self):
        variables = Variables(ALFA)
        with pytest.raises(VariableConflict) as e:
            variables.append(SimpleVar(Bytes.from_position(0), "alfa"))
        assert "name" in str(e.value).lower()

    @pytest.mark.parametrize(["name", "variable"], [("alfa", ALFA), ("charlie", CHARLIE), ("non_existing", None)])
    def test_find_by_name(self, name: str, variable: Variable | None):
        variables = Variables(*VARIABLES)
        assert variables.find_by_name(name) == variable

    @pytest.mark.parametrize(["position", "label"], [(0x123456, CHARLIE), (0x7EFFFF, None)])
    def test_find_by_position(self, position: int, label: Label | None):
        variables = Variables(*VARIABLES)
        assert variables.find_by_position(Bytes.from_position(position)) == label

    def test_sort(self):
        variables = Variables(*VARIABLES[::-1])

        assert variables.simple_variables == [DELTA, BRAVO, ALFA]
        assert variables.labels == [ECHO, CHARLIE]

        variables.sort()

        assert variables.simple_variables == [ALFA, BRAVO, DELTA]
        assert variables.labels == [CHARLIE, ECHO]

    @pytest.mark.parametrize(
        ["variable", "expected"], [(ALFA, True), (CHARLIE, True), (SimpleVar(Bytes.from_int(0), "non_existing"), False)]
    )
    def test_contains(self, variable: Variable, expected: bool):
        variables = Variables(*VARIABLES)
        assert (variable in variables) is expected
