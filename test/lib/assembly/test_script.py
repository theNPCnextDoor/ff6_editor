from pathlib import Path

import pytest

from src.lib.assembly.artifact.variables import Variables
from src.lib.assembly.data_structure.blob import Blob
from src.lib.assembly.data_structure.array import Array
from src.lib.assembly.data_structure.instruction.operand import Operand, OperandType
from src.lib.assembly.data_structure.string.string import String, StringTypes
from src.lib.assembly.bytes import Bytes, Endian
from src.lib.assembly.artifact.flags import Flags
from src.lib.assembly.data_structure.instruction.instruction import Instruction
from src.lib.assembly.artifact.variable import Label, SimpleVar
from src.lib.assembly.data_structure.pointer import Pointer
from src.lib.assembly.script import (
    Script,
    ScriptMode,
    ScriptSection,
    SubSection,
)
from src.lib.misc.exception import LineConflict, UnrecognizedLine
from src.lib.assembly.data_structure.string.charset import MENU_CHARSET, Charset
from test import RESOURCES_FOLDER
from test.lib.assembly.conftest import TEST_BYTE, TEST_WORD, TEST_POSITION, ALFA, BRAVO


CONFLICTING_FILE_1 = Path(RESOURCES_FOLDER, "conflicting_file_1.asm")
CONFLICTING_FILE_2 = Path(RESOURCES_FOLDER, "conflicting_file_2.asm")
CONFLICTING_LABELS_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_labels_script.asm")
CONFLICTING_LINES_SCRIPT = Path(RESOURCES_FOLDER, "conflicting_lines_script.asm")
DUMMY_INPUT_SCRIPT_1 = Path(RESOURCES_FOLDER, "dummy_input_script_1.asm")
DUMMY_INPUT_SCRIPT_2 = Path(RESOURCES_FOLDER, "dummy_input_script_2.asm")
DUMMY_ERROR_SCRIPT = Path(RESOURCES_FOLDER, "dummy_error_script.asm")
DUMMY_OUTPUT_SCRIPT = Path(RESOURCES_FOLDER, "dummy_output_script.asm")
DUMMY_INPUT_ROM = Path(RESOURCES_FOLDER, "dummy_input_rom.sfc")
DUMMY_OUTPUT_ROM = Path(RESOURCES_FOLDER, "dummy_output_rom.sfc")


