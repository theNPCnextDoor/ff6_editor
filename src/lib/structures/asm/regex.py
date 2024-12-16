from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod

if TYPE_CHECKING:
    from src.lib.structures.asm.label import Label


class Regex:
    NOT_HEXA = r"(?![0-9A-F])"
    BYTE = r"[0-9A-F]{2}"
    TWO_BYTES = rf"[0-9A-F]{{4}}{NOT_HEXA}"
    DATA = rf"({BYTE}){{1,3}}{NOT_HEXA}"
    BLOB = rf"^ +blob \$((?P<n1>({BYTE})+){NOT_HEXA}(?! \$)|(?P<n2>({BYTE})+){NOT_HEXA} \$(?P<delimiter>{BYTE}){NOT_HEXA})"
    CHUNK = rf"(?P<chunk>(\[\$(?P<n1>{DATA})\](,Y)?)|\(\$(?P<n2>{DATA})(,S)?\),Y|\(\$(?P<n3>{DATA})(,X)?\)|\$(?P<n4>{DATA}),[SXY]|#\$(?P<n5>{DATA})(,#\$(?P<mov2>{BYTE}))?|\$(?P<n6>{DATA}))"
    FLAGS = r"^m=(8|16|true|false),x=(8|16|true|false)$"
    LABEL = r"(?P<label>[a-z][0-9a-z_]+)"
    SNES_ADDRESS = rf"(?P<snes_address>[C-F][0-9A-F]/{TWO_BYTES})"
    LABEL_LINE = rf"^{LABEL}(={SNES_ADDRESS})?"
    POINTER = rf"^ +ptr ((?P<chunk>\$(?P<number>{TWO_BYTES}))|{LABEL})"
    INSTRUCTION = rf"^ +(?P<command>[A-Z]{{3}})( {CHUNK})?"
    BRANCHING_INSTRUCTION = rf"^ +(?P<command>(BCC|BCS|BEQ|BMI|BNE|BPL|BRA|BRL|BVC|BVS|JMP|JML|JSR|JSL)) ({CHUNK}|{LABEL})"

class ToLineMixin:
    @abstractmethod
    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        pass

