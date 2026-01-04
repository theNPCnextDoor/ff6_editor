from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod

if TYPE_CHECKING:
    from src.lib.assembly.artifact.label import Label


class Regex:
    NOT_HEXA = r"(?![0-9A-F])"
    BYTE = r"[0-9A-F]{2}"
    WORD = rf"[0-9A-F]{{4}}{NOT_HEXA}"
    DATA = rf"({BYTE}){{1,3}}{NOT_HEXA}"
    MENU_CHAR = r"[0-9a-zA-Z!?/:“”\'\-.,…;#+\(\)%~=¨↑→↙× _]|<[xA-Z0-9 ]+>"
    DELIMITER_1 = rf",\$(?P<d1>{BYTE}){NOT_HEXA}"
    DELIMITER_2 = rf",\$(?P<d2>{BYTE}){NOT_HEXA}"
    CHUNK = rf"(?P<chunk>(\[\$(?P<n1>{DATA})\](,Y)?)|\(\$(?P<n2>{DATA})(,S)?\),Y|\(\$(?P<n3>{DATA})(,X)?\)|\$(?P<n4>{DATA}),[SXY]|#\$(?P<n5>{DATA})(,#\$(?P<mov2>{BYTE}))?|\$(?P<n6>{DATA}))"
    VARIABLE = r"[a-z][0-9a-z_]+"
    SNES_ADDRESS = rf"(?P<snes_address>[C-F][0-9A-F]{WORD})"

    BLOB = rf"\$((?P<n1>({BYTE})+){NOT_HEXA}(?!,)|(?P<n2>({BYTE})+){NOT_HEXA}{DELIMITER_1})"
    MENU_STRING = rf'"((?P<s1>({MENU_CHAR})+)"{DELIMITER_2}|(?P<s2>({MENU_CHAR})+)"(?!,))'
    ANY_BLOB = rf"({BLOB}|{MENU_STRING})"

    FLAGS_LINE = r"^m=(8|16|true|false),x=(8|16|true|false)$"
    LABEL_LINE = rf"^@(?P<label>{VARIABLE})(={SNES_ADDRESS})?"
    BLOB_LINE = rf"^ +{BLOB}"
    MENU_STRING_LINE = rf"^ +{MENU_STRING}"
    DESCRIPTION_LINE = rf"^ +(?P<string_type>txt2) {MENU_STRING}"
    BLOB_GROUP_LINE = rf"^ *((((\$({BYTE})+)|\"({MENU_CHAR})+\")(,\${BYTE})?) \| )+(((\$({BYTE})+)|\"({MENU_CHAR})+\")(,\${BYTE})?)( ?;.*)?"
    INSTRUCTION_LINE = rf"^ +(?P<command>[A-Z]{{3}})( {CHUNK})?"
    BRANCHING_INSTRUCTION_LINE = (
        rf"^ +(?P<command>(BCC|BCS|BEQ|BMI|BNE|BPL|BRA|BRL|BVC|BVS|JMP|JML|JSR|JSL)) ({CHUNK}|(?P<label>{VARIABLE}))"
    )
    POINTER_LINE = rf"^ +(?P<is_relative>r)?ptr ((?P<chunk>\$(?P<number>{WORD}))|(?P<label>{VARIABLE}))"
    VARIABLE_ASSIGNMENT = rf"let (?P<length>[.!@])(?P<name>{VARIABLE}) *= *\$(?P<value>{DATA})"
    ANCHOR = rf"^anchor: (\${SNES_ADDRESS}|(?P<label>{VARIABLE}))"


class ToLineMixin:
    @abstractmethod
    def to_line(self, show_address: bool = False, labels: list[Label] | None = None) -> str:
        pass