class ScriptImpl:
    def __init__(self):
        self.script = Script()

        self.script.flags = Flags()

        self.script.variables = Variables(
            ALFA,
            BRAVO,
            SimpleVar(Bytes.from_int(0), "delta"),
            Label(value=Bytes.from_position(0x000001), name="start"),
            Label(value=Bytes.from_position(0x000005), name="archie"),
            Label(Bytes.from_position(0x001234)),
            Label(value=Bytes([0x12, 0x00, 0x01]), name="anchor_1"),
            Label(value=Bytes([0x00, 0xFE, 0xDC])),
        )

        self.script.pointers = [
            Pointer(
                position=Bytes([0x00, 0x00, 0x01]),
                operand=Operand(Bytes([0x12, 0x34]), variable=self.script.variables[5]),
            ),
            Pointer(
                position=Bytes([0x00, 0x00, 0x03]),
                operand=Operand(Bytes([0x00, 0x05]), variable=self.script.variables[4]),
            ),
        ]

        self.script.instructions = [
            Instruction(position=Bytes([0x00, 0x00, 0x05]), opcode=Bytes([0xAA]), operands=None),
            Instruction(
                position=Bytes([0x00, 0x00, 0x06]),
                opcode=Bytes([0xA1]),
                operands=[Operand(TEST_BYTE, "(_,X)", variable=ALFA)],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x0B]), opcode=Bytes([0xC2]), operands=[Operand(Bytes([0x30]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x0D]),
                opcode=Bytes([0xA9]),
                operands=[Operand(Bytes([0x12, 0x34]), "#_", variable=BRAVO)],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x10]),
                opcode=Bytes([0xA2]),
                operands=[
                    Operand(
                        Bytes([0xFE, 0xDC]), "#_", variable=Label(value=Bytes([0x00, 0xFE, 0xDC]), name="label_c0fedc")
                    )
                ],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x13]), opcode=Bytes([0xE2]), operands=[Operand(Bytes([0x30]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x15]),
                opcode=Bytes([0xA9]),
                operands=[
                    Operand(Bytes([0x00]), "#_", variable=Label(value=Bytes([0x00, 0xFE, 0xDC]), name="label_c0fedc"))
                ],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x17]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xCC]), "#_")]
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x19]),
                opcode=Bytes([0x44]),
                operands=[Operand(Bytes([0x34]), "#_"), Operand(Bytes([0x12]), "#_", variable=ALFA)],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x1C]),
                opcode=Bytes([0x4C]),
                operands=[
                    Operand(
                        Bytes([0x00, 0x05]),
                        "_",
                        OperandType.JUMPING,
                        variable=Label(value=Bytes([0x00, 0x00, 0x05]), name="archie"),
                    )
                ],
            ),
            Instruction(
                position=Bytes([0x00, 0x00, 0x1F]),
                opcode=Bytes([0x80]),
                operands=[
                    Operand(
                        Bytes([0xE0]),
                        "_",
                        OperandType.BRANCHING,
                        variable=Label(value=Bytes([0x00, 0x00, 0x01]), name="start"),
                    )
                ],
            ),
        ]

        self.script.blobs = [
            Blob(position=Bytes([0x00, 0x00, 0x21]), operand=Operand(TEST_WORD)),
            Blob(
                position=Bytes([0x00, 0x00, 0x23]),
                operand=Operand(Bytes([0x56, 0x78])),
                delimiter=Operand(Bytes([0xFF])),
            ),
            Blob(
                position=Bytes([0x00, 0x00, 0x26]),
                operand=Operand(Bytes([0xAB, 0xCD])),
                delimiter=Operand(Bytes([0x00]), variable=self.script.variables[2]),
            ),
            String(
                position=Bytes([0x00, 0x00, 0x29]),
                operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xFF], endian=Endian.BIG)),
                delimiter=Operand(Bytes([0x88])),
            ),
            String(
                position=Bytes([0x00, 0x00, 0x34]),
                operand=Operand(Bytes([0x81, 0xA8, 0x9B, 0x01, 0xDC], endian=Endian.BIG)),
                delimiter=Operand(Bytes([0x00])),
                string_type=StringTypes.DESCRIPTION,
            ),
        ]

        self.script.arrays = [
            Array(
                blobs=[
                    Blob(position=Bytes([0x00, 0x00, 0x2E]), operand=Operand(Bytes([0xAA]))),
                    String(position=Bytes([0x00, 0x00, 0x2F]), operand=Operand(Bytes([0x9A]))),
                    Blob(
                        position=Bytes([0x00, 0x00, 0x30]),
                        operand=Operand(Bytes([0xBB])),
                        delimiter=Operand(Bytes([0xFF])),
                    ),
                    String(
                        position=Bytes([0x00, 0x00, 0x32]),
                        operand=Operand(Bytes([0x9B])),
                        delimiter=Operand(Bytes([0x00])),
                    ),
                ],
                position=Bytes([0x00, 0x00, 0x2E]),
            )
        ]

        # Relative pointers
        self.script.pointers.append(
            Pointer(
                position=Bytes([0x00, 0x00, 0x3A]),
                operand=Operand(Bytes([0x34, 0x55]), variable=Label(Bytes.from_position(0x123456))),
                anchor=Operand(Bytes([0x12, 0x00, 0x01])),
            )
        )
        self.script.pointers.append(
            Pointer(
                position=Bytes([0x00, 0x00, 0x3C]),
                operand=Operand(Bytes([0x34, 0x56]), variable=Label(Bytes.from_position(0x123457))),
                anchor=Operand(Bytes([0x12, 0x00, 0x01])),
            )
        )
        self.script.pointers.append(
            Pointer(
                position=Bytes([0x00, 0x00, 0x3E]),
                operand=Operand(Bytes([0x34, 0x55]), variable=Label(Bytes.from_position(0x123457))),
                anchor=Operand(Bytes([0x12, 0x00, 0x02])),
            )
        )


