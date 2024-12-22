import re

import pytest

from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.instruction import Instruction, BranchingInstruction
from src.lib.misc.exception import NoCandidateException
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.regex import Regex
from src.lib.structures.bytes import Bytes, Position, Endian


class TestInstruction:
    @pytest.mark.parametrize(
        ["line", "flags", "opcode", "data"],
        [
            (" BRK", Flags(), Bytes("00"), None),
            (" COP #$FF", Flags(), Bytes("02"), Bytes("FF")),
            (" MVP #$ED,#$CB", Flags(), Bytes("44"), Bytes("CBED")),
            (" TSB $19", Flags(), Bytes("04"), Bytes("19")),
            (" ORA $CC,S", Flags(), Bytes("03"), Bytes("CC")),
            (" ORA $99,X", Flags(), Bytes("15"), Bytes("99")),
            (" ORA $8877,Y", Flags(), Bytes("19"), Bytes("8877")),
            (" ORA ($13)", Flags(), Bytes("12"), Bytes("13")),
            (" ORA ($44),Y", Flags(), Bytes("11"), Bytes("44")),
            (" ORA ($69,S),Y", Flags(), Bytes("13"), Bytes("69")),
            (" ORA ($00,X)", Flags(), Bytes("01"), Bytes("00")),
            (" ORA [$DD]", Flags(), Bytes("07"), Bytes("DD")),
            (" ORA [$AA],Y", Flags(), Bytes("17"), Bytes("AA")),
            (" ORA #$1234", Flags(m=False), Bytes("09"), Bytes("1234")),
            (" ORA #$12", Flags(m=True), Bytes("09"), Bytes("12")),
            (" LDY #$1234", Flags(x=False), Bytes("A0"), Bytes("1234")),
            (" LDY #$12", Flags(x=True), Bytes("A0"), Bytes("12")),
            (" ORA $123456", Flags(), Bytes("0F"), Bytes("123456")),
        ],
    )
    def test_from_regex_match(self, line: str, flags: Flags, opcode: Bytes, data: Bytes):
        match = re.match(Regex.INSTRUCTION, line)
        instruction = Instruction.from_regex_match(match=match, position=Position("123456"), flags=flags)
        assert instruction.position == Position(0x123456)
        assert instruction.opcode == opcode
        assert instruction.data == data

    @pytest.mark.parametrize(
        ["instruction", "expected"],
        [
            (Instruction(opcode=Bytes("00"), data=None), b"\x00"),
            (Instruction(opcode=Bytes(0x10), data=Bytes("FF")), b"\x10\xFF"),
            (Instruction(opcode=Bytes(0x0F), data=Bytes("123456", in_endian=Endian.LITTLE)), b"\x0F\x12\x34\x56"),
            (Instruction(opcode=Bytes(0x54), data=Bytes("1234")), b"\x54\x12\x34"),
        ],
    )
    def test_to_bytes(self, instruction: Instruction, expected: bytes):
        assert bytes(instruction) == expected

    @pytest.mark.parametrize(
        ["command", "mode", "length", "flags", "opcode"],
        [
            ("BRK", "_", 0, Flags(), Bytes(0x00)),
            ("COP", "#$_", 1, Flags(m=True), Bytes(0x02)),
            ("MVP", "#$_,#$_", 2, Flags(x=True), Bytes(0x44)),
            ("TSB", "$_", 1, Flags(), Bytes(0x04)),
            ("ORA", "$_,S", 1, Flags(), Bytes(0x03)),
            ("ORA", "$_,X", 1, Flags(), Bytes(0x15)),
            ("ORA", "$_,Y", 2, Flags(), Bytes(0x19)),
            ("ORA", "($_)", 1, Flags(), Bytes(0x12)),
            ("ORA", "($_),Y", 1, Flags(), Bytes(0x11)),
            ("ORA", "($_,S),Y", 1, Flags(), Bytes(0x13)),
            ("ORA", "($_,X)", 1, Flags(), Bytes(0x01)),
            ("ORA", "[$_]", 1, Flags(), Bytes(0x07)),
            ("ORA", "[$_],Y", 1, Flags(), Bytes(0x17)),
            ("ORA", "#$_", 2, Flags(m=False), Bytes(0x09)),
            ("ORA", "#$_", 1, Flags(m=True), Bytes(0x09)),
            ("LDY", "#$_", 2, Flags(x=False), Bytes(0xA0)),
            ("LDY", "#$_", 1, Flags(x=True), Bytes(0xA0)),
            ("ORA", "$_", 3, Flags(), Bytes(0x0F)),
        ],
    )
    def test_find_opcode(self, command: str, mode: str, length: int, flags: Flags, opcode: Bytes):
        assert Instruction.find_opcode(command=command, mode=mode, length=length, flags=flags) == opcode

    @pytest.mark.parametrize(
        ["command", "mode", "length", "flags"],
        [
            ("BRK", "_", 1, Flags()),
            ("BRK", "#$_", 1, Flags(m=True)),
            ("MVP", "$_,$_", 2, Flags(x=True)),
            ("TSB", "$_", 4, Flags()),
            ("ROR", "$_", 0, Flags()),
            ("ORA", "$_,S", 2, Flags()),
            ("ORA", "#$_", 1, Flags(m=False)),
            ("ORA", "#$_", 2, Flags(m=True)),
            ("LDY", "#$_", 1, Flags(x=False)),
            ("LDY", "#$_", 2, Flags(x=True)),
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
        match = re.match(Regex.INSTRUCTION, line)
        assert Instruction.mode(match) == mode
        assert Instruction.data(match) == data

    @pytest.mark.parametrize(
        ["instruction", "command"],
        [
            (Instruction(opcode=Bytes("00"), data=None), "BRK"),
            (Instruction(opcode=Bytes("C3"), data=Bytes("13")), "CMP"),
        ],
    )
    def test_command(self, instruction: Instruction, command: str):
        assert instruction.command(instruction.opcode) == command

    @pytest.mark.parametrize(
        ["instruction", "is_flag_setter"],
        [
            (Instruction(opcode=Bytes("00"), data=None), False),
            (Instruction(opcode=Bytes("C3"), data=Bytes("13")), False),
            (Instruction(opcode=Bytes("C2"), data=Bytes("13")), True),
            (Instruction(opcode=Bytes("E2"), data=Bytes("13")), True),
        ],
        ids=["BRK", "CMP", "REP", "SEP"],
    )
    def test_is_flag_setter(self, instruction: Instruction, is_flag_setter: bool):
        assert instruction.is_flag_setter() == is_flag_setter

    @pytest.mark.parametrize(
        ["instruction", "input", "output"],
        [
            (Instruction(opcode=Bytes("C2"), data=Bytes("00")), Flags(m=True, x=True), Flags(m=True, x=True)),
            (Instruction(opcode=Bytes("C2"), data=Bytes("10")), Flags(m=True, x=True), Flags(m=True, x=False)),
            (Instruction(opcode=Bytes("C2"), data=Bytes("20")), Flags(m=True, x=True), Flags(m=False, x=True)),
            (Instruction(opcode=Bytes("C2"), data=Bytes("3F")), Flags(m=True, x=True), Flags(m=False, x=False)),
            (Instruction(opcode=Bytes("C2"), data=Bytes("30")), Flags(m=False, x=False), Flags(m=False, x=False)),
            (Instruction(opcode=Bytes("E2"), data=Bytes("00")), Flags(m=False, x=False), Flags(m=False, x=False)),
            (Instruction(opcode=Bytes("E2"), data=Bytes("10")), Flags(m=False, x=False), Flags(m=False, x=True)),
            (Instruction(opcode=Bytes("E2"), data=Bytes("20")), Flags(m=False, x=False), Flags(m=True, x=False)),
            (Instruction(opcode=Bytes("E2"), data=Bytes("3F")), Flags(m=False, x=False), Flags(m=True, x=True)),
            (Instruction(opcode=Bytes("E2"), data=Bytes("30")), Flags(m=True, x=True), Flags(m=True, x=True)),
        ],
    )
    def test_set_flags(self, instruction: Instruction, input: Flags, output: Flags):
        assert instruction.set_flags(input) == output

    @pytest.mark.parametrize(
        ["instruction", "expected"],
        [
            (Instruction(opcode=Bytes("AA")), "TAX"),
            (Instruction(opcode=Bytes("A9"), data=Bytes("1234")), "LDA #$1234"),
            (Instruction(opcode=Bytes("44"), data=Bytes("1234")), "MVP #$12,#$34"),
        ],
    )
    def test_str(self, instruction: Instruction, expected: str):
        assert str(instruction) == expected

    @pytest.mark.parametrize(
        ["instruction", "show_address", "expected"],
        [
            (Instruction(opcode=Bytes("AA")), False, "  TAX"),
            (Instruction(opcode=Bytes("A9"), data=Bytes("1234")), False, "  LDA #$1234"),
            (Instruction(opcode=Bytes("44"), data=Bytes("1234")), False, "  MVP #$12,#$34"),
            (Instruction(opcode=Bytes("AA")), True, "  TAX # C0/0000"),
            (Instruction(opcode=Bytes("A9"), data=Bytes("1234")), True, "  LDA #$1234 # C0/0000"),
            (Instruction(opcode=Bytes("44"), data=Bytes("1234")), True, "  MVP #$12,#$34 # C0/0000"),
        ],
    )
    def test_to_line(self, instruction: Instruction, show_address: bool, expected: str):
        assert instruction.to_line(show_address=show_address) == expected


class TestBranchingInstruction:
    @pytest.mark.parametrize(
        ["position", "destination", "command", "expected_result"],
        [
            (Position("000080"), Position("000002"), "BVC", True),
            (Position("000080"), Position("000001"), "BVC", False),
            (Position("000080"), Position("000101"), "BVS", True),
            (Position("000080"), Position("000102"), "BVS", False),
            (Position("008000"), Position("00FFFF"), "BRL", True),
            (Position("008000"), Position("000000"), "BRL", True),
            (Position("008000"), Position("008000"), "BRL", True),
            (Position("008000"), Position("010000"), "BRL", False),
            (Position("012345"), Position("00FFFF"), "BVS", False),
            (Position("123456"), Position("124567"), "JMP", True),
            (Position("123456"), Position("ABCDEF"), "JMP", True),
            (Position("123456"), Position("124567"), "JSR", True),
            (Position("123456"), Position("FFFFFF"), "JSR", False),
            (Position("123456"), Position("ABCDEF"), "JSL", True),
        ],
    )
    def test_is_destination_possible(
        self, command: str, position: Position, destination: Position, expected_result: bool
    ):
        assert (
            BranchingInstruction.is_destination_possible(position=position, destination=destination, command=command)
            == expected_result
        )

    @pytest.mark.parametrize(
        ["line", "position", "data"],
        [
            (" BRA #$05", Position("000000"), Bytes("05")),
            (" BRA #$FF", Position("000000"), Bytes("FF")),
            (" BRL #$0005", Position("000000"), Bytes("0005")),
            (" JMP $1234", Position("000000"), Bytes("1234")),
            (" JML $123456", Position("000000"), Bytes("123456")),
            (" JSR $1234", Position("000000"), Bytes("1234")),
            (" JSL $123456", Position("000000"), Bytes("123456")),
            (" JML label_1", Position("000000"), Bytes("563412")),
            (" JSL label_1", Position("123454"), Bytes("563412")),
            (" JMP label_1", Position("000000"), Bytes("5634")),
            (" BRA label_1", Position("123454"), Bytes("00")),
            (" BRA label_1", Position("1234D4"), Bytes("80")),
            (" BRA label_1", Position("1233D5"), Bytes("7F")),
            (" BRL label_1", Position("120000"), Bytes("5334")),
            (" BRL label_1", Position("12FFFF"), Bytes("5434")),
            (" BRL label_1", Position("12B453"), Bytes("0080")),
            (" BRL label_1", Position("12B454"), Bytes("FF7F")),
            (" BRL label_1", Position("123453"), Bytes("0000")),
        ],
    )
    def test_from_regex_match(self, line: str, position: Position, data: Bytes, labels: list[Label]):
        match = re.match(Regex.BRANCHING_INSTRUCTION, line)
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
            (b"\x00", Instruction(opcode=Bytes("00")), Flags()),
            (b"\x44\x30", Instruction(opcode=Bytes("44"), data=Bytes("30")), Flags()),
            (b"\xA9\x34\x12", Instruction(opcode=Bytes("A9"), data=Bytes("1234")), Flags()),
            (b"\xA9\x56", Instruction(opcode=Bytes("A9"), data=Bytes("56")), Flags(m=True)),
            (b"\xA2\x34\x12", Instruction(opcode=Bytes("A2"), data=Bytes("1234")), Flags()),
            (b"\xA2\x56", Instruction(opcode=Bytes("A2"), data=Bytes("56")), Flags(x=True)),
            (b"\x4F\x56\x34\x12", Instruction(opcode=Bytes("4F"), data=Bytes("123456")), Flags()),
        ],
    )
    def test_from_bytes(self, value: bytes, instruction: Instruction, flags: Flags):
        assert Instruction.from_bytes(value=value, flags=flags) == instruction

    @pytest.mark.parametrize(
        ["instruction", "show_address", "output"],
        [
            (
                BranchingInstruction(position=Position(0x120000), opcode=Bytes(0x4C), destination=Position(0x123456)),
                True,
                "  JMP label_1 # D2/0000",
            ),
            (
                BranchingInstruction(position=Position(0x120000), opcode=Bytes(0x4C), destination=Position(0x123457)),
                True,
                "  JMP $5734 # D2/0000",
            ),
            (
                BranchingInstruction(position=Position(0x120000), opcode=Bytes(0x4C), destination=Position(0x123456)),
                False,
                "  JMP label_1",
            ),
            (
                BranchingInstruction(position=Position(0x120000), opcode=Bytes(0x4C), destination=Position(0x123457)),
                False,
                "  JMP $5734",
            ),
        ],
    )
    def test_to_line(self, instruction: BranchingInstruction, show_address: bool, labels: list[Label], output: str):
        assert instruction.to_line(show_address=show_address, labels=labels) == output
