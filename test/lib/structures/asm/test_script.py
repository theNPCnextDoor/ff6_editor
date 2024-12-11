from pathlib import Path

from src.lib.structures.bytes import Bytes, Position
from src.lib.structures.asm.flags import Flags
from src.lib.structures.asm.instruction import Instruction, BranchingInstruction
from src.lib.structures.asm.label import Label
from src.lib.structures.asm.pointer import Pointer
from src.lib.structures.asm.script import Script, ScriptMode, ScriptSection
from test import TEST_FOLDER

DUMMY_INPUT_SCRIPT = Path(TEST_FOLDER, "dummy_input_script.asm")
DUMMY_OUTPUT_SCRIPT = Path(TEST_FOLDER, "dummy_output_script.asm")
DUMMY_INPUT_ROM = Path(TEST_FOLDER, "dummy_input_rom.sfc")
DUMMY_OUTPUT_ROM = Path(TEST_FOLDER, "dummy_output_rom.sfc")


class ScriptImpl:
    def __init__(self):
        self.script = Script()

        self.script.flags = Flags()

        self.script.labels = [
            Label(position=Position("000001"), name="start"),
            Label(position=Position("000005"), name="archie")
        ]

        self.script.pointers = [
            Pointer(position=Position("000001"), destination=Position("001234")),
            Pointer(position=Position("000003"), destination=Position("000005"))
        ]

        self.script.instructions = [
            Instruction(position=Position("000005"), opcode=Bytes("AA"), data=None),
            Instruction(position=Position("000006"), opcode=Bytes("A1"), data=Bytes("12")),
            Instruction(position=Position("000008"), opcode=Bytes("A2"), data=Bytes("DCFE")),
            Instruction(position=Position("00000B"), opcode=Bytes("C2"), data=Bytes("30")),
            Instruction(position=Position("00000D"), opcode=Bytes("A9"), data=Bytes("5634")),
            Instruction(position=Position("000010"), opcode=Bytes("A2"), data=Bytes("DCFE")),
            Instruction(position=Position("000013"), opcode=Bytes("E2"), data=Bytes("30")),
            Instruction(position=Position("000015"), opcode=Bytes("A9"), data=Bytes("BB")),
            Instruction(position=Position("000017"), opcode=Bytes("A2"), data=Bytes("CC")),
            Instruction(position=Position("000019"), opcode=Bytes("44"), data=Bytes("1234"))
        ]

        self.script.branching_instructions = [
            BranchingInstruction(position=Position("00001C"), opcode=Bytes("4C"), data=Bytes("0500")),
            BranchingInstruction(position=Position("00001F"), opcode=Bytes("80"), data=Bytes("E0"))
        ]


