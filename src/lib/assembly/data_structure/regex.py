class Regex:
    COMMENTED_LINE = r'[^";]*("[^"]+"[^";]*)?(?P<comment>(;.*)?)'
    NOT_HEXA = r"(?![0-9A-F])"
    BYTE = r"[0-9A-F]{2}"
    WORD = rf"[0-9A-F]{{4}}{NOT_HEXA}"
    DATA = rf"({BYTE}){{1,3}}{NOT_HEXA}"
    CHAR = r"[0-9a-zA-Z!?/:“”\'\-.,…;#+\(\)%~=¨↑→↙× _]|<[xA-Z0-9 ]+>"
    VARIABLE = r"[a-z][0-9a-z_]+"
    SNES_ADDRESS = rf"[4-9A-F][0-9A-F]{WORD}"

    DELIMITER = rf"(\.?{VARIABLE}|\${BYTE}){NOT_HEXA}"
    BLOB = rf"(?P<operand>([.!]?{VARIABLE}|\$({BYTE})+){NOT_HEXA})(,(?P<delimiter>{DELIMITER}))?"
    STRING = rf'((?P<string_type>desc) )?"(?P<string>({CHAR})+)"(,(?P<delimiter>{DELIMITER}))?'
    FLAGS = r"m *= *(?P<m_flag>(8|16)), *x *= *(?P<x_flag>(8|16))"
    LABEL = rf"^@(?P<name>{VARIABLE}) *(= *(?P<snes_address>\${SNES_ADDRESS}))?"
    POINTER = rf"(?P<relative>r)?ptr (?P<operand>(\${WORD})|!{VARIABLE})"
    VARIABLE_DECLARATION = rf"d(?P<length>[bw]) (?P<name>{VARIABLE}) *= *(?P<operand>\$({BYTE}){{1,2}})"
    ANCHOR = rf"#(?P<operand>\${SNES_ADDRESS}|{VARIABLE})"


class InstructionRegex:
    OP_VALUE = rf"(\${Regex.DATA}|[.!]?{Regex.VARIABLE})"
    IMMEDIATE_MODE = rf"#{OP_VALUE}"
    ABSOLUTE_MODE = rf"{OP_VALUE}(,[SXY])?"
    DIRECT_MODE = rf"\({OP_VALUE}(,X\)|\),Y|,S\),Y|\))"
    DIRECT_LONG_MODE = rf"\[{OP_VALUE}\](,Y)?"
    OPERAND = rf"{IMMEDIATE_MODE}(,{IMMEDIATE_MODE})?|{DIRECT_MODE}|{DIRECT_LONG_MODE}|{ABSOLUTE_MODE}"
    INSTRUCTION = rf"(?P<command>[A-Z]{{3}})( (?P<operand>{OPERAND}))?"
