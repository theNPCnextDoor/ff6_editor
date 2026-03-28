from src.lib.assembly.artifact.variable import Label, SimpleVar, Variable
from src.lib.assembly.bytes import Bytes


class VariableConflict(Exception):
    pass


class Variables:
    """
    Variables consists of two lists. One for simple variables, the other for labels. Labels are used to name an address
    in the ROM, which are 3 bytes. Simple variables contains 1 or 2-bytes values.
    """

    def __init__(self, *variables: Variable):
        self._labels = list()
        self._simple_variables = list()
        for variable in variables:
            self.append(variable)

    def append(self, variable: Variable) -> None:
        """
        First detects if the new variable is conflicting with the known ones. Then, appends the variable either in
        the simple variable list or the label one.
        :param variable: The Variable or Label to be added.
        :return: None.
        """
        self._detect_conflicts(variable)
        if isinstance(variable, Label):
            self._labels.append(variable)
        else:
            self._simple_variables.append(variable)

    def _detect_conflicts(self, variable: Variable) -> None:
        """
        If the variable is a Label, checks first if the position it represents is also represented by another label.
        Then, checks if the name of the variable already exists.
        :param variable: The variable to be inserted in the list.
        :return: None.
        :raises VariableConflict: Raised when a conflict is detected.
        """
        if isinstance(variable, Label):
            for label in self._labels:
                if self.find_by_position(variable.value):
                    raise VariableConflict(
                        f"Position conflict. Label '{label.name}', with position {repr(variable.value)} already exists."
                    )
        if self.find_by_name(variable.name):
            raise VariableConflict(f"Name conflict. Variable '{variable.name}' already exists.")

    def find_by_name(self, name: str) -> Variable | None:
        """
        Returns the variable by its name.
        :param name: The name of the variable.
        :return: The variable if found. None otherwise.
        """
        for variable in self.all():
            if variable.name == name:
                return variable
        return None

    def find_by_position(self, position: Bytes) -> Label | None:
        """
        Return the label by its position.
        :param position: The position of the label.
        :return: The label if found. None otherwise.
        """
        for label in self._labels:
            if label.value == position:
                return label
        return None

    def sort(self) -> None:
        """
        Sorts the simple variables by name and the labels by their position.
        :return: None.
        """
        self._simple_variables.sort(key=lambda x: x.name)
        self._labels.sort(key=lambda x: x.value)

    def all(self) -> list[Variable]:
        """
        :return: A list containing all simple variables and labels.
        """
        return self._simple_variables + self._labels

    @property
    def simple_variables(self) -> list[SimpleVar]:
        """
        :return: The list of simple variables.
        """
        return self._simple_variables

    @property
    def labels(self) -> list[Label]:
        """
        :return: The list of labels.
        """
        return self._labels

    def __contains__(self, item: Variable) -> bool:
        """
        Checks if variable exists in list.
        :param item: The variable to check.
        :return: True if found.
        """
        for var in self.all():
            if item == var:
                return True
        return False
