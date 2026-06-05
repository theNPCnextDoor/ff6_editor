class DelimiterLengthError(Exception):
    pass


class ForbiddenVarName(Exception):
    pass


class ImpossibleDestination(Exception):
    pass


class LineConflict(Exception):
    pass


class MissingSectionAttribute(Exception):
    pass


class NoCandidateException(Exception):
    pass


class NoVariableException(Exception):
    pass


class TooManyCandidatesException(Exception):
    pass


class UndefinedDestination(Exception):
    pass


class UndefinedFlags(Exception):
    pass


class UnderflowError(Exception):
    pass


class UnrecognizedPart(Exception):
    pass


class UnrecognizedLine(Exception):
    pass


class UnrecognizedPrefix(Exception):
    pass


class UnrecognizedSubsectionMode(Exception):
    pass


class VariableConflict(Exception):
    pass


class VariableLengthMismatch(Exception):
    pass
