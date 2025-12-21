import re

import pytest

from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.instruction import Instruction, BranchingInstruction
from src.lib.misc.exception import NoCandidateException
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import Bytes


class TestInstruction:
    @pytest.mark.parametrize(
        ["line", "flags", "opcode", "data"],
        [
            (" BRK", Flags(), Bytes([0x00]), None),
            (" COP #$FF", Flags(), Bytes([0x02]), Bytes([0xFF])),
            (" MVP #$ED,#$CB", Flags(), Bytes([0x44]), Bytes([0xCB, 0xED])),
            (" TSB $19", Flags(), Bytes([0x04]), Bytes([0x19])),
            (" ORA $CC,S", Flags(), Bytes([0x03]), Bytes([0xCC])),
            (" ORA $99,X", Flags(), Bytes([0x15]), Bytes([0x99])),
            (" ORA $8877,Y", Flags(), Bytes([0x19]), Bytes([0x88, 0x77])),
            (" ORA ($13)", Flags(), Bytes([0x12]), Bytes([0x13])),
            (" ORA ($44),Y", Flags(), Bytes([0x11]), Bytes([0x44])),
            (" ORA ($69,S),Y", Flags(), Bytes([0x13]), Bytes([0x69])),
            (" ORA ($00,X)", Flags(), Bytes([0x01]), Bytes([0x00])),
            (" ORA [$DD]", Flags(), Bytes([0x07]), Bytes([0xDD])),
            (" ORA [$AA],Y", Flags(), Bytes([0x17]), Bytes([0xAA])),
            (" ORA #$1234", Flags(m=16), Bytes([0x09]), Bytes([0x12, 0x34])),
            (" ORA #$12", Flags(m=8), Bytes([0x09]), Bytes([0x12])),
            (" LDY #$1234", Flags(x=16), Bytes([0xA0]), Bytes([0x12, 0x34])),
            (" LDY #$12", Flags(x=8), Bytes([0xA0]), Bytes([0x12])),
            (" ORA $123456", Flags(), Bytes([0x0F]), Bytes([0x12, 0x34, 0x56])),
        ],
    )
    def test_from_regex_match(self, line: str, flags: Flags, opcode: Bytes, data: Bytes):
        match = re.match(Regex.INSTRUCTION_LINE, line)
        instruction = Instruction.from_regex_match(match=match, position=Bytes([0x12, 0x34, 0x56]), flags=flags)
        assert instruction.position == Bytes([0x12, 0x34, 0x56])
        assert instruction.opcode == opcode
        assert instruction.data == data

    @pytest.mark.parametrize(
        ["instruction", "expected"],
        [
            (Instruction(opcode=Bytes([0x00]), data=None), b"\x00"),
            (Instruction(opcode=Bytes([0x10]), data=Bytes([0xFF])), b"\x10\xff"),
            (Instruction(opcode=Bytes([0x54]), data=Bytes([0x12, 0x34])), b"\x54\x34\x12"),
            (BranchingInstruction(opcode=Bytes([0x5C]), data=Bytes([0xD3, 0xE4, 0xF5])), b"\x5c\xf5\xe4\xd3"),
        ],
    )
    def test_to_bytes(self, instruction: Instruction, expected: bytes):
        assert bytes(instruction) == expected

    @pytest.mark.parametrize(
        ["command", "mode", "length", "flags", "opcode"],
        [
            ("BRK", "_", 0, Flags(), Bytes([0x00])),
            ("COP", "#$_", 1, Flags(m=True), Bytes([0x02])),
            ("MVP", "#$_,#$_", 2, Flags(x=True), Bytes([0x44])),
            ("TSB", "$_", 1, Flags(), Bytes([0x04])),
            ("ORA", "$_,S", 1, Flags(), Bytes([0x03])),
            ("ORA", "$_,X", 1, Flags(), Bytes([0x15])),
            ("ORA", "$_,Y", 2, Flags(), Bytes([0x19])),
            ("ORA", "($_)", 1, Flags(), Bytes([0x12])),
            ("ORA", "($_),Y", 1, Flags(), Bytes([0x11])),
            ("ORA", "($_,S),Y", 1, Flags(), Bytes([0x13])),
            ("ORA", "($_,X)", 1, Flags(), Bytes([0x01])),
            ("ORA", "[$_]", 1, Flags(), Bytes([0x07])),
            ("ORA", "[$_],Y", 1, Flags(), Bytes([0x17])),
            ("ORA", "#$_", 2, Flags(m=16), Bytes([0x09])),
            ("ORA", "#$_", 1, Flags(m=8), Bytes([0x09])),
            ("LDY", "#$_", 2, Flags(x=16), Bytes([0xA0])),
            ("LDY", "#$_", 1, Flags(x=8), Bytes([0xA0])),
            ("ORA", "$_", 3, Flags(), Bytes([0x0F])),
        ],
    )
    def test_find_opcode(self, command: str, mode: str, length: int, flags: Flags, opcode: Bytes):
        assert Instruction.find_opcode(command=command, mode=mode, length=length, flags=flags) == opcode

    @pytest.mark.parametrize(
        ["command", "mode", "length", "flags"],
        [
            ("BRK", "_", 1, Flags()),
            ("BRK", "#$_", 1, Flags(m=8)),
            ("MVP", "$_,$_", 2, Flags(x=8)),
            ("TSB", "$_", 4, Flags()),
            ("ROR", "$_", 0, Flags()),
            ("ORA", "$_,S", 2, Flags()),
            ("ORA", "#$_", 1, Flags(m=16)),
            ("ORA", "#$_", 2, Flags(m=8)),
            ("LDY", "#$_", 1, Flags(x=16)),
            ("LDY", "#$_", 2, Flags(x=8)),
        ],
        ids=[
            "Unallowed length for command with mode _",
            "Unallowed mode for command",
            "Unexisting mode",
            "Length is 4",
            "Length is 0 when mode is not _",
            "Bad length for command when mode is not _",
            "Bad length when flag m is false",
            "Bad length when flag m is true",
            "Bad length when flag x is false",
            "Bad length when flag x is true",
        ],
    )
    def test_find_opcode_but_raises_no_candidate_exception(self, command: str, mode: str, length: int, flags: Flags):
        with pytest.raises(NoCandidateException):
            Instruction.find_opcode(command=command, mode=mode, length=length, flags=flags)

    @pytest.mark.parametrize(
        "line,data",
        [
            ("#$FFEEDD", "FFEEDD"),
            ("#$FF,#$00", "00FF"),
            ("#$1A1A", "1A1A"),
            ("#$123456", "123456"),
            ("$FF", "FF"),
            ("$1A1A", "1A1A"),
            ("$123456", "123456"),
            ("$FF,S", "FF"),
            ("$1A1A,S", "1A1A"),
            ("$123456,S", "123456"),
            ("$FF,X", "FF"),
            ("$1A1A,X", "1A1A"),
            ("$123456,X", "123456"),
            ("$FF,Y", "FF"),
            ("$1A1A,Y", "1A1A"),
            ("$123456,Y", "123456"),
            ("($FF)", "FF"),
            ("($1A1A)", "1A1A"),
            ("($123456)", "123456"),
            ("($FF,X)", "FF"),
            ("($1A1A,X)", "1A1A"),
            ("($123456,X)", "123456"),
            ("($FF),Y", "FF"),
            ("($1A1A),Y", "1A1A"),
            ("($123456),Y", "123456"),
            ("($FF,S),Y", "FF"),
            ("($1A1A,S),Y", "1A1A"),
            ("($123456,S),Y", "123456"),
            ("[$FF]", "FF"),
            ("[$1A1A]", "1A1A"),
            ("[$123456]", "123456"),
            ("[$FF],Y", "FF"),
            ("[$1A1A],Y", "1A1A"),
            ("[$123456],Y", "123456"),
        ],
    )
    def test_regex_data(self, line: str, data: str):
        match = re.match(Regex.CHUNK, line)
        assert Instruction.data(match) == data

    @pytest.mark.parametrize(
        "line,mode",
        [
            ("", "_"),
            ("#$FF,#$00", "#$_,#$_"),
            ("#$FF", "#$_"),
            ("$FF", "$_"),
            ("$FF,S", "$_,S"),
            ("$FF,X", "$_,X"),
            ("$FF,Y", "$_,Y"),
            ("($FF)", "($_)"),
            ("($FF,X)", "($_,X)"),
            ("($FF),Y", "($_),Y"),
            ("($FF,S),Y", "($_,S),Y"),
            ("[$FF]", "[$_]"),
            ("[$FF],Y", "[$_],Y"),
        ],
    )
    def test_regex_mode(self, line: str, mode: str):
        match = re.search(Regex.CHUNK, line)
        assert Instruction.mode(match) == mode

    @pytest.mark.parametrize(
        ["line", "mode", "data"],
        [
            (" AAA", "_", None),
            (" AAA $12", "$_", "12"),
            (" AAA #$12", "#$_", "12"),
            (" AAA #$12,#$34", "#$_,#$_", "3412"),
            (" AAA $12,S", "$_,S", "12"),
            (" AAA $12,X", "$_,X", "12"),
            (" AAA $12,Y", "$_,Y", "12"),
            (" AAA ($12)", "($_)", "12"),
            (" AAA ($12),Y", "($_),Y", "12"),
            (" AAA ($12,S),Y", "($_,S),Y", "12"),
            (" AAA ($12,X)", "($_,X)", "12"),
            (" AAA [$12]", "[$_]", "12"),
            (" AAA [$12],Y", "[$_],Y", "12"),
        ],
    )
    def test_instruction(self, line: str, mode: str, data: str):
        match = re.match(Regex.INSTRUCTION_LINE, line)
        assert Instruction.mode(match) == mode
        assert Instruction.data(match) == data

    @pytest.mark.parametrize(
        ["instruction", "command"],
        [
            (Instruction(opcode=Bytes([0x00]), data=None), "BRK"),
            (Instruction(opcode=Bytes([0xC3]), data=Bytes([0x13])), "CMP"),
        ],
    )
    def test_command(self, instruction: Instruction, command: str):
        assert instruction.command(instruction.opcode) == command

    @pytest.mark.parametrize(
        ["instruction", "is_flag_setter"],
        [
            (Instruction(opcode=Bytes([0x00]), data=None), False),
            (Instruction(opcode=Bytes([0xC3]), data=Bytes([0x13])), False),
            (Instruction(opcode=Bytes([0xC2]), data=Bytes([0x13])), True),
            (Instruction(opcode=Bytes([0xE2]), data=Bytes([0x13])), True),
        ],
        ids=["BRK", "CMP", "REP", "SEP"],
    )
    def test_is_flag_setter(self, instruction: Instruction, is_flag_setter: bool):
        assert instruction.is_flag_setter() == is_flag_setter

    @pytest.mark.parametrize(
        ["instruction", "input", "output"],
        [
            (Instruction(opcode=Bytes([0xC2]), data=Bytes([0x00])), Flags(m=8, x=8), Flags(m=8, x=8)),
            (Instruction(opcode=Bytes([0xC2]), data=Bytes([0x10])), Flags(m=8, x=8), Flags(m=8, x=16)),
            (Instruction(opcode=Bytes([0xC2]), data=Bytes([0x20])), Flags(m=8, x=8), Flags(m=16, x=8)),
            (Instruction(opcode=Bytes([0xC2]), data=Bytes([0x3F])), Flags(m=8, x=8), Flags(m=16, x=16)),
            (
                Instruction(opcode=Bytes([0xC2]), data=Bytes([0x30])),
                Flags(m=16, x=16),
                Flags(m=16, x=16),
            ),
            (
                Instruction(opcode=Bytes([0xE2]), data=Bytes([0x00])),
                Flags(m=16, x=16),
                Flags(m=16, x=16),
            ),
            (
                Instruction(opcode=Bytes([0xE2]), data=Bytes([0x10])),
                Flags(m=16, x=16),
                Flags(m=16, x=8),
            ),
            (
                Instruction(opcode=Bytes([0xE2]), data=Bytes([0x20])),
                Flags(m=16, x=16),
                Flags(m=8, x=16),
            ),
            (Instruction(opcode=Bytes([0xE2]), data=Bytes([0x3F])), Flags(m=16, x=16), Flags(m=8, x=8)),
            (Instruction(opcode=Bytes([0xE2]), data=Bytes([0x30])), Flags(m=8, x=8), Flags(m=8, x=8)),
        ],
    )
    def test_set_flags(self, instruction: Instruction, input: Flags, output: Flags):
        assert instruction.set_flags(input) == output

    @pytest.mark.parametrize(
        ["instruction", "expected"],
        [
            (Instruction(opcode=Bytes([0xAA])), "TAX"),
            (Instruction(opcode=Bytes([0xA9]), data=Bytes([0x12, 0x34])), "LDA #$1234"),
            (Instruction(opcode=Bytes([0x44]), data=Bytes([0x12, 0x34])), "MVP #$12,#$34"),
        ],
    )
    def test_str(self, instruction: Instruction, expected: str):
        assert str(instruction) == expected

    @pytest.mark.parametrize(
        ["instruction", "show_address", "expected"],
        [
            (Instruction(opcode=Bytes([0xAA])), False, "  TAX"),
            (Instruction(opcode=Bytes([0xA9]), data=Bytes([0x12, 0x34])), False, "  LDA #$1234"),
            (Instruction(opcode=Bytes([0x44]), data=Bytes([0x12, 0x34])), False, "  MVP #$12,#$34"),
            (Instruction(opcode=Bytes([0xAA])), True, "  TAX ; C00000"),
            (Instruction(opcode=Bytes([0xA9]), data=Bytes([0x12, 0x34])), True, "  LDA #$1234 ; C00000"),
            (Instruction(opcode=Bytes([0x44]), data=Bytes([0x12, 0x34])), True, "  MVP #$12,#$34 ; C00000"),
        ],
    )
    def test_to_line(self, instruction: Instruction, show_address: bool, expected: str):
        assert instruction.to_line(show_address=show_address) == expected


