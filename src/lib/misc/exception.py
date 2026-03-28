from __future__ import annotations


class TooManyCandidatesException(Exception):
    pass


class NoCandidateException(Exception):
    pass


class MissingSectionAttribute(Exception):
    pass


class UnderflowError(Exception):
    pass


class UnrecognizedBlob(Exception):
    pass


class ReassignmentException(Exception):
    pass


class ImpossibleDestination(Exception):
    pass


class NoLabelException(Exception):
    pass


class NoVariableException(Exception):
    pass


class LabelConflict(Exception):
    pass


class LineConflict(Exception):
    pass


class UnrecognizedLine(Exception):
    pass