class TestScript:

    def test_from_script(self):
        script = Script.from_script_file(filename=DUMMY_INPUT_SCRIPT)

        assert len(script.labels) == 2
        assert script.labels[0] == Label(position=Position("000001"), name="start")
        assert script.labels[1] == Label(position=Position("000005"), name="archie")

        assert len(script.pointers) == 2
        assert script.pointers[0] == Pointer(position=Position("000001"), destination=Position("001234"))
        assert script.pointers[1] == Pointer(position=Position("000003"), destination=Position("000005"))

        assert len(script.instructions) == 10
        assert script.instructions[0] == Instruction(position=Position("000005"), opcode=Bytes("AA"), data=None)
        assert script.instructions[1] == Instruction(position=Position("000006"), opcode=Bytes("A1"), data=Bytes("12"))
        assert script.instructions[2] == Instruction(position=Position("000008"), opcode=Bytes("A2"), data=Bytes("DCFE"))

        assert script.instructions[3] == Instruction(position=Position("00000B"), opcode=Bytes("C2"), data=Bytes("30"))
        assert script.instructions[4] == Instruction(position=Position("00000D"), opcode=Bytes("A9"), data=Bytes("5634"))
        assert script.instructions[5] == Instruction(position=Position("000010"), opcode=Bytes("A2"), data=Bytes("DCFE"))

        assert script.instructions[6] == Instruction(position=Position("000013"), opcode=Bytes("E2"), data=Bytes("30"))
        assert script.instructions[7] == Instruction(position=Position("000015"), opcode=Bytes("A9"), data=Bytes("BB"))
        assert script.instructions[8] == Instruction(position=Position("000017"), opcode=Bytes("A2"), data=Bytes("CC"))

        assert script.instructions[9] == Instruction(position=Position("000019"), opcode=Bytes("44"), data=Bytes("3412"))

        assert len(script.branching_instructions) == 2
        assert script.branching_instructions[0] == BranchingInstruction(position=Position("00001C"), opcode=Bytes("4C"), data=Bytes("0500"))
        assert script.branching_instructions[1] == BranchingInstruction(position=Position("00001F"), opcode=Bytes("80"), data=Bytes("E0"))

    def test_to_rom(self):

        with open(DUMMY_OUTPUT_ROM, "wb") as f:
            f.write(b"\x00")

        ScriptImpl().script.to_rom(filename=DUMMY_OUTPUT_ROM)
        with open(DUMMY_OUTPUT_ROM, "rb") as f:
            output = f.read()

        assert output == (
            b"\x00" # Script starts at byte 0x000001, so this is a byte of buffer
            b"\x34\x12\x05\x00" # Pointers
            b"\xAA\xA1\x12\xa2\xDC\xFE" # Instructions 0-2
            b"\xC2\x30\xA9\x56\x34\xA2\xDC\xFE" # Instructions 3-5
            b"\xE2\x30\xA9\xBB\xA2\xCC" # Instruction 6-8
            b"\x44\x12\x34\x4C\x05\x00\x80\xE0" # Instruction 9-11
        )

    def test_from_rom(self):
        sections = [
            ScriptSection(start=0x000000, end=0x000008, mode=ScriptMode.POINTERS),
            ScriptSection(start=0x000008, end=0x000012, mode=ScriptMode.INSTRUCTIONS)
        ]
        script = Script.from_rom(filename=DUMMY_INPUT_ROM, sections=sections)

        assert len(script.pointers) == 4
        assert script.pointers[0] == Pointer(position=Position(0x000000), destination=Position("2301"))
        assert script.pointers[1] == Pointer(position=Position(0x000002), destination=Position("6745"))
        assert script.pointers[2] == Pointer(position=Position(0x000004), destination=Position("AB89"))
        assert script.pointers[3] == Pointer(position=Position(0x000006), destination=Position("EFCD"))

        assert len(script.instructions) == 4
        assert script.instructions[0] == Instruction(position=Position(0x000008), opcode=Bytes("00"))
        assert script.instructions[1] == Instruction(position=Position(0x000009), opcode=Bytes("AA"))
        assert script.instructions[2] == Instruction(position=Position(0x00000A), opcode=Bytes("A9"), data=Bytes("3456"))
        assert script.instructions[3] == Instruction(position=Position(0x00000D), opcode=Bytes("A2"), data=Bytes("FEDC"))

        assert len(script.branching_instructions) == 1
        assert script.branching_instructions[0] == BranchingInstruction(position=Position(0x000010), opcode=Bytes("80"), data=Bytes("FE"))

        assert len(script.labels) == 5
        assert script.labels[0] == Label(position=Position(0x002301))
        assert script.labels[1] == Label(position=Position(0x006745))
        assert script.labels[2] == Label(position=Position(0x00AB89))
        assert script.labels[3] == Label(position=Position(0x00EFCD))
        assert script.labels[4] == Label(position=Position(0x000010))

    def test_to_script_file(self):
        ScriptImpl().script.to_script_file(filename=DUMMY_OUTPUT_SCRIPT, flags=Flags(m=True, x=True))
        with open(DUMMY_OUTPUT_SCRIPT) as f:
            script = f.read()
        assert script == (
            """m=8,x=8

start=C0/0001
  ptr label_c01234
  ptr archie
archie
  TAX
  LDA ($12,X)
  LDX #$DCFE
  REP #$30
  LDA #$5634
  LDX #$DCFE
  SEP #$30
  LDA #$BB
  LDX #$CC
  MVP #$12,#$34
  JMP archie
  BRA start

label_c01234=C0/1234"""
        )