class TestBranchingInstruction:
    @pytest.mark.parametrize(
        ["position", "destination", "command", "expected_result"],
        [
            (Bytes([0x00, 0x00, 0x80]), Bytes([0x00, 0x00, 0x02]), "BVC", True),
            (Bytes([0x00, 0x00, 0x80]), Bytes([0x00, 0x00, 0x01]), "BVC", False),
            (Bytes([0x00, 0x00, 0x80]), Bytes([0x00, 0x01, 0x01]), "BVS", True),
            (Bytes([0x00, 0x00, 0x80]), Bytes([0x00, 0x01, 0x02]), "BVS", False),
            (Bytes([0x00, 0x80, 0x00]), Bytes([0x00, 0xFF, 0xFF]), "BRL", True),
            (Bytes([0x00, 0x80, 0x00]), Bytes([0x00, 0x00, 0x00]), "BRL", True),
            (Bytes([0x00, 0x80, 0x00]), Bytes([0x00, 0x80, 0x00]), "BRL", True),
            (Bytes([0x00, 0x80, 0x00]), Bytes([0x01, 0x00, 0x00]), "BRL", False),
            (Bytes([0x01, 0x23, 0x45]), Bytes([0x00, 0xFF, 0xFF]), "BVS", False),
            (Bytes([0x12, 0x34, 0x56]), Bytes([0x12, 0x45, 0x67]), "JMP", True),
            (Bytes([0x12, 0x34, 0x56]), Bytes([0xAB, 0xCD, 0xEF]), "JMP", True),
            (Bytes([0x12, 0x34, 0x56]), Bytes([0x12, 0x45, 0x67]), "JSR", True),
            (Bytes([0x12, 0x34, 0x56]), Bytes([0xFF, 0xFF, 0xFF]), "JSR", False),
            (Bytes([0x12, 0x34, 0x56]), Bytes([0xAB, 0xCD, 0xEF]), "JSL", True),
        ],
    )
    def test_is_destination_possible(self, command: str, position: Bytes, destination: Bytes, expected_result: bool):
        assert (
            BranchingInstruction.is_destination_possible(position=position, destination=destination, command=command)
            == expected_result
        )

    @pytest.mark.parametrize(
        ["line", "position", "data"],
        [
            (" BRA #$05", Bytes([0x00, 0x00, 0x00]), Bytes([0x05])),
            (" BRA #$FF", Bytes([0x00, 0x00, 0x00]), Bytes([0xFF])),
            (" BRL #$0005", Bytes([0x00, 0x00, 0x00]), Bytes([0x00, 0x05])),
            (" JMP $1234", Bytes([0x00, 0x00, 0x00]), Bytes([0x12, 0x34])),
            (" JML $D23456", Bytes([0x00, 0x00, 0x00]), Bytes([0xD2, 0x34, 0x56])),
            (" JSR $1234", Bytes([0x00, 0x00, 0x00]), Bytes([0x12, 0x34])),
            (" JSL $D23456", Bytes([0x00, 0x00, 0x00]), Bytes([0xD2, 0x34, 0x56])),
            (" JML label_1", Bytes([0x00, 0x00, 0x00]), Bytes([0xD2, 0x34, 0x56])),
            (" JSL label_1", Bytes([0x12, 0x34, 0x54]), Bytes([0xD2, 0x34, 0x56])),
            (" JMP label_1", Bytes([0x00, 0x00, 0x00]), Bytes([0x34, 0x56])),
            (" BRA label_1", Bytes([0x12, 0x34, 0x54]), Bytes([0x00])),
            (" BRA label_1", Bytes([0x12, 0x34, 0xD4]), Bytes([0x80])),
            (" BRA label_1", Bytes([0x12, 0x33, 0xD5]), Bytes([0x7F])),
            (" BRL label_1", Bytes([0x12, 0x00, 0x00]), Bytes([0x34, 0x53])),
            (" BRL label_1", Bytes([0x12, 0xFF, 0xFF]), Bytes([0x34, 0x54])),
            (" BRL label_1", Bytes([0x12, 0xB4, 0x53]), Bytes([0x80, 0x00])),
            (" BRL label_1", Bytes([0x12, 0xB4, 0x54]), Bytes([0x7F, 0xFF])),
            (" BRL label_1", Bytes([0x12, 0x34, 0x53]), Bytes([0x00, 0x00])),
        ],
    )
    def test_from_regex_match(self, line: str, position: Bytes, data: Bytes, labels: list[Label]):
        match = re.match(Regex.BRANCHING_INSTRUCTION_LINE, line)
        instruction = BranchingInstruction.from_regex_match(match=match, position=position, labels=labels)
        assert instruction.position == position
        assert instruction.data == data

    @pytest.mark.parametrize(
        ["command", "length"], [("BRA", 1), ("BRL", 2), ("JMP", 2), ("JML", 3), ("JSR", 2), ("JSL", 3)]
    )
    def test_find_length(self, command: str, length: int):
        assert BranchingInstruction.find_length(command=command) == length

    @pytest.mark.parametrize(
        ["value", "instruction", "flags"],
        [
            (b"\x00", Instruction(opcode=Bytes([0x00])), Flags()),
            (b"\x44\x30", Instruction(opcode=Bytes([0x44]), data=Bytes([0x30])), Flags()),
            (b"\xa9\x34\x12", Instruction(opcode=Bytes([0xA9]), data=Bytes([0x12, 0x34])), Flags()),
            (b"\xa9\x56", Instruction(opcode=Bytes([0xA9]), data=Bytes([0x56])), Flags(m=8)),
            (b"\xa2\x34\x12", Instruction(opcode=Bytes([0xA2]), data=Bytes([0x12, 0x34])), Flags()),
            (b"\xa2\x56", Instruction(opcode=Bytes([0xA2]), data=Bytes([0x56])), Flags(x=8)),
            (b"\x4f\x56\x34\x12", Instruction(opcode=Bytes([0x4F]), data=Bytes([0x12, 0x34, 0x56])), Flags()),
        ],
    )
    def test_from_bytes(self, value: bytes, instruction: Instruction, flags: Flags):
        assert Instruction.from_bytes(value=value, flags=flags) == instruction

    @pytest.mark.parametrize(
        ["instruction", "show_address", "output"],
        [
            (
                BranchingInstruction(
                    position=Bytes([0x12, 0x00, 0x00]),
                    opcode=Bytes([0x4C]),
                    destination=Bytes([0x12, 0x34, 0x56]),
                ),
                True,
                "  JMP label_1 ; D20000",
            ),
            (
                BranchingInstruction(
                    position=Bytes([0x12, 0x00, 0x00]),
                    opcode=Bytes([0x4C]),
                    destination=Bytes([0x12, 0x34, 0x57]),
                ),
                True,
                "  JMP $3457 ; D20000",
            ),
            (
                BranchingInstruction(
                    position=Bytes([0x12, 0x00, 0x00]),
                    opcode=Bytes([0x4C]),
                    destination=Bytes([0x12, 0x34, 0x56]),
                ),
                False,
                "  JMP label_1",
            ),
            (
                BranchingInstruction(
                    position=Bytes([0x12, 0x00, 0x00]),
                    opcode=Bytes([0x4C]),
                    destination=Bytes([0x12, 0x34, 0x57]),
                ),
                False,
                "  JMP $3457",
            ),
        ],
    )
    def test_to_line(self, instruction: BranchingInstruction, show_address: bool, labels: list[Label], output: str):
        assert instruction.to_line(show_address=show_address, labels=labels) == output