class TestScript:

    def test_from_script(self):
        script = Script.from_text_files(DUMMY_INPUT_SCRIPT_1, DUMMY_INPUT_SCRIPT_2)

        labels = script.variables.labels

        assert len(labels) == 5
        assert labels[0] == Label(value=Bytes([0x00, 0x00, 0x01]), name="start")
        assert labels[1] == Label(value=Bytes([0x00, 0x00, 0x05]), name="archie")
        assert labels[2] == Label(value=Bytes([0x12, 0x00, 0x01]), name="anchor_1")
        assert labels[3] == Label(value=TEST_POSITION, name="rptr_1")
        assert labels[4] == Label(value=Bytes([0x12, 0x34, 0x57]), name="rptr_2")

        assert len(script.pointers) == 5
        assert script.pointers[0] == Pointer(position=Bytes([0x00, 0x00, 0x01]), operand=Operand(Bytes([0x12, 0x34])))
        assert script.pointers[1] == Pointer(position=Bytes([0x00, 0x00, 0x03]), operand=Operand(Bytes([0x00, 0x05])))
        assert script.pointers[2] == Pointer(
            position=Bytes([0x00, 0x00, 0x3A]),
            anchor=Operand(Bytes([0x12, 0x00, 0x01]), variable=labels[2]),
            operand=Operand(Bytes([0x34, 0x55]), variable=labels[3]),
        )
        assert script.pointers[3] == Pointer(
            position=Bytes([0x00, 0x00, 0x3C]),
            anchor=Operand(Bytes([0x12, 0x00, 0x01]), variable=labels[2]),
            operand=Operand(Bytes([0x34, 0x56]), variable=labels[4]),
        )
        assert script.pointers[4] == Pointer(
            position=Bytes([0x00, 0x00, 0x3E]),
            anchor=Operand(Bytes([0x12, 0x00, 0x02])),
            operand=Operand(Bytes([0x34, 0x55]), variable=labels[4]),
        )

        assert len(script.instructions) == 12
        assert script.instructions[0] == Instruction(
            position=Bytes([0x00, 0x00, 0x05]), opcode=Bytes([0xAA]), operands=None
        )
        assert script.instructions[1] == Instruction(
            position=Bytes([0x00, 0x00, 0x06]),
            opcode=Bytes([0xA1]),
            operands=[Operand(TEST_BYTE, "(_,X)", variable=ALFA)],
        )
        assert script.instructions[2] == Instruction(
            position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )

        assert script.instructions[3] == Instruction(
            position=Bytes([0x00, 0x00, 0x0B]), opcode=Bytes([0xC2]), operands=[Operand(Bytes([0x30]), "#_")]
        )
        assert script.instructions[4] == Instruction(
            position=Bytes([0x00, 0x00, 0x0D]),
            opcode=Bytes([0xA9]),
            operands=[Operand(Bytes([0x12, 0x34]), "#_", variable=BRAVO)],
        )
        assert script.instructions[5] == Instruction(
            position=Bytes([0x00, 0x00, 0x10]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )

        assert script.instructions[6] == Instruction(
            position=Bytes([0x00, 0x00, 0x13]), opcode=Bytes([0xE2]), operands=[Operand(Bytes([0x30]), "#_")]
        )
        assert script.instructions[7] == Instruction(
            position=Bytes([0x00, 0x00, 0x15]), opcode=Bytes([0xA9]), operands=[Operand(Bytes([0xBB]), "#_")]
        )
        assert script.instructions[8] == Instruction(
            position=Bytes([0x00, 0x00, 0x17]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xCC]), "#_")]
        )

        assert script.instructions[9] == Instruction(
            position=Bytes([0x00, 0x00, 0x19]),
            opcode=Bytes([0x44]),
            operands=[Operand(Bytes([0x34]), "#_"), Operand(Bytes([0x12]), "#_", variable=ALFA)],
        )
        assert script.instructions[10] == Instruction(
            position=Bytes([0x00, 0x00, 0x1C]),
            opcode=Bytes([0x4C]),
            operands=[
                Operand(
                    Bytes([0x00, 0x05]), "_", OperandType.JUMPING, Label(value=Bytes([0x00, 0x00, 0x05]), name="archie")
                )
            ],
        )
        assert script.instructions[11] == Instruction(
            position=Bytes([0x00, 0x00, 0x1F]),
            opcode=Bytes([0x80]),
            operands=[
                Operand(Bytes([0xE0]), "_", OperandType.BRANCHING, Label(value=Bytes([0x00, 0x00, 0x01]), name="start"))
            ],
        )

        assert len(script.blobs) == 5
        assert script.blobs[0] == Blob(position=Bytes([0x00, 0x00, 0x21]), operand=Operand(TEST_WORD, variable=BRAVO))
        assert script.blobs[1] == Blob(
            position=Bytes([0x00, 0x00, 0x23]), operand=Operand(Bytes([0x56, 0x78])), delimiter=Operand(Bytes([0xFF]))
        )
        assert script.blobs[2] == Blob(
            position=Bytes([0x00, 0x00, 0x26]),
            operand=Operand(Bytes([0xAB, 0xCD])),
            delimiter=Operand(Bytes([0x00]), variable=SimpleVar(Bytes.from_int(0), "delta")),
        )
        assert script.blobs[3] == String(
            position=Bytes([0x00, 0x00, 0x29]),
            operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xFE])),
            delimiter=Operand(Bytes([0x88])),
        )
        assert script.blobs[4] == String(
            position=Bytes([0x00, 0x00, 0x34]),
            operand=Operand(Bytes([0x81, 0xA8, 0x9B, 0x01, 0xDC])),
            delimiter=Operand(Bytes([0x00])),
            string_type=StringTypes.DESCRIPTION,
        )

        assert len(script.arrays) == 1
        assert len(script.arrays[0].blobs) == 4
        assert script.arrays[0].blobs[0] == Blob(position=Bytes([0x00, 0x00, 0x2E]), operand=Operand(Bytes([0xAA])))
        assert script.arrays[0].blobs[1] == String(position=Bytes([0x00, 0x00, 0x2F]), operand=Operand(Bytes([0x9A])))
        assert script.arrays[0].blobs[2] == Blob(
            position=Bytes([0x00, 0x00, 0x30]), operand=Operand(Bytes([0xBB])), delimiter=Operand(Bytes([0xFF]))
        )

    def test_from_script_file_raises_error_when_line_is_unrecognized(self):
        with pytest.raises(UnrecognizedLine) as e:
            Script.from_text_files(DUMMY_ERROR_SCRIPT)
        assert "is not recognized." in str(e.value)

    def test_from_script_files_raises_error_when_lines_conflict(self):
        with pytest.raises(LineConflict) as e:
            Script.from_text_files(CONFLICTING_LINES_SCRIPT)
        assert (
            str(e.value)
            == "Lines '  LDA #$1234 ; C01234' and '  LDX #$5678 ; C01235' are conflicting with one another."
        )

    def test_from_script_files_raises_error_when_lines_conflict_in_multiple_files(self):
        with pytest.raises(LineConflict) as e:
            Script.from_text_files(CONFLICTING_FILE_1, CONFLICTING_FILE_2)
        assert str(e.value) == "Lines '  TAX ; C01237' and '  STA $1337 ; C01237' are conflicting with one another."

    def test_to_rom(self):
        with open(DUMMY_OUTPUT_ROM, "wb") as f:
            f.write(b"\x00")

        ScriptImpl().script.to_rom(output_path=DUMMY_OUTPUT_ROM)
        with open(DUMMY_OUTPUT_ROM, "rb") as f:
            output = f.read()

        assert output[0x00:0x01] == b"\x00"  # Padding
        assert output[0x01:0x03] == b"\x34\x12"  # ptr !label_c01234
        assert output[0x03:0x05] == b"\x05\x00"  # ptr !archie
        assert output[0x05:0x06] == b"\xaa"  # TAX
        assert output[0x06:0x08] == b"\xa1\x12"  # LDA (alfa,X)
        assert output[0x08:0x0B] == b"\xa2\xdc\xfe"  # LDX #$FEDC
        assert output[0x0B:0x0D] == b"\xc2\x30"  # REP #$30
        assert output[0x0D:0x10] == b"\xa9\x34\x12"  # LDA #bravo
        assert output[0x10:0x13] == b"\xa2\xdc\xfe"  # LDX #!label_c0fedc
        assert output[0x13:0x15] == b"\xe2\x30"  # SEP #$30
        assert output[0x15:0x17] == b"\xa9\xc0"  # LDA #.label_c0fedc
        assert output[0x17:0x19] == b"\xa2\xcc"  # LDX #$CC
        assert output[0x19:0x1C] == b"\x44\x34\x12"  # MVP #$34,#alfa
        assert output[0x1C:0x1F] == b"\x4c\x05\x00"  # JMP !archie
        assert output[0x1F:0x21] == b"\x80\xe0"  # BRA start
        assert output[0x21:0x23] == b"\x34\x12"  # bravo
        assert output[0x23:0x26] == b"\x78\x56\xff"  # $5678,$FF
        assert output[0x26:0x29] == b"\xcd\xab\x00"  # $ABCD,delta
        assert output[0x29:0x2E] == b"\x00\x80\xd8\xff\x88"  # "<0x00>A<KNIFE>_",$88
        assert output[0x2E:0x34] == b"\xaa\x9a\xbb\xff\x9b\x00"  # $AA | "a" | $BB,$FF | "b",$00
        assert output[0x34:0x3A] == b"\x81\xa8\x9b\x01\xdc\x00"  # desc "Bob<LINE><FIRE>",$00
        assert output[0x3A:0x3C] == b"\x55\x34"  # rptr !label_d23456
        assert output[0x3C:0x3E] == b"\x56\x34"  # rptr !label_d23457
        assert output[0x3E:0x40] == b"\x55\x34"  # rptr !label_d23457

    def test_from_rom(self):
        sections = [
            ScriptSection(start=0x000000, end=0x000008, mode=ScriptMode.POINTERS),
            ScriptSection(start=0x000008, end=0x000012, mode=ScriptMode.INSTRUCTIONS, flags=Flags()),
            ScriptSection(start=0x000012, end=0x000014, mode=ScriptMode.BLOBS, length=2),
            ScriptSection(start=0x000014, end=0x000017, mode=ScriptMode.BLOBS, delimiter=Bytes([0xFF])),
            ScriptSection(start=0x000017, end=0x00001A, mode=ScriptMode.BLOBS, delimiter=Bytes([0x00])),
            ScriptSection(
                start=0x00001A,
                end=0x00001F,
                mode=ScriptMode.MENU_STRINGS,
                delimiter=b"\x88",
                charset=Charset(charset=MENU_CHARSET),
            ),
            ScriptSection(
                start=0x00001F,
                end=0x000025,
                mode=ScriptMode.ARRAYS,
                sub_sections=[
                    SubSection(mode=ScriptMode.BLOBS, length=1),
                    SubSection(mode=ScriptMode.MENU_STRINGS, length=1),
                    SubSection(mode=ScriptMode.BLOBS, delimiter=Bytes([0xFF])),
                    SubSection(mode=ScriptMode.MENU_STRINGS, delimiter=Bytes([0x00])),
                ],
            ),
        ]
        script = Script.from_rom(filename=DUMMY_INPUT_ROM, sections=sections)

        assert len(script.pointers) == 4
        assert script.pointers[0] == Pointer(position=Bytes([0x00, 0x00, 0x00]), operand=Operand(Bytes([0x23, 0x01])))
        assert script.pointers[1] == Pointer(position=Bytes([0x00, 0x00, 0x02]), operand=Operand(Bytes([0x67, 0x45])))
        assert script.pointers[2] == Pointer(position=Bytes([0x00, 0x00, 0x04]), operand=Operand(Bytes([0xAB, 0x89])))
        assert script.pointers[3] == Pointer(position=Bytes([0x00, 0x00, 0x06]), operand=Operand(Bytes([0xEF, 0xCD])))

        assert len(script.instructions) == 5
        assert script.instructions[0] == Instruction(position=Bytes([0x00, 0x00, 0x08]), opcode=Bytes([0x00]))
        assert script.instructions[1] == Instruction(position=Bytes([0x00, 0x00, 0x09]), opcode=Bytes([0xAA]))
        assert script.instructions[2] == Instruction(
            position=Bytes([0x00, 0x00, 0x0A]), opcode=Bytes([0xA9]), operands=[Operand(Bytes([0x34, 0x56]), "#_")]
        )
        assert script.instructions[3] == Instruction(
            position=Bytes([0x00, 0x00, 0x0D]), opcode=Bytes([0xA2]), operands=[Operand(Bytes([0xFE, 0xDC]), "#_")]
        )
        assert script.instructions[4] == Instruction(
            position=Bytes([0x00, 0x00, 0x10]),
            opcode=Bytes([0x80]),
            operands=[Operand(Bytes([0xFE]), "_", OperandType.BRANCHING, Label(Bytes.from_position(0x10)))],
        )

        assert len(script.blobs) == 4
        assert script.blobs[0] == Blob(position=Bytes([0x00, 0x00, 0x12]), operand=Operand(Bytes([0x34, 0x12])))
        assert script.blobs[1] == Blob(
            position=Bytes([0x00, 0x00, 0x14]), operand=Operand(Bytes([0x78, 0x56])), delimiter=Operand(Bytes([0xFF]))
        )
        assert script.blobs[2] == Blob(
            position=Bytes([0x00, 0x00, 0x17]), operand=Operand(Bytes([0xCD, 0xAB])), delimiter=Operand(Bytes([0x00]))
        )
        assert script.blobs[3] == Blob(
            position=Bytes([0x00, 0x00, 0x1A]),
            operand=Operand(Bytes([0x00, 0x80, 0xD8, 0xFF])),
            delimiter=Operand(Bytes([0x88])),
        )

        labels = script.variables.labels

        assert len(labels) == 5
        assert labels[0] == Label(value=Bytes([0x00, 0x00, 0x10]))
        assert labels[1] == Label(value=Bytes([0x00, 0x23, 0x01]))
        assert labels[2] == Label(value=Bytes([0x00, 0x67, 0x45]))
        assert labels[3] == Label(value=Bytes([0x00, 0xAB, 0x89]))
        assert labels[4] == Label(value=Bytes([0x00, 0xEF, 0xCD]))

    def test_to_script_file(self):
        ScriptImpl().script.to_text_file(filename=DUMMY_OUTPUT_SCRIPT, flags=Flags(m=8, x=8))
        with open(DUMMY_OUTPUT_SCRIPT) as f:
            script = f.read()
        assert script == (
            """m=8,x=8

db alfa = $12
dw bravo = $1234
db delta = $00

@start = $C00001
  ptr !label_c01234
  ptr !archie
@archie
  TAX
  LDA (alfa,X)
  LDX #$FEDC
  REP #$30
  LDA #bravo
  LDX #!label_c0fedc
  SEP #$30
  LDA #.label_c0fedc
  LDX #$CC
  MVP #$34,#alfa
  JMP !archie
  BRA start
  $1234
  $5678,$FF
  $ABCD,delta
  "<0x00>A<KNIFE>_",$88
  $AA | "a" | $BB,$FF | "b",$00
  desc "Bob<LINE><FIRE>",$00

#anchor_1
  rptr !label_d23456
  rptr !label_d23457

#$D20002
  rptr !label_d23457

@label_c01234 = $C01234

@label_c0fedc = $C0FEDC

@anchor_1 = $D20001

@label_d23456 = $D23456

@label_d23457 = $D23457"""
        )